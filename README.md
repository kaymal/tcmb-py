# tcmb

[![PyPI Latest Release](https://img.shields.io/pypi/v/tcmb)](https://pypi.org/project/tcmb/)
[![License](https://img.shields.io/github/license/kaymal/tcmb-py)](https://github.com/kaymal/tcmb-py/blob/main/LICENSE)
[![Downloads](https://static.pepy.tech/badge/tcmb)](https://pepy.tech/project/tcmb)
[![Python Version](https://img.shields.io/pypi/pyversions/tcmb)]()
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![Package workflow](https://github.com/kaymal/tcmb-py/actions/workflows/python-package.yml/badge.svg)

`tcmb` is a Python API wrapper around the Central Bank of the Republic of Türkiye (TCMB) Web Service. It is an _unofficial_ open-source Python package intended for personal use ([Disclaimer](#disclaimer)).

---

_`tcmb`, Türkiye Cumhuriyeti Merkez Bankası (TCMB) Web Servisi'ne Python aracılığıyla erişimi sağlayan resmi olmayan API uygulamasıdır. Kişisel kullanım ve araştırma maksadıyla hazırlanmıştır ([Elektronik Veri Dağıtım Sistemi (EVDS) Kullanım Koşulları](https://evds3.tcmb.gov.tr/igmevdsms-dis/documents/showDocument?docId=18))._

## Quickstart

```shell
pip install tcmb

# or with uv
uv add tcmb
```

```python
import tcmb

client = tcmb.Client(api_key="...")

data = client.read(series="TP.DK.USD.S.YTL")
```

## Overview

### Data Hierarchy

1. Categories:

Categories are at the top level of the TCMB data hierarchy.

```python
client = tcmb.Client(api_key="...")

# show categories
client.categories

{'CATEGORY_ID': 1.0,
 'TOPIC_TITLE_ENG': 'MARKET STATISTICS',
 'TOPIC_TITLE_TR': 'PİYASA VERİLERİ'}
```

It is also possible to get the same information using the `client.get_categories_metadata()` method.

2. Data Groups:

Each category consists of a number of data groups.

```python
client = tcmb.Client(api_key="...")

# show data groups
client.datagroups

[{'DATAGROUP_CODE': 'bie_pyrepo',
  'CATEGORY_ID': 1,
  'DATAGROUP_NAME': 'Açık Piyasa Repo ve Ters Repo İşlemleri',
  'DATAGROUP_NAME_ENG': 'Open Market Repo and Reverse Repo Transactions',
  ...}
 {'DATAGROUP_CODE': 'bie_mkbral',
  'CATEGORY_ID': 0,
  'DATAGROUP_NAME': 'Altın Borsası İşlemleri-İstanbul (TL-ABD Doları)(Arşiv)',
  'DATAGROUP_NAME_ENG': 'Istanbul Gold Exchange (TRY-USD)(Archive)',
  ...}]
```

It is also possible to filter the datagroups metadata using the `client.get_datagroups_metadata()` method.

3. Series

Datagroups consist of time series, each with a series key such as `TP.YSSK.A1` or `TP.DK.USD.S.YTL`. Series can be read using the `.read()` method.

```python
import tcmb

client = tcmb.Client(api_key="...")

# read one time series
data = client.read("TP.YSSK.A1")

# read multiple time series
data = client.read(["TP.YSSK.A1", "TP.YSSK.A2", "TP.YSSK.A3"])
```

A convenient way to read time series without initializing a `Client` instance is to use the package-level `read()` function.

```python
import tcmb

# read one time series
data = tcmb.read("TP.YSSK.A1", api_key="...")

# read multiple time series
data = tcmb.read(["TP.YSSK.A1", "TP.YSSK.A2", "TP.YSSK.A3"], api_key="...")
```

Series metadata can be fetched with the `.get_series_metadata()` method.

```python
# show metadata of each series within a data group
client.get_series_metadata(datagroup="bie_yssk")

[{'SERIE_CODE': 'TP.YSSK.A1',
  'DATAGROUP_CODE': 'bie_yssk',
  'SERIE_NAME': '1-2 Yıl(ABD doları)',
  'SERIE_NAME_ENG': '1-2 Years(USD)',
  ...},
  {'SERIE_CODE': 'TP.YSSK.A2',
  'DATAGROUP_CODE': 'bie_yssk',
  'SERIE_NAME': '3 Yıl(ABD doları)',
  'SERIE_NAME_ENG': '3 Years(USD)',
  ...}]

# show metadata of a specific time series
client.get_series_metadata(series="TP.YSSK.A1")

[{'SERIE_CODE': 'TP.YSSK.A1',
  'DATAGROUP_CODE': 'bie_yssk',
  'SERIE_NAME': '1-2 Yıl(ABD doları)',
  'SERIE_NAME_ENG': '1-2 Years(USD)',
  ...}]
```

## Wildcard Characters

Wildcard characters are `*` and `?`. The asterisk `*` matches zero or more characters, and the question mark `?` matches exactly one character. Additionally, omitting a value has the same effect as using an asterisk. Note that wildcard support is not a feature of the TCMB web service itself; pattern matching is implemented inside `tcmb` package and depends on package data.

```python
>>> data = tcmb.read("TP.DK.USD.*.YTL")
>>> print(data.columns)

Index(['TP_DK_USD_A_YTL', 'TP_DK_USD_S_YTL', 'TP_DK_USD_C_YTL',
       'TP_DK_USD_A_EF_YTL', 'TP_DK_USD_S_EF_YTL'],
      dtype='object')
```

## Installation

```sh
pip install tcmb

# or with uv
uv add tcmb
```

## Authentication

An API key is required to access the web service. Users can sign up on the [login](https://evds3.tcmb.gov.tr/login) page. After signing in, generate an API key from the Profile page.

There are two ways to provide an API key to `tcmb`.
- Using environment variables:

```shell
$ export TCMB_API_KEY="..."
```

```python
import os
os.environ["TCMB_API_KEY"] = "..."
```

- Passing `api_key` when initializing the `Client` class.

```python
import tcmb

client = tcmb.Client(api_key="...")

# optional: override EVDS base URL
client = tcmb.Client(api_key="...", base_url="https://evds3.tcmb.gov.tr/igmevdsms-dis/)
```

## Disclaimer
`tcmb` is an **unofficial** open-source package intended for personal use and research purposes. Please see TCMB's [EVDS Disclaimer](https://evds3.tcmb.gov.tr/igmevdsms-dis/documents/showDocument?docId=18) for the official terms of use of the EVDS Web Service.
