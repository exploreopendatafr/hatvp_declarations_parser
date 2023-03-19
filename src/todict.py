"""
EXPERIMENTATION. For easier work with python structure
"""
import json
from pathlib import Path

import xmltodict

from src.config import HATVP_FILE_SHORT


def with_xmltodict(file: Path):
    result = xmltodict.parse(file.read_text(encoding="utf-8"))
    Path(file.as_posix().replace(".xml", ".json")).write_text(json.dumps(result, indent=4))


if __name__ == '__main__':
    with_xmltodict(HATVP_FILE_SHORT)
