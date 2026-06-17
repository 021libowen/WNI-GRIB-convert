## ADDED Requirements

### Requirement: GeoJSON FeatureCollection Output
The system SHALL convert parsed weather data into a GeoJSON FeatureCollection.

#### Scenario: Generate valid GeoJSON
- **WHEN** weather data is successfully parsed
- **THEN** output is a valid GeoJSON FeatureCollection with features array

### Requirement: Feature Geometry Type
The system SHALL use LineString geometry for each feature.

#### Scenario: Create LineString features
- **WHEN** converting weather grid data to GeoJSON
- **THEN** each feature contains a LineString geometry with coordinates array

### Requirement: Feature Properties
The system SHALL include ZLEVEL property in each feature's properties.

#### Scenario: Feature with ZLEVEL
- **WHEN** a feature is created
- **THEN** its properties contain ZLEVEL field with integer value 1-5

### Requirement: Feature ID
The system SHALL assign sequential integer IDs to features starting from 0.

#### Scenario: Feature ID assignment
- **WHEN** multiple features are created
- **THEN** each feature has a unique id from 0 to n-1
