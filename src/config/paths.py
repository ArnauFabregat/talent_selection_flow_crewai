# src/config/paths.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
CHROMA_DIR = DATA_DIR / "chroma"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = DATA_DIR / "reports"

JOBS_PATH_RAW = RAW_DIR / "vacantes_dataset.csv"
CVS_PATH_RAW = RAW_DIR / "cvs_dataset.csv"

JOBS_PATH_PROCESSED = PROCESSED_DIR / "jobs_processed.csv"
CVS_PATH_PROCESSED = PROCESSED_DIR / "cvs_processed.csv"

REPORT_OUTPUT_PATH = REPORTS_DIR / "latest_report.md"
