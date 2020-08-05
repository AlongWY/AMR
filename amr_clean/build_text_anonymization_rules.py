import json
from editdistance import distance
from os import path

from amr_clean.io import AMRIO

templates = {
    "priority_lists": [
        [
            "Germany",
            "German"
        ],
        [
            "China",
            "Chinese"
        ],
        [
            "Russia",
            "Russian"
        ],
        [
            "Brazil",
            "Brazilian"
        ],
        [
            "Venezuela",
            "Venezuelans"
        ],
        [
            "Islamic Republic of Iran",
            "Iran",
            "Iranian"
        ],
        [
            "Kenya",
            "Kenyan"
        ],
        [
            "Vietnam",
            "Vietnamese"
        ],
        [
            "Philippines",
            "Philippine"
        ],
        [
            "South Africa",
            "South African"
        ],
        [
            "North Korea",
            "North Korean",
            "Korea",
            "Korean"
        ],
        [
            "Peru",
            "Peruvian"
        ],
        [
            "1 - to - 1",
            "1"
        ]
    ],
    "INVP": [
        "^(\\d+|a|or|by|be|my|he|around|against|between|at-least|cut-down|for|to|every|visit|April|September)$",
        "^for$",
        "^(a|the|or|to|by|my|he|visit|every|around|against|at-least|cut-down)$",
        "^a$",
        "^between$",
        "^(my|ever|'s)$"
    ],
    "INVS": [
        "^(\\d+|''|of|anti|percent|pence|offer|month|-|week|million|billion|spanish|year|stage|advance|branch|province|customer|meeting|member|continent|document|soldier|police|foreign|country|to|May|July)$",
        "^time$",
        "^(of|to|and|round|anti|offer|million|billion|percent|stage|advance|branch|province|meeting|member|continent|document|soldier|police|customer|foreign|country|\\.)$",
        "^(\\d+|\\d+th)$",
        "^country$",
        "^(of|reason|team|and|minute|way|\\.|,|!)$"
    ],
    "VNE": "^(competition|player)$",
    "LOCEN1": [
        "^[Ww]",
        "^(-|a|in)$",
        "^[A-HJ-MOQ-Z]"
    ],
    "LOCEN2": [
        "^(Africa|Korea)$",
        "^(South|North)$"
    ],
    "N": [
        "^(one|two)$",
        "^(2nd|17th|13th)$",
        "between the 2 country",
        "between the two country"
    ],
    "M": "^September$",
    "R": [
        "^(report|party)$",
        "^round$"
    ]
}

type_map = {
    "named-entity": "NNP",
    "url-entity": "NN",
    "score-entity": "NNP",
    "ordinal-entity": "JJ",
    "date-entity": "NNP",
    "quantity": "CD"
}

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser('builder.py')
    parser.add_argument('--amr_files', nargs='+', default=[])
    parser.add_argument('--util_dir', required=True)

    args = parser.parse_args()

    rules = {}

    with open(path.join(args.util_dir, "entity_type_cooccur_counter.json"), encoding='utf-8') as f:
        type_counter = json.load(f)

    type_ner_mapper = {}

    for key, value in type_counter.items():
        max_ner = None
        max_ner_count = None
        for ner, count in value.items():
            if max_ner is None:
                max_ner = ner
                max_ner_count = count
                continue
            if count > max_ner_count:
                max_ner = ner
                max_ner_count = count
        type_ner_mapper[key] = max_ner

    for file_path in args.amr_files:
        for amr in AMRIO.read(file_path):
            for key, value in amr.abstract_map.items():
                value_type = value["type"]
                value_span = value["span"]

                if len(value_span) <= 1:
                    continue

                if (value_type == 'named-entity' or value_type == 'ordinal-entity') \
                        and distance(value_span, value["ops"]) > 3:
                    continue

                value["ner"] = type_ner_mapper.get(
                    value_span.lower(), {
                        "named-entity": "PERSON",
                        "url-entity": "URL",
                        "score-entity": "SCORE_ENTITY",
                        "ordinal-entity": "ORDINAL_ENTITY",
                        "date-entity": "DATE_ATTRS",
                        "quantity": f"_QUANTITY_{key}"
                    }[value_type]
                )

                rules.setdefault(value_type, [{}, type_map[value_type]])
                rules[value_type][0][value_span] = value

    templates["text_maps"] = rules

    with open(path.join(args.util_dir, "text_anonymization_rules.json"), 'w', encoding='utf-8') as f:
        json.dump(templates, f, ensure_ascii=False, sort_keys=True)
