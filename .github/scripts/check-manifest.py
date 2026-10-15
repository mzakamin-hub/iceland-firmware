#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Manifest and notice check of the published firmware (run by .github/workflows/manifest.yml; also usable locally).

  python3 .github/scripts/check-manifest.py

- MANIFEST.tsv: 8 tab-separated fields per line, unique paths below /usr/lib/firmware, /usr/share or /etc
- every manifest line: root/<path> exists, its size and sha256 equal the recorded ones
- every file under root/ has its manifest line (a blob cannot change, appear or go without a manifest change)
- no file of EXCLUDED.tsv (unit-specific data) is under root/
- notices: NOTICE.md and README.md exist; every notice named in the manifest's notice column is either "none", has
  its own Notice-<name>.txt, or is covered by NOTICE.md; the spec ships the notice files as %license
"""
import hashlib
import os
import re
import sys

fails = 0


def fail(path, msg, line=None):
    global fails
    fails += 1
    print(f"::error file={path}" + (f",line={line}" if line else "") + f",title=manifest::{msg}")


rows, seen = [], set()
for n, raw in enumerate(open("MANIFEST.tsv", encoding="utf-8"), 1):
    line = raw.rstrip("\n")
    if not line or line.startswith("#"):
        continue
    f = line.split("\t")
    if len(f) != 8:
        fail("MANIFEST.tsv", f"{len(f)} fields, expected 8", n)
        continue
    path, sha, size = f[0], f[1], f[2]
    if not re.match(r"^/(usr/lib/firmware|usr/share|etc)/", path) or ".." in path.split("/"):
        fail("MANIFEST.tsv", f"path outside the packaged trees: {path}", n)
    if path in seen:
        fail("MANIFEST.tsv", f"duplicate path {path}", n)
    seen.add(path)
    if not re.fullmatch(r"[0-9a-f]{64}", sha) or not size.isdigit():
        fail("MANIFEST.tsv", f"bad sha256 / size field for {path}", n)
        continue
    rows.append((n, path, sha, int(size), f[6]))

for n, path, sha, size, _ in rows:
    p = "root" + path
    if not os.path.isfile(p):
        fail("MANIFEST.tsv", f"listed file missing: {p}", n)
        continue
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    if os.path.getsize(p) != size:
        fail(p, f"size {os.path.getsize(p)} != manifest {size} (MANIFEST.tsv line {n})")
    if h.hexdigest() != sha:
        fail(p, f"sha256 differs from MANIFEST.tsv line {n}: update the manifest with the blob")

on_disk = set()
for d, _, names in os.walk("root"):
    for name in names:
        on_disk.add(os.path.join(d, name)[len("root"):].replace(os.sep, "/"))
for p in sorted(on_disk - seen):
    fail("root" + p, "file under root/ without a MANIFEST.tsv line")

if os.path.exists("EXCLUDED.tsv"):
    for n, raw in enumerate(open("EXCLUDED.tsv", encoding="utf-8"), 1):
        if raw.startswith("#") or not raw.strip():
            continue
        ex = raw.split("\t")[0].rstrip("/")
        if os.path.exists("root" + ex):
            fail("EXCLUDED.tsv", f"excluded (unit-specific) path is present: root{ex}", n)

for need in ("NOTICE.md", "README.md"):
    if not os.path.isfile(need):
        fail(need, "missing")
notice_md = open("NOTICE.md", encoding="utf-8").read() if os.path.isfile("NOTICE.md") else ""
for name in sorted({r[4] for r in rows}):
    key = name.split(" ")[0]
    if key == "none":
        continue
    if os.path.isfile(f"Notice-{key}.txt"):
        if f"Notice-{key}.txt" not in notice_md:
            fail("NOTICE.md", f"Notice-{key}.txt is not named in NOTICE.md")
        continue
    if not notice_md:
        fail("NOTICE.md", f"no notice for '{name}'")
spec = [f for f in os.listdir(".") if f.endswith(".spec")]
for s in spec:
    lic = " ".join(l for l in open(s, encoding="utf-8") if l.startswith("%license"))
    for f in ["NOTICE.md"] + [f for f in os.listdir(".") if re.match(r"Notice-.*\.txt$", f)]:
        if f not in lic:
            fail(s, f"{f} is not shipped as %license")

print(f"manifest: {len(rows)} lines, {len(on_disk)} files under root/, {fails} failure(s)")
sys.exit(1 if fails else 0)
