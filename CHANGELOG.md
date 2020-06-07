# Changelog

Changes between project versions will be documented here.


## [3.0.1]
### Changed
- README now gives accurate install instructions via pip


## [3.0.0]
### Added
- Ability to only start capturing output and allowing commands to be issued when process output line matches start condition

### Changed
- exit_condition positional argument now replaced with keyword arguments for start_condition regex string and exit_condition regex string

### Removed
- Positional argument for exit_condition


## [2.0.3]
### Fixed
- Removed accidental pass keyword where regex exit condition would not be set to None on error


## [2.0.2]
### Changed
- Changed stdin/stdout buffering to -1 (default) for subprocess to properly process data as binary buffered
- Removed unecessary conditionals

### Fixed
- Broken pipe errors not being handled
- Issue where stdin would error but input would already be removed from input queue


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
