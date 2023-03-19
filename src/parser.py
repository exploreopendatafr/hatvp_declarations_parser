import json
import logging
import re
from collections import defaultdict
from pathlib import Path

from humanize import naturalsize

from src.config import PARSED_DATA, HATVP_FILE_SHORT_JSON, HATVP_FILE_JSON

LOG = logging.getLogger("hatvp")
LOG.setLevel(logging.INFO)

WORK_SECTIONS: list[tuple[str, str]] = [("activProfCinqDerniereDto", "description"),
                                        ("mandatElectifDto", "descriptionMandat"),
                                        ("participationDirigeantDto", "commentaire"),
                                        ("activConsultantDto", "description")]

PARTICIPATION_SECTIONS: list[tuple[str, str]] = [("participationFinanciereDto", "commentaire")]


def safe_list(value: list | dict) -> list:
    """
    xmltodict transform one 'items' to dict and multiple to list
    """
    return value if isinstance(value, list) else [value]


def parse_declarant(declarant: dict):
    return f'{declarant["civilite"]} {declarant["nom"]} {declarant["prenom"]}'


def parse_declaration(declaration: dict) -> tuple[dict, ...] | None:
    # print(declaration, declaration["uuid"])
    if declaration["uuid"] is None:
        return

    salaires = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    participations = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    declarant = parse_declarant(declaration["general"]["declarant"])
    LOG.info("%s %s %s", declaration["uuid"], declaration["dateDepot"], declarant)

    for key, desc in WORK_SECTIONS:
        section = key.removesuffix("dto")

        if (activ := declaration.get(key)) and activ.get("neant", "false") == "false" and activ.get("items"):

            for item in safe_list(activ["items"]["items"]):
                LOG.debug("%s", re.sub(r"\s+", " ", item[desc] or ''))
                brutNet = None
                if (rem := item["remuneration"]) and (brutNet := rem["brutNet"]) and rem.get("montant"):
                    for montant in safe_list(rem["montant"]["montant"]):
                        montant_value = int(re.sub(r"\D", "", montant["montant"] or '0') or '0')
                        LOG.debug("%s %s %s", brutNet, montant["annee"], montant_value)
                        salaires[declarant][section][item[desc]].append({"type": brutNet,
                                                                         "year": int(montant["annee"]),
                                                                         "value": montant_value})
        else:
            LOG.warning("no %s", key)

    for key, desc in PARTICIPATION_SECTIONS:
        section = key.removesuffix("dto")

        if (activ := declaration.get(key)) and activ.get("neant", "false") == "false" and activ.get("items"):

            for iitem, item in enumerate(safe_list(activ["items"]["items"])):
                LOG.info("%s", re.sub(r"\s+", " ", item[desc] or ''))

                participations[declarant][section][f"{iitem}_{item[desc]}"].append({
                    "nomSociete": item["nomSociete"],
                    "capitalDetenu": int(item["capitalDetenu"] or '0'),
                    "remuneration": item["remuneration"],
                    "evaluation": int(item["evaluation"])
                })
        else:
            LOG.warning("no %s", key)

    return salaires, participations


def parse(file: Path) -> None:
    """
    Parsing entrypoint
    :param file: the XML file to parse
    """
    content = json.loads(file.read_text())
    salaires_total = {}
    participations_total = {}
    for declaration in content["declarations"]["declaration"]:
        if parsed := parse_declaration(declaration):
            salaires, participations = parsed
            salaires_total.update(salaires)
            participations_total.update(participations)
        LOG.info("=" * 30)

    LOG.info("Parsed %s declarations, of %s person",
             len(content["declarations"]["declaration"]), len(salaires_total))

    salaires_file = PARSED_DATA.joinpath(r"salaires.json")
    salaires_file.write_text(json.dumps(salaires_total, indent=None))
    print(naturalsize(salaires_file.stat().st_size))

    participations_file = PARSED_DATA.joinpath(r"participations.json")
    participations_file.write_text(json.dumps(participations_total, indent=None))
    print(naturalsize(participations_file.stat().st_size))


if __name__ == '__main__':
    print(HATVP_FILE_JSON)
    print(HATVP_FILE_SHORT_JSON)

    parse(HATVP_FILE_JSON)
    # parse(HATVP_FILE_SHORT_JSON)
