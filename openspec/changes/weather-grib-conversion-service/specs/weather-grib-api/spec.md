## ADDED Requirements

### Requirement: Weather Conversion REST API
The system SHALL provide a RESTful POST endpoint at `/weather/convert` that accepts GRIB file parameters and returns the converted GeoJSON file path.

#### Scenario: Successful weather data conversion
- **WHEN** client sends POST request with valid gribFile, weatherType, height, time, version and prefix parameters
- **THEN** system parses the GRIB file, converts to GeoJSON, stores the file, and returns success with filePath

#### Scenario: Missing required parameters
- **WHEN** client sends POST request with missing required parameter (gribFile, weatherType, height, or time)
- **THEN** system returns 400 Bad Request with error message indicating missing parameter

#### Scenario: Invalid weather type
- **WHEN** client sends POST request with weatherType not in (TURB, CONV, ICE)
- **THEN** system returns 400 Bad Request with error message "Invalid weather type"

#### Scenario: GRIB file not found
- **WHEN** client sends POST request with non-existent gribFile path
- **THEN** system returns 404 Not Found with error message "GRIB file not found"

#### Scenario: Conversion processing error
- **WHEN** client sends valid request but GRIB parsing or conversion fails
- **THEN** system returns 500 Internal Server Error with error message and logs the exception

### Requirement: API Request Parameters
The system SHALL accept the following parameters in the POST request body:

#### Scenario: All parameters provided
- **WHEN** POST request contains version, gribFile, weatherType, height, time, and prefix
- **THEN** system uses all provided values in processing

#### Scenario: Default prefix value
- **WHEN** POST request does not contain prefix parameter
- **THEN** system uses default value "1" for prefix

### Requirement: API Response Format
The system SHALL return a JSON response with filePath, message, and success fields.

#### Scenario: Success response
- **WHEN** conversion completes successfully
- **THEN** response contains filePath pointing to the output file, message "Conversion completed", and success true

#### Scenario: Failure response
- **WHEN** conversion fails
- **THEN** response contains empty filePath, error message, and success false
