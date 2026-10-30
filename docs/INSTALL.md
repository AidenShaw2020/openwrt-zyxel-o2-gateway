# Installing from Stock

This is the tested migration sequence for one Zyxel O2 GateWay with stock
firmware `V5.50(ACBD.0)b2`, adapted for your own build. It is not a vendor-
supported installation or an unattended installer, and it has not been
repeated on a second unit. Do not flash a production or irreplaceable device.

The stock firmware is **removed** in step 6. Make your own backups first; this
repository does not contain any vendor firmware or device data.
**Do not upload an OpenWrt image to the stock web updater.**

## 1. Prerequisites

- A completed build following [README](../README.md#build).
- A 3.3 V USB-UART adapter connected to J606, see [Hardware](HARDWARE.md#uart).
- A PC with Python 3, `pyserial` and `tftpy` (0.8.7 or later) for
  `tools/o2-ramboot.py`, plus `ssh`/`scp`.
- An Ethernet cable from the PC to **LAN port 1** and a static PC address
  `192.168.1.2/24` on that interface, without a gateway.
- Reliable power. Physical access to the power switch.

## 2. Boot OpenWrt in RAM

Power the router off, start the helper, then power the router on:

```sh
python3 tools/o2-ramboot.py --port /dev/ttyUSB0 --wait-power-cycle \
  --image bin/targets/econet/en751627/openwrt-econet-en751627-zyxel_o2-gateway-initramfs-kernel.bin
```

It stops autoboot, unlocks the BootExtension prompt (`ATSE ZYXEL O2 GateWay`,
then `ATEN 1,<password>` computed by `tools/atenv3.py`), loads the image with
`ATLD` over TFTP, compares three 256-byte RAM samples with the file and only
then runs `jump 80020000`. Nothing is written to flash.

Manual equivalent at the console: Enter at `Hit any key to stop autoboot`,
`ATSE ZYXEL O2 GateWay`, `ATEN 1,$(tools/atenv3.py <seed>)`,
`ATLD openwrt.bin,0x80020000`, upload the file with a TFTP client **put** to
`192.168.1.1`, `ATGU`, `jump 80020000`. The loader occasionally stops
acknowledging packets for several seconds; use a client with generous retries
and abort a stuck transfer with Ctrl+C.

The RAM system is reachable at `192.168.1.1` (SSH root without password).
The kernel attaches the bootloader's BMT; check:

```sh
dmesg | grep en75_bmt      # "BBT & BMT found", factory_bad/worn counts
cat /proc/mtd              # bootloader romfile tclinux rootfs ubi reservearea bootflag
en75_chboot                # "Current boot flag set to OS B (Factory)"
```

Stop if the BMT is not found or reports a reserve size other than 81.

## 3. Back up the flash

Copy every partition to the PC **before** writing anything, one at a time,
because `/tmp` is RAM:

```sh
# on the PC
for p in bootloader romfile tclinux ubi reservearea; do
  ssh root@192.168.1.1 "dd if=/dev/mtd\$(grep '\"$p\"' /proc/mtd | cut -c4)" > o2-$p.bin
done
sha256sum o2-*.bin
```

Keep these files private: `bootloader` contains the serial number, MAC
address and service passwords, `reservearea` the Wi-Fi calibration. `ubi` here
is the stock second firmware slot plus its data partitions. For a physical
dump including OOB data, use `nanddump -o` from an image without the BMT
(not part of this guide).

## 4. Prepare UBI

This erases the stock second slot, `wwan`, `data`, `rom-d` and `misc`.

```sh
ubiformat /dev/mtd4 -y          # mtd4 = "ubi", check /proc/mtd
ubiattach -p /dev/mtd4
ubimkvol /dev/ubi0 -N rootfs_data -m
ubidetach -p /dev/mtd4
```

## 5. Write OpenWrt to the main slot

```sh
# on the PC
scp -O openwrt-econet-en751627-zyxel_o2-gateway-squashfs-tclinux.trx root@192.168.1.1:/tmp/o2.trx
# on the router
mtd write /tmp/o2.trx tclinux
head -c "$(wc -c < /tmp/o2.trx)" /dev/mtd2 | md5sum; md5sum /tmp/o2.trx
```

Both checksums must match.

## 6. Select the main slot and reboot

```sh
en75_chboot openwrt     # writes ASCII "0" to the boot flag
reboot
```

The console shows `boot flag = 0`, `main tclinux.bin have ECONET trx header!`,
then `mount_root: switching to ubifs overlay`. LuCI is at `http://192.168.1.1/`.
Set a root password.

## Updates

Use `openwrt-…-squashfs-sysupgrade.bin` through LuCI or `sysupgrade`. The
platform hook writes `tclinux`, recreates `rootfs_data` and restores the saved
configuration into it.

## Recovery

The bootloader is never written. If OpenWrt does not start, the bootloader
falls back to its prompt; boot the initramfs again (step 2) and repeat step 5.
Failsafe mode (`f` on the console or RESET during the blinking LED) gives
`192.168.1.1` on LAN port 1 with the read-only root.

Returning to the stock firmware requires your own backup from step 3: write
`o2-ubi.bin` back to `ubi` (after `ubidetach`), `o2-tclinux.bin` to `tclinux`
and set the flag back if needed (`en75_chboot factory` selects the slave slot).
This path has not been tested.
