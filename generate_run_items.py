import json
from itertools import product


# Load input JSON files
def load_json(filename):
    with open(filename, "r") as file:
        return json.load(file)


datasets = load_json("datasets.json")
parameters = load_json("parameters.json")
layers = load_json("layers.json")

institute_list = parameters["dataset_parameters"]["institute_list"]
etl_parameters = parameters["etl_parameters"]
run_parameters = parameters.get("run_parameters", {})

# Prepare output structure
output = {"run_parameters": run_parameters, "layers": []}

# Initialize run_item_id counter
run_item_id_counter = 1

# Process layers
for layer in sorted(layers["layers"], key=lambda x: x["order"]):
    if layer["layer_enabled"]:
        run_item_detail = []

        if layer["dataset_scope"]:  # Dataset-scoped layers
            for dataset, institute in product(datasets, institute_list):
                if dataset["enabled"]:
                    source_query = dataset["source_details"]["source_query"]
                    source_query = source_query.replace(
                        "<<INSTITUTE_ID>>", str(institute["INSTITUTE_ID"])
                    )

                    delta_enabled = dataset.get("delta_details", {}).get(
                        "delta_enabled", False
                    )
                    if delta_enabled:
                        dt_start = dataset["delta_details"].get("dtStart")
                        dt_end = dataset["delta_details"].get("dtEnd")

                        if dt_start:
                            dt_start = f"'{dt_start.strip("'")}'"
                            source_query = source_query.replace("<<dtStart>>", dt_start)
                        if dt_end:
                            dt_end = f"'{dt_end.strip("'")}'"
                            source_query = source_query.replace("<<dtEnd>>", dt_end)

                    run_item = {
                        "run_item_id": run_item_id_counter,
                        "dataset_name": dataset["dataset_name"],
                        "enabled": dataset["enabled"],
                        "data_group": dataset.get("data_group", ""),
                        "dataset_parameters": {
                            **institute,
                            "state_details": parameters["dataset_parameters"].get(
                                "state_details", {"status": ""}
                            ),  # Default status is blank
                        },
                        "source_details": {
                            **dataset["source_details"],
                            "source_query": source_query,
                        },
                    }

                    if delta_enabled:
                        run_item["delta_details"] = dataset["delta_details"]

                    run_item["target_details"] = dataset["target_details"]
                    run_item_detail.append(run_item)
                    run_item_id_counter += 1
        else:  # Non-dataset-scoped layers (use only matching etl_parameters)
            for param_category, param_values in etl_parameters.items():
                if param_values["layer"] == layer["layer"]:
                    run_item_detail.append(
                        {
                            "run_item_id": run_item_id_counter,
                            "etl_category": param_category,
                            "layer": param_values["layer"],
                            "sp_list": [
                                {"sp_name": sp, "state": ""}
                                for sp in param_values["sp_list"]
                            ],
                        }
                    )
                    run_item_id_counter += 1

        layer_entry = {
            "layer": layer["layer"],
            "layer_name": layer["layer_name"],
            "layer_enabled": layer["layer_enabled"],
            "order": layer["order"],
            "dataset_scope": layer["dataset_scope"],
            "specific_datasets": layer["specific_datasets"],
            "run_item_detail": run_item_detail,
            "pipelines": layer["pipelines"],
        }
        output["layers"].append(layer_entry)

# Save output JSON
with open("run_items.json", "w") as outfile:
    json.dump(output, outfile, indent=4)
