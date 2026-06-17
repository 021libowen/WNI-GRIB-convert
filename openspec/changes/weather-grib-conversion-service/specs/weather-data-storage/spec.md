## ADDED Requirements

### Requirement: Output File Directory Structure
The system SHALL store converted GeoJSON files in a structured directory based on the configuration.

#### Scenario: Generate correct directory path
- **WHEN** converting weather data with baseDir "D://weatherData", date "2026-04-24", type "TURB", height "FL100", version "V20260417000000", time "20260417030000"
- **THEN** file is stored at "D://weatherData/2026-04-24/TURB/FL100/V20260417000000/20260417030000/TURB_FL100_20260417030000.txt"

### Requirement: Create Parent Directories
The system SHALL create parent directories if they do not exist.

#### Scenario: Create nested directories
- **WHEN** output directory path contains non-existent directories
- **THEN** system creates all required parent directories before writing file

### Requirement: File Overwrite
The system SHALL overwrite existing file if it already exists at the target path.

#### Scenario: Overwrite existing file
- **WHEN** a file already exists at the calculated output path
- **THEN** system overwrites it with the new converted data

### Requirement: File Content Format
The system SHALL write GeoJSON content as formatted text to the output file.

#### Scenario: Write valid GeoJSON text
- **WHEN** writing to output file
- **THEN** file contains valid GeoJSON text that can be parsed
