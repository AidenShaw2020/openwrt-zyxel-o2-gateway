# Zyxel O2 GateWay / OpenWrt 25.12.6 Source Port

Experimental first release for the tested Zyxel O2 GateWay hardware only.
Read README.md and docs/INSTALL.md before building or flashing. Built images
are not O2/Zyxel web-update packages.

## Contents

Source-only: EN751627 subtarget, device trees, kernel and Ethernet driver
patches, board scripts, `sysupgrade` support, configuration seed, exported
vanilla patch, upstream revision pins, UART/TFTP RAM-boot helper and the
installation guide. No prebuilt images, dependency-source archive, vendor
firmware or device backups are supplied. SHA256SUMS covers the exported patch
only.

## Highlights

- Boot from NAND through the unmodified stock bootloader; squashfs root and
  UBIFS overlay on the former stock slave/data area.
- EcoNet BMT/BBT compatible with the O2 bootloader (250-entry BBT checksum).
- SPI NAND through the manual-mode `airoha,en7523-spi` controller driver.
- Writable `bootflag` partition and `en75_chboot` support for this board.
- Ethernet: 4 × LAN + WAN through DSA, special-tag source port handling,
  Ethernet driver loaded at boot so failsafe has network.
- MT7615 dual-band AP with calibration and MAC addresses from flash; WPS.
- LED and button map from the stock `led.conf`; Internet and WPS indications.
- `sysupgrade` preserving settings, factory reset and failsafe verified.

## Caveats

Validated on one unit only. First installation needs UART access and erases
the stock firmware. Throughput, IPv6, PPPoE/FTTx VLAN and long-term stability
are not validated. DSL and the phone port are unsupported. Fresh root has no
password and management uses HTTP; set a strong password and keep management
on a trusted LAN. See docs/VALIDATION.md.
