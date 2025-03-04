import json

# This script is called by generate_run_items.py and provides functions to validate the run_config.json


# Load input JSON files
def load_json(filename):
    with open(filename, "r") as file:
        return json.load(file)


config = load_json("run_config.json")


def validate_mode_settings(config):
    mode_settings = config.get("mode_settings", {})

    if (
        mode_settings.get("run_from_layer", 0) == 0
        and mode_settings.get("run_from_sublayer", 0) > 0
    ):
        raise ValueError(
            "Invalid mode settings: 'run_from_sublayer' specified without 'run_from_layer'."
        )

    if (
        mode_settings.get("rerun_from_failure", None)
        or mode_settings.get("rerun_from_completed", None)
        or mode_settings.get("rerun_failed_runitems_only", None)
    ) and (
        mode_settings.get("run_from_layer", None) > 0
        or mode_settings.get("run_layer_only", None) > 0
        or mode_settings.get("run_from_sublayer", None) > 0
        or mode_settings.get("run_sublayer_only", None) > 0
        or mode_settings.get("run_from_runitem", None) > 0
        or mode_settings.get("run_runitem_only", None) > 0
    ):
        raise ValueError(
            "Invalid mode settings: At least one boolean is true with one or more run point values specified."
        )

    if (
        mode_settings.get("run_from_layer", None) > 0
        and mode_settings.get("run_layer_only", None) > 0
    ):
        raise ValueError(
            "Invalid mode settings: 'run_from_layer' and 'run_layer_only' cannot both be specified."
        )

    if (
        mode_settings.get("run_from_sublayer", None) > 0
        and mode_settings.get("run_sublayer_only", None) > 0
    ):
        raise ValueError(
            "Invalid mode settings: 'run_from_sublayer' and 'run_sublayer_only' cannot both be specified."
        )

    if (
        mode_settings.get("run_from_runitem", None) > 0
        and mode_settings.get("run_runitem_only", None) > 0
    ):
        raise ValueError(
            "Invalid mode settings: 'run_from_runitem' and 'run_runitem_only' cannot both be specified."
        )

    if (
        config.get("mode", "") == "filtered"
        and not (mode_settings.get("rerun_from_failure", None))
        and not (mode_settings.get("rerun_from_completed", None))
        and not (mode_settings.get("rerun_failed_runitems_only", None))
        and mode_settings.get("run_from_layer", None) == 0
        and mode_settings.get("run_layer_only", None) == 0
        and mode_settings.get("run_from_sublayer", None) == 0
        and mode_settings.get("run_sublayer_only", None) == 0
        and mode_settings.get("run_from_runitem", None) == 0
        and mode_settings.get("run_runitem_only", None) == 0
        and mode_settings.get("run_specific_parameters_only", None) == []
        and mode_settings.get("run_specific_datasets_only", None) == []
    ):
        raise ValueError(
            "Invalid mode settings: mode is set to filtered but all mode_settings are set to their default values. This means no filtering logic is specified. Please change mode to default if you intend to generate the default run items and use those. If you want to filter, please specify valid filter values."
        )
