# Changelog

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added 
- 
### Changed
-
### Removed
-
### Fixed
- 

## [0.3.0] - 2023-04-26
### Added 
- Add wildcard option when reading a series key. The wildcard characters are represented as an asterisk `*` or a question mark `?`. The asterisk `*` represents any number of characters, while the question mark `?` represents a single character.
- Add new error types.
- Add a convenient reader function to be used standalone without the need of creating a Client instance. Example usage:

```python
import tcmb

data = tcmb.read(["...", "..."])
```

### Changed
- Catch `HTTPError` instead of the generic Exception. Print more detailed traceback.


## [0.2.0] - 2023-01-25
### Added 
- Add monkeypatch to mock response for tests.
### Changed
- Accept arguments for the parameters `start` and `end` in the `YYYY-MM-DD` format as well as `DD-MM-YYYY` format.
- Update method docstrings.


## [0.1.0] - 2023-01-15
- First release
