import json
import re
import sys
from pathlib import Path


lab = Path(__file__).resolve().parents[1] / "lab"
project = json.load(sys.stdin.buffer)

for node in project["topology"]["nodes"]:
    if node["compute_id"] != "local":
        continue

    node["console"] = None
    if node["node_type"] != "qemu":
        continue

    properties = node["properties"]
    qemu_path = properties.get("qemu_path")
    if qemu_path:
        executable = qemu_path.replace("\\", "/").rsplit("/", 1)[-1]
        properties["qemu_path"] = re.sub(r"w?\.exe$", "", executable, flags=re.IGNORECASE)

    for key in ("hda_disk_image", "hdb_disk_image", "hdc_disk_image", "hdd_disk_image", "cdrom_image"):
        image = properties.get(key)
        if image and Path(image).is_absolute():
            path = Path(image).resolve()
            if path.is_relative_to(lab):
                properties[key] = path.relative_to(lab).as_posix()

serialized = json.dumps(project, ensure_ascii=False, sort_keys=True, indent=4) + "\n"
sys.stdout.buffer.write(serialized.encode("utf-8"))
