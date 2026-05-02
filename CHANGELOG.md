# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-05-02
### Added
*   **Dry Run Preview**: Added a "Preview" button that logs intended file changes without modifying any local files.
*   **Directory History**: Implemented a `history.json` system to remember and suggest previously used project root directories.
*   **Root Selector Combobox**: Replaced the standard entry field with a `CTkComboBox` for quick access to project history.
*   **Folder Quick-Access**: Added an "Open Folder" button to immediately jump to the project root in the OS file explorer.
### Changed
*   **Extraction Workflow**: Disabled automatic extraction upon file drop to prevent accidental overwrites; the tool now waits for an explicit "Apply" or "Preview" command.
*   **UI Layout**: Increased default window height to accommodate the new history and control elements.
*   **Cleaner Logging**: Updated the log output to distinguish between previewing and active extraction modes.
### Fixed
*   **Release Note Bloat**: Updated the GitHub Actions workflow to surgically extract only the current version's notes from the changelog for release bodies, rather than uploading the entire file.
*   **Path Normalization**: Improved path handling for drag-and-drop events to ensure consistent formatting across different operating systems.

## [1.3.0] - 2026-05-02
### Added
* **Dynamic File Extraction**: Introduced the `extract_filename` function to dynamically identify target file paths from diverse markdown structures, including explicit boundaries, numbered headings, and bold text notations.
### Changed
* **Extraction Loop Refactor**: Updated the main `execute_extraction` loop to leverage the new dynamic filename parser, replacing the rigid header regex.
* **Path Validation**: Added robust filtering to reject standard prose, purely numeric version strings, and standard markdown elements from being misidentified as target filenames.

## [1.2.0] - 2026-05-02
### Added
* **GitHub Actions Release Integration**: Configured the CI/CD pipeline to automatically use `CHANGELOG.md` as the source for GitHub Release notes.
### Changed
* **Refactored Markdown Preprocessor**: Replaced the previous formatting logic with a more robust citation remover designed to prevent structural corruption of the Markdown document.
* **Preservation Logic**: Updated the `process_text` function to use refined regex patterns that safely pull up citation tags while preserving intentional paragraph breaks and code indentation.
### Fixed
* **Aggressive Formatting Issues**: Resolved a bug where the old logic incorrectly forced indentation on lists and stripped necessary newlines following headers.

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