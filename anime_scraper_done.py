# -*- coding: utf-8 -*-
"""
二次元番剧排行榜爬虫（完整版）
功能：抓取 B 站「番剧榜」和「国创榜」，解析后合并存成 CSV
运行前：pip install requests
运行：  python anime_scraper_done.py
"""

import os
import subprocess
import requests
import csv
import time

# ---- 接口与请求头（告诉网站"我是浏览器"）----
URL = "https://api.bilibili.com/pgc/web/rank/list"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Referer": "https://www.bilibili.com",
}


def fetch_ranking(season_type):
    """发请求，返回某一类的原始数据列表"""
    params = {"season_type": season_type, "day": 7}
    response = requests.get(URL, headers=HEADERS, params=params)
    data = response.json()
    return data["result"]["list"]


def parse_item(item, name):
    """从一条原始数据里挑出关心的字段，整理成干净的小字典（name=番剧/国创）"""
    rating_str = item.get("rating", "0分")   # 没有评分就当 0分
    try:
        rating = float(rating_str.replace("分", ""))
    except ValueError:
        rating = 0.0

    return {
        "rank": item["rank"],
        "title": item["title"],
        "type": name,                           # 类型：番剧 / 国创
        "cover": item.get("cover", ""),         # 封面图链接（B站返回的图片URL）
        "rating": rating,
        "follow": item["stat"]["follow"],
        "danmaku": item["stat"]["danmaku"],
        "view": item["stat"]["view"],          # 播放量（也在 stat 里）
        "url": item["url"],
        "danmaku_rate": round(item["stat"]["danmaku"] / item["stat"]["follow"], 4) if item["stat"]["follow"] else 0,

    }


def save_to_csv(rows, filename):
    """把字典列表写成 CSV（utf-8-sig 让 Excel 中文不乱码）"""
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        if not rows:
            return
        fieldnames = list(rows[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    """主流程：抓番剧(1) ，合并存一个 CSV"""
    categories = [("番剧", 1)]

    all_rows = []
    for name, season_type in categories:
        print(f"正在抓【{name}】排行榜...")
        raw_list = fetch_ranking(season_type)
        for item in raw_list:
            all_rows.append(parse_item(item, name))
        print(f"  {name} 抓到 {len(raw_list)} 条，累计 {len(all_rows)} 条")
        time.sleep(1)   # 礼貌限速

    save_to_csv(all_rows, "anime_ranking_full.csv")
    print(f"\n✅ 全部完成，共 {len(all_rows)} 条，已存到 anime_ranking_full.csv")


if __name__ == "__main__":
    main()
    # 跑完自动打开结果文件（优先 VS Code，失败则用系统默认程序）
    try:
        subprocess.run(["code", "anime_ranking_full.csv"], check=False, shell=True)
    except Exception:
        try:
            os.startfile("anime_ranking_full.csv")
        except Exception:
            pass
