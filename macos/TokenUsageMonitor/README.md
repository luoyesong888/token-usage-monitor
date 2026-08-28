# Token监测 for macOS

Native macOS 13+ menu-bar companion for the Token Usage Monitor Codex plugin.

## Features

- Live Codex remaining-quota percentage and reset countdown
- White circular remaining-quota indicator in the menu bar and quota cards
- Exact consumed percentage beneath each remaining-quota bar
- Cached quota fallback with a friendly automatic-retry status during network interruptions
- Product Logo in the panel and macOS application icon
- Daily token chart and account summary
- Mouse-hover details with exact date and Token count on the recent-usage chart
- Automatic panel opening when the app launches
- Header pin switch for a compact always-front quota badge across macOS Spaces
- Readable date ticks, 14-day total, and hover guide in the recent-usage chart
- Automatic GitHub release checks with an in-app update link
- Standard 1024×1024 black graphite application icon with transparent safe margins
- Standard resizable 420×640 macOS window with a 390×540 minimum size
- Local notifications at configurable thresholds
- Detection of scheduled resets and newly granted reset credits
- Manual refresh, local-only storage, and optional launch at login
- Five-second per-task token totals with local conversation titles
- Local usage ingestion for OpenAI, DeepSeek, and compatible API responses
- OpenAI/DeepSeek Token budgets with used and remaining quota displays
- Selectable Codex, OpenAI, or DeepSeek quota source for the menu-bar ring
- DeepSeek balance and model discovery with API keys stored in macOS Keychain
- Per-provider API calls, input/output/cache/reasoning tokens, and recent activity
- No prompt text, response text, email address, or API key in the usage database

## Build

```sh
./scripts/build_app.sh
```

The finished app is written to `dist/Token监测.app`. Move it to the
Applications folder and launch it; the remaining-quota percentage will appear in the
menu bar. The app requires a local Codex CLI installation, an authenticated
Codex session, and macOS 13 or newer.

The app is ad-hoc signed for local use. Public distribution requires an Apple
Developer ID signature and notarization.

## DeepSeek

Open settings, paste a DeepSeek API key, and choose **连接并验证**. The app uses
the key only to call DeepSeek's read-only balance and model endpoints and stores
it in macOS Keychain. Token history is accumulated from each API response's
`usage` object through the local `http://127.0.0.1:47821/v1/usage` endpoint; the
included `scripts/api_usage_client.py` helper performs this metadata-only step.
