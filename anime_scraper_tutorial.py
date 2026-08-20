# -*- coding: utf-8 -*-
"""
二次元爬虫 · 手把手教学版（孤独摇滚/B站番剧排行榜）
====================================================
目标：抓取 B站「番剧 + 国创」排行榜，存成 CSV，并算出评分 Top10。

怎么用这个文件：
  1) 命令行先装库：  pip install requests
  2) 运行：          python anime_scraper_tutorial.py
  3) 看生成的 anime_tutorial.csv

阅读顺序：从上往下读，每个 🎯 大步骤就是"写一个爬虫要做的动作"。
每个函数前面的注释写的是「这一步你在学什么」，配合下面的对话讲解一起看。
"""

# 📦 准备：import 就是"引入别人写好的工具"
#   类比 C 的 #include <stdio.h> / 引入第三方库
#    requests = 发 HTTP 请求的库（等价于帮你封装了 socket 那一套）
#    csv     = 读写 CSV 文件的库（等价于帮你封装了 fopen/fprintf）
#    time    = 时间相关，这里用来"睡 1 秒"控制速度
import requests
import csv
import time


# ============================================================
# 🎯 第 1 步：搞懂"发请求"——给网站一句话，它回你一段话
# ------------------------------------------------------------
# 在 C 里发一次 HTTP 请求，你要自己：
#   socket() -> connect() 连服务器
#   -> send("GET /path HTTP/1.1\r\nHost: xxx\r\n\r\n")  发请求报文
#   -> recv() 收响应
# Python 的 requests 把这一整套封装成一行：requests.get(...)
# 你只要告诉它：URL 是谁、带什么参数(params)、以什么身份(headers)
# ============================================================

# URL = 要访问的接口地址（B站公开的排行榜接口，无需登录）
URL = "https://api.bilibili.com/pgc/web/rank/list"

# headers（请求头）：相当于进门时声明"我是正常浏览器，不是机器人"
# 很多网站看到没有 User-Agent 的请求会直接拒绝（反爬的基本操作）
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0 Safari/537.36",
    "Referer": "https://www.bilibili.com",
}

# params（查询参数）：会被自动拼到 URL 后面，变成 ?season_type=1&day=3
#   season_type=1 是「番剧」，=4 是「国创」
#   day=3 表示「近 3 天榜」
# 类比：这就是 GET 请求里 URL 问号后面的那串东西


# ============================================================
# 🎯 第 2 步：把"JSON 文本"解析成能操作的数据结构
# ------------------------------------------------------------
# 服务器返回的是一段 JSON 字符串，长这样：
#   {"code":0, "result": {"list": [ {"title":"xxx","rating":"8.8分",...}, ... ]}}
# JSON 和 Python 类型的对应关系：
#   { }  -> dict    （字典，类比 C 的哈希表 / 结构体，用 key 取 value）
#   [ ]  -> list    （列表，类比数组，用下标取元素）
#   "8.8分" -> str  （字符串）
# requests 的 .json() 一步就把 JSON 字符串变成 Python 的 dict/list
# ============================================================

def fetch_ranking(season_type: int, day: int = 3) -> list:
    """发一次请求，返回榜单条目列表。

    这一整个函数就是"第 1 步 + 第 2 步"的组合：
      发请求 -> 收响应 -> 解析 JSON -> 取出 list
    """
    params = {"season_type": season_type, "day": day}
    # 真正发请求。timeout=15 表示最多等 15 秒，防止卡死
    resp = requests.get(URL, headers=HEADERS, params=params, timeout=15)

    # raise_for_status()：如果 HTTP 状态码是 4xx/5xx（失败）就直接抛异常
    # 类比：C 里你要自己判断 recv 到的状态行是不是 "200 OK"
    resp.raise_for_status()

    data = resp.json()   # 第 2 步：JSON 文本 -> Python dict

    # B站用 data["code"] 表示"这次业务是否成功"，0 才是成功
    if data.get("code") != 0:
        raise RuntimeError(f"接口返回错误: {data.get('message')}")

    # 真正的数据列表藏在 data["result"]["list"] 这一层
    return data["result"]["list"]


