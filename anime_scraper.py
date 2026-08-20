"""
B站番剧排行榜爬虫 —— 二次元主题学习项目（阶段二：API 抓取）
----------------------------------------------------------------
这个脚本做三件事：
  1. 调用 B站公开排行榜 API，抓取「番剧」和「国创」的榜单
  2. 从返回的 JSON 里只挑我们关心的字段（排名/标题/评分/追番数/弹幕数）
  3. 存成 CSV 文件，并打印一个简单的「评分 Top10」分析

为什么拿它当第一个项目？
  - 不用登录、不用解析 HTML，直接拿结构化 JSON，新手最不容易卡住
  - 数据就是你天天看的番，学起来有动力
  - 后面可以接 AI 做推荐、接 UI 做展示，一条龙

依赖：pip install -r requirements.txt
运行：python anime_scraper.py
"""

import csv
import time

import requests

# ---------- 1. 配置区（想改哪里看这里）----------

# B站排行榜 API。season_type=1 是「番剧」，=4 是「国创」
API_URL = "https://api.bilibili.com/pgc/web/rank/list"

# 请求头：网站靠 User-Agent / Referer 判断是否像浏览器，缺了容易被拒
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0 Safari/537.36",
    "Referer": "https://www.bilibili.com",
}

# 输出文件名
OUTPUT_FILE = "anime_ranking.csv"


# ---------- 2. 抓取（发请求拿数据）----------

def fetch_ranking(season_type: int, day: int = 3) -> list:
    """向 API 发一次 GET 请求，返回条目列表。

    关键知识点：
      - requests.get(...) 就是在发一个 HTTP GET 请求
      - params 会自动拼成 URL 上的 ?season_type=1&day=3
      - .json() 把服务器返回的 JSON 文本变成 Python 字典/列表
    """
    params = {"season_type": season_type, "day": day}
    resp = requests.get(API_URL, headers=HEADERS, params=params, timeout=15)
    resp.raise_for_status()            # 如果 HTTP 状态码是 4xx/5xx 就直接报错
    data = resp.json()
    if data.get("code") != 0:          # B站用 code 字段表示业务是否成功
        raise RuntimeError(f"API 返回错误: {data.get('message')}")
    return data["result"]["list"]      # 真正的条目列表在这一层


# ---------- 3. 解析（从原始数据里挑字段）----------

def parse_item(item: dict) -> dict:
    """把一条「原始数据」精简成我们关心的几个字段。

    item 是 API 返回的完整字典（含封面、badge 等几十个字段），
    我们只要其中几个，这步也叫「提取 / 清洗」。
    """
    stat = item.get("stat", {})        # 统计信息：追番数、弹幕数都在这
    rating_raw = item.get("rating", "")  # 形如 '8.8分'

    # '8.8分' -> 8.8；如果没有评分（空字符串）就记 0.0
    try:
        rating = float(rating_raw.replace("分", ""))
    except ValueError:
        rating = 0.0

    return {
        "rank":    item.get("rank"),                 # 榜单名次
        "title":   item.get("title", ""),            # 番剧名称
        "rating":  rating,                           # 评分（浮点数）
        "follow":  stat.get("follow") or 0,          # 追番人数
        "danmaku": stat.get("danmaku") or 0,         # 弹幕总数
        "badge":   item.get("badge", ""),            # 标签，如「大会员」
        "url":     item.get("url", ""),              # 播放页链接
    }


# ---------- 4. 存储（写 CSV）----------

def save_to_csv(rows: list, filename: str):
    """把列表写成 CSV。

    utf-8-sig 这个编码能让 Excel 直接打开中文不乱码（Windows 必加）。
    """
    fields = ["rank", "title", "rating", "follow", "danmaku", "badge", "url"]
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()        # 写表头
        writer.writerows(rows)      # 写数据
    print(f"已保存 {len(rows)} 条到 {filename}")


# ---------- 5. 分析（用刚学到的 Python 排序）----------

def analyze(rows: list):
    """做个最简单的分析：按评分取 Top10。"""
    top = sorted(rows, key=lambda x: x["rating"], reverse=True)[:10]
    print("\n=== 评分 Top10 ===")
    for r in top:
        print(f"  {r['rating']:>4}  {r['title']}")


# ---------- 6. 主流程（把上面串起来）----------

def main():
    all_rows = []
    # 抓两类：番剧 + 国创
    for name, stype in [("番剧", 1), ("国创", 4)]:
        print(f"正在抓取【{name}】...")
        try:
            items = fetch_ranking(stype)
            rows = [parse_item(it) for it in items]
            all_rows.extend(rows)
            print(f"  {name} 抓到 {len(rows)} 条")
        except Exception as e:
            print(f"  {name} 抓取失败: {e}")
        time.sleep(1)               # 礼貌：两次请求之间停 1 秒，别把人家压垮

    save_to_csv(all_rows, OUTPUT_FILE)
    analyze(all_rows)


# 当脚本被直接运行（而不是被别的文件 import）时才执行 main
if __name__ == "__main__":
    main()
