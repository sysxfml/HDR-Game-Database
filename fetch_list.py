import requests
import json
import re
import time

# PCGamingWiki API
API_URL = "https://www.pcgamingwiki.com/w/api.php"

# 【关键修改】伪装成标准的 Windows Chrome 浏览器
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.pcgamingwiki.com/'
}

# 正则表达式
EXE_PATTERN = re.compile(r'[\w\-\.]+\.exe', re.IGNORECASE)

def fetch_hdr_games():
    print("Step 1: 正在扫描 HDR 游戏列表...")
    
    # 稍微调整一下 limit，避免请求太大数据包被拦截
    params = {
        "action": "cargoquery",
        "format": "json",
        "tables": "Video",
        "fields": "_pageName=Name,HDR", 
        "where": "Video.HDR HOLDS LIKE '%true%'",
        "limit": "200" 
    }
    
    games_list = []
    offset = 0
    retry_count = 0
    
    while True:
        params["offset"] = offset
        try:
            # 打印正在请求的 URL，方便调试 (在 Actions 日志里能看到)
            print(f"Requesting offset {offset}...")
            
            response = requests.get(API_URL, params=params, headers=HEADERS, timeout=30)
            
            # 调试：如果有问题，打印返回的前200个字符看看是什么
            if response.status_code != 200:
                print(f"Error: Status {response.status_code}")
                print(response.text[:200])
                break

            try:
                data = response.json()
            except json.JSONDecodeError:
                print("Error: 返回的不是有效的 JSON，可能被防火墙拦截了。")
                print(response.text[:500]) # 打印网页内容看看是不是验证码
                break
            
            if "cargoquery" not in data:
                print("Warning: JSON 中没有 cargoquery 字段")
                break

            if len(data["cargoquery"]) == 0:
                break
            
            for item in data["cargoquery"]:
                game_info = item["title"]
                name = game_info["Name"]
                hdr_status = game_info["HDR"]
                
                if "false" in hdr_status.lower() or "hack" in hdr_status.lower():
                    continue
                    
                games_list.append(name)
            
            offset += 200 # 对应 limit
            print(f" - 已累计发现 {len(games_list)} 个游戏...")
            
            time.sleep(2) # 增加延迟，假装我们读得很慢
            
        except Exception as e:
            print(f"Exception: {e}")
            retry_count += 1
            if retry_count > 3: break
            time.sleep(5) # 出错歇一会再试
            
    return games_list

def find_exe_in_wikitext(game_name):
    # 如果名字里已经包含 exe (极少情况)，直接返回
    if game_name.lower().endswith('.exe'):
        return game_name

    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content", 
        "titles": game_name,
        "format": "json"
    }
    
    try:
        resp = requests.get(API_URL, params=params, headers=HEADERS, timeout=10)
        data = resp.json()
        
        pages = data.get("query", {}).get("pages", {})
        for page_id in pages:
            if "revisions" in pages[page_id]:
                content = pages[page_id]["revisions"][0]["*"]
                matches = EXE_PATTERN.findall(content)
                if matches:
                    clean_matches = [
                        m for m in matches 
                        if "setup" not in m.lower() 
                        and "install" not in m.lower()
                        and "config" not in m.lower()
                        and "crash" not in m.lower()
                        and "unity" not in m.lower()
                        and "ue4" not in m.lower()
                    ]
                    if clean_matches:
                        return max(set(clean_matches), key=clean_matches.count)
    except:
        pass
    return None

def heuristic_convert(game_name):
    clean_name = re.sub(r'[^a-zA-Z0-9]', '', game_name)
    return f"{clean_name}.exe".lower()

if __name__ == "__main__":
    games = fetch_hdr_games()
    
    if len(games) == 0:
        print("【严重错误】依然未找到任何游戏！可能是 IP 被 PCGW 封禁。")
        exit(1) 

    print(f"\nStep 2: 正在解析 {len(games)} 个游戏的 Exe (仅演示前 5 个日志)...")
    
    final_exe_list = set()
    count = 0
    
    for game in games:
        count += 1
        if count % 20 == 0:
            print(f"进度: {count}/{len(games)}")
            
        real_exe = find_exe_in_wikitext(game)
        if real_exe:
            final_exe_list.add(real_exe.lower())
        else:
            final_exe_list.add(heuristic_convert(game))
            
        time.sleep(0.2) # 稍微慢一点
    
    print(f"\nStep 3: 保存 {len(final_exe_list)} 条数据...")
    with open("games_list.txt", "w", encoding="utf-8") as f:
        for exe in sorted(final_exe_list):
            f.write(exe + "\n")
            
    print("✅ 成功完成！")
