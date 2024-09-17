import json
import os
import argparse

def generate_custom_layer(base_dir, output_file, layer_version):
    tactics_dir = os.path.join(base_dir, "tactic")
    techniques_dir = os.path.join(base_dir, "technique")

    if not os.path.exists(tactics_dir) or not os.path.exists(techniques_dir):
        print("Tactic or Technique directory does not exist.")
        return

    layer = {
        "name": "GenAI Attacks Matrix",
        "versions": {
            "attack": "9",
            "navigator": "4.5.5",
            "layer": layer_version
        },
        "domain": "enterprise-attack",
        "description": "Custom layer for GenAI Attacks Matrix with links to Github Pages.",
        "techniques": [],
        "gradient": {
            "colors": ["#ffffff", "#66b1ff"],
            "minValue": 0,
            "maxValue": 100
        },
        "legendItems": [
            {
                "label": "technique",
                "color": "#66b1ff"
            }
        ]
    }

    for directory in [tactics_dir, techniques_dir]:
        for file in os.listdir(directory):
            if file.endswith(".json"):
                file_path = os.path.join(directory, file)
                with open(file_path, "r") as f:
                    obj = json.load(f)
                if obj["$type"] == "tactic":
                    tactic_id = obj["$id"].split("/")[-1]
                    layer["techniques"].append({
                        "techniqueID": tactic_id,
                        "tactic": obj["name"],
                        "score": 100,
                        "comment": obj["description"],
                        "enabled": True,
                        "metadata": [
                            {
                                "name": "link",
                                "value": f"https://zenitysec.github.io/genai-app-attacks/tactic/{tactic_id}.html"
                            }
                        ]
                    })
                elif obj["$type"] == "technique":
                    technique_id = obj["$id"].split("/")[-1]
                    layer["techniques"].append({
                        "techniqueID": technique_id,
                        "tactic": obj["name"],
                        "score": 100,
                        "comment": obj["description"],
                        "enabled": True,
                        "metadata": [
                            {
                                "name": "link",
                                "value": f"https://zenitysec.github.io/genai-app-attacks/technique/{technique_id}.html"
                            }
                        ]
                    })

    with open(output_file, "w") as f:
        json.dump(layer, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate custom layer for MITRE ATT&CK Navigator")
    parser.add_argument("--input-dir", type=str, default=".", help="Input directory containing tactic and technique JSON files")
    parser.add_argument("--output-file", type=str, default="gai_nav.json", help="Output file for the custom layer JSON")
    parser.add_argument("--layer-version", type=str, default="0.0.0", help="Version number for the custom layer")
    args = parser.parse_args()

    generate_custom_layer(args.input_dir, args.output_file, args.layer_version)
