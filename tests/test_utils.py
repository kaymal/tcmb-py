from tcmb import utils

import pytest


test_date_data = [
    ("01-01-2024", "01-01-2024"),
    ("17.12.2009", "17-12-2009"),
    ("2011-06-18", "18-06-2011"),
    ("2018.04.10", "10-04-2018"),
]


@pytest.mark.parametrize("date_str, expected", test_date_data)
def test_standardize_date(date_str, expected):
    result = utils.standardize_date(date_str)
    print(result)
    assert result == expected


def test_wildcard_search():
    items_expected = [
        "TP.API.REP.TL.A12",
        "TP.API.REP.TL.A23",
        "TP.API.REP.TL.G1",
        "TP.API.REP.TL.G1530",
        "TP.API.REP.TL.G214",
    ]
    items = utils.wildcard_search("TP.API.REP.TL.*")

    assert all(item in items_expected for item in items)
