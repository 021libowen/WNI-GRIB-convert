## ADDED Requirements

### Requirement: GRIB File Parsing
The system SHALL parse GRIB format weather data files and extract messages matching the specified weather type.

#### Scenario: Parse TURB GRIB file
- **WHEN** system receives a GRIB file with TURB data type
- **THEN** system extracts all TURB-related messages from the file

#### Scenario: Parse CONV GRIB file
- **WHEN** system receives a GRIB file with CONV data type
- **THEN** system extracts all CONV-related messages from the file

#### Scenario: Parse ICE GRIB file
- **WHEN** system receives a GRIB file with ICE data type
- **THEN** system extracts all ICE-related messages from the file

### Requirement: Height Level Filtering
The system SHALL filter GRIB data by specified height level.

#### Scenario: Filter by flight level (TURB)
- **WHEN** height parameter is "FL100" for TURB type
- **THEN** system extracts data for 10000 feet level (100 * 100 feet)

#### Scenario: Filter by pressure level (CONV/ICE)
- **WHEN** height parameter is "850" for CONV or ICE type
- **THEN** system extracts data for 850 hPa pressure level

### Requirement: Time Point Filtering
The system SHALL filter GRIB data by specified forecast time point.

#### Scenario: Filter by valid time
- **WHEN** time parameter is "2026-04-23 18:00:00"
- **THEN** system extracts data for that specific forecast time

### Requirement: Resource Management
The system SHALL properly release all GRIB-related resources after processing.

#### Scenario: Resources released after successful parse
- **WHEN** GRIB file is parsed successfully
- **THEN** all file handles and GRIB message resources are closed

#### Scenario: Resources released after parse error
- **WHEN** GRIB file parsing fails with exception
- **THEN** all opened resources are still properly closed

### Requirement: ZLEVEL Severity Mapping
The system SHALL map raw weather severity values to standardized ZLEVEL grades.

#### Scenario: TURB severity mapping
- **WHEN** raw TURB severity value is extracted
- **THEN** system maps it to ZLEVEL 1-5 based on severity thresholds

#### Scenario: ICE severity mapping
- **WHEN** raw ICE severity value is extracted
- **THEN** system maps it to ZLEVEL 1-2 based on severity thresholds

#### Scenario: CONV severity mapping
- **WHEN** raw CONV severity value is extracted
- **THEN** system maps it to ZLEVEL 1-2 based on severity thresholds
