# HDR Game Database / HDR 游戏白名单数据库

![Update Status](https://github.com/sysxfml/HDR-Game-Database/actions/workflows/daily_update.yml/badge.svg)

[English](#english) | [中文](#chinese)

---

<a name="english"></a>
## 🇬🇧 English

### Introduction
This repository serves as the central database for **AutoGameHDR**. It hosts an automatically updated list of PC games that support **Native HDR**.

### How it Works
1.  **Data Source:** We leverage the [PCGamingWiki API](https://www.pcgamingwiki.com/) to fetch the latest list of games flagged with HDR support.
2.  **Smart Processing:** A Python script (`fetch_list.py`) runs daily via **GitHub Actions**. It parses the wiki source code to intelligently identify the main executable name (e.g., converting "Elden Ring" to `eldenring.exe`).
3.  **Auto-Update:** The generated `games_list.txt` is committed back to this repository automatically every day.

### Usage
This list is designed to be consumed by the [AutoGameHDR](https://github.com/sysxfml/AutoGameHDR) client software. However, it is a plain text file and can be used by any other utility that needs a list of HDR games.

* **Raw List URL:** `https://raw.githubusercontent.com/sysxfml/HDR-Game-Database/main/games_list.txt`

---

<a name="chinese"></a>
## 🇨🇳 中文

### 简介
本仓库是 **AutoGameHDR** 软件的核心数据库。它托管了一份自动更新的列表，包含了所有支持 **原生 HDR (Native HDR)** 的 PC 游戏进程名。

### 工作原理
1.  **数据来源：** 我们利用 [PCGamingWiki API](https://www.pcgamingwiki.com/) 抓取最新的 HDR 游戏列表。
2.  **智能处理：** 通过 **GitHub Actions** 每日运行 Python 脚本 (`fetch_list.py`)。该脚本会深入解析 Wiki 页面源码，智能识别游戏的主程序文件名（例如将 "Elden Ring" 转换为 `eldenring.exe`），而非简单的猜测。
3.  **自动更新：** 生成的 `games_list.txt` 文件会每天自动提交并推送到本仓库，无需人工干预。

### 如何使用
该列表主要供 [AutoGameHDR](https://github.com/sysxfml/AutoGameHDR) 客户端下载使用。但它是一个纯文本文件，任何需要 HDR 游戏名单的工具都可以引用它。

* **原始文件 (Raw) 地址：** `https://raw.githubusercontent.com/sysxfml/HDR-Game-Database/main/games_list.txt`
