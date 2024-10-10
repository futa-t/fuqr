import sys
from pathlib import Path


def gen_icon_path():
    try:
        __base_path = Path(sys._MEIPASS)
    except Exception:
        __base_path = Path().resolve()
    return __base_path / "favicon.ico"
