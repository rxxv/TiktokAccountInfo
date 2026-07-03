# TikTok Username Info Fetcher

This Python script allows you to fetch and display detailed information about a TikTok user based on their username. The data includes the user's nickname, bio, region, number of followers, following, likes, videos, and more.

## Features
- Fetches detailed information about a TikTok user, including:
  - **Username**
  - **Nickname**
  - **Bio**
  - **Language**
  - **User ID**
  - **Account Creation Date**
  - **Followers, Following, Likes, and Videos Count**
  - **Avatar URL**
  - **Verified Badge**
  - **Private Account** indicator
  - **Engagement Rate** (likes / videos / followers)
- Supports both interactive and command-line usage.
- JSON output for scripting and automation.
- Proper error handling with logging.
- Module is importable in other Python scripts.

## Requirements
- **Python 3.9+**
- Required Python packages:
  - `requests`
  - `beautifulsoup4`

Install these dependencies using pip:

```bash
pip install requests beautifulsoup4
```

## How to Use

### 1. Clone the Repository
```bash
git clone https://github.com/rxxv/TikTokAccountInfo.git
cd TikTokAccountInfo
```

### 2. Install Required Packages
```bash
pip install requests beautifulsoup4
```

### 3. Run the Script

**Interactive mode** (prompts for username):
```bash
python info.py
```

**Command-line mode** (pass username as argument):
```bash
python info.py johndoe
```

**JSON output** (machine-readable):
```bash
python info.py johndoe --json
```

**Verbose logging**:
```bash
python info.py johndoe --verbose
```

### 4. Example Output

**Formatted display:**
```
[+] Enter TikTok Username: johndoe
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ✦ Username:       @johndoe
    ✦ Name:           John Doe
    ✦ Bio:            Just a TikToker
    ✦ ID:             1234567890
    ✦ Language:       en
    ✦ Account Created: 2020-05-12 15:23:45
    ✦ Engagement Rate: 2.45%
    ✦ Followers:      12.3k
    ✦ Following:      456
    ✦ Likes:          1.2m
    ✦ Videos:         35
    ✦ ✓ Verified
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**JSON output (`--json`):**
```json
{
  "username": "johndoe",
  "nickname": "John Doe",
  "bio": "Just a TikToker",
  "language": "en",
  "user_id": "1234567890",
  "avatar": "https://p16-sign.tiktokcdn.com/...",
  "verified": true,
  "private_account": false,
  "created": "2020-05-12 15:23:45",
  "followers": 12300,
  "following": 456,
  "likes": 1200000,
  "videos": 35,
  "engagement_rate": 2.45
}
```

### 5. Use as a Python Module
```python
from info import get_info

data = get_info("johndoe")
if data:
    print(data["followers"])   # 12300
    print(data["verified"])    # True
    print(data["avatar"])      # https://...
```

## Error Handling

- **Network errors**: Connection timeouts, DNS failures, and HTTP errors are caught and logged.
- **HTTP failures**: Non-200 responses produce a clear error message with the status code.
- **Missing user data**: If no data can be extracted from the page, the message `"[×] No user data found for @username"` is shown.
- **JSON parsing errors**: If the script encounters issues decoding TikTok data, an appropriate error message is displayed.

## License
This project is licensed under the MIT License.
