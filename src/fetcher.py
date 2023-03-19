from ftfy import fix_encoding
from requests import get

from src.config import HATVP_DECLARATIONS_URL, HATVP_FILE, HATVP_FILE_SHORT, HATVP_FILE_RAW
from src.todict import with_xmltodict


def fetch():
    """
    Fetch entrypoint, fetch all and build JSON representation
    """
    fetch_declarations()

    build_declaration_subset()
    with_xmltodict(HATVP_FILE_SHORT)

    with_xmltodict(HATVP_FILE)


def fetch_declarations() -> None:
    """
    Fetch the declarations in XML format from the HATVP official site
    """
    if not HATVP_FILE_RAW.exists():
        rep = get(HATVP_DECLARATIONS_URL)
        HATVP_FILE_RAW.write_bytes(
            rep.content
            .replace(b"\xef\xbf\xbd", b"")  # replacement char
            .replace(b"\xe2\x80\xaf", b"")  # remove NSBP
            .replace(b"\xa0", b"")  # remove space
        )
    HATVP_FILE.write_text(
        fix_encoding(HATVP_FILE_RAW.read_text(encoding="latin-1").encode("utf8").decode("utf-8")),
        encoding="utf-8"
    )


def build_declaration_subset(count_max=10) -> None:
    """
    Build a smaller declaration file, to test parsing code faster
    :param count_max: the amount of declaration to keep in the file, from beginning
    """
    content = HATVP_FILE.read_text(encoding="utf-8")
    find_at, counter = 0, 0
    while counter < count_max:
        find_at = content.find("</declaration>", find_at + 1)
        counter += 1
    HATVP_FILE_SHORT.write_text(content[:find_at] + "    </declaration>\n</declarations>", encoding="utf-8")


if __name__ == '__main__':
    fetch()