# ============================================================
# 🎯 第 3 步：从一条原始数据里，挑出你关心的字段（数据提取/清洗）
# ------------------------------------------------------------
# API 返回的每一条有几十个字段（封面图、badge、各种 stat...）
# 我们只要其中几个：排名 / 标题 / 评分 / 追番数 / 弹幕数 / 链接
# 这步就是"爬虫里最日常的活儿"：把杂乱的原始数据，筛成干净的表。
# ============================================================

def parse_item(item: dict) -> dict:
    """把一条原始数据，精简成我们关心的几个字段。

    item 是一个 dict（几十个 key）。
    返回也是一个 dict，但只有 6 个 key，干净好用。
    """
    # 追番数、弹幕数藏在 item["stat"] 这个子字典里
    stat = item.get("stat", {})          # .get 取不到就返回 {}，不会报错崩程序

    rating_raw = item.get("rating", "")  # 评分原始值是字符串，如 "8.8分"

    # "8.8分" -> 8.8（浮点数）。
    # 为什么用 try/except？因为有的条目没评分（空串 ""），
    # 直接 float("") 会报错，try 包一下，出错就记 0.0，程序不崩。
    try:
        rating = float(rating_raw.replace("分", ""))
    except ValueError:
        rating = 0.0

    return {
        "rank":    item.get("rank"),               # 榜单名次
        "title":   item.get("title", ""),          # 番剧名字
        "rating":  rating,                          # 评分（数字，方便排序）
        "follow":  stat.get("follow") or 0,        # 追番人数
        "danmaku": stat.get("danmaku") or 0,       # 弹幕总数
        "url":     item.get("url", ""),            # 播放页链接
    }


# ============================================================
# 🎯 第 4 步：把多条数据写进 CSV 文件
# ------------------------------------------------------------
# CSV = 逗号分隔的纯文本，Excel 能直接打开。
# 类比 C：你要 fopen -> 一行行 fprintf -> fclose；
#        Python 用 csv.DictWriter 把"字典列表"直接写成表格。
# ============================================================

def save_to_csv(rows: list, filename: str):
    fields = ["rank", "title", "rating", "follow", "danmaku", "url"]
    # encoding="utf-8-sig" 很关键！
    #   它会在文件头写 BOM，让 Windows 上的 Excel 打开中文不乱码。
    #   （纯 utf-8 在 Excel 里中文会乱码，这是新手一大坑）
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()      # 写第一行表头
        writer.writerows(rows)    # 写所有数据行
    print(f"已保存 {len(rows)} 条 -> {filename}")


# ============================================================
# 🎯 第 5 步：做个最简单的分析——评分 Top10
# ------------------------------------------------------------
# sorted() 排序：key=lambda x: x["rating"] 表示"按 rating 字段排序"
# reverse=True = 从大到小；[:10] = 取前 10 个（切片，类比数组截断）
# 这步练的是 Python 的"列表排序 + lambda"，也是算法课里排序的实用版。
# ============================================================

def print_top10(rows: list):
    top = sorted(rows, key=lambda x: x["rating"], reverse=True)[:10]
    print("\n=== 评分 Top10 ===")
    for r in top:
        # :>4 表示占 4 个字符宽度、右对齐，排版好看
        print(f"  {r['rating']:>4}  {r['title']}")


# ============================================================
# 🎯 第 6 步：主流程——把上面 5 步串起来
# ------------------------------------------------------------
# 先抓「番剧」(1)，再抓「国创」(4)，合并后存 CSV + 分析。
# 两次请求之间 time.sleep(1) 停 1 秒 = 爬虫礼貌，别把人家服务器压垮。
# ============================================================

def main():
    all_rows = []
    for name, stype in [("番剧", 1), ("国创", 4)]:
        print(f"正在抓取【{name}】...")
        try:
            raw = fetch_ranking(stype)
            rows = [parse_item(it) for it in raw]   # 列表推导式：对每条调用 parse_item
            all_rows.extend(rows)                   # 合并到总列表
            print(f"  {name} 抓到 {len(rows)} 条")
        except Exception as e:
            print(f"  {name} 抓取失败: {e}")         # 一类失败不影响另一类
        time.sleep(1)                               # 礼貌限速

    save_to_csv(all_rows, "anime_tutorial.csv")
    print_top10(all_rows)


# 这个 if 的意思是：只有"直接运行这个文件"时才执行 main()
# 如果别的文件 import 它，main() 不会自动跑（这是 Python 的标准写法）
if __name__ == "__main__":
    main()
