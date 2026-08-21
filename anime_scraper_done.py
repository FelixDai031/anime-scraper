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


def fetch_ranking(season_type, day=7):
    """发请求，返回某一类的原始数据列表。
    day=7 周榜，day=3 三日榜（还有 day=30 月榜，按需传参即可）"""
    params = {"season_type": season_type, "day": day}
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


def analyze_top(rows, key="follow", top_n=10, filename=None):
    """按某个字段降序排，返回前 top_n 名（不修改原列表）。
    key 可以取：follow(追番) / view(播放) / danmaku(弹幕) / rating(评分) / danmaku_rate(弹幕率)
    传 filename 会把 Top 结果另存一份 CSV。"""
    ranked = sorted(rows, key=lambda r: r.get(key, 0), reverse=True)[:top_n]
    if filename:
        save_to_csv(ranked, filename)
    return ranked


def main():
    """主流程：抓番剧(1) → 合并存 CSV → 多维分析 Top10"""
    categories = [("番剧", 1)]
    DAY = 7  # 周榜；想试三日榜改成 3，月榜改成 30

    all_rows = []
    for name, season_type in categories:
        print(f"正在抓【{name}】排行榜（day={DAY}）...")
        raw_list = fetch_ranking(season_type, day=DAY)
        for item in raw_list:
            all_rows.append(parse_item(item, name))
        print(f"  {name} 抓到 {len(raw_list)} 条，累计 {len(all_rows)} 条")
        time.sleep(1)   # 礼貌限速

    save_to_csv(all_rows, "anime_ranking_full.csv")
    print(f"\n✅ 全部完成，共 {len(all_rows)} 条，已存到 anime_ranking_full.csv")

    # ---- Day5 新增：按多种维度排 Top10 ----
    print("\n📊 追番数 Top10：")
    for i, r in enumerate(analyze_top(all_rows, "follow", 10), 1):
        print(f"  {i:2d}. {r['title']} — 追番 {r['follow']:,}")

    print("\n📊 播放量 Top10：")
    for i, r in enumerate(analyze_top(all_rows, "view", 10), 1):
        print(f"  {i:2d}. {r['title']} — 播放 {r['view']:,}")

    print("\n📊 弹幕率 Top10：")
    for i, r in enumerate(analyze_top(all_rows, "danmaku_rate", 10), 1):
        print(f"  {i:2d}. {r['title']} — 弹幕率 {r['danmaku_rate']}")

    # 把追番 Top10 另存一份 CSV（方便你直接打开看）
    analyze_top(all_rows, "follow", 10, filename="anime_top10_follow.csv")
    print("\n💾 追番 Top10 已存到 anime_top10_follow.csv")


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
