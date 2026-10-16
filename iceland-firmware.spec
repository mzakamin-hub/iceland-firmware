# SPDX-License-Identifier: GPL-2.0-or-later
# iceland-firmware: the GENERIC firmware of the OnePlus Pad 4 (OPD2514, stock 11.A.38) at the paths the installer's
# extractor (iceland-fw-extract) writes today, so those files become package-owned with no gap: the package's files
# are byte-identical to the extracted ones (MANIFEST.tsv = the extraction's sha256), rpm replaces an unowned file
# with the same content in place, so nothing is ever absent. Unit-specific data (the Bluetooth address, the
# extraction record) is NOT in this package (EXCLUDED.tsv) and stays extractor-written.
# 11.A.38-5 adds stock's GPU GMU firmware v5.3.39 and SQE microcode 0x103 (gen80200) in their own directory,
# /usr/lib/firmware/iceland-gpu-stock/qcom, which the kernel does NOT search by default: Fedora's linux-firmware
# copies stay untouched and in use unless the kernel command line has
# firmware_class.path=/usr/lib/firmware/iceland-gpu-stock (iceland-device >= 0.28-19 sets it, and puts the pair into
# the initramfs; it also rebuilds the initramfs, so this package still has no scriptlet).
# 11.A.38-4 adds the sensor hub registry (persist:/sensors/registry/registry, 352 files): generic by the owner's
# decision of 15 Oct 2026. Its files are %config(noreplace): a registry the extractor wrote from a unit's own persist
# partition stays in place (rpm writes .rpmnew next to a differing file) and rpm -V reports it as configuration.
# 11.A.38-3 adds ONE non-firmware file: /etc/iceland/thermal-model.json, stock's shell-temperature model for
# iceland-thermal (decoded from the vendor's encrypted horae configs, generic; owner's decision 12 Oct 2026). A plain
# package file, NOT %config: the installer no longer writes it, rpm replaces an unowned copy of the same bytes, and an
# install never holds a second, disagreeing copy (no .rpmnew); rpm -V reports any edit.
# Firmware only otherwise: no scriptlets (no /bin/sh dependency), no services, no initramfs rebuild: 11.A.38-1 installs
# byte-identical copies, so the initramfs copies of gen80200_zap.mbn and novatek_nt36536_fw.bin (90-iceland-dracut.conf)
# stay valid. A later release that changes either file must add a posttrans scriptlet running
# "dracut -f --regenerate-all".
%global stock 11.A.38
# Hexagon / ARM ELF firmware in a noarch package: no strip, no build-id links, no debuginfo, no compression
%global _binaries_in_noarch_packages_terminate_build 0
%global _build_id_links none
%global debug_package %{nil}
%global __os_install_post %{nil}
%undefine _missing_build_ids_terminate_build

Name:           iceland-firmware
Version:        11.A.38
Release:        5%{?dist}
Summary:        Generic firmware of the OnePlus Pad 4 (Snapdragon 8 Elite Gen 5 / kaanapali)
License:        LicenseRef-Callaway-Redistributable-no-modification-permitted
URL:            https://github.com/mzakamin-hub/iceland-firmware
Source0:        iceland-firmware-%{version}.tar.gz
BuildArch:      noarch
# nothing to obsolete or conflict with: the first package of these paths; Fedora's linux-firmware ships no file
# under /usr/lib/firmware/updates (searched first by the kernel) and none under /usr/share/qcom/kaanapali/OnePlus
Provides:       iceland-firmware(stock) = %{stock}
# the sensor hub tree is root:fastrpc, dirs 0750 / files 0640: exactly what iceland-device's tmpfiles rule
# (iceland-dsp-tree.conf: Z /usr/share/qcom/kaanapali/OnePlus/iceland ~0750 root fastrpc) sets at every boot, so rpm -V
# stays clean (11.A.38-1 shipped root:root 0644 / 0755 -> 266 rpm -V lines on the 2nd boot, r143b); hexagonrpc's
# sysusers.d provides the group
Requires(pre):  group(fastrpc)

