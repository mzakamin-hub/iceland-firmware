# iceland-firmware

Generic firmware of the OnePlus Pad 4 (OPD2514, `iceland`; Snapdragon 8 Elite Gen 5, kaanapali) for mainline Linux. The
files are taken from the stock software release 11.A.38 and packaged for Fedora as the `iceland-firmware` RPM (noarch).

The package holds the generic files only. Unit-specific data is never packaged; [EXCLUDED.tsv](EXCLUDED.tsv) lists what
is left out. The hub explains where the firmware is used:
[iceland-mainline](https://github.com/mzakamin-hub/iceland-mainline#boot-chain).

## Current release

The [`11.A.38-6` release](https://github.com/mzakamin-hub/iceland-firmware/releases/tag/11.A.38-6) has
`iceland-firmware-11.A.38-6.fc44.noarch.rpm`, its source RPM and `SHA256SUMS`. The RPM's SHA-256 starts `f8e202b3`.
Check the files with `sha256sum -c SHA256SUMS`.

| Tag | What it added |
|---|---|
| 11.A.38-6 (current) | the vendor GPU firmware pair, GMU v5.3.33 and SQE 0x094 (a third-party copy, see below) |
| 11.A.38-5 | stock's GPU firmware pair, GMU v5.3.39 and SQE 0x103 |
| 11.A.38-4 | the sensor hub registry (`sensors/registry`, 352 files) |
| 11.A.38-3 | the decoded thermal model, `/etc/iceland/thermal-model.json` |
| 11.A.38-2 | the generic firmware files and the sensor hub tree |

## Contents

- `root/`: the files, laid out as they are installed:
  - `/usr/lib/firmware/updates/`: the ADSP and CDSP images, the GPU zap shader, the video (VPU) firmware, the WCN7860
    Wi-Fi and Bluetooth firmware and board files, and the Novatek touch firmware;
  - `/usr/share/qcom/kaanapali/OnePlus/iceland/`: the sensor hub's file tree (DSP libraries, sensor configuration and the
    audio calibration database) and the sensor hub registry;
  - `/usr/lib/firmware/iceland-gpu-stock/qcom/` and `/usr/lib/firmware/iceland-gpu-vendor533/qcom/`: the two GPU pairs
    (see below);
  - `/etc/iceland/thermal-model.json`: stock's shell-temperature model, decoded (see below).
- `iceland-firmware.spec`: the RPM spec. It has no scriptlets and no services. Only the `fastrpc` group is required.
- `MANIFEST.tsv`: one row per packaged file: path, sha256, size, class, the stock source (partition and path in 11.A.38),
  the transformation, the notice, and the comparison with SuperTurtleDev's firmware repository.
- `EXCLUDED.tsv`: what is never packaged.
- `superturtle-compare.tsv`: the file-by-file comparison with that third-party repository.
- `NOTICE.md` and `Notice-qca-atheros.txt`: the notices.

Each stock file is a byte copy of its source in 11.A.38, except for the transformations listed in [NOTICE.md](NOTICE.md).
The vendor GPU pair is a third-party copy. Before you use a copy of any file from another source, compare its sha256
with the value in `MANIFEST.tsv`.

## The sensor hub registry

Since 11.A.38-4 the package includes the sensor hub registry (`sensors/registry`). Its files are installed as
`%config(noreplace)`: a registry that the installer's extractor wrote from a unit's own `persist` partition is kept.

## The two GPU firmware pairs

The GPU firmware comes in two pairs, each in its own directory. The kernel does not search these directories by default.
`iceland-device` sets the search path and chooses the pair with `GPU_FW` in `/etc/iceland/boot.conf`.

- **Stock's pair**, GMU v5.3.39 and SQE 0x103, from 11.A.38. It is used only with GPU preemption off: in testing, stock's
  pair with preemption on reset the tablet early in boot.
- **The vendor pair**, GMU v5.3.33 and SQE 0x094, as used by other ports of this chip. Stock 11.A.38 does not ship it.
  The files are third-party copies, byte-identical in SuperTurtleDev/iceland-mainline-kernel-firmware,
  map220v/iceland-firmware and the TB323FU manifest (ZUI 18.0.12.104). `MANIFEST.tsv` has their sha256 values.

## The decoded thermal model

`/etc/iceland/thermal-model.json` is stock's shell-temperature model, the input of `iceland-thermal`. It was decoded from
the vendor's encrypted thermal configuration of 11.A.38. It is generic and the same on every unit: it has no serial,
address or calibration value. The encrypted inputs, the key and the decoder are not published ([NOTICE.md](NOTICE.md)).

## Not in this repository

`EXCLUDED.tsv` lists what is never packaged. It is data of one unit, or an input of the vendor's own programs:

- the Bluetooth address and the record of the extraction (the installer still writes them from the tablet);
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
- `/etc/iceland/thermal-model.json`: not a byte copy; stock's thermal model, decoded (see above).

All rights remain with their owners. No licence is granted beyond the right to use the files with OnePlus Pad 4
hardware as the owners permit.

`Notice-qca-atheros.txt` is Qualcomm Atheros' notice file for the WCN7860 Wi-Fi firmware.

## Related repositories

- [iceland-linux](https://github.com/mzakamin-hub/iceland-linux): the kernel that loads these files.
- [iceland-u-boot](https://github.com/mzakamin-hub/iceland-u-boot): the boot loader.
- [iceland-mainline](https://github.com/mzakamin-hub/iceland-mainline): the project, the install guide and the device package.
