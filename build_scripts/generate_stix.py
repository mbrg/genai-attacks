import argparse
import json
import logging
import os
import uuid
from datetime import datetime


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


def get_platforms(base_dir):
    platforms_dir = os.path.join(base_dir, "platform")
    platforms = []
    if os.path.exists(platforms_dir):
        for file in os.listdir(platforms_dir):
            if file.endswith(".json"):
                platform = load_json_file(os.path.join(platforms_dir, file))
                platforms.append(platform["name"])
    return platforms


def load_tactics(base_dir):
    tactics_dir = os.path.join(base_dir, "tactic")
    tactics = []
    if os.path.exists(tactics_dir):
        for file in os.listdir(tactics_dir):
            if file.endswith(".json"):
                tactic = load_json_file(os.path.join(tactics_dir, file))
                tactics.append(tactic)
    return tactics


def generate_stix_bundle(base_dir, output_file, base_url):
    techniques_dir = os.path.join(base_dir, "technique")

    if not os.path.exists(techniques_dir):
        logging.error("Technique directory does not exist.")
        return

    platforms = get_platforms(base_dir)
    logging.info(f"Found platforms: {platforms}")

    tactics = load_tactics(base_dir)
    logging.info(f"Loaded {len(tactics)} custom tactics")

    bundle = {
        "type": "bundle",
        "id": f"bundle--{uuid.uuid4()}",
        "spec_version": "2.0",
        "objects": [],
    }

    # Add custom tactics
    for tactic in tactics:
        stix_tactic = {
            "type": "x-mitre-tactic",
            "id": f"x-mitre-tactic--{uuid.uuid4()}",
            "created": datetime.now().isoformat() + "Z",
            "modified": datetime.now().isoformat() + "Z",
            "name": tactic["name"],
            "description": tactic["description"],
            "x_mitre_shortname": tactic["$id"].split("/")[-1],
            "external_references": [
                {
                    "source_name": "mitre-attack",
                    "external_id": tactic["$id"].split("/")[-1],
                }
            ],
        }
        bundle["objects"].append(stix_tactic)

    # Process techniques
    technique_count = 0
    for file in os.listdir(techniques_dir):
        if file.endswith(".json"):
            technique = load_json_file(os.path.join(techniques_dir, file))
            technique_id = technique["$id"].split("/")[-1]

            logging.debug(f"Processing technique: {technique_id} - {technique['name']}")

            # Find associated tactic(s)
            kill_chain_phases = []
            for ref in technique.get("object_references", []):
                if ref["$type"] == "tactic":
                    custom_tactic_id = ref["$id"].split("/")[-1]
                    kill_chain_phases.append(
                        {
                            "kill_chain_name": "mitre-attack",
                            "phase_name": custom_tactic_id,
                        }
                    )

            if not kill_chain_phases:
                logging.warning(f"Technique {technique_id} has no associated tactics")
                continue

            stix_technique = {
                "type": "attack-pattern",
                "id": f"attack-pattern--{uuid.uuid4()}",
                "created": datetime.now().isoformat() + "Z",
                "modified": datetime.now().isoformat() + "Z",
                "name": technique["name"],
                "description": technique["description"],
                "kill_chain_phases": kill_chain_phases,
                "external_references": [
                    {
                        "source_name": "mitre-attack",
                        "external_id": technique_id,
                        "url": f"{base_url}/technique/{technique_id}.html",
                    }
                ],
                "x_mitre_platforms": platforms,
            }
            bundle["objects"].append(stix_technique)
            technique_count += 1
            logging.debug(f"Added technique {technique_id} to STIX bundle")

    # Add a custom x-mitre-matrix
    matrix = {
        "type": "x-mitre-matrix",
        "id": f"x-mitre-matrix--{uuid.uuid4()}",
        "name": "GenAI Attacks Matrix",
        "description": "Custom matrix for GenAI Attacks",
        "tactic_refs": [
            obj["id"] for obj in bundle["objects"] if obj["type"] == "x-mitre-tactic"
        ],
        "created": datetime.now().isoformat() + "Z",
        "modified": datetime.now().isoformat() + "Z",
    }
    bundle["objects"].append(matrix)

    logging.info(f"Processed {technique_count} techniques")

    with open(output_file, "w") as f:
        json.dump(bundle, f, indent=2)

    logging.info(f"Custom STIX bundle generated and saved to {output_file}")
    logging.info(f"Total objects in bundle: {len(bundle['objects'])}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate custom STIX bundle for MITRE ATT&CK Navigator"
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
        default="genai_attacks_stix_bundle.json",
        help="Output file for the custom STIX bundle",
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
    generate_stix_bundle(args.input_dir, args.output_file, args.base_url)
