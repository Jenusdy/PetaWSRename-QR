import shutil
from pathlib import Path


class FileService:
    def save(self, source_path: str, output_dir: str, idsls: str):
        destination = (
            Path(output_dir)
            / idsls[:4]
            / idsls[4:7]
            / idsls[7:10]
        )

        destination.mkdir(parents=True, exist_ok=True)

        shutil.copy2(
            source_path,
            destination / f"{idsls}{Path(source_path).suffix}"
        )