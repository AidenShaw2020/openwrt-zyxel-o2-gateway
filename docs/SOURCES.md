# Build Inputs

This project distributes the Zyxel O2 GateWay source overlay and patches only.
It does not distribute prebuilt firmware or a bundled dependency-source
archive. Follow the pinned revisions and build commands in
[README](../README.md#build).

The project-specific inputs are in Git:

- `target/linux/econet/`: EN751627 subtarget, device trees, image recipes,
  kernel patches, kernel configuration and board scripts.
- `package/kernel/econet-eth/`: recipe and EN751627 patches for the
  out-of-tree [econet_eth](https://github.com/cjdelisle/econet_eth) driver,
  pinned to `96448504029bd3b8014f1de7fd0e7799d52d66f2`.
- `package/kernel/linux/modules/usb.mk`: USB module recipe change.
- `zyxel-o2-openwrt-25.12.6-bringup.patch`: these inputs as one patch.
- `zyxel-o2-gateway.config`: configuration seed.

Apply the exported patch once to the pinned OpenWrt tree; do not also copy the
same directories. OpenWrt downloads dependency sources from their upstream
locations and checks the hashes in the package recipes. Internet access is
required; bit-for-bit reproducibility has not been established.

No device dump, private source tree, vendor firmware or calibration file is
needed to build the images. The MT7615 calibration and the MAC addresses are
read from the router's own flash at runtime.

## Redistribution

If you distribute your own compiled images, satisfy each component's source,
license, copyright and firmware redistribution obligations. This overlay plus
generic upstream links is not automatically complete corresponding source for
a whole firmware image. Keep the actual build configuration, modified sources,
scripts and applicable notices for your build.
