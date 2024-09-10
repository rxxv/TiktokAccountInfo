# TikTok Username Info Fetcher

This Python script allows you to fetch and display detailed information about a TikTok user based on their username. The data includes the user's nickname, bio, region, number of followers, following, likes, videos, and more.

## Features
- Fetches detailed information about a TikTok user, including:
  - **Username**
  - **Nickname**
  - **Bio**
  - **Region**
  - **User ID**
  - **Account Creation Date**
  - **Followers, Following, Likes, and Videos Count**
- Handles errors such as invalid usernames or failed data retrieval.
  
## Requirements
- Python 3.x
- Required Python packages:
  - `requests`
  - `beautifulsoup4`
  
Install these dependencies using pip:

```bash
pip install requests beautifulsoup4
```

## How to Use

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/rxxv/TikTokAccountInfo.git
   cd TikTokAccountInfo
   ```

2. **Install Required Packages**:
   Install the required Python packages:
   ```bash
   pip install requests beautifulsoup4
   ```

3. **Run the Script**:
   Execute the script and enter a TikTok username when prompted:
   ```bash
   python info.py
   ```

4. **Example Input and Output**:
   You will be prompted to enter a TikTok username. The script will fetch and display information like this:

   ```
   [+] Enter TikTok Username: johndoe
   ━━━━━━━━━━━━━━━━━━━━━
   ✦ Username: @johndoe
   ✦ Name: John Doe
   ✦ Bio: Just a TikToker
   ✦ ID: 1234567890
   ✦ Region: US
   ✦ Account Created: 2020-05-12 15:23:45
   ✦ Followers: 12.3k
   ✦ Following: 456
   ✦ Likes: 1.2m
   ✦ Videos: 35
   ━━━━━━━━━━━━━━━━━━━━━
   ```

## Error Handling

- **Failed to Retrieve Data**: If the TikTok profile page cannot be found or accessed, a message will be displayed: `"[×] Failed to retrieve data for username"`.
- **Invalid or Missing User Data**: If no data can be extracted from the page, the message `"[×] No user data found in the script for username"` will be shown.
- **JSON Parsing Errors**: If the script encounters issues decoding TikTok data, an appropriate error message will be displayed.

## License
This project is licensed under the MIT License.
