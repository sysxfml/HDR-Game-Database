import requests
import json
import re
import time

# PCGamingWiki API
API_URL = "https://www.pcgamingwiki.com/w/api.php"

# 【修复点】添加身份标识，防止被服务器当成恶意攻击拦截
HEADERS = {
    'User-Agent': 'AutoGameHDR-Scraper/1.0 (github.com/sysxfml; Open Source Project)',
    'Accept': 'application/json'
}

# 正则表达式
EXE_PATTERN = re.compile(r'[\w\-\.]+\.exe', re.IGNORECASE)

def fetch_hdr_games():
    print("Step 1: 正在扫描 HDR 游戏列表...")
    
    params = {
        "action": "cargoquery",
        "format": "json",
        "tables": "Video",
        "fields": "_pageName=Name,HDR", 
        "where": "Video.HDR HOLDS LIKE '%true%'",
        "limit": "500"
    }
    
    games_list = []
    offset = 0
    
    while True:
        params["offset"] = offset
        try:
            # 【修复点】这里加入了 headers=HEADERS
            response = requests.get(API_URL, params=params, headers=HEADERS, timeout=30)
            
            # 调试信息：如果请求失败，打印状态码
            if response.status_code != 200:
                print(f"Warning: API returned status code {response.status_code}")
                break

            data = response.json()
            
            if "cargoquery" not in data or len(data["cargoquery"]) == 0:
                break
            
            for item in data["cargoquery"]:
                game_info = item["title"]
                name = game_info["Name"]
                hdr_status = game_info["HDR"]
                
                # 排除不支持的
                if "false" in hdr_status.lower() or "hack" in hdr_status.lower():
                    continue
                    
                games_list.append(name)
            
            offset += 500
            print(f" - 已发现 {len(games_list)} 个游戏...")
            
            # 稍微慢一点，防止太快被封
            time.sleep(1)
            
        except Exception as e:
            print(f"Error fetching list: {e}")
            break
            
    return games_list

def find_exe_in_wikitext(game_name):
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content", 
        "titles": game_name,
        "format": "json"
    }
    
    try:
        # 【修复点】这里也加入了 headers=HEADERS
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
                    ]
                    
                    if clean_matches:
                        most_common = max(set(clean_matches), key=clean_matches.count)
                        return most_common
    except Exception:
        pass
    return None

def heuristic_convert(game_name):
    clean_name = re.sub(r'[^a-zA-Z0-9]', '', game_name)
    return f"{clean_name}.exe".lower()

if __name__ == "__main__":
    games = fetch_hdr_games()
    
    if len(games) == 0:
        print("错误：未找到任何游戏，请检查 API 连接或 User-Agent。")
        exit(1) # 让 Actions 报错停止，而不是生成空文件

    print(f"\nStep 2: 正在深度解析 {len(games)} 个游戏的 Exe 名称...")
    
    final_exe_list = set()
    count = 0
    total = len(games)
    
    for game in games:
        count += 1
        # 每10个打印一次进度，减少日志量
        if count % 10 == 0:
            print(f"进度: {count}/{total}")

        real_exe = find_exe_in_wikitext(game)
        
        if real_exe:
            final_exe_list.add(real_exe.lower())
        else:
            final_exe_list.add(heuristic_convert(game))
            
        time.sleep(0.1)
    
    print(f"\nStep 3: 正在保存 {len(final_exe_list)} 个唯一进程名...")
    with open("games_list.txt", "w", encoding="utf-8") as f:
        for exe in sorted(final_exe_list):
            f.write(exe + "\n")
            
    print("✅ 全部完成！智能白名单已生成。")
