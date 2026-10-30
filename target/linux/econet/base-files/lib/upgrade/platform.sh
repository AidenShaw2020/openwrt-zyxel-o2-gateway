# SPDX-License-Identifier: GPL-2.0

REQUIRE_IMAGE_METADATA=1

# The bootloader boots a tclinux.trx (2RDH header, LZMA kernel, squashfs)
# from "tclinux"; the overlay lives in the rootfs_data volume on "ubi".
zyxel_o2_do_upgrade() {
	local ubidev

	CI_UBIPART=ubi

	sync
	echo 3 > /proc/sys/vm/drop_caches
	get_image "$1" | mtd write - tclinux || exit 1

	ubidev=$(nand_attach_ubi "$CI_UBIPART")
	[ -n "$ubidev" ] || exit 1

	# Start from an empty overlay, the backup is restored into it below.
	[ -n "$(nand_find_volume "$ubidev" rootfs_data)" ] &&
		ubirmvol "/dev/$ubidev" -N rootfs_data
	ubimkvol "/dev/$ubidev" -N rootfs_data -m || exit 1

	nand_do_restore_config
}

platform_check_image() {
	case "$(board_name)" in
	zyxel,o2-gateway)
		[ "$(get_magic_long "$1")" = "32524448" ] || {
			echo "Invalid image, expected a tclinux.trx (2RDH header)."
			return 1
		}
		return 0
		;;
	esac

	return 1
}

platform_do_upgrade() {
	case "$(board_name)" in
	zyxel,o2-gateway)
		zyxel_o2_do_upgrade "$1"
		;;
	*)
		default_do_upgrade "$1"
		;;
	esac
}
