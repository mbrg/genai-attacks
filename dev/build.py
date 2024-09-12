import json
import logging
import os
import shutil
from collections import defaultdict

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def load_json_files(base_dir):
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
    content = "# ATT&CK-like Matrix\n\n"
    sorted_tactics = sorted(tactics.values(), key=lambda x: x["tactic_order"])

    # Generate header row
    content += (
        "| "
        + " | ".join(
            [
                f"[{tactic['name']}](tactics/{tactic['$id'].split('/')[-1]}.md)"
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
                    f"[{techniques[tech_id]['name']}](techniques/{tech_id.split('/')[-1]}.md)"
                )
            else:
                row.append("")
        if any(row):  # Only add the row if it's not entirely empty
            content += "| " + " | ".join(row) + " |\n"

    return content


def generate_object_page(obj, all_objects):
    logger.debug(f"Generating page for object: {obj['$id']}")
    content = f"# {obj['name']}\n\n"
    content += f"**Type:** {obj['$type']}\n\n"
    content += f"**Description:** {obj['description']}\n\n"

    if "tactic_order" in obj:
        content += f"**Tactic Order:** {obj['tactic_order']}\n\n"

    if "entity_type" in obj:
        content += f"**Entity Type:** {obj['entity_type']}\n\n"

    content += "## References\n\n"
    content += "### Object References\n"
    for ref in obj.get("object_references", []):
        if ref["$id"] in all_objects:
            content += f"- [{all_objects[ref['$id']]['name']}]({ref['$type']}s/{ref['$id'].split('/')[-1]}.md): {ref['description']}\n"
        else:
            content += f"- {ref['$id']}: {ref['description']} (Reference not found)\n"

    content += "\n### External References\n"
    for ref in obj.get("external_references", []):
        content += f"- [{ref['title']}]({ref['href']}) ({ref['source']})\n"

    content += "\n### Framework References\n"
    for ref in obj.get("framework_references", []):
        content += (
            f"- [{ref['framework_name']} - {ref['framework_id']}]({ref['href']})\n"
        )

    content += "\n## Referenced By\n"
    for other_obj in all_objects.values():
        for ref in other_obj.get("object_references", []):
            if ref["$id"] == obj["$id"]:
                content += f"- [{other_obj['name']}]({other_obj['$type']}s/{other_obj['$id'].split('/')[-1]}.md): {ref['description']}\n"

    return content


def main():
    base_dir = "."  # Adjust this to the root of your repo
    build_dir = os.path.join(base_dir, "build")

    # Delete existing build folder
    if os.path.exists(build_dir):
        logger.info(f"Deleting existing build folder: {build_dir}")
        shutil.rmtree(build_dir)

    logger.info(f"Creating new build folder: {build_dir}")
    os.makedirs(build_dir, exist_ok=True)

    all_objects = load_json_files(base_dir)

    if not all_objects:
        logger.error("No valid objects found. Please check your JSON files.")
        return

    tactics = {k: v for k, v in all_objects.items() if v["$type"] == "tactic"}
    techniques = {k: v for k, v in all_objects.items() if v["$type"] == "technique"}

    logger.info(f"Found {len(tactics)} tactics and {len(techniques)} techniques")

    if not tactics or not techniques:
        logger.error("No tactics or techniques found. Please check your JSON files.")
        return

    matrix = create_matrix(tactics, techniques)

    # Debugging: Print the contents of the matrix
    for tactic_id, technique_list in matrix.items():
        logger.debug(f"Tactic {tactic_id}: {technique_list}")

    # Generate main page (README.md)
    readme_content = generate_main_page(tactics, techniques, matrix)
    readme_path = os.path.join(build_dir, "README.md")
    logger.info(f"Writing main page to: {readme_path}")
    with open(readme_path, "w") as f:
        f.write(readme_content)

    # Generate individual pages
    object_types = ["tactic", "technique", "procedure", "platform", "entity"]

    for obj_type in object_types:
        type_dir = os.path.join(build_dir, obj_type)
        logger.info(f"Creating directory: {type_dir}")
        os.makedirs(type_dir, exist_ok=True)
        for obj in all_objects.values():
            if obj["$type"] == obj_type:
                page_content = generate_object_page(obj, all_objects)
                file_name = f"{obj['$id'].split('/')[-1]}.md"
                file_path = os.path.join(type_dir, file_name)
                logger.debug(f"Writing file: {file_path}")
                try:
                    with open(file_path, "w") as f:
                        f.write(page_content)
                    logger.debug(f"Successfully wrote file: {file_path}")
                except Exception as e:
                    logger.error(f"Error writing file {file_path}: {str(e)}")

    logger.info("Documentation generation complete.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate documentation for ATT&CK-like matrix"
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug logging"
    )
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    main()
