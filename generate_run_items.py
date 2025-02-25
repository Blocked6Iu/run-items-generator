import json
from datetime import datetime, timezone
from itertools import product
from math import ceil

# Configurable sublayer size
sublayer_size = 30  # Default maximum number of run items per sublayer


# Load input JSON files
def load_json(filename):
    with open(filename, "r") as file:
        return json.load(file)


datasets = load_json("datasets.json")
parameters = load_json("parameters.json")
layers = load_json("layers.json")

# Prepare output structure
output = {"metadata": {"layers": []}, "layers": []}

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
                if delta_enabled:
                    dt_start = dataset["delta_details"].get("dtStart")
                    dt_end = dataset["delta_details"].get("dtEnd")

                    if dt_start:
                        dt_start = f"'{dt_start.strip("'")}'"
                    if dt_end:
                        dt_end = f"'{dt_end.strip("'")}'"

                run_item = {
                    "run_item_id": run_item_id,
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

        # Determine sublayers
        num_sublayers = (
            ceil(len(run_item_detail) / sublayer_size) if run_item_detail else 1
        )
        sublayers = [
            {
                "sublayer": i + 1,
                "run_items": run_item_detail[
                    i * sublayer_size : (i + 1) * sublayer_size
                ],
            }
            for i in range(num_sublayers)
        ]

        # Store metadata about sublayers
        output["metadata"]["layers"].append(
            {
                "layer": layer["layer"],
                "sublayers": [
                    {
                        "sublayer": sub["sublayer"],
                        "run_items": [item["run_item_id"] for item in sub["run_items"]],
                    }
                    for sub in sublayers
                ],
            }
        )

        layer_entry = {
            "layer": layer["layer"],
            "layer_name": layer["layer_name"],
            "layer_enabled": layer["layer_enabled"],
            "order": layer["order"],
            "sublayers": sublayers,
            "pipelines": layer["pipelines"],
        }
        output["layers"].append(layer_entry)

# Save output JSON
with open("run_items.json", "w") as outfile:
    json.dump(output, outfile, indent=4)
