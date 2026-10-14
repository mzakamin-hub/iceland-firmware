# iceland-firmware

Generic firmware of the OnePlus Pad 4 (OPD2514, "iceland"; Snapdragon 8 Elite Gen 5 / kaanapali) for mainline Linux,
taken from the stock software release 11.A.38 and packaged for Fedora as `iceland-firmware` (noarch).

## Releases

| Version | Tag / commit | What changed | RPM sha256 prefix |
|---|---|---|---|
| **11.A.38-3** (current) | `11.A.38-3` / `70ea8f1` | adds `/etc/iceland/thermal-model.json` (sha256 `4f476a7d4b0b9c5266aacd83d430f454e6175922f0c1c21f9f9dfd0a36f1debd`) | `297669a0` |
| 11.A.38-2 | `11.A.38-2` / `c40c33e` | the 278 generic firmware files, the sensor hub tree with its permissions (root:fastrpc) | `14833f71` |

The 11.A.38-3 file is stock's shell-temperature model for `iceland-thermal`. It was decoded from the vendor's encrypted
thermal configuration of 11.A.38. It is generic and the same on every unit (no serial, address or calibration value).
The owner decided to publish it on 12 Oct 2026. The firmware files themselves are the same in -2 and -3.

The tablet runs 11.A.38-3: it is part of the B149 image installed on 13 Oct 2026.

## Contents

- `root/`: the files, laid out as they are installed. 279 files, 129,208,105 bytes (about 123 MiB) in all. The largest
  is `adsp.mbn` (40,814,792 bytes):
  - `/usr/lib/firmware/updates/`: the ADSP and CDSP images, the GPU zap shader, the video (VPU) firmware, the
    WCN7860 Wi-Fi and Bluetooth firmware and board files, and the Novatek touch firmware;
  - `/usr/share/qcom/kaanapali/OnePlus/iceland/`: the sensor hub's file tree (DSP libraries, sensor configuration and
    the audio calibration database), without the sensor calibration registry;
  - `/etc/iceland/thermal-model.json`: the thermal model (11.A.38-3 only).
- `iceland-firmware.spec`: the RPM spec. It has no scriptlets and no services. Only the `fastrpc` group is required.
- `MANIFEST.tsv`: one row per packaged file: path, sha256, bytes, class, the stock source (partition and path in
  11.A.38), the transformation, the notice, and the comparison with the copy in SuperTurtleDev's
  [iceland-mainline-kernel-firmware](https://github.com/SuperTurtleDev/iceland-mainline-kernel-firmware) repository.
- `EXCLUDED.tsv`: the unit-specific data and the inputs that are never published (see below).
- `superturtle-compare.tsv`: the file-by-file comparison with that third-party repository.
- `NOTICE.md` and `Notice-qca-atheros.txt`: the notices (see below).

Every file is byte-identical to what `iceland-fw-extract` in [iceland-mainline](https://github.com/mzakamin-hub/iceland-mainline)
writes from a tablet's own stock partitions. `sha256sum -c` against `MANIFEST.tsv` proves it. Before a third-party copy
of any file is used, compare its sha256 with `MANIFEST.tsv`.

## Not in this repository

`EXCLUDED.tsv` lists what is never packaged. It is data of one unit, or an input of the vendor's own programs:

- the sensor calibration registry of the unit, the Bluetooth address and the record of the extraction (the installer
  still writes them from the tablet);
- the vendor's encrypted thermal configuration files, the vendor's thermal program and its key, the tool that decodes
  them, and the full decoded configuration (only the narrower model in `thermal-model.json` is published);
- persist and modem data, partition backups, camera traces and test media.

## Notices and licence

The files are proprietary firmware of Qualcomm Technologies, Inc. / Qualcomm Atheros, Inc., Novatek Microelectronics
Corp. and OnePlus (OPLUS), as shipped in 11.A.38. They are redistributed unmodified, except for these documented,
byte-exact transformations (see [NOTICE.md](NOTICE.md)):

- `*.mbn` built from split images: the `.mdt` header and its `.bNN` segments are joined into one ELF (the segments are
  byte-identical to the stock files);
- `novatek_nt36536_fw.bin`: the stock container's header and trailer are removed; the payload is byte-identical;
- `socinfo/*`: SoC identification values, not vendor code.

All rights remain with their owners. No licence is granted beyond the right to use the files with OnePlus Pad 4
hardware as the owners permit.

## Related repositories

- [iceland-linux](https://github.com/mzakamin-hub/iceland-linux): the kernel that loads these files.
- [iceland-u-boot](https://github.com/mzakamin-hub/iceland-u-boot): the bootloader.
- [iceland-mainline](https://github.com/mzakamin-hub/iceland-mainline): the project, the extractor and the install guide.
