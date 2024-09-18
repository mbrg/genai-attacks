import argparse
import json
import logging
import os
from datetime import datetime

import requests


def setup_logging(log_level):
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    logging.basicConfig(
        level=numeric_level, format="%(asctime)s - %(levelname)s - %(message)s"
    )


def load_json_file(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


def get_mitre_tactics():
    url = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
    response = requests.get(url)
    data = response.json()

    tactics = {}
    for obj in data["objects"]:
        if obj["type"] == "x-mitre-tactic":
            tactic_id = obj["external_references"][0]["external_id"]
            tactics[tactic_id] = {
                "name": obj["name"],
                "shortname": obj["x_mitre_shortname"],
            }
    return tactics


def get_platforms(base_dir):
    platforms_dir = os.path.join(base_dir, "platform")
    platforms = []
    if os.path.exists(platforms_dir):
        for file in os.listdir(platforms_dir):
            if file.endswith(".json"):
                platform = load_json_file(os.path.join(platforms_dir, file))
                platforms.append(platform["name"])
    return platforms


def load_tactic_mapping(base_dir):
    tactics_dir = os.path.join(base_dir, "tactic")
    tactic_mapping = {}
    if os.path.exists(tactics_dir):
        for file in os.listdir(tactics_dir):
            if file.endswith(".json"):
                tactic = load_json_file(os.path.join(tactics_dir, file))
                custom_id = tactic["$id"]
                for ref in tactic.get("framework_references", []):
                    if ref["framework_name"] == "MITRE ATT&CK":
                        tactic_mapping[custom_id] = ref["framework_id"]
                        break
    return tactic_mapping


def generate_custom_layer(base_dir, output_file, layer_version, base_url):
    techniques_dir = os.path.join(base_dir, "technique")

    if not os.path.exists(techniques_dir):
        logging.error("Technique directory does not exist.")
        return

    platforms = get_platforms(base_dir)
    logging.info(f"Found platforms: {platforms}")

    mitre_tactics = get_mitre_tactics()
    logging.info(f"Retrieved {len(mitre_tactics)} MITRE tactics")

    tactic_mapping = load_tactic_mapping(base_dir)
    logging.info(f"Loaded mapping for {len(tactic_mapping)} custom tactics")

    layer = {
        "name": "GenAI Attacks Matrix",
        "versions": {"attack": "15", "navigator": "4.9.0", "layer": "4.5"},
        "domain": "enterprise-attack",
        "description": "Custom layer for GenAI Attacks Matrix with links to Github Pages, using MITRE tactics.",
        "filters": {"platforms": platforms},
        "sorting": 0,
        "layout": {"layout": "side", "showName": True, "showID": True},
        "hideDisabled": False,
        "techniques": [],
        "gradient": {"colors": ["#ffffff", "#66b1ff"], "minValue": 0, "maxValue": 100},
        "legendItems": [{"label": "GenAI Attack Technique", "color": "#66b1ff"}],
        "metadata": [
            {
                "name": "Generated on",
                "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
            {"name": "Layer version", "value": layer_version},
        ],
    }

    # Process techniques
    technique_count = 0
    for file in os.listdir(techniques_dir):
        if file.endswith(".json"):
            technique = load_json_file(os.path.join(techniques_dir, file))
            technique_id = technique["$id"].split("/")[-1]

            logging.debug(f"Processing technique: {technique_id} - {technique['name']}")

            # Find associated tactic(s)
            associated_tactics = []
            for ref in technique.get("object_references", []):
                if ref["$type"] == "tactic":
                    custom_tactic_id = ref["$id"]
                    mitre_tactic_id = tactic_mapping.get(custom_tactic_id)
                    if mitre_tactic_id in mitre_tactics:
                        associated_tactics.append(
                            mitre_tactics[mitre_tactic_id]["shortname"]
                        )

            if not associated_tactics:
                logging.warning(
                    f"Technique {technique_id} has no associated MITRE tactics"
                )
                continue

            technique_entry = {
                "techniqueID": technique_id,
                "tactic": associated_tactics,
                "color": "#66b1ff",
                "comment": technique["description"],
                "enabled": True,
                "showSubtechniques": False,
                "metadata": [
                    {"name": "Description", "value": technique["description"]}
                ],
                "links": [
                    {
                        "label": "More info",
                        "url": f"{base_url}/technique/{technique_id}.html",
                    }
                ],
            }
            layer["techniques"].append(technique_entry)
            technique_count += 1
            logging.debug(f"Added technique {technique_id} to layer")

    logging.info(f"Processed {technique_count} techniques")

    with open(output_file, "w") as f:
        json.dump(layer, f, indent=2)

    logging.info(f"Custom layer generated and saved to {output_file}")
    logging.info(f"Total items in layer: {len(layer['techniques'])}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate custom layer for MITRE ATT&CK Navigator"
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        default=".",
        help="Input directory containing technique JSON files",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default="genai_attacks_navigator_layer.json",
        help="Output file for the custom layer JSON",
    )
    parser.add_argument(
        "--layer-version",
        type=str,
        default="1.0",
        help="Version number for the custom layer",
    )
    parser.add_argument(
        "--base-url", type=str, required=True, help="Base URL for the GitHub Pages"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
    )
    args = parser.parse_args()

    setup_logging(args.log_level)
    generate_custom_layer(
        args.input_dir, args.output_file, args.layer_version, args.base_url
    )
