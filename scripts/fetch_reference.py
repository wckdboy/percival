"""Fetch the pinned ToddlerBot reference geometry, not printable chassis parts."""
import concurrent.futures
import hashlib
import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = "e337f3b177b4b53abff70b31d1695a7b66cc6d2e"
REMOTE = f"https://raw.githubusercontent.com/hshi74/toddlerbot/{REV}/"
DEST = ROOT / "reference" / "toddlerbot"
MODEL = "toddlerbot/descriptions/toddlerbot_2xc_gripper/"


def fetch(path):
    dest = DEST / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    data = urllib.request.urlopen(REMOTE + path, timeout=60).read()
    dest.write_bytes(data)
    return {"path": str(dest.relative_to(ROOT)), "url": REMOTE + path,
            "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def main():
    first = fetch(MODEL + "toddlerbot_2xc_gripper.urdf")
    urdf = ET.parse(ROOT / first["path"]).getroot()
    paths = {MODEL + m.attrib["filename"] for m in urdf.findall(".//mesh")}
    paths.update(["README.md", "LICENSE", "docs/hardware/03_3d_printing.rst",
                  "docs/hardware/04_assembly_manual.rst", "docs/hardware/01_bill_of_materials.rst"])
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        entries = list(pool.map(fetch, sorted(paths)))
    manifest = {"repository": "https://github.com/hshi74/toddlerbot", "revision": REV,
                "design_license": "CC BY-NC-SA 4.0", "code_and_documentation_license": "MIT",
                "warning": "URDF visual meshes contain merged purchased and printed components. NOT print-ready chassis parts.",
                "files": [first] + entries}
    (DEST / "SOURCE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"revision": REV, "files": len(entries)+1,
                      "bytes": sum(e["bytes"] for e in entries)+first["bytes"]}))


if __name__ == "__main__":
    main()
