# -*- coding: utf-8 -*-
"""Python 基础练手：list / dict / 推导式 / set（基于你自己爬的番剧榜）
运行： cd anime-scraper && py practice_list_dict.py
每道题先给「目标 + C类比提示」，下面紧跟着参考实现。
建议：先盖住参考实现自己写，跑通后再对照。
"""

import csv


# ---- 读 CSV：得到一个 list，每个元素是一部番的 dict ----
def load_rows(path):
    # 容错：WPS 可能把编码改坏，依次试 utf-8-sig / gbk / utf-8
    for enc in ("utf-8-sig", "gbk", "utf-8"):
        try:
            with open(path, encoding=enc, newline="") as f:
                return list(csv.DictReader(f))
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise SystemExit("读不了 CSV，请确认文件没被 WPS 改坏编码")


rows = load_rows("anime_ranking_full.csv")
# rows 就是 C 里的： Anime arr[N];
# arr[i] 是一部番(dict)，arr[i]["title"] 取字段


# ============ 题1：list 基础 ============
# 目标：打印总共多少部番，以及第一部番的名字
# C类比： printf("%d\n", N);  printf("%s\n", arr[0].title);
print("===== 题1：list 基础 =====")
print("总共", len(rows), "部番")            # len() = 数组长度
print("第一部：", rows[0]["title"])          # rows[0] 取第1个(dict)，["title"] 取字段
for i, r in enumerate(rows[:3]):             # enumerate 同时给 下标 和 元素
    print(f"  第{i + 1}部: {r['title']} (评分 {r['rating']})")


# ============ 题2：dict 取值 + 找最大 ============
# 目标：找出评分最高的一部，打印它的全部字段
# C类比： 遍历 arr，比较 arr[i].rating 找最大
print("\n===== 题2：dict 取值 + 找最大 =====")
best = rows[0]
for r in rows:
    if float(r["rating"] or 0) > float(best["rating"] or 0):
        best = r
print("评分最高的番：", best["title"], "评分", best["rating"])
print("它的全部信息：")
for k, v in best.items():                    # dict.items() 同时遍历 键和值
    print(f"  {k}: {v}")


# ============ 题3：推导式 · 过滤 ============
# 目标：用一行列表推导式，挑出「评分 >= 9.0」的所有番名
# C类比： for(i...) if(arr[i].rating>=9.0) collect(arr[i].title)
print("\n===== 题3：推导式过滤（评分>=9.0 的番名）=====")
high_rated = [r["title"] for r in rows if float(r["rating"] or 0) >= 9.0]
print(f"共 {len(high_rated)} 部评分≥9.0，前 8 个：")
print("  ", high_rated[:8])


# ============ 题4：推导式 + 排序 · Top5 ============
# 目标：弹幕率(danmaku_rate)最高的 5 部，打印 排名/名称/弹幕率
# 思路：先推导式复制出一份 list，再 sorted 按弹幕率从大到小取前5
print("\n===== 题4：推导式+sorted 弹幕率 Top5 =====")
ranked = sorted(
    [r for r in rows],                       # 推导式：复制一份 list
    key=lambda r: float(r["danmaku_rate"] or 0),
    reverse=True,                            # 从大到小
)[:5]
for r in ranked:
    print(f"  #{r['rank']} {r['title']}  弹幕率 {r['danmaku_rate']}")


# ============ 题5（选做）：set 去重统计 ============
# 目标：看看这些番的评分都有哪些不同的值（自动去重）
print("\n===== 题5：set 去重（评分有哪些不同值）=====")
ratings = set(r["rating"] for r in rows)     # 集合推导式：自动去重
print("出现的评分值（去重后，按大小排）：",
      sorted(ratings, key=lambda x: float(x or 0)))
