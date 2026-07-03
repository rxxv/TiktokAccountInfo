"""
TikTok Username Info Fetcher
Fetches and displays detailed information about a TikTok user by username.
Supports interactive input, CLI arguments, and JSON output.
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

# ── Constants ──────────────────────────────────────────────────────────────────
SCOPE_KEY = "__DEFAULT_SCOPE__"
USER_DETAIL_KEY = "webapp.user-detail"
USER_INFO_KEY = "userInfo"
REQUEST_TIMEOUT = 15

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ── Helpers ────────────────────────────────────────────────────────────────────
def format_number(value: Any) -> str:
    """Format large numbers with k/m suffixes. Returns the value as-is on failure."""
    try:
        num = float(value)
    except (ValueError, TypeError):
        return str(value)

    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}m"
    if num >= 1_000:
        return f"{num / 1_000:.1f}k"
    return str(int(num))


def _safe_get(data: Dict[str, Any], *keys: str, default: Any = "N/A") -> Any:
    """Walk a nested dict chain, returning *default* on any missing key."""
    for key in keys:
        if not isinstance(data, dict):
            return default
        data = data.get(key, {})
    return data if data != {} else default


def _ts_to_str(ts: int) -> str:
    """Convert a Unix timestamp to a readable UTC string."""
    if not ts:
        return "N/A"
    try:
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    except (OSError, ValueError):
        return "N/A"


_SETTING_LABELS: Dict[int, str] = {0: "Everyone", 1: "Friends", 2: "Off"}


# ── Fetch ──────────────────────────────────────────────────────────────────────
def fetch_profile(username: str) -> requests.Response:
    """HTTP GET the TikTok profile page for *username*."""
    safe_username = quote(username, safe="")
    url = f"https://www.tiktok.com/@{safe_username}"

    headers = {
        "Host": "www.tiktok.com",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "upgrade-insecure-requests": "1",
        "user-agent": (
            "Mozilla/5.0 (Linux; Android 8.0.0; Plume L2) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.88 "
            "Mobile Safari/537.36"
        ),
        "accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,image/apng,*/*;q=0.8,"
            "application/signed-exchange;v=b3;q=0.9"
        ),
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "accept-language": "en-US,en;q=0.9",
    }

    return requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)


# ── Extract ────────────────────────────────────────────────────────────────────
def extract_user_info(response: requests.Response, username: str) -> Optional[Dict[str, Any]]:
    """Parse TikTok's SSR JSON blob from the page and return a user-info dict.

    Returns ``None`` when the data cannot be found or parsed.
    """
    soup = BeautifulSoup(response.text, "html.parser")

    user_data_text: Optional[str] = None
    for script in soup.find_all("script"):
        inner = script.text
        if inner and "userInfo" in inner:
            user_data_text = inner
            break

    if not user_data_text:
        logger.warning("No script tag containing 'userInfo' found for %s", username)
        return None

    try:
        data = json.loads(user_data_text)
    except json.JSONDecodeError as exc:
        logger.error("JSON decode failed for %s: %s", username, exc)
        return None

    user_info = _safe_get(data, SCOPE_KEY, USER_DETAIL_KEY, USER_INFO_KEY, default={})
    if not user_info:
        logger.warning("Could not locate userInfo in extracted data for %s", username)
        return None

    user = user_info.get("user", {})
    stats = user_info.get("stats", {})
    stats_v2 = user_info.get("statsV2", {})

    # ── Timestamps ────────────────────────────────────────────────────────────
    created = _ts_to_str(user.get("createTime", 0))
    nickname_modified = _ts_to_str(user.get("nickNameModifyTime", 0))
    unique_id_modified = _ts_to_str(user.get("uniqueIdModifyTime", 0))

    # ── Numeric stats ─────────────────────────────────────────────────────────
    def _stat(key: str) -> int:
        """Get a stat count, falling back to statsV2 (string) when stats is zero or overflowed."""
        val = stats.get(key, 0)
        if val <= 0 and stats_v2:
            str_val = stats_v2.get(key)
            if str_val is not None:
                try:
                    val = int(str_val)
                except (ValueError, TypeError):
                    pass
        return val

    followers = _stat("followerCount")
    following = _stat("followingCount")
    likes = _stat("heartCount")
    videos = _stat("videoCount")
    friends = _stat("friendCount")

    # ── Engagement rate ───────────────────────────────────────────────────────
    engagement_rate: Optional[float] = None
    if followers > 0 and videos > 0:
        engagement_rate = round((likes / videos / followers) * 100, 2)

    # ── Avatar ────────────────────────────────────────────────────────────────
    avatar = (
        user.get("avatarLarger")
        or user.get("avatarMedium")
        or user.get("avatarThumb")
        or "N/A"
    )

    # ── Identity ──────────────────────────────────────────────────────────────
    commerce_info = user.get("commerceUserInfo", {}) or {}
    is_commerce = (
        commerce_info.get("commerceUser", False)
        if isinstance(commerce_info, dict)
        else False
    )
    following_visible = user.get("followingVisibility", 1) == 1

    # ── Profile tabs ──────────────────────────────────────────────────────────
    tabs = user.get("profileTab", {}) or {}

    # ── Privacy / permission flags ────────────────────────────────────────────
    def _setting(val: int) -> str:
        return _SETTING_LABELS.get(val, str(val))

    return {
        # Identity
        "username": username,
        "nickname": user.get("nickname", "N/A"),
        "unique_id": user.get("uniqueId", username),
        "sec_uid": user.get("secUid", ""),
        "short_id": user.get("shortId", ""),
        "user_id": user.get("id", "N/A"),
        "bio": user.get("signature", "N/A"),
        "language": user.get("language", "N/A"),
        "avatar": avatar,
        # Status
        "verified": user.get("verified", False),
        "private_account": user.get("privateAccount", False),
        "is_commerce_user": is_commerce,
        "is_organization": bool(user.get("isOrganization", 0)),
        "is_ad_virtual": user.get("isADVirtual", False),
        # Dates
        "created": created,
        "nickname_modified": nickname_modified,
        "unique_id_modified": unique_id_modified,
        # Stats
        "followers": followers,
        "following": following,
        "friends": friends,
        "likes": likes,
        "videos": videos,
        "engagement_rate": engagement_rate,
        # Visibility
        "following_visible": following_visible,
        # Permissions
        "duet_setting": _setting(user.get("duetSetting", 0)),
        "stitch_setting": _setting(user.get("stitchSetting", 0)),
        "comment_setting": _setting(user.get("commentSetting", 0)),
        "download_setting": _setting(user.get("downloadSetting", 0)),
        # Tabs
        "show_music_tab": tabs.get("showMusicTab", False),
        "show_playlist_tab": tabs.get("showPlayListTab", False),
        "show_question_tab": tabs.get("showQuestionTab", False),
    }


# ── Format ─────────────────────────────────────────────────────────────────────
def format_profile(info: Dict[str, Any]) -> str:
    """Render the user-info dict as a pretty terminal string."""
    # ── Badge row ────────────────────────────────────────────────────────────
    badges = []
    if info.get("verified"):
        badges.append("✓ Verified")
    if info.get("private_account"):
        badges.append("🔒 Private")
    if info.get("is_commerce_user"):
        badges.append("🛒 TikTok Shop")
    if info.get("is_organization"):
        badges.append("🏢 Organization")
    if not info.get("following_visible", True):
        badges.append("👥 Following Hidden")
    badge_line = f"✦ {' | '.join(badges)}" if badges else ""

    # ── Engagement line ──────────────────────────────────────────────────────
    engagement_line = ""
    if info.get("engagement_rate") is not None:
        engagement_line = f"\n✦ Engagement Rate: {info['engagement_rate']}%"

    # ── Tabs line ────────────────────────────────────────────────────────────
    tabs = []
    if info.get("show_music_tab"):
        tabs.append("🎵 Music")
    if info.get("show_playlist_tab"):
        tabs.append("📋 Playlists")
    if info.get("show_question_tab"):
        tabs.append("❓ Q&A")
    tabs_line = f"✦ Profile Tabs:   {', '.join(tabs)}" if tabs else ""

    # ── Permissions block ────────────────────────────────────────────────────
    perm_lines = []
    for label, key in [
        ("Duet", "duet_setting"),
        ("Stitch", "stitch_setting"),
        ("Comments", "comment_setting"),
        ("Downloads", "download_setting"),
    ]:
        perm_lines.append(f"    {label:<10} {info.get(key, '?')}")

    return f"""
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ✦ Username:       @{info['username']}
    ✦ Name:           {info['nickname']}
    ✦ Bio:            {info['bio']}
    ✦ User ID:        {info['user_id']}
    ✦ Short ID:       {info['short_id'] or 'N/A'}
    ✦ Language:       {info['language']}
    ✦ Account Created:{' ' + info['created']}{engagement_line}
    ── Stats ────────────────────────────────────
    ✦ Followers:      {format_number(info['followers'])}
    ✦ Following:      {format_number(info['following'])}
    ✦ Friends:        {format_number(info['friends'])}
    ✦ Likes:          {format_number(info['likes'])}
    ✦ Videos:         {format_number(info['videos'])}
    ── Permissions ──────────────────────────────
{chr(10).join(perm_lines)}
    ── Info ─────────────────────────────────────
    {badge_line}
    {tabs_line}
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """


# ── Orchestrate ────────────────────────────────────────────────────────────────
def get_info(username: str) -> Optional[Dict[str, Any]]:
    """Fetch and parse TikTok profile data for *username*.

    Returns a dict on success, ``None`` otherwise.
    """
    try:
        resp = fetch_profile(username)
    except requests.RequestException as exc:
        logger.error("[×] Network error for @%s: %s", username, exc)
        return None

    if resp.status_code != 200:
        logger.error(
            "[×] Failed to retrieve data for @%s (HTTP %d)", username, resp.status_code
        )
        return None

    info = extract_user_info(resp, username)
    if info is None:
        logger.error("[×] No user data found for @%s", username)
        return None

    return info


# ── CLI / Entry-point ──────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch detailed TikTok profile information by username.",
    )
    parser.add_argument(
        "username",
        nargs="?",
        help="TikTok username (omit for interactive prompt)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw data as JSON instead of a formatted display",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable debug logging",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    username = args.username or input("[+] Enter TikTok Username: ").strip()
    if not username:
        print("[×] Username cannot be empty.", file=sys.stderr)
        sys.exit(1)

    info = get_info(username)
    if info is None:
        sys.exit(1)

    if args.json:
        print(json.dumps(info, indent=2, default=str))
    else:
        print(format_profile(info))


if __name__ == "__main__":
    main()
