# -*- coding: utf-8 -*-
"""
少女乐队番 排行榜爬虫（完整版）
================================
背景：B站番剧排行榜接口(pgc/web/rank/list)只有"番剧/国创"两类，
      没有"少女乐队"这种题材榜。所以这里换个思路：
      1) 用综合搜索接口(x/web-interface/search/all/v2)按具体番名搜到每部番；
      2) 用单部番统计接口(pgc/web/season/stat)拿到播放量/追番数/弹幕数；
      3) 合并去重后，按播放量(view)降序排，做成一个"少女乐队番人气排行"。
运行前：pip install requests
运行：  python anime_scraper_band.py
"""

import requests
import csv
import time
import re

# ---- 两个接口 ----
SEARCH_URL = "https://api.bilibili.com/x/web-interface/search/all/v2"
STAT_URL = "https://api.bilibili.com/pgc/web/season/stat"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Referer": "https://www.bilibili.com",
}

# 少女乐队番核心作品（用具体番名搜，比"少女乐队"这种题材词精准）
NAMES = [
    "MyGO!!!!!", "Ave Mujica", "孤独摇滚",
    "轻音少女 第一季", "轻音少女 第二季",
    "BanG Dream! 第三季", "少女歌剧",
    "CAROLE & TUESDAY", "Love Live! Superstar!!",
]

# 标题里含这些词的，算衍生（泡面番/LIVE录像），跳过不要
DERIV = ["PICO", "LIVE", "revival", "大份", "The LIVE", "☆PICO"]


def search_bangumi(keyword):
    """搜一个番名，从结果里挑第一个『非衍生』的番剧条目；没找到返回 None"""
    r = requests.get(SEARCH_URL, params={"keyword": keyword, "page": 1}, headers=HEADERS, timeout=15)
    d = r.json()
    for b in d["data"]["result"]:
        if b.get("result_type") != "media_bangumi":
            continue
        for it in (b.get("data") or []):
            title = re.sub(r"<[^>]+>", "", it.get("title", ""))   # 去掉 <em> 高亮标签
            if any(tag in title for tag in DERIV):
                continue
            return it          # 第一个非衍生的就是要的正片
    return None


def fetch_stats(season_id):
    """查单部番统计：播放量 views / 追番数 follow / 弹幕数 danmakus"""
    r = requests.get(STAT_URL, params={"season_id": season_id}, headers=HEADERS, timeout=15)
    return r.json().get("result", {})     # 注意：stat 数据在 result 字段，不是 data


def parse_item(raw, stats):
    """把搜索条目 + 统计拼成干净的小字典（字段顺序和原爬虫一致）"""
    title = re.sub(r"<[^>]+>", "", raw.get("title", ""))
    score = (raw.get("media_score") or {}).get("score", 0.0)
    try:
        rating = float(score)
    except (ValueError, TypeError):
        rating = 0.0
    return {
        "title": title,
        "type": "少女乐队番",
        "cover": raw.get("cover", ""),
        "rating": rating,
        "follow": stats.get("follow", 0),
        "danmaku": stats.get("danmakus", 0),
        "view": stats.get("views", 0),
        "url": raw.get("url") or raw.get("goto_url", ""),
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
    """主流程：搜每部番 → 查统计 → 合并去重 → 按播放量排名 → 存 CSV"""
    seen = set()
    all_rows = []

    for name in NAMES:
        print(f"搜索【{name}】...")
        raw = search_bangumi(name)
        if not raw:
            print("  没找到，跳过")
            continue
        sid = raw.get("season_id")
        if sid in seen:
            continue
        seen.add(sid)

        stats = fetch_stats(sid)
        all_rows.append(parse_item(raw, stats))
        time.sleep(1)     # 礼貌限速

    # 按播放量降序排，加排名
    all_rows.sort(key=lambda x: x["view"], reverse=True)
    ordered = []
    for i, row in enumerate(all_rows, 1):
        ordered.append({
            "rank": i,
            "title": row["title"],
            "type": row["type"],
            "cover": row["cover"],
            "rating": row["rating"],
            "follow": row["follow"],
            "danmaku": row["danmaku"],
            "view": row["view"],
            "url": row["url"],
        })

    save_to_csv(ordered, "band_ranking.csv")
    print(f"\n✅ 共 {len(ordered)} 部少女乐队番，已存到 band_ranking.csv")


if __name__ == "__main__":
    main()
