# Third-Party Notices

This project builds on the work of the following projects and their
contributors. Existing notices in imported patches are retained.

- [OpenWrt](https://openwrt.org/): build system, base system, the `econet`
  target and package recipes; the pinned base is identified in README.md.
  OpenWrt is a mixed-license distribution; its component licenses are not
  replaced by this repository's LICENSE.
- [Linux](https://kernel.org/): Linux 6.12.112 with the OpenWrt patch set and
  the included EN751627 changes, principally GPL-2.0-only with per-file licenses.
- EN7528 SoC, timer, PCIe, UART and USB patches by Ahmed Naseef, and the
  Airoha/EcoNet drivers they extend, under their upstream licenses.
- [econet_eth](https://github.com/cjdelisle/econet_eth) and the `en75_bmt`
  driver by Caleb James DeLisle (GPL-2.0-only).
- [ATENv3](https://github.com/cjdelisle/ATENv3) by Caleb James DeLisle
  (GPL-2.0); `tools/atenv3.py` is a Python translation.
- [LuCI](https://github.com/openwrt/luci) and the OpenWrt packages feed.
- [linux-firmware](https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git/):
  MT7615 firmware selected by OpenWrt is governed by its upstream license.

The MT7615 calibration data and the MAC addresses stay in the router's own
flash. This repository does not redistribute Zyxel, O2, EcoNet/Airoha or
MediaTek firmware, calibration or device backups.

Product and organization names identify compatibility and provenance only.
They are not endorsements.
