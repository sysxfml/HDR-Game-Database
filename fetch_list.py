import requests
import json
import re
import time

# ==========================================
# 1. 超大内置核心库 (自带干粮)
# 既然 API 容易挂，我们把目前市面上主流 HDR 游戏全部预置进去
# 这保证了软件发布时，哪怕断网也是好用的
# ==========================================
MANUAL_DATA = {
    # --- 热门大作 ---
    "black myth wukong": "b1-win64-shipping.exe",
    "cyberpunk 2077": "cyberpunk2077.exe",
    "red dead redemption 2": "rdr2.exe",
    "elden ring": "eldenring.exe",
    "god of war": "gow.exe",
    "god of war ragnarok": "gowr.exe",
    "spider-man remastered": "spider-man.exe",
    "spider-man miles morales": "spider-man-miles.exe",
    "horizon zero dawn": "horizonzerodawn.exe",
    "horizon forbidden west": "horizonforbiddenwest.exe",
    "ratchet & clank: rift apart": "riftapart.exe",
    "returnal": "returnal.exe",
    "the last of us part i": "tlou-i.exe",
    "uncharted legacy of thieves": "u4.exe",
    "days gone": "daysgone.exe",
    "death stranding": "ds.exe",
    "control": "control.exe",
    "alan wake 2": "alanwake2.exe",
    "starfield": "starfield.exe",
    "hogwarts legacy": "hogwartslegacy.exe",
    "baldur's gate 3": "bg3.exe",
    "witcher 3": "witcher3.exe",
    "final fantasy vii remake": "ff7remake.exe",
    "final fantasy xv": "ffxv_s.exe",
    "forspoken": "forspoken.exe",
    "ghostwire: tokyo": "ghostwire.exe",
    
    # --- 射击/动作 ---
    "call of duty": "cod.exe",
    "call of duty hq": "cod.exe",
    "doom eternal": "doometernalx64vk.exe",
    "halo infinite": "haloinfinite.exe",
    "gears 5": "gears5.exe",
    "metro exodus": "metroexodus.exe",
    "destiny 2": "destiny2.exe",
    "warframe": "warframe.x64.exe",
    "borderlands 3": "borderlands3.exe",
    "tiny tina's wonderlands": "wonderlands.exe",
    "far cry 6": "farcry6.exe",
    "far cry 5": "farcry5.exe",
    "assassin's creed valhalla": "acvalhalla.exe",
    "assassin's creed odyssey": "acodyssey.exe",
    "assassin's creed mirage": "acmirage.exe",
    "immortals fenyx rising": "immortalsfenyxrising.exe",
    "watch dogs: legion": "watchdogslegion.exe",
    "tom clancy's the division 2": "thedivision2.exe",
    "ghost recon breakpoint": "grb.exe",
    "hitman 3": "hitman3.exe",
    
    # --- 赛车/体育 ---
    "forza horizon 5": "forzahorizon5.exe",
    "forza horizon 4": "forzahorizon4.exe",
    "forza motorsport": "forzamotorsport.exe",
    "f1 23": "f1_23.exe",
    "f1 22": "f1_22.exe",
    "f1 24": "f1_24.exe",
    "need for speed unbound": "nfs_unbound.exe",
    "need for speed heat": "nfsheat.exe",
    "dirt 5": "dirt5.exe",
    "grid legends": "gridlegends.exe",
    "ea sports fc 24": "fc24.exe",
    "fifa 23": "fifa23.exe",
    "nba 2k24": "nba2k24.exe",
    "madden nfl 24": "madden24.exe",
    
    # --- 恐怖/生化 ---
    "resident evil 4": "re4.exe",
    "resident evil village": "re8.exe",
    "resident evil 2": "re2.exe",
    "resident evil 3": "re3.exe",
    "resident evil 7": "re7.exe",
    "devil may cry 5": "dmc5.exe",
    "monster hunter rise": "mhrise.exe",
    "monster hunter world": "monsterhunterworld.exe",
    "dead space": "deadspace.exe",
    "calisto protocol": "calistoprotocol.exe",
    "dying light 2": "dyinglightgame_x64_rwdi.exe",
    
    # --- 其他热门 ---
    "genshin impact": "genshinimpact.exe",
    "honkai: star rail": "starrail.exe",
    "no man's sky": "nomanssky.exe",
    "sea of thieves": "sotgame.exe",
    "microsoft flight simulator": "flightsimulator.exe",
    "shadow of the tomb raider": "sottr.exe",
    "rise of the tomb raider": "rottr.exe",
    "mass effect legendary edition": "masseffect1.exe", 
    "guardians of the galaxy": "gotg.exe",
    "avatar: frontiers of pandora": "afop.exe"
}

API_URL = "https://www.pcgamingwiki.com/w/api.php"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Referer': 'https://www.pcgamingwiki.com/'
}

def fetch_hdr_games_lightweight():
    """
    轻量级抓取：只获取游戏名字，不进详情页。
    这通常不会被封锁。
    """
    print("Step 1: 尝试轻量级联网获取新游戏...")
    
    params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": "Category:Games_with_high_dynamic_range_support",
        "cmlimit": "500",
        "cmtype": "page"
    }
    
    games_found = []
    
    try:
        response = requests.get(API_URL, params=params, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if "query" in data and "categorymembers" in data["query"]:
                for item in data["query"]["categorymembers"]:
                    games_found.append(item["title"])
            print(f" -> 联网成功！获取到 {len(games_found)} 个游戏标题。")
        else:
            print(f" -> 联网失败 (状态码 {response.status_code})。将使用内置离线库。")
    except Exception as e:
        print(f" -> 联网出错 ({e})。将使用内置离线库。")
        
    return games_found

def guess_exe_name(game_name):
    """算法猜测：去掉空格和特殊符号"""
    clean = re.sub(r'[^a-zA-Z0-9]', '', game_name).lower()
    return f"{clean}.exe"

if __name__ == "__main__":
    # 1. 准备最终集合
    final_exe_set = set()
    
    # 2. 先装填内置的 Manual Data (这些是最准的)
    print(f"Step 0: 加载内置核心库 ({len(MANUAL_DATA)} 个)...")
    for exe in MANUAL_DATA.values():
        final_exe_set.add(exe.lower())
        
    # 3. 尝试联网补充
    online_games = fetch_hdr_games_lightweight()
    
    # 4. 处理联网数据 (如果有)
    if online_games:
        print(f"Step 2: 正在合并联网数据...")
        for game in online_games:
            # 先看内置库里有没有，有就跳过（因为内置库的exe更准）
            is_known = False
            for key in MANUAL_DATA.keys():
                if key in game.lower():
                    is_known = True
                    break
            
            # 如果是新游戏，才进行猜测
            if not is_known:
                guess = guess_exe_name(game)
                final_exe_set.add(guess)
    
    # 5. 保存
    sorted_list = sorted(list(final_exe_set))
    print(f"\nStep 3: 最终生成 {len(sorted_list)} 个白名单进程！")
    
    with open("games_list.txt", "w", encoding="utf-8") as f:
        for exe in sorted_list:
            f.write(exe + "\n")
            
    print("✅ 数据库更新完成。")
