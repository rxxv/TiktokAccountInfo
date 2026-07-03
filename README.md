# TikTok Username Info Fetcher

This Python script fetches and displays detailed information about a TikTok user from their public profile page. No API key or authentication required — parses the server-rendered page directly.

## Features

- **33 fields** extracted from TikTok's SSR JSON, including:
  - **Username**, **Nickname**, **Bio**, **User ID**, **Short ID**, **Sec UID**
  - **Avatar URL** (largest available)
  - **Verified Badge**, **Private Account**, **Organization**, **Commerce User**, **AD Virtual**
  - **Account Created**, **Nickname Modified**, **Username Modified** timestamps
  - **Followers**, **Following**, **Friends**, **Likes**, **Videos**
  - **Engagement Rate** (likes / videos / followers)
  - **Permissions**: Duet, Stitch, Comments, Downloads (Everyone / Friends / Off)
  - **Following Visibility**, **Language**
  - **Profile Tabs**: Music, Playlists, Q&A
- **CLI arguments**: `python info.py username --json --verbose`
- **JSON output** for scripting and automation
- **Importable module**: `from info import get_info`
- Proper error handling with logging and retries
- Stats overflow protection (TikTok's int32 overflow → auto-corrected via statsV2)

## Requirements

- **Python 3.9+**
- `requests`, `beautifulsoup4`

```bash
pip install requests beautifulsoup4
```

## How to Use

### 1. Clone and install
```bash
git clone https://github.com/rxxv/TikTokAccountInfo.git
cd TikTokAccountInfo
pip install requests beautifulsoup4
```

### 2. Run

```bash
python info.py                  # interactive prompt
python info.py johndoe          # CLI argument
python info.py johndoe --json   # machine-readable JSON
python info.py johndoe --verbose # debug logging
```

### 3. Import as a module
```python
from info import get_info

data = get_info("johndoe")
if data:
    print(data["followers"])    # 821700
    print(data["verified"])     # True
    print(data["engagement_rate"])  # 7.9
```

## Example Output

**Formatted display:**
```
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ✦ Username:       @tiktok
    ✦ Name:           TikTok
    ✦ Bio:            One TikTok can make a big impact
    ✦ User ID:        107955
    ✦ Short ID:       N/A
    ✦ Language:       en
    ✦ Account Created: 2015-02-28 17:22:29
    ✦ Engagement Rate: 0.33%
    ── Stats ────────────────────────────────────
    ✦ Followers:      94.7m
    ✦ Following:      0
    ✦ Friends:        1
    ✦ Likes:          461.3m
    ✦ Videos:         1.5k
    ── Permissions ──────────────────────────────
    Duet       Everyone
    Stitch     Everyone
    Comments   Everyone
    Downloads  Everyone
    ── Info ─────────────────────────────────────
    ✦ ✓ Verified | 🛒 TikTok Shop | 🏢 Organization
    ✦ Profile Tabs:   📋 Playlists, ❓ Q&A
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**JSON output (`--json`):**
```json
{
  "username": "tiktok",
  "nickname": "TikTok",
  "unique_id": "tiktok",
  "sec_uid": "MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM",
  "short_id": "",
  "user_id": "107955",
  "bio": "One TikTok can make a big impact",
  "language": "en",
  "avatar": "https://p16-common-sign.tiktokcdn.com/...",
  "verified": true,
  "private_account": false,
  "is_commerce_user": true,
  "is_organization": true,
  "is_ad_virtual": false,
  "created": "2015-02-28 17:22:29",
  "nickname_modified": "2021-12-03 19:26:40",
  "unique_id_modified": "N/A",
  "followers": 94700000,
  "following": 0,
  "friends": 1,
  "likes": 461300000,
  "videos": 1466,
  "engagement_rate": 0.33,
  "following_visible": true,
  "duet_setting": "Everyone",
  "stitch_setting": "Everyone",
  "comment_setting": "Everyone",
  "download_setting": "Everyone",
  "show_music_tab": false,
  "show_playlist_tab": true,
  "show_question_tab": true
}
```

## Error Handling

- **Network errors**: Connection timeouts, DNS failures, HTTP errors — caught and logged
- **HTTP 404**: `"[×] Profile not found for @username"`
- **HTTP non-200**: `"[×] Failed to retrieve data for @username (HTTP xxx)"`
- **Missing data**: `"[×] No user data found for @username"`
- **JSON parse errors**: Logged with details
- **Stats overflow**: TikTok returns int32-wrapped values for large accounts (likes >2.1B) — automatically corrected from `statsV2`

## License

MIT
