# Changelog

Changes between project versions will be documented here.


## [2.0.1]
### Added
- Docstrings to classes and functions

### Fixed
- PPSP stop function explicitly sets stopping flag to True to stop execution every time when calling it


## [2.0.0]
### Added
- Ability to run multiple shell commands at one time
- example2.py for an example of multiple shell commands at once

### Changed
- Shell commands now get executed in a daemon thread and must be stopped when status is stopping
- Made PPSP class private

### Removed
- PPSP Exception classes


## [1.0.1]
### Added
- Stopping status flag

### Changed 
- Command line arguments for example.py

### Fixed
- PPSP would not exit after subprocess was finished executing


## [1.0.0]
### Added 
- PPSP class for running a persistent shell, allowing for stdout or stdin
