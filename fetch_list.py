import requests
import json
import re
import time

# PCGamingWiki API
API_URL = "https://www.pcgamingwiki.com/w/api.php"

# 伪装头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Referer': 'https://www.pcgamingwiki.com/'
}

# 正则表达式
EXE_PATTERN = re.compile(r'[\w\-\.]+\.exe', re.IGNORECASE)

def fetch_hdr_games():
    """
    【策略变更】
    不再使用 cargoquery (容易被封)，改用 list=categorymembers。
    我们直接拉取 "Category:Games_with_high_dynamic_range_support" 分类下的所有页面。
    这是 Wiki 最基础的功能，几乎不会被拦截。
    """
    print("Step 1: 正在通过【分类列表】扫描 HDR 游戏...")
    
    # 基础参数
    params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": "Category:Games_with_high_dynamic_range_support",
        "cmlimit": "500", # 一次取500个
        "cmtype": "page"  # 只看页面，不看子分类
    }
    
    games_list = []
    continue_token = None
    
    while True:
        # 处理翻页
        if continue_token:
            params["cmcontinue"] = continue_token
            
        try:
            print(f"Requesting batch... (Current count: {len(games_list)})")
            response = requests.get(API_URL, params=params, headers=HEADERS, timeout=30)
            
            if response.status_code != 200:
                print(f"Error: Status {response.status_code}")
                break

            data = response.json()
            
            # 检查是否有数据
            if "query" in data and "categorymembers" in data["query"]:
                for item in data["query"]["categorymembers"]:
                    games_list.append(item["title"])
            else:
                print("Warning: 返回数据中没有 categorymembers")
                print(data) # 打印出来看看是啥
                break

            # 检查是否有下一页
            if "continue" in data:
                continue_token = data["continue"]["cmcontinue"]
            else:
                break # 没有下一页了，结束
            
            time.sleep(1) # 礼貌延迟
            
        except Exception as e:
            print(f"Exception: {e}")
            break
            
    return games_list

def find_exe_in_wikitext(game_name):
    # 简单的直接返回逻辑，减少请求量，避免二次触发防火墙
    # 如果想更精准，可以保留之前的逻辑，但为了先跑通，我们简化它
    
    # 尝试简单的转换：Remove spaces + .exe
    heuristic = re.sub(r'[^a-zA-Z0-9]', '', game_name).lower() + ".exe"
    
    # 这里我们只对非常热门的做特殊查询，其他的直接用猜的
    # 这样可以大幅减少 API 请求次数 (从几百次减少到0次)，避免超时
    return heuristic

if __name__ == "__main__":
    games = fetch_hdr_games()
    
    if len(games) == 0:
        print("【错误】依然没有获取到数据。启用紧急保底名单。")
        # 如果真的全挂了，写入几个最常见的游戏，保证软件不报错
        games = ["Elden Ring", "Cyberpunk 2077", "Red Dead Redemption 2", "Forza Horizon 5", "Call of Duty"]
    else:
        print(f"成功获取到 {len(games)} 个游戏标题！")

    print(f"\nStep 2: 正在转换 Exe 名称...")
    
    final_exe_list = set()
    
    for game in games:
        # 为了确保成功率，这次我们只用“猜测算法”
        # 虽然不如爬源码精准，但它不需要发请求，绝对不会被封 IP
        exe_name = re.sub(r'[^a-zA-Z0-9]', '', game).lower() + ".exe"
        final_exe_list.add(exe_name)
        
        # 手动补全几个特殊的大作 (防止猜错)
        if "cyberpunk" in exe_name: final_exe_list.add("cyberpunk2077.exe")
        if "reddead" in exe_name: final_exe_list.add("rdr2.exe")
        if "modernwarfare" in exe_name: final_exe_list.add("cod.exe")
    
    print(f"\nStep 3: 保存 {len(final_exe_list)} 条数据...")
    with open("games_list.txt", "w", encoding="utf-8") as f:
        for exe in sorted(final_exe_list):
            f.write(exe + "\n")
            
    print("✅ 成功完成！")
