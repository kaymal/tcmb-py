# tcmb

[![PyPI Latest Release](https://img.shields.io/pypi/v/tcmb)](https://pypi.org/project/tcmb/)
[![License](https://img.shields.io/github/license/kaymal/tcmb-py)](https://github.com/kaymal/tcmb-py/blob/main/LICENSE)
[![Downloads](https://static.pepy.tech/badge/tcmb)](https://pepy.tech/project/tcmb)
[![Python Version](https://img.shields.io/pypi/pyversions/tcmb)]()
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

`tcmb` is a Python API wrapper around the Central Bank of the Republic of Türkiye (TCMB) Web Service. It is an _unofficial_ open-source Python package intended for personal use ([Disclaimer](#disclaimer)).

---

_`tcmb`, Türkiye Cumhuriyeti Merkez Bankası (TCMB) Web Servisi'ne Python aracılığıyla erişimi sağlayan resmi olmayan API uygulamasıdır. Kişisel kullanım ve araştırma maksadıyla hazırlanmıştır ([Elektronik Veri Dağıtım Sistemi (EVDS) Kullanım Koşulları](https://evds2.tcmb.gov.tr/help/videos/EVDS_Kullanim_Sartlari.pdf))._

## Quickstart

```shell
pip install tcmb
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
Client.categories

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
Client.datagroups

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

Datagroups consist of time series, each having a series key such as `TP.YSSK.A1` or `TP.DK.USD.S.YTL`. Series is read using the `.read()` method.

```python
import tcmb

client = tcmb.Client(api_key="...")

# read one time series
data = client.read("TP.YSSK.A1")

# read multiple time series
data = client.read(["TP.YSSK.A1", "TP.YSSK.A2", "TP.YSSK.A3"])
```

A convenient way to read time series without initializing the Client instance is using the `read()` function in the `core.py` module.

```python
import tcmb

# read one time series
data = tcmb.read("TP.YSSK.A1", api_key="...")

# read multiple time series
data = tcmb.read(["TP.YSSK.A1", "TP.YSSK.A2", "TP.YSSK.A3"], api_key="...")
```

Series metadata can be fetched with `.get_series_metadata()` method.

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

The wildcard characters are represented as an asterisk `*` or a question mark `?`. The asterisk `*` represents any number of characters, while the question mark `?` represents a single character. Additionally, omitting the value has the same effect as using an asterisk. Note that, wildcard character option is not a feature of TCMB web service. Wildcard pattern search is implemented within the `tcmb` package and depends on the package data.

## Installation

```sh
pip install tcmb
```

## Authentication

An API key is required to access the Web Service. Users can sign up from the [login](https://evds2.tcmb.gov.tr/index.php?/evds/login) page. Once logged in, API Key is generated from the Profile page.

There are two ways of providing API key to the `tcmb` client.
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
client = Client(api_key="...")
```

## Disclaimer
`tcmb` is an **unofficial** open-source package intended for personal use and research purposes. Please see TCMB's [EVDS Disclaimer](https://evds2.tcmb.gov.tr/help/videos/EVDS_Disclaimer.pdf) for the official terms of use of the EVDS Web Service.
