#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
#
# Boot an OpenWrt initramfs image from RAM on the Zyxel O2 GateWay through
# the stock bootloader (UART + TFTP). Nothing is written to flash.
#
# Sequence: stop autoboot -> ZHAL -> ATSE/ATEN unlock -> ATLD (the loader
# acts as a TFTP *server* on 192.168.1.1, the PC uploads) -> ATGU ->
# compare three 256-byte RAM samples with the local file -> jump 80020000.
#
# Requirements: pyserial, tftpy (>= 0.8.7), a PC address in 192.168.1.0/24
# (for example 192.168.1.2) on the cable connected to a LAN port.
#
# usage: o2-ramboot.py --port COM3 --image openwrt-...-initramfs-kernel.bin
#        [--wait-power-cycle | --reboot-command CMD | --at-zhal]
import argparse
import io
import os
import re
import sys
import threading
import time

import serial
import tftpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import atenv3  # noqa: E402

LOAD_ADDR = 0x80020000


class Console:
	def __init__(self, port, log):
		self.port = serial.Serial(port=None, baudrate=115200, timeout=0.1)
		self.port.dtr = False
		self.port.rts = False
		self.port.port = port
		self.port.open()
		self.log = open(log, 'ab', buffering=0) if log else None
		self.buf = bytearray()
		self.lock = threading.Lock()
		self.stop = False
		threading.Thread(target=self._reader, daemon=True).start()

	def _reader(self):
		while not self.stop:
			data = self.port.read(4096)
			if data:
				if self.log:
					self.log.write(data)
				with self.lock:
					self.buf.extend(data)

	def mark(self):
		with self.lock:
			return len(self.buf)

	def wait(self, pattern, start, timeout):
		end = time.time() + timeout
		while time.time() < end:
			with self.lock:
				text = bytes(self.buf[start:])
			match = re.search(pattern, text)
			if match:
				return text, match
			time.sleep(0.05)
		raise TimeoutError('timeout waiting for %r' % pattern)

	def send(self, line):
		self.port.write(line.encode() + b'\r')
		self.port.flush()

	def write(self, data):
		self.port.write(data)
		self.port.flush()

	def close(self):
		self.stop = True
		time.sleep(0.2)
		self.port.close()


def step(msg):
	print('[%s] %s' % (time.strftime('%H:%M:%S'), msg), flush=True)


def unlock(con, model):
	m = con.mark()
	con.send('ATSE ' + model)
	_, match = con.wait(rb'\n([0-9A-F]{36})\r?\n', m, 10)
	m = con.mark()
	con.send('ATEN 1,' + atenv3.decode(match.group(1).decode()))
	con.wait(rb'ZHAL>', m, 10)
	step('BootExtension unlocked')


def upload(con, data, remote, attempts):
	for attempt in range(1, attempts + 1):
		m = con.mark()
		con.send('ATLD %s,0x%08x' % (remote, LOAD_ADDR))
		con.wait(rb'TFTP server is started', m, 10)
		step('loader TFTP server started (attempt %d)' % attempt)
		time.sleep(4)
		src = io.BytesIO(data)
		src.name = remote
		try:
			# The loader occasionally stops acknowledging for a few
			# seconds; allow plenty of retransmissions.
			tftpy.TftpClient('192.168.1.1', 69).upload(
				remote, src, timeout=5, retries=20)
		except Exception as e:  # noqa: BLE001
			step('upload failed: %r' % e)
		try:
			_, match = con.wait(
				rb'Total (\d+) \(0x[0-9A-F]+\) bytes received', m, 30)
		except TimeoutError:
			step('no completion from loader, aborting its TFTP server')
			con.write(b'\x03')
			time.sleep(1.5)
			con.write(b'\r')
			con.wait(rb'ZHAL>', m, 10)
			continue
		con.wait(rb'ZHAL>', m, 10)
		received = int(match.group(1))
		step('loader received %d bytes, image has %d' % (received, len(data)))
		if received == len(data):
			return
	raise RuntimeError('upload failed, not jumping')


def verify_and_jump(con, data):
	m = con.mark()
	con.send('ATGU')
	con.wait(rb'bldr>', m, 10)
	end = LOAD_ADDR + len(data)
	for addr in (LOAD_ADDR, LOAD_ADDR + 0x100000, (end - 256) & ~0xF):
		m = con.mark()
		con.send('dump %x 100' % addr)
		text, _ = con.wait(rb'bldr>', m + 5, 10)
		got = bytearray()
		for line in text.decode('latin1').splitlines():
			match = re.match(
				r'([0-9a-f]{8})  ((?:[0-9a-f]{2}[ .]){15}[0-9a-f]{2})', line)
			if match:
				got += bytes.fromhex(re.sub('[ .]', '', match.group(2)))
		expected = data[addr - LOAD_ADDR:addr - LOAD_ADDR + 256]
		if bytes(got) != expected:
			raise RuntimeError('RAM sample at %x differs, not jumping' % addr)
		step('RAM sample at %x matches' % addr)
	m = con.mark()
	con.send('jump %x' % LOAD_ADDR)
	step('jump %x' % LOAD_ADDR)
	con.wait(rb'Please press Enter to activate this console', m, 180)
	step('OpenWrt userspace is up')


def main():
	ap = argparse.ArgumentParser(description=__doc__)
	ap.add_argument('--port', required=True, help='serial port, e.g. COM3 or /dev/ttyUSB0')
	ap.add_argument('--image', required=True, help='OpenWrt initramfs-kernel.bin')
	ap.add_argument('--model', default='ZYXEL O2 GateWay',
			help='product model for ATSE (as printed by ATSH)')
	ap.add_argument('--log', help='append raw console output to this file')
	ap.add_argument('--attempts', type=int, default=4)
	start = ap.add_mutually_exclusive_group()
	start.add_argument('--wait-power-cycle', action='store_true',
			   help='wait (10 min) for the user to power-cycle the router')
	start.add_argument('--reboot-command', default=None,
			   help='shell command sent to a running system, e.g. /sbin/reboot')
	start.add_argument('--at-zhal', action='store_true',
			   help='the console is already at an unlocked ZHAL> prompt')
	args = ap.parse_args()

	data = open(args.image, 'rb').read()
	remote = os.path.basename(args.image)
	con = Console(args.port, args.log)
	try:
		if not args.at_zhal:
			m = con.mark()
			if args.reboot_command:
				con.send(args.reboot_command)
				step('sent %r' % args.reboot_command)
			else:
				step('waiting for power cycle')
			con.wait(rb'Hit any key to stop autoboot', m, 600)
			con.write(b'\r')
			time.sleep(0.3)
			con.write(b'\r')
			con.wait(rb'ZHAL>', m, 20)
			step('autoboot stopped')
			unlock(con, args.model)
		upload(con, data, remote, args.attempts)
		verify_and_jump(con, data)
	finally:
		con.close()


if __name__ == '__main__':
	main()
