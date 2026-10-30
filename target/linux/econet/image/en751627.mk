define Device/zyxel_o2-gateway-ram
  DEVICE_VENDOR := Zyxel
  DEVICE_MODEL := O2 GateWay RAM-only
  DEVICE_DTS := en751627_zyxel_o2-gateway-ram
  KERNEL_INITRAMFS := kernel-bin | append-dtb
  IMAGES :=
  DEVICE_PACKAGES := luci -kmod-leds-gpio -kmod-gpio-button-hotplug -wpad-basic-mbedtls -nand-utils
endef
TARGET_DEVICES += zyxel_o2-gateway-ram

define Device/zyxel_o2-gateway-ap-probe
  $(Device/zyxel_o2-gateway-ram)
  DEVICE_MODEL := O2 GateWay RAM-only AP probe
  DEVICE_DTS := en751627_zyxel_o2-gateway-ap-probe
  DEVICE_PACKAGES := luci kmod-mt7615e kmod-mt7615-firmware wpad-basic-mbedtls -kmod-leds-gpio -kmod-gpio-button-hotplug -nand-utils
endef
TARGET_DEVICES += zyxel_o2-gateway-ap-probe

define Device/zyxel_o2-gateway-usb-probe
  $(Device/zyxel_o2-gateway-ap-probe)
  DEVICE_MODEL := O2 GateWay RAM-only USB probe
  DEVICE_DTS := en751627_zyxel_o2-gateway-usb-probe
  DEVICE_PACKAGES += kmod-usb3 kmod-usb-storage kmod-fs-vfat kmod-fs-ext4
endef
TARGET_DEVICES += zyxel_o2-gateway-usb-probe

define Device/zyxel_o2-gateway-ethernet-probe
  $(Device/zyxel_o2-gateway-usb-probe)
  DEVICE_MODEL := O2 GateWay RAM-only Ethernet probe
  DEVICE_DTS := en751627_zyxel_o2-gateway-ethernet-probe
  DEVICE_PACKAGES += kmod-econet-eth kmod-leds-gpio kmod-gpio-button-hotplug -wpad-basic-mbedtls wpad-mbedtls nand-utils
endef
TARGET_DEVICES += zyxel_o2-gateway-ethernet-probe

define Device/zyxel_o2-gateway
  DEVICE_VENDOR := Zyxel
  DEVICE_MODEL := O2 GateWay
  DEVICE_DTS := en751627_zyxel_o2-gateway
  KERNEL_INITRAMFS := kernel-bin | append-dtb
  IMAGES := tclinux.trx sysupgrade.bin
  IMAGE/tclinux.trx := append-kernel | lzma | tclinux-trx | check-size 0x2800000
  IMAGE/sysupgrade.bin := append-kernel | lzma | tclinux-trx | check-size 0x2800000 | append-metadata
  DEVICE_PACKAGES := luci wpad-mbedtls kmod-mt7615e kmod-mt7615-firmware 	kmod-econet-eth kmod-leds-gpio kmod-gpio-button-hotplug 	kmod-usb3 kmod-usb-storage kmod-fs-vfat kmod-fs-ext4 nand-utils
endef
TARGET_DEVICES += zyxel_o2-gateway
