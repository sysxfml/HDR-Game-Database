import requests
import json
import re
import time
import sys

# ==========================================
# 配置区域
# ==========================================
API_URL = "https://www.pcgamingwiki.com/w/api.php"

# 伪装成浏览器，防止被拦截
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Referer': 'https://www.pcgamingwiki.com/'
}

# 正则表达式：专门匹配 Wiki 源码中的路径部分
# 例子: {{Path|Windows|Steam|...|Game.exe}}
EXE_PATH_PATTERN = re.compile(r'\{\{Path\|.*?\|(.*?\.exe)\}\}', re.IGNORECASE)
# 备用正则：匹配任意 .exe 结尾的单词
SIMPLE_EXE_PATTERN = re.compile(r'[\w\-\.]+\.exe', re.IGNORECASE)

# 人工校准库 (优先级最高)
MANUAL_FIXES = {
    "red dead redemption 2": "rdr2.exe",
    "cyberpunk 2077": "cyberpunk2077.exe",
    "elden ring": "eldenring.exe",
    "call of duty": "cod.exe",
    "doom eternal": "doometernalx64vk.exe",
    "god of war": "gow.exe",
    "forza horizon 5": "forzahorizon5.exe",
    "halo infinite": "haloinfinite.exe",
    "black myth wukong": "b1-win64-shipping.exe",
    "starfield": "starfield.exe",
    "hogwarts legacy": "hogwartslegacy.exe",
    "alan wake 2": "alanwake2.exe",
    "baldur's gate 3": "bg3.exe",
    "control": "control.exe",
    "death stranding": "ds.exe",
    "destiny 2": "destiny2.exe",
    "f1 22": "f1_22.exe",
    "f1 23": "f1_23.exe",
    "final fantasy xv": "ffxv_s.exe",
    "gears 5": "gears5.exe",
    "genshin impact": "genshinimpact.exe",
    "hitman 3": "hitman3.exe",
    "metro exodus": "metroexodus.exe",
    "monster hunter rise": "mhrise.exe",
    "no man's sky": "nomanssky.exe",
    "resident evil 2": "re2.exe",
    "resident evil 3": "re3.exe",
    "resident evil 4": "re4.exe",
    "resident evil village": "re8.exe",
    "spider-man remastered": "spider-man.exe",
    "miles morales": "spider-man-miles.exe",
    "the last of us part i": "tlou-i.exe",
    "uncharted: legacy of thieves collection": "u4.exe",
    "watch dogs: legion": "watchdogslegion.exe",
    "witcher 3": "witcher3.exe"
}

# 垃圾过滤词
BLACKLIST_EXE = ["setup.exe", "installer.exe", "unins000.exe", "config.exe", "crashreporter.exe", "unitycrashhandler64.exe", "dxsetup.exe"]

def fetch_hdr_game_names():
    """第一步：获取所有支持 HDR 的游戏名称列表"""
    print("Step 1: 正在扫描 HDR 游戏列表 (使用 Category 接口)...")
    
    params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": "Category:Games_with_high_dynamic_range_support",
        "cmlimit": "500",
        "cmtype": "page"
    }
    
    games_list = []
    continue_token = None
    
    while True:
        if continue_token: params["cmcontinue"] = continue_token
            
        try:
            response = requests.get(API_URL, params=params, headers=HEADERS, timeout=30)
            if response.status_code != 200: break
            data = response.json()
            
            if "query" in data and "categorymembers" in data["query"]:
                for item in data["query"]["categorymembers"]:
                    games_list.append(item["title"])
            
            if "continue" in data:
                continue_token = data["continue"]["cmcontinue"]
            else:
                break
            time.sleep(0.5)
        except:
            break
            
    print(f" -> 共发现 {len(games_list)} 个游戏条目。")
    return games_list

def deep_scan_exe_name(game_name):
    """第二步：下载网页源码，正则提取 .exe"""
    
    # 1. 先查字典
    for key, val in MANUAL_FIXES.items():
        if key.lower() == game_name.lower():
            return val

    # 2. 查字典没查到，开始爬取源码
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content", # 获取源码
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
                
                # 策略 A: 搜索 {{Path|...|Game.exe}} 这种高可信度标签
                path_matches = EXE_PATH_PATTERN.findall(content)
                if path_matches:
                    # 过滤垃圾
                    valid_matches = [m for m in path_matches if m.lower() not in BLACKLIST_EXE]
                    if valid_matches:
                        # 找到最长的一个通常是最准确的完整文件名
                        return max(valid_matches, key=len)

                # 策略 B: 如果没找到 Path 标签，搜索全文里的 .exe
                simple_matches = SIMPLE_EXE_PATTERN.findall(content)
                if simple_matches:
                    valid_matches = [
                        m for m in simple_matches 
                        if m.lower() not in BLACKLIST_EXE 
                        and "redist" not in m.lower()
                        and "directx" not in m.lower()
                    ]
                    if valid_matches:
                        # 统计出现频率最高的 exe
                        return max(set(valid_matches), key=valid_matches.count)
    except:
        pass
    
    # 3. 实在抓不到，只能猜了
    clean_name = re.sub(r'[^a-zA-Z0-9]', '', game_name).lower()
    return f"{clean_name}.exe"

if __name__ == "__main__":
    all_games = fetch_hdr_game_names()
    
    # 如果 API 彻底挂了，至少保证 Manual Fixes 里的游戏能用
    if not all_games:
        print("【警告】API 获取失败，仅使用内置列表。")
        all_games = list(MANUAL_FIXES.keys())

    final_set = set()
    
    # 强制添加内置列表的 Value (exe名)
    for val in MANUAL_FIXES.values():
        final_set.add(val.lower())

    print(f"\nStep 2: 深度解析 {len(all_games)} 个游戏 (这就比较慢了，请耐心等待)...")
    
    count = 0
    for game in all_games:
        count += 1
        if count % 10 == 0:
            print(f"进度: {count}/{len(all_games)}...")
            
        exe = deep_scan_exe_name(game)
        if exe:
            final_set.add(exe.lower())
            
        # 稍微慢一点，防止触发 429 Too Many Requests
        time.sleep(0.2)

    print(f"\nStep 3: 写入文件，共 {len(final_set)} 个有效进程...")
    with open("games_list.txt", "w", encoding="utf-8") as f:
        for exe in sorted(final_set):
            f.write(exe + "\n")
            
    print("✅ 更新完成。")
