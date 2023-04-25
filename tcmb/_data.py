import json
import os.path


def read_package_data() -> list:
    """Read series codes from the package resources."""
    file_path = os.path.join(os.path.dirname(__file__), "resources", "series.json")

    with open(file_path, "r") as file:
        dg_series = json.load(file)

    series_list = []

    for item in dg_series.values():
        series_list.extend(item)

    return series_list


def fetch_dg_series_codes() -> dict:
    """Get series codes for each datagroup."""
    from tcmb import Client

    client = Client()
    dg_codes = [dg["DATAGROUP_CODE"] for dg in client.datagroups]

    # There are 439 data groups as of 2023-04-25
    print(f"There are {len(dg_codes)} in total.")

    dg_series = {}
    for dg_code in dg_codes:
        series_codes = []
        series_metadata = client.get_series_metadata(datagroup=dg_code)

        if isinstance(series_metadata, dict):
            series_metadata = [series_metadata]

        for item in series_metadata:
            series_codes.append(item["SERIE_CODE"])

        dg_series[dg_code] = series_codes

    return dg_series


def _update_package_data():
    """Update package resources."""
    dg_series = fetch_dg_series_codes()

    file_path = os.path.join(os.path.dirname(__file__), "resources", "series.json")

    with open(file_path, "w") as file:
        json.dump(dg_series, file)
