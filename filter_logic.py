import json
import os


def load_json(filename):
    """Load a JSON file."""
    with open(filename, "r") as file:
        return json.load(file)


def save_json(filename, data):
    """Save data to a JSON file."""
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


def apply_filtering():
    """Apply filtering to the filtered output directory based on run_config.json."""
    # Load config and metadata
    config = load_json("run_config.json")
    metadata_file = "filtered/run_items_metadata.json"
    run_items_metadata = load_json(metadata_file)

    # Exit if mode is not 'filtered'
    if config.get("mode") != "filtered":
        print("Skipping filtering as mode is not 'filtered'")
        return

    # Extract filtering rules from config
    mode_settings = config.get("mode_settings", {})
    run_from_layer = mode_settings.get("run_from_layer", 0)
    run_layer_only = mode_settings.get("run_layer_only", 0)
    run_from_sublayer = mode_settings.get("run_from_sublayer", 0)
    run_sublayer_only = mode_settings.get("run_sublayer_only", 0)
    run_from_runitem = mode_settings.get("run_from_runitem", 0)
    run_runitem_only = mode_settings.get("run_runitem_only", 0)

    updated_layers = []

    # Process metadata layers
    for layer_data in run_items_metadata["metadata"]["layers"]:
        layer = layer_data["layer"]
        if (run_layer_only > 0 and layer != run_layer_only) or (layer < run_from_layer):
            # Delete all files in this layer
            for sublayer_data in layer_data["sublayers"]:
                os.remove(sublayer_data["filename"])
            continue  # Skip adding this layer

        updated_sublayers = []
        for sublayer_data in layer_data["sublayers"]:
            sublayer = sublayer_data["sublayer"]
            filename = sublayer_data["filename"]
            run_items = sublayer_data["run_items"]

            # Check if sublayer should be removed
            if (run_sublayer_only > 0 and sublayer != run_sublayer_only) or (
                sublayer < run_from_sublayer and layer == run_from_layer
            ):
                os.remove(filename)  # Delete file
                continue  # Skip adding this sublayer

            # Filter out specific run_items
            if run_runitem_only:
                run_items = [ri for ri in run_items if ri == run_runitem_only]
            elif run_from_runitem:
                run_items = [ri for ri in run_items if ri >= run_from_runitem]

            # If file is empty, remove it
            if not run_items:
                os.remove(filename)
            else:
                # Load and update file
                file_data = load_json(filename)
                file_data["run_items"] = [
                    item
                    for item in file_data["run_items"]
                    if item["run_item_id"] in run_items
                ]
                save_json(filename, file_data)
                updated_sublayers.append(
                    {"sublayer": sublayer, "filename": filename, "run_items": run_items}
                )

        if updated_sublayers:
            updated_layers.append({"layer": layer, "sublayers": updated_sublayers})

    # Save updated metadata
    run_items_metadata["metadata"]["layers"] = updated_layers
    save_json(metadata_file, run_items_metadata)
    print("Filtering applied successfully.")


if __name__ == "__main__":
    apply_filtering()
