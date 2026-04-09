from pathlib import Path
import pandas as pd
from models.process_result import ProcessResult


class ReportService:
    def export(self, output_dir: str, results: list[ProcessResult]):
        df = pd.DataFrame(
            [r.to_list() for r in results],
            columns=["Nama File", "Nama Hasil", "Status", "Info"]
        )

        df.to_excel(Path(output_dir) / "Hasil.xlsx", index=False)