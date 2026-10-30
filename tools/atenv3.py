#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
#
# Python translation of Caleb James DeLisle's ATENv3 algorithm:
# https://github.com/cjdelisle/ATENv3/blob/main/atenv3_passwd.c
#
# Derives the Zyxel BootExtension unlock password ("ATEN 1,<password>")
# from the 36 hex character seed printed by "ATSE <product model>".
import sys


def decode(atse):
	if len(atse) != 36:
		raise ValueError('Expected 36 hex characters')
	int(atse, 16)
	a = atse[1::3]
	b = atse[0::3]
	values = [int(b[i:i + 4] + a[i:i + 4], 16) for i in (0, 4, 8)]
	total = sum(int(atse[i] + atse[i + 3], 16) for i in (2, 8, 14))
	tail = int(''.join(atse[i] for i in range(20, 36, 3)), 16)
	key = (tail + (0x10f0a563, 0xbeafbeaf, 0x14387052)[total % 3]) & 0xffffffff
	loops = (key >> (total & 3)) & 0xff
	for _ in range(loops):
		values = [((v >> r) | (v << (32 - r))) & 0xffffffff
			  for v, r in zip(values, (1, 2, 3))]
	return ''.join(str(v ^ key) for v in values)


if __name__ == '__main__':
	# Reference vector from the upstream C implementation.
	assert decode('2400C00C09503316E000148493987B03118E') == \
		'363943360710703246723488897955'
	if len(sys.argv) != 2:
		sys.exit('usage: atenv3.py <36 hex character ATSE seed>')
	print(decode(sys.argv[1]))
