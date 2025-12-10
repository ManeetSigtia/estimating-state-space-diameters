from pathlib import Path

TESTS_ROOT = Path(__file__).parent
PROJECT_ROOT = TESTS_ROOT.parent
DATA_DIR = PROJECT_ROOT / "data"


def get_data_file(filename: str) -> Path:
    return DATA_DIR / filename
