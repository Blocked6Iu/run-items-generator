import json
import os
from datetime import datetime, timezone
from itertools import product
from math import ceil

import filter_logic
import filter_logic_validate


# Load input JSON files
def load_json(filename):
    with open(filename, "r") as file:
        return json.load(file)


datasets = load_json("datasets.json")
parameters = load_json("parameters.json")
layers = load_json("layers.json")
config = load_json("run_config.json")


# validate the user values in run_config.json
filter_logic_validate.validate_mode_settings(config)

# Create RunItems directory if it doesn't exist
mode = config.get("mode", "")
output_dir = mode
os.makedirs(output_dir, exist_ok=True)

# Clear existing files in output directory
for file in os.listdir(output_dir):
    file_path = os.path.join(output_dir, file)
    if os.path.isfile(file_path):
        os.remove(file_path)

# Prepare metadata structure
metadata_output = {
    "metadata": {"generated_at": datetime.now(timezone.utc).isoformat(), "layers": []}
}

# Generate a sequential run_item_id
run_item_id = 1

# Process layers
for layer in sorted(layers["layers"], key=lambda x: x["order"]):
    if layer["layer_enabled"]:
        run_item_detail = []

        # Identify relevant parameters for the layer
        applicable_parameters = [
            param
            for param in parameters["parameters"]
            if layer["layer"] in param["layer_scope"]
        ]

        # Identify relevant datasets for the layer
        applicable_datasets = [
            dataset
            for dataset in datasets
            if layer["layer"] in dataset["layer_scope"] and dataset["dataset_enabled"]
        ]

        if applicable_datasets:  # Dataset-scoped layers
            for dataset, param_value in product(
                applicable_datasets,
                next((p["parameter_values"] for p in applicable_parameters), []),
            ):
                delta_enabled = dataset.get("delta_details", {}).get(
                    "delta_enabled", False
                )

                run_item = {
                    "run_item_id": run_item_id,
                    "pipeline_name": (
                        layer["pipelines"][0]["pipeline_name"]
                        if layer["pipelines"]
                        else None
                    ),
                    "parameter_details": {
                        "parameter_name": next(
                            (
                                p["parameter_name"]
                                for p in applicable_parameters
                                if param_value in p["parameter_values"]
                            ),
                            "",
                        ),
                        "parameter_values": [param_value],
                    },
                    "dataset_details": {
                        "dataset_name": dataset["dataset_name"],
                        "dataset_enabled": dataset["dataset_enabled"],
                        "data_group": dataset.get("data_group", None),
                        "source_details": {**dataset["source_details"]},
                        "target_details": dataset["target_details"],
                    },
                    "state_details": {
                        "state": "",
                        "state_updated": datetime.now(timezone.utc).isoformat(),
                    },
                }

                if delta_enabled:
                    run_item["dataset_details"]["delta_details"] = dataset[
                        "delta_details"
                    ]

                run_item_detail.append(run_item)
                run_item_id += 1
        else:  # Parameter-based layers
            for param in applicable_parameters:
                param_values = param["parameter_values"]
                if isinstance(param_values, str):
                    param_values = [{"value": param_values}]
                elif isinstance(param_values, list):
                    param_values = [
                        {**(value if isinstance(value, dict) else {"value": value})}
                        for value in param_values
                    ]

                for param_value in param_values:
                    run_item_detail.append(
                        {
                            "run_item_id": run_item_id,
                            "pipeline_name": (
                                layer["pipelines"][0]["pipeline_name"]
                                if layer["pipelines"]
                                else None
                            ),
                            "parameter_details": {
                                "parameter_name": param["parameter_name"],
                                "parameter_values": [param_value],
                            },
                            "dataset_details": None,
                            "state_details": {
                                "state": "",
                                "state_updated": datetime.now(timezone.utc).isoformat(),
                            },
                        }
                    )
                    run_item_id += 1

        # Determine sublayers using per-layer sublayer size
        sublayer_size = layer.get("sublayer_size", 30)  # Default to 30 if not provided
        num_sublayers = (
            ceil(len(run_item_detail) / sublayer_size) if run_item_detail else 1
        )
        sublayers = []

        for i in range(num_sublayers):
            sublayer_items = run_item_detail[
                i * sublayer_size : (i + 1) * sublayer_size
            ]
            sublayer_number = i + 1
            filename = f"{output_dir}/run_items_{layer['layer']}_{sublayer_number}.json"

            # Write sublayer file with timestamp
            with open(filename, "w") as sublayer_file:
                json.dump(
                    {
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        "run_items": sublayer_items,
                    },
                    sublayer_file,
                    indent=4,
                )

            sublayers.append(
                {
                    "sublayer": sublayer_number,
                    "filename": filename,
                    "run_items": [item["run_item_id"] for item in sublayer_items],
                }
            )

        # Store metadata about sublayers
        metadata_output["metadata"]["layers"].append(
            {"layer": layer["layer"], "sublayers": sublayers}
        )

# Save metadata output JSON
metadata_filename = f"{output_dir}/run_items_metadata.json"
with open(metadata_filename, "w") as metadata_file:
    json.dump(metadata_output, metadata_file, indent=4)


# filter out any files from filtered directory based on run_config.json
filter_logic.apply_filtering()
