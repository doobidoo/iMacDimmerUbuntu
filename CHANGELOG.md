# Changelog

All notable changes to iMac Dimmer Ubuntu will be documented in this file.

## [1.7.0] - 2025-07-09

### Added
- Safety feature to prevent getting stuck at 0% brightness
  - Automatic recovery when user activity is detected while screen is at 0%
  - If original brightness was 0%, restore to 10% instead
- Support for decimal minutes in auto-dimmer (e.g., 0.5 minutes = 30 seconds)
- Comprehensive hardware setup documentation in README
- Reference to detailed wiring guide (Medium article by @fixingthings)
- Hardware requirements section with PCI-E 6-pin cable details

### Fixed
- ESP32 firmware now accepts 0% brightness commands
  - Fixed serial command parsing for "0" input
  - Fixed HTTP endpoint validation for 0% brightness
- Build script error with __file__ in PlatformIO environment

### Changed
- WiFi credentials now managed through environment variables
- Updated firmware version to 1.7.0-safety-features
- Enhanced README with security considerations section

### Security
- WiFi credentials removed from source code
- Environment variable system for sensitive configuration
- Added .env file to gitignore

## [1.6.0] - Previous Release

### Added
- Dynamic IP discovery with mDNS support
- Zero-maintenance network adaptation
- HTTP API with fallback mechanisms
- Complete system integration with keyboard shortcuts
- Auto-dimmer functionality