# Changelog
All notable changes to this project will be documented in this file.

## [0.4.0] - 2026-04-10
### Changed
- Refactored architecture into a single-file deployment. 
- Frontend HTML/JS is now served directly from the Python backend via the root `/` route.
- Updated UI version numbers to match v0.4.0.

## [0.3.0] - 2026-04-10
### Added
- Memory-based rate limiting to prevent message spam.
- Users are warned via system message if they type too fast.
- Cleanup logic updated to clear rate-limit memory on disconnect.

## [0.2.0] - Previous
### Added
- Migrated backend from FastAPI to Flask + Flask-SocketIO.
- Implemented SocketIO "Rooms" for cleaner matchmaking.
- Added "Typing..." indicators.
- Added "Skip" button functionality to quickly rematch without refreshing.
- Explicit "Start Search" action required to join queue.

## [0.1.0] - Initial Prototype
### Added
- Basic WebSocket connection established.
- Memory queue for matchmaking.
- Cloudflare Tunnel header extraction (`CF-IPCountry`, `CF-Connecting-IP`).
- Raw text message routing between two paired users.