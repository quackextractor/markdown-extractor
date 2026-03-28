# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-03-28

### Added
- **Dedicated Text Input**: Added a multi-line textbox for direct Markdown pasting.
- **Auto-Cleaning Preprocessor**: Integrated a citation remover and Markdown fixer that triggers automatically upon pasting text.
- **Open Folder Shortcut**: Added a button to instantly open the Project Root in the system file explorer.
- **Improved UI Layout**: Reorganized the interface into a logical step-by-step workflow with enhanced spacing.

### Fixed
- **Paste Interception**: Resolved issues where standard OS paste commands might bypass the cleaning logic by using a timed buffer.

## [1.0.0] - 2026-03-28

### Added
* Initial release of the Markdown Code Extractor.
* Graphical User Interface with Drag and Drop support.
* Background threading for responsive UI during extraction.