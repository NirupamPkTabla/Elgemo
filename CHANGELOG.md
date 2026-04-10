# Changelog
All notable changes to this project will be documented in this file.

## [0.9.1] - 2026-04-10
### Changed
- UI Logic: Replaced the "Skip" button with a dynamic stateful button.
- Interaction Flow: When in a chat, the button displays as "Stop." Clicking it ends the current session and reverts the button to "Find Match."
- Control: Users must now explicitly click "Find Match" again to start a new search after stopping, providing a more controlled user experience.

## [0.9.0] - 2026-04-10
### Added
- UI: Added a welcome modal that displays community guidelines and cautions (including the profanity ban warning) when a user first lands on the page.
- UI: Implemented a live "Online Users" badge in the header to show the total number of currently connected clients.
- Backend: Added WebSocket broadcasting to keep the online user count synchronized in real-time across all active sessions.

## [0.8.1] - 2026-04-10
### Changed
- Moderation Logic: Simplified the 3-strike profanity rule. *Any* 3 profane messages (repetitive or unique, back-to-back or spaced out) will now trigger the 5-minute IP ban.
- Partner Notification: Updated the system message sent to the innocent party upon a user's ban to: "We disconnected the stranger to maintain a good service."

## [0.7.6] - 2026-04-10
### Added
- Security: Integrated `better_profanity` on the Python backend to automatically censor toxic language.
- Messages are now sanitized server-side before being broadcast to the partner, preventing client-side bypasses.

## [0.7.3] - 2026-04-10
### Changed
- UI Polish: Replaced the previous clunky moon icon with a clean, minimalist outlined SVG for better cross-browser rendering and a more modern aesthetic on the theme toggle button.

## [0.7.2] - 2026-04-10
### Fixed
- Reverted CSS layout engine back to stable `0.6.0` state. Removed the `position: fixed` bug that was freezing the app and corrupting the UI.
- Implemented a much safer `data-theme` architecture that respects system defaults but allows manual toggling without breaking gradients.
- Applied a non-destructive JavaScript `visualViewport` fix for the mobile keyboard that dynamically adjusts height without locking the screen.

## [0.7.1] - 2026-04-10
### Fixed
- Hotfix: Resolved a CSS specificity bug introduced in 0.7.0 that corrupted the color palette. Restored native `@media` queries for base theming and isolated `data-theme` purely for manual overrides.

## [0.7.0] - 2026-04-10
### Added
- Manual Dark/Light theme toggle button in the header.
- Theme preference is now saved locally (`localStorage`) so it persists across visits.

### Fixed
- Fixed mobile virtual keyboard bug. Implemented the `visualViewport` API to ensure the chat input box stays perfectly anchored above the keyboard without glitchy scrolling.

## [0.6.0] - 2026-04-10
### Added
- Rebranded the application to "Elgemo".

### Changed
- Major UI overhaul targeting a modern "2026" aesthetic (frosted glass, gradients, fluid layout).
- Upgraded viewport sizing to `100dvh` to ensure the input box is never hidden under mobile browser address bars.
- Changed default theme to emphasize a sleek, dark-mode native look with vibrant accents.

### Fixed
- Resolved a state bug where the "Start" button remained disabled after a partner disconnected, forcing a page refresh.

## [0.5.0] - 2026-04-10
### Changed
- Total UI/UX overhaul. Implemented modern, mobile-responsive Flexbox layout.
- Added automatic Dark/Light mode detection based on system preferences.
- Chat messages are now styled as bubbles (Me on right, Stranger on left).
- Replaced text typing indicator with a modern CSS bouncing-dot animation.
- Bound Flask server to `host="0.0.0.0"` to allow local network and proper tunnel access.

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