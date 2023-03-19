import logging
import os
from pathlib import Path

LOG = logging.getLogger("hatvp")
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s - %(message)s')
ch.setFormatter(formatter)
LOG.addHandler(ch)

HATVP_DECLARATIONS_URL = "https://www.hatvp.fr/livraison/merge/declarations.xml"

# store data to work on it then
HATVP_DATA = Path(os.getenv("HATVP_DATA", "../local_data")).resolve().absolute()

HATVP_FILE_RAW = HATVP_DATA.joinpath("declarations_hatvp.raw.xml")
HATVP_FILE = HATVP_DATA.joinpath("declarations_hatvp.xml")
HATVP_FILE_SHORT = HATVP_DATA.joinpath("declarations_hatvp_short.xml")

HATVP_FILE_JSON = HATVP_DATA.joinpath("declarations_hatvp.json")
HATVP_FILE_SHORT_JSON = HATVP_DATA.joinpath("declarations_hatvp_short.json")

# final data to export
PARSED_DATA = Path("../_parsed_data")
