import requests
import json
import re
import time

# ==========================================
# 1. 内置核心库 (保证热门游戏 100% 准确)
# 这些是 API 经常猜错，或者一定要保证支持的大作
# ==========================================
MANUAL_FIXES = {
    # 格式: "游戏名关键字": "准确的exe名"
    "red dead redemption 2": "rdr2.exe",
    "cyberpunk 2077": "cyberpunk2077.exe",
    "elden ring": "eldenring.exe",
    "call of duty": "cod.exe", # 现代战争等
    "doom eternal": "doometernalx64vk.exe",
    "god of war": "gow.exe",
    "horizon zero dawn": "horizonzerodawn.exe",
    "forza horizon 5": "forzahorizon5.exe",
    "forza horizon 4": "forzahorizon4.exe",
    "halo infinite": "haloinfinite.exe",
    "resident evil village": "re8.exe",
    "resident evil 4": "re4.exe",
    "resident evil 2": "re2.exe",
    "resident evil 3": "re3.exe",
    "devil may cry 5": "dmc5.exe",
    "monster hunter rise": "mhrise.exe",
    "monster hunter world": "monsterhunterworld.exe",
    "assassin's creed valhalla": "acvalhalla.exe",
    "assassin's creed odyssey": "acodyssey.exe",
    "far cry 6": "farcry6.exe",
    "hitman 3": "hitman3.exe",
    "spiderman remastered": "spider-man.exe",
    "miles morales": "spider-man-miles.exe",
    "uncharted": "u4.exe",
    "last of us": "tlou-i.exe",
    "witcher 3": "witcher3.exe",
    "shadow of the tomb raider": "sottr.exe",
    "death stranding": "ds.exe",
    "final fantasy vii remake": "ff7remake.exe",
    "black myth wukong": "b1-win64-shipping.exe", # 黑神话
    "ratchet and clank": "riftapart.exe",
    "returnal": "returnal.exe",
    "starfield": "starfield.exe",
    "hogwarts legacy": "hogwartslegacy.exe",
    "alan wake 2": "alanwake2.exe",
    "baldur's gate 3": "bg3.exe"
}

# ==========================================
# 2. API 配置
# ==========================================
API_URL = "https://www.pcgamingwiki.com/w/api.php"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Referer': 'https://www.pcgamingwiki.com/'
}

def fetch_from_api():
    """尝试从 Wiki 获取更多游戏"""
    print("正在尝试联网获取新游戏列表...")
    
    # 使用 CargoQuery 获取原生 HDR 游戏
    params = {
        "action": "cargoquery",
        "format": "json",
        "tables": "Video",
        "fields": "_pageName=Name", 
        "where": "Video.HDR HOLDS LIKE '%true%'", # 只要支持HDR的
        "limit": "300" 
    }
    
    found_names = []
    try:
        response = requests.get(API_URL, params=params, headers=HEADERS, timeout=15)
        data = response.json()
        
        if "cargoquery" in data:
            for item in data["cargoquery"]:
                found_names.append(item["title"]["Name"])
                
        print(f"API 成功返回了 {len(found_names)} 个游戏名。")
    except Exception as e:
        print(f"API 连接部分失败 (使用本地库兜底): {e}")
        
    return found_names

def smart_convert(game_name):
    """
    智能转换逻辑：
    1. 先查字典 (Manual Fixes)
    2. 查不到再用算法猜
    """
    lower_name = game_name.lower()
    
    # 1. 优先匹配人工校准库
    for key, val in MANUAL_FIXES.items():
        if key in lower_name:
            return val
            
    # 2. 算法猜测 (去空格 + .exe)
    # 比如 "Sea of Thieves" -> "seaofthieves.exe" (通常是准的)
    clean_name = re.sub(r'[^a-zA-Z0-9]', '', lower_name)
    return f"{clean_name}.exe"

if __name__ == "__main__":
    # 1. 收集所有游戏名
    all_game_names = set()
    
    # 加入 API 抓取到的
    api_games = fetch_from_api()
    for g in api_games:
        all_game_names.add(g)
        
    # 加入手动库里的 Key (确保即使 API 挂了，这些游戏也能被处理)
    for k in MANUAL_FIXES.keys():
        all_game_names.add(k)
        
    print(f"合并后共有 {len(all_game_names)} 个游戏条目等待处理...")
    
    # 2. 转换为 exe
    final_exe_list = set()
    
    for game in all_game_names:
        exe = smart_convert(game)
        final_exe_list.add(exe)
        
    # 3. 再次强制注入手动库的 Value (双重保险)
    # 防止因为某种算法原因把手动库漏了
    for correct_exe in MANUAL_FIXES.values():
        final_exe_list.add(correct_exe)

    # 4. 保存
    sorted_list = sorted(list(final_exe_list))
    print(f"最终生成 {len(sorted_list)} 个有效进程白名单！")
    
    with open("games_list.txt", "w", encoding="utf-8") as f:
        for exe in sorted_list:
            f.write(exe + "\n")
            
    print("✅ database 更新完成。")
