# Privacy Review

Review date: 2026-10-30.

The publication directory was populated from an explicit allowlist: the files
changed or added in the OpenWrt checkout (`package/kernel/econet-eth`,
`package/kernel/linux/modules/usb.mk`, `target/linux/econet`), the exported
patch generated from exactly those paths, newly written documentation, two
helper tools and one UART wiring photo. The development workspace, device backups and
diagnostic directories were not used as the Git repository.

The source overlay, patch and documentation were scanned for the tested
unit's MAC address, serial number, manufacturing-data strings, service and
Wi-Fi passwords, test SSIDs, private network addresses, build account names,
host names and absolute build paths. The only e-mail addresses present are
upstream authors' `Signed-off-by`/copyright lines in imported kernel patches,
which are retained deliberately.

Excluded publication material includes:

- NAND dumps (logical and physical), the stock firmware and bootloader images.
- Manufacturing data, MAC addresses, serial number, service passwords.
- MT7615 calibration/EEPROM data and private device trees containing it.
- UART logs, configuration backups, credentials and host keys.
- Compiled images: they contained a private build identity and are not
  distributed. The configuration seed sets `builder@buildhost`.

This was a scoped static review, not a guarantee that arbitrary future builds
are anonymous. Audit new images independently before publishing them.
