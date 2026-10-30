# Validation

All results below come from one physical Zyxel O2 GateWay (stock firmware
`V5.50(ACBD.0)b2`), tested on 2026-10-30 with privately built images from this
overlay. They do not certify other units, hardware revisions or your own build.

## Boot and storage

- RAM boot through the stock bootloader (`ATLD` + `jump 80020000`), with three
  256-byte RAM samples compared before every jump.
- `spi-nand` with `airoha,en7523-spi` detects the W25N01G (128 MiB, 2048 + 64).
- Before any write, every NAND partition read by Linux (without the BMT) was
  byte-identical to logical backups taken earlier under the stock firmware,
  except the live stock `data` partition. A full physical dump including OOB
  was taken and kept privately.
- `en75_bmt` with the 250-entry BBT checksum patch: "BBT & BMT found",
  1024 blocks, 943 user, 0 factory bad, 0 worn, 81 reserve.
- `tclinux.trx` written with `mtd`, read back with a matching MD5. The
  bootloader accepted it ("main tclinux.bin have ECONET trx header") with boot
  flag 0 and booted it.
- Root on squashfs from NAND, UBI attached automatically (613 PEBs, 0 bad),
  overlay on UBIFS `rootfs_data`. Settings survived reboots.

## Upgrade, reset, failsafe

- `sysupgrade -T` accepts the image (metadata `zyxel,o2-gateway`, magic `2RDH`).
- `sysupgrade` keeping settings: performed twice (once with the hook copied
  into an older build, once natively). Wi-Fi, country and network settings
  were preserved; the router came back from the main slot.
- Factory reset (`factoryreset -y`, the same action as RESET ≥ 5 s): overlay
  erased, defaults regenerated with LAN MAC = base and WAN MAC = base + 1,
  no `board_detect` errors.
- Failsafe entered with `f` on the console: read-only root, `lan1` at
  `192.168.1.1`, ping and SSH from the PC worked. This required loading
  `econet-eth` as a boot module.
- RESET short press (reboot) and the WLAN button were confirmed on hardware.
  Failsafe entered **by the RESET button** and factory reset **by a long press**
  have not been triggered physically; the underlying actions were.

## Network

- `econet_eth` with the EN751627 DSA special tag: all four LAN ports and WAN
  as DSA user ports, link on LAN port 1 and WAN at 1 Gb/s.
- WAN DHCP lease from an upstream router, Internet reachable (ICMP, DNS) from
  the router; LAN client reached the router at `192.168.1.1`.
- No more "rx: on unexpected fport" messages after the sport patch
  (0 messages after about 148,000 WAN frames).
- Throughput, long-term stability, IPv6, PPPoE and the O2 FTTx VLAN (the stock
  firmware probes VLAN 835 on WAN) have **not** been tested.

## Wi-Fi

- MT7615 calibration read through nvmem from `reservearea` is byte-identical
  to the blob validated in earlier RAM tests.
- AP on 2.4 GHz (HT20) and 5 GHz (VHT80), WPA2-PSK, country `CZ`, clients
  connected. Range, throughput and transmit power accuracy were not measured.
- WPS push button: hostapd entered PBC on both radios and a client paired.

## LEDs, buttons, USB

- All LEDs from the stock `led.conf` lit when driven manually; power, LAN, WAN,
  WLAN, Internet and the amber WPS indication work with their triggers.
- RESET, WLAN and WPS buttons generate events.
- USB: xHCI with USB 2.0 and 3.0 root hubs; a FAT32 flash drive was detected
  and read on USB 2.0. Writing and USB 3.0 transfers were not tested.

## Known limitations

- First installation needs UART access and is a manual procedure.
- The loader's TFTP server occasionally stalls for several seconds; clients
  need generous retries (the helper uses 20).
- The Ethernet driver uses one RX interrupt bank; the stock firmware uses four.
  Performance under load has not been characterised.
- Wi-Fi transmit power follows the regulatory defaults; no per-board limits
  beyond the calibration data are applied.
- DSL, the FXS phone port and PCIe port 1 are unsupported.
- Returning to the stock firmware from a backup has not been tested.
