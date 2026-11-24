"""Export everything to a single zip on Drive for download / sharing."""

from __future__ import annotations

import shutil
import zipfile
from datetime import datetime
from pathlib import Path

from src.checkpoint import CheckpointManager, utc_now
from src.manifest import build_manifest, write_manifest
from src.paths import drive_root, load_config


def export_bundle(drive: Path | None = None) -> Path:
    drive = Path(drive or drive_root())
    ckpt = CheckpointManager(drive)
    write_manifest(drive)

    export_dir = drive / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_dated = export_dir / f"fairness_experiment_{stamp}.zip"
    zip_latest = export_dir / "fairness_experiment_latest.zip"

    manifest = build_manifest(drive)

    include_paths = [
        drive / "state" / "MANIFEST.json",
        drive / "state" / "SESSION_SUMMARY.txt",
        drive / "state" / "progress.json",
        drive / "experiment_config.json",
        drive / "prompts" / "prompts_v1.csv",
        drive / "checkpoints" / "README.txt",
    ]
    for name in ("generations", "scores_primary", "scores_secondary", "embeddings", "failures"):
        p = ckpt.csv_path(name)
        if p.exists():
            include_paths.append(p)
        bak = ckpt.backup_path(name)
        if bak.exists():
            include_paths.append(bak)

    outputs = drive / "outputs"
    if outputs.exists():
        for p in outputs.rglob("*"):
            if p.is_file():
                include_paths.append(p)

    for zpath in (zip_dated, zip_latest):
        if zpath.exists():
            zpath.unlink()
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in include_paths:
                if not path.exists():
                    continue
                arcname = path.relative_to(drive)
                zf.write(path, arcname=str(arcname))

            # Inline export index for instant assistant read
            index = {
                "exported_at": utc_now(),
                "zip_name": zpath.name,
                "manifest": manifest,
                "files_in_zip": [str(p.relative_to(drive)) for p in include_paths if p.exists()],
            }
            zf.writestr("EXPORT_INDEX.json", __import__("json").dumps(index, indent=2))

    ckpt.log_session(f"Exported bundle: {zip_latest} ({zip_latest.stat().st_size} bytes)")
    return zip_latest


def main() -> None:
    drive = drive_root()
    zpath = export_bundle(drive)
    print(f"Export complete: {zpath}")
    print(f"Size: {zpath.stat().st_size / 1024 / 1024:.2f} MB")
    print("\nDownload this file and upload to your assistant.")
    print("Path on Drive:", zpath)


if __name__ == "__main__":
    main()
