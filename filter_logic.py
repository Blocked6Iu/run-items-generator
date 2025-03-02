# This script is called by generate_run_items.py and provides functions to:
# 1) validate the run_config.json
# 2) filter out files and run_items from the filtered directory based on the run_config.json

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
        config.get("rerun_from_failure", None)
        or config.get("rerun_from_completed", None)
        or config.get("rerun_failed_runitems_only", None)
    ) and (
        config.get("run_from_layer", None) > 0
        or config.get("run_layer_only", None) > 0
        or config.get("run_from_sublayer", None) > 0
        or config.get("run_sublayer_only", None) > 0
        or config.get("run_from_runitem", None) > 0
        or config.get("run_runitem_only", None) > 0
    ):
        raise ValueError(
            "Invalid mode settings: At least one boolean is true with one or more run point values specified."
        )


def apply_filtering(config)
    #this function is run at the very end of generate_run_items.py and applys filtering to the filtered output directory
    #based on the run_config.json
    

    return
