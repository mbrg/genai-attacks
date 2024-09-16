"""
AI-generated attacks matrix documentation generator
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
from collections import defaultdict
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def get_git_timestamps(file_path):
    try:
        # Get the earliest commit date for this file
        created_at = (
            subprocess.check_output(
                ["git", "log", "--follow", "--format=%ai", "--reverse", file_path]
            )
            .decode()
            .split("\n")[0]
            .strip()
        )

        # Get the latest commit date for this file
        modified_at = (
            subprocess.check_output(["git", "log", "-1", "--format=%ai", file_path])
            .decode()
            .strip()
        )

        # If created_at is empty, the file might not be tracked by git yet
        if not created_at:
            # Use file system creation time as a fallback
            logger.debug(
                f"File {file_path} is not tracked by Git. Using file system creation time."
            )
            created_at = datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()

        # If modified_at is empty, use the file system modification time
        if not modified_at:
            logger.debug(
                f"File {file_path} has no Git modification time. Using file system modification time."
            )
            modified_at = datetime.fromtimestamp(
                os.path.getmtime(file_path)
            ).isoformat()

        return created_at, modified_at
    except subprocess.CalledProcessError:
        logger.warning(f"Unable to get Git timestamps for {file_path}")
        # Use file system times as a fallback
        created_at = datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
        modified_at = datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
        return created_at, modified_at


def load_json_files(base_dir, version):
    data = {}
    search_dirs = [
        os.path.join(base_dir, "tactic"),
        os.path.join(base_dir, "technique"),
        os.path.join(base_dir, "procedure"),
        os.path.join(base_dir, "platform"),
        os.path.join(base_dir, "entity"),
    ]

    for directory in search_dirs:
        logger.debug(f"Searching directory: {directory}")
        if not os.path.exists(directory):
            logger.warning(f"Directory {directory} does not exist. Skipping.")
            continue

        for file in os.listdir(directory):
            if file.endswith(".json"):
                file_path = os.path.join(directory, file)
                logger.debug(f"Processing file: {file_path}")
                try:
                    with open(file_path, "r") as f:
                        obj = json.load(f)
                    if "$id" not in obj or "$type" not in obj:
                        logger.warning(
                            f"File {file_path} does not contain required keys. Skipping."
                        )
                        continue

                    # Add new properties
                    obj["version"] = version
                    created_at, modified_at = get_git_timestamps(file_path)
                    obj["created_at"] = created_at
                    obj["last_modified_at"] = modified_at

                    data[obj["$id"]] = obj
                    logger.debug(f"Successfully loaded object with $id: {obj['$id']}")
                except json.JSONDecodeError:
                    logger.error(f"Unable to parse JSON in file {file_path}. Skipping.")
                except Exception as e:
                    logger.error(
                        f"Error processing file {file_path}: {str(e)}. Skipping."
                    )
    return data


def create_matrix(tactics, techniques):
    logger.debug("Creating matrix of tactics and techniques")
    matrix = defaultdict(list)
    for technique in techniques.values():
        for ref in technique.get("object_references", []):
            if ref["$type"] == "tactic":
                matrix[ref["$id"]].append(technique["$id"])
                logger.debug(
                    f"Added technique {technique['$id']} to tactic {ref['$id']}"
                )
    return matrix


def generate_main_page(tactics, techniques, matrix):
    logger.debug("Generating main page content")
    content = "# GenAI Attacks Matrix\n\n"
    sorted_tactics = sorted(tactics.values(), key=lambda x: x["tactic_order"])

    # Generate header row
    content += (
        "| "
        + " | ".join(
            [
                f"[{tactic['name']}](tactic/{tactic['$id'].split('/')[-1]}.md)"
                for tactic in sorted_tactics
            ]
        )
        + " |\n"
    )
    content += "|" + "---|" * len(tactics) + "\n"

    # Find the maximum number of techniques for any tactic
    max_techniques = max(len(matrix[tactic["$id"]]) for tactic in sorted_tactics)
    logger.debug(f"Found max techniques-per-tactic: {max_techniques}")

    # Generate rows for techniques
    for i in range(max_techniques):
        row = []
        for tactic in sorted_tactics:
            if i < len(matrix[tactic["$id"]]):
                tech_id = matrix[tactic["$id"]][i]
                row.append(
                    f"[{techniques[tech_id]['name']}](technique/{tech_id.split('/')[-1]}.md)"
                )
            else:
                row.append("")
        if any(row):  # Only add the row if it's not entirely empty
            content += "| " + " | ".join(row) + " |\n"

    return content


def generate_object_page(obj, all_objects, base_dir):
    logger.debug(f"Generating page for object: {obj['$id']}")
    content = f"# {obj['name']}\n\n"
    content += f"**Type:** {obj['$type']}\n\n"
    content += f"**Description:** {obj['description']}\n\n"
    content += f"**Version:** {obj['version']}\n\n"
    content += f"**Created At:** {obj['created_at']}\n\n"
    content += f"**Last Modified At:** {obj['last_modified_at']}\n\n"

    if "tactic_order" in obj:
        content += f"**Tactic Order:** {obj['tactic_order']}\n\n"

    if "entity_type" in obj:
        content += f"**Entity Type:** {obj['entity_type']}\n\n"

    content += "\n\n---\n\n"

    content += "### External References\n"
    for ref in obj.get("external_references", []):
        content += f"- [{ref['title']}]({ref['href']}), {ref['source']}\n"

    content += "\n### Reference To Other Objects\n"
    for ref in obj.get("object_references", []):
        if ref["$id"] in all_objects:
            referenced_obj = all_objects[ref["$id"]]
            content += f"- [{referenced_obj['name']}](../{referenced_obj['$type']}/{ref['$id'].split('/')[-1]}.md) ({referenced_obj['$type']}): {ref['description']}\n"
        else:
            content += f"- {ref['$id']} ({ref['$type']}): {ref['description']} (Reference not found)\n"

    content += "\n### Referenced By Over Objects\n"
    for other_obj in all_objects.values():
        for ref in other_obj.get("object_references", []):
            if ref["$id"] == obj["$id"]:
                content += f"- [{other_obj['name']}](../{other_obj['$type']}/{other_obj['$id'].split('/')[-1]}.md) ({other_obj['$type']}): {ref['description']}\n"

    content += "\n### Related Frameworks\n"
    for ref in obj.get("framework_references", []):
        content += (
            f"- [{ref['framework_name']} - {ref['framework_id']}]({ref['href']})\n"
        )

    return content


def generate_summary_page(tactics, techniques, procedures, platforms, entities, matrix):
    logger.debug("Generating summary page content")
    content = "# GenAI Attacks\n\n"
    content += "* [Attacks Matrix](matrix.md)\n"

    content += "\n## Tactics\n"
    content += "* [Tactics](tactics.md)\n"
    sorted_tactics = sorted(tactics.values(), key=lambda x: x["tactic_order"])
    for tactic in sorted_tactics:
        content += f"  * [{tactic['name']}](tactic/{tactic['$id'].split('/')[-1]}.md)\n"
        for tech_id in matrix[tactic["$id"]]:
            content += f"    * [{techniques[tech_id]['name']}](technique/{tech_id.split('/')[-1]}.md)\n"

    content += "\n## Procedures\n"
    content += "* [Procedures](procedures.md)\n"
    for procedure in procedures.values():
        content += f"    * [{procedure['name']}](procedure/{procedure['$id'].split('/')[-1]}.md)\n"

    content += "\n## Platforms\n"
    content += "* [Platforms](platforms.md)\n"
    for platform in platforms.values():
        content += f"    * [{platform['name']}](platform/{platform['$id'].split('/')[-1]}.md)\n"

    content += "\n## Entities\n"
    content += "* [Entities](entities.md)\n"
    for entity in entities.values():
        content += (
            f"    * [{entity['name']}](entity/{entity['$id'].split('/')[-1]}.md)\n"
        )

    return content


def main():
    parser = argparse.ArgumentParser(
        description="Generate documentation for GenAI Attacks Matrix"
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug logging"
    )
    parser.add_argument(
        "-v", "--version", default="0.0.0", help="Version number for the objects"
    )
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    base_dir = "."  # Adjust this to the root of your repo
    build_dir = os.path.join(base_dir, "build")

    # Delete existing build folder
    if os.path.exists(build_dir):
        logger.info(f"Deleting existing build folder: {build_dir}")
        shutil.rmtree(build_dir)

    logger.info(f"Creating new build folder: {build_dir}")
    os.makedirs(build_dir, exist_ok=True)

    all_objects = load_json_files(base_dir, args.version)

    if not all_objects:
        logger.error("No valid objects found. Please check your JSON files.")
        return

    tactics = {k: v for k, v in all_objects.items() if v["$type"] == "tactic"}
    techniques = {k: v for k, v in all_objects.items() if v["$type"] == "technique"}
    procedures = {k: v for k, v in all_objects.items() if v["$type"] == "procedure"}
    platforms = {k: v for k, v in all_objects.items() if v["$type"] == "platform"}
    entities = {k: v for k, v in all_objects.items() if v["$type"] == "entity"}

    logger.info(
        f"Found {len(tactics)} tactics, {len(techniques)} techniques, {len(procedures)} procedures, {len(platforms)} platforms, and {len(entities)} entities"
    )

    if not tactics or not techniques:
        logger.error("No tactics or techniques found. Please check your JSON files.")
        return

    matrix = create_matrix(tactics, techniques)

    # Generate main page (MATRIX.md)
    matrix_content = generate_main_page(tactics, techniques, matrix)
    matrix_path = os.path.join(build_dir, "MATRIX.md")
    logger.info(f"Writing main matrix page to: {matrix_path}")
    with open(matrix_path, "w") as f:
        f.write(matrix_content)

    object_types = ["tactic", "technique", "procedure", "platform", "entity"]

    for obj_type in object_types:
        type_dir = os.path.join(build_dir, obj_type)
        logger.info(f"Creating directory: {type_dir}")
        os.makedirs(type_dir, exist_ok=True)
        for obj in all_objects.values():
            if obj["$type"] == obj_type:
                page_content = generate_object_page(obj, all_objects, base_dir)
                file_name = f"{obj['$id'].split('/')[-1]}.md"
                file_path = os.path.join(type_dir, file_name)
                logger.debug(f"Writing file: {file_path}")
                try:
                    with open(file_path, "w") as f:
                        f.write(page_content)
                    logger.debug(f"Successfully wrote file: {file_path}")
                except Exception as e:
                    logger.error(f"Error writing file {file_path}: {str(e)}")

    # Generate summary page (SUMMARY.md)
    summary_content = generate_summary_page(
        tactics, techniques, procedures, platforms, entities, matrix
    )
    summary_path = os.path.join(build_dir, "SUMMARY.md")
    logger.info(f"Writing summary page to: {summary_path}")
    with open(summary_path, "w") as f:
        f.write(summary_content)

    logger.info("Documentation generation complete.")


if __name__ == "__main__":
    main()
