"""
Export utilities for research data tables, run artifacts, and experiment summaries.
"""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd


def export_dataframe_csv(df: pd.DataFrame) -> str:
    """Export DataFrame as CSV string."""
    return df.to_csv(index=False)


def export_json(data: Any) -> str:
    """Export data structure as formatted JSON string."""
    return json.dumps(data, indent=2)


def zip_run_artifacts(run_folder: Path | str) -> bytes:
    """Create a ZIP archive of all files inside a single run artifact folder."""
    folder = Path(run_folder)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in folder.iterdir():
            if file_path.is_file():
                zf.write(file_path, arcname=file_path.name)
    buffer.seek(0)
    return buffer.getvalue()
