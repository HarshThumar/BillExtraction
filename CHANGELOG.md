# Status Monitoring and Control Service

A unified service to monitor and manage smart home devices (Tuya, SwitchBot, etc.) via local APIs, exposing metrics for Prometheus/Grafana.

## Changelog

### v1.2.0 (Latest)
- **Status Endpoint**: Added `/status` endpoint to the HTTP server providing real-time device health and metrics.
- **Improved Sync Loop**: Enhanced the main loop with better error handling and logging.
- **Sync Interval**: Introduced configurable `SYNC_INTERVAL` (default: 60s) for status updates.
- **Device Support**: Refined polling logic for Tuya and SwitchBot devices.

### v1.1.0
- **Modular Logic**: Refactored status update logic into dedicated modules for better extensibility.
- **Enhanced Logging**: Added standardized logging for energy metrics (Power, Current, Voltage).
- **Polling Logic**: Improved reliability of periodic polling for specific device types.

### v1.0.1
- **SwitchBot Support**: Added support for SwitchBot (WO-Plug) devices.
- **Multi-device Configuration**: Support for monitoring multiple devices simultaneously.
- **Prometheus Integration**: Dedicated Prometheus exporter for each configured device.
- **Retry Logic**: Improved connection resilience with built-in retry mechanisms.

### v1.0.0
- **Initial Release**: Basic support for Tuya-based energy plugs (TS011F).
- **Core Metrics**: Real-time logging of power, current, voltage, and total energy.
- **Metrics Server**: Local HTTP server for Prometheus scraping.

## Key Features
- **Cross-Platform**: Designed for Containerized environments (Docker).
- **Lightweight**: Optimized for low resource consumption on edge devices (e.g., Raspberry Pi).
- **Extensible**: Easily add support for new device types.
- **Observable**: Full integration with Prometheus and Grafana.

---
*Maintained by the Automation Team*