%description
The generic firmware every OnePlus Pad 4 runs in stock software 11.A.38: the ADSP / CDSP images, the GPU zap shader,
the video (VPU) firmware, the WCN7860 Wi-Fi and Bluetooth firmware and board files, the Novatek touch firmware, and the
sensor hub's file tree (DSP libraries, sensor configuration, audio calibration database). Installed under
/usr/lib/firmware/updates and /usr/share/qcom/kaanapali/OnePlus/iceland, where the mainline kernel, hexagonrpcd and
the iceland-device package expect them. MANIFEST.tsv lists each file's stock source and sha256.
Also stock's shell-temperature model for iceland-thermal (/etc/iceland/thermal-model.json), decoded from the
vendor's thermal configuration: generic, the same on every unit.
Also the sensor hub registry of stock 11.A.38 (generic; configuration files, a unit's own registry is kept).
Also stock's GPU GMU firmware v5.3.39 and SQE microcode 0x103 (gen80200) in /usr/lib/firmware/iceland-gpu-stock,
a directory the kernel does NOT search by default: Fedora's linux-firmware copies (v5.3.23 / 0x088) stay in use
unless the command line selects stock's pair with firmware_class.path=/usr/lib/firmware/iceland-gpu-stock.
Unit-specific data (Bluetooth / Wi-Fi addresses) is not included.

%prep
%setup -q -n iceland-firmware-%{version}

%build
# nothing to build

%install
cp -a root/. %{buildroot}/
# the file list = exactly MANIFEST.tsv, plus every directory below /usr/lib/firmware and /usr/share that holds one of
# its files; the sensor registry files are %config(noreplace)
awk -F'\t' '!/^#/ && NF >= 2 { print $1 }' MANIFEST.tsv | sort > files.txt
: > %{name}.files
T=/usr/share/qcom/kaanapali/OnePlus/iceland
while read -r f; do case "$f" in "$T"/sensors/registry/*) printf '%%%%config(noreplace) %%%%attr(0640,root,fastrpc) "%%s"
' "$f" ;; "$T"/*) printf '%%%%attr(0640,root,fastrpc) "%%s"\n' "$f" ;; *) printf '"%%s"\n' "$f" ;; esac; done < files.txt >> %{name}.files
python3 - files.txt >> %{name}.files <<'PY'
import sys
dirs = set()
for f in open(sys.argv[1]).read().split():
    d = f.rsplit("/", 1)[0]
    while d not in ("/usr/lib/firmware", "/usr/share", "/etc", ""):
        dirs.add(d)
        d = d.rsplit("/", 1)[0]
T = "/usr/share/qcom/kaanapali/OnePlus/iceland"
for d in sorted(dirs):
    a = "%%%%attr(0750,root,fastrpc) " if d == T or d.startswith(T + "/") else ""
    print("%%%%dir " + a + "\"" + d + "\"")
PY

%check
# every packaged file = the manifest's sha256 (the extraction), every manifest line packaged, nothing else
cd %{buildroot}
awk -F'\t' '!/^#/ && NF >= 2 { print $2 "  ." $1 }' %{_builddir}/iceland-firmware-%{version}/MANIFEST.tsv | sha256sum --quiet -c -
test "$(find . -type f | wc -l)" = "$(grep -c -v '^#' %{_builddir}/iceland-firmware-%{version}/MANIFEST.tsv)"
test "$(find ./usr/share/qcom/kaanapali/OnePlus/iceland/sensors/registry -type f | wc -l)" = 352
# stock's GPU pair: exactly the GMU and the SQE file in their own directory, nothing of linux-firmware's names elsewhere
test "$(find ./usr/lib/firmware/iceland-gpu-stock -type f | wc -l)" = 2
echo '7e2f9381dbae6ba3eda632e51e07377a90a9549e2e164a033255ab4ecd431ba8  ./usr/lib/firmware/iceland-gpu-stock/qcom/gen80200_gmu.bin' | sha256sum --quiet -c -
echo '1f1c7bae8050a9910902ec42b3d741ff3a68bc21114dea966a502ade2a9b606d  ./usr/lib/firmware/iceland-gpu-stock/qcom/gen80200_sqe.fw' | sha256sum --quiet -c -
test ! -e ./usr/lib/firmware/qcom/gen80200_gmu.bin && test ! -e ./usr/lib/firmware/qcom/gen80200_sqe.fw
# the thermal model: valid JSON with the five shell models; nothing else under /etc
python3 -c 'import json, sys; d = json.load(open(sys.argv[1])); sys.exit(0 if len(d.get("models", [])) == 5 else 1)' ./etc/iceland/thermal-model.json
test "$(find ./etc -type f | wc -l)" = 1

%files -f %{name}.files
%license NOTICE.md Notice-qca-atheros.txt
%doc README.md MANIFEST.tsv EXCLUDED.tsv

%changelog
* Fri Oct 16 2026 mzak <mzak.amin@gmail.com> - 11.A.38-5
- Add stock's GPU GMU firmware (gen80200_gmu.bin v5.3.39, sha256 7e2f9381) and SQE microcode (gen80200_sqe.fw
  0x103, sha256 1f1c7bae) of 11.A.38, byte copies from vendor_a:/firmware, under
  /usr/lib/firmware/iceland-gpu-stock/qcom: NOT on the kernel's default firmware search path, so linux-firmware's
  v5.3.23 / 0x088 stay untouched; the kernel parameter firmware_class.path=/usr/lib/firmware/iceland-gpu-stock
  (set by iceland-device >= 0.28-19) selects stock's pair: that directory is searched first and holds only these
  two files. Tested in the RAM rehearsal R4 (16 Oct 2026, kernel q89m, GPU preemption off): clean GPU start,
  0 GMU errors, 0 fenced writes, WebGL 180 s without a GPU-process crash. Generic GPU blobs, published by the
  owner's decision of 16 Oct 2026. No other file changed.

* Fri Oct 16 2026 mzak <mzak.amin@gmail.com> - 11.A.38-4
- Add the sensor hub registry (/usr/share/qcom/kaanapali/OnePlus/iceland/sensors/registry, 352 files from
  persist:/sensors/registry/registry of 11.A.38, sha256 in MANIFEST.tsv): generic by the owner's decision of
  15 Oct 2026, so a generic install image needs no per-unit extraction. %config(noreplace): a registry written
  from a unit's own persist partition stays. Firmware files and the thermal model unchanged.

* Mon Oct 12 2026 mzak <mzak.amin@gmail.com> - 11.A.38-3
- Add /etc/iceland/thermal-model.json (sha256 4f476a7d): stock's shell-temperature model for iceland-thermal,
  decoded from the vendor's encrypted thermal configuration of 11.A.38; generic, identical on every unit (owner's
  decision, 12 Oct 2026). A plain package file (not %config): one file, one owner. The encrypted inputs, the
  vendor's program, its key and the decoder are not included (EXCLUDED.tsv). Firmware files unchanged.

* Mon Oct 12 2026 mzak <mzak.amin@gmail.com> - 11.A.38-2
- The sensor hub tree as iceland-device's tmpfiles rule keeps it (root:fastrpc, dirs 0750, files 0640): rpm -V clean
  after a reboot (r143b: 266 mode / group lines with -1). Requires(pre) group(fastrpc). Content unchanged.

* Mon Oct 12 2026 mzak <mzak.amin@gmail.com> - 11.A.38-1
- First package: the generic files the installer extracted from stock 11.A.38 (sha256 = the extraction); the
  sensor registry (calibration), the Bluetooth address and the extraction record stay unit-specific and unpackaged.
