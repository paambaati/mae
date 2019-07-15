# Mae Changelog

`mae` follows [Semantic Versioning](http://semver.org/).

## [1.0.10] - 2019-07-15
### Added
- Add code coverage.

## [1.0.9] - 2019-07-14
### Changed
- Bump `requests` and `mock` dependencies to latest versions. Thanks @dependabot!

## [1.0.8] - 2019-02-28
### Fixed
- 🐞 Return 200 for when no scrape targets are found, so Prometheus can pick it up.

## [1.0.7] - 2019-02-28
### Fixed
- 🐞 Fixed a bug ([#1](https://github.com/paambaati/mae/issues/1)) where an app without labels can cause an empty response.

## [1.0.6] - 2018-12-31
### Added
- Tests for CLI.

## [1.0.5] - 2018-12-31
### Added
- Type hints 🎉
### Fixed
- 🐞 Python3 import errors - via 39b4a7d.

## [1.0.4] - 2018-12-27
### Added
- Included documentation about Mesos/Marathon task labels.

## [1.0.3] - 2018-12-27
### Changed
- Updated Pydoc.
### Fixed
- CI config fixes.

## [1.0.2] - 2018-12-27
### Added
- `mae` CLI.

## [1.0.1] - 2018-12-27
### Added
- Travis CI builds.

## [1.0.0] - 2018-12-27
### Added
- Initial release.
