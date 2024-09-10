import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def format_number(value):
    value = float(value)
    if value >= 1000000:
        return f"{value / 1000000:.1f}m"
    elif value >= 1000:
        return f"{value / 1000:.1f}k"
    return str(int(value))

def get_info(username):
    headers = {
        "Host": "www.tiktok.com",
        "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"99\", \"Google Chrome\";v=\"99\"",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "\"Android\"",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Linux; Android 8.0.0; Plume L2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.88 Mobile Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "accept-language": "en-US,en;q=0.9"
    }
    
    response = requests.get(f'https://www.tiktok.com/@{username}', headers=headers)
    
    if response.status_code != 200:
        print(f"[×] Failed to retrieve data for username: {username}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    user_data_script = None
    for script in soup.find_all('script'):
        if 'userInfo' in script.text:
            user_data_script = script.string
            break
    
    if not user_data_script:
        print(f"[×] No user data found in the script for username: {username}")
        return
    
    try:
        user_data_json = json.loads(user_data_script)
        user_info = user_data_json.get('__DEFAULT_SCOPE__', {}).get('webapp.user-detail', {}).get('userInfo', {})
        user = user_info.get('user', {})
        
        nickname = user.get('nickname', 'N/A')
        bio = user.get('signature', 'N/A')
        region = user.get('region', 'N/A')
        user_id = user.get('id', 'N/A')
        create_time_unix = user.get('createTime', 0)
        create_time = datetime.utcfromtimestamp(create_time_unix).strftime('%Y-%m-%d %H:%M:%S') if create_time_unix else 'N/A'
        
        stats = user_info.get('stats', {})
        followers = stats.get('followerCount', 0)
        following = stats.get('followingCount', 0)
        likes = stats.get('heartCount', 0)
        videos = stats.get('videoCount', 0)

        followers = format_number(followers)
        following = format_number(following)
        likes = format_number(likes)
        
        result = f"""
        ━━━━━━━━━━━━━━━━━━━━━
        ✦ Username: @{username}
        ✦ Name: {nickname}
        ✦ Bio: {bio}
        ✦ ID: {user_id}
        ✦ Region: {region}
        ✦ Account Created: {create_time}
        ✦ Followers: {followers}
        ✦ Following: {following}
        ✦ Likes: {likes}
        ✦ Videos: {videos}
        ━━━━━━━━━━━━━━━━━━━━━
        """
        print(result)
    
    except json.JSONDecodeError as e:
        print(f"[×] JSON decoding error: {e}")
    except Exception as e:
        print(f"[×] Error while processing data: {e}")

get_info(username=input('[+] Enter TikTok Username: '))
