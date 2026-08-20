# -*- coding: utf-8 -*-
"""把 band_ranking.csv 渲染成带【本地封面图】的 HTML 表格，输出到 site_band/ 用于部署
封面会从 B站图床下载到 site_band/covers/，避免公开页被防盗链挡住。
运行： cd anime-scraper && py csv_to_html_band.py
"""
import csv
import os
import requests

SRC = "band_ranking.csv"
OUT_DIR = "site_band"
COVERS_DIR = os.path.join(OUT_DIR, "covers")
OUT = os.path.join(OUT_DIR, "index.html")

HEADERS_REQ = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Referer": "https://www.bilibili.com",
}

os.makedirs(COVERS_DIR, exist_ok=True)

with open(SRC, encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    cols = reader.fieldnames

def fmt(n):
    try:
        return f"{int(float(n)):,}"
    except (ValueError, TypeError):
        return n

cn = {
    "rank": "排名", "title": "番剧名称", "rating": "评分",
    "follow": "追番数", "danmaku": "弹幕数", "view": "播放量",
    "cover": "封面", "type": "类型", "url": "链接",
}
headers = [cn.get(c, c) for c in cols]

def local_cover(url, idx):
    """下载封面到本地，返回可访问路径（失败则返回原外链兜底）"""
    if not url:
        return url
    for ext in ("jpg", "png", "webp"):
        if os.path.exists(os.path.join(COVERS_DIR, f"cover_{idx}.{ext}")):
            return f"covers/cover_{idx}.{ext}"
    try:
        r = requests.get(url, headers=HEADERS_REQ, timeout=15)
        if r.status_code == 200 and len(r.content) > 500:
            if r.content[:3] == b"\xff\xd8\xff":
                ext = "jpg"
            elif r.content[:4] == b"\x89PNG":
                ext = "png"
            elif r.content[:4] == b"RIFF" and r.content[8:12] == b"WEBP":
                ext = "webp"
            else:
                ext = "jpg"
            with open(os.path.join(COVERS_DIR, f"cover_{idx}.{ext}"), "wb") as imgf:
                imgf.write(r.content)
            return f"covers/cover_{idx}.{ext}"
    except Exception:
        pass
    return url

html = [
    "<!DOCTYPE html>", "<html lang='zh-CN'>", "<head>",
    "<meta charset='utf-8'>",
    "<meta name='viewport' content='width=device-width, initial-scale=1'>",
    "<title>少女乐队番 人气排行榜</title>", "<style>",
    "body{font-family:-apple-system,'Segoe UI',Roboto,'Microsoft YaHei',sans-serif;margin:0;background:#f7f8fa;color:#222;}",
    ".wrap{max-width:1040px;margin:24px auto;padding:0 16px;}",
    "h1{font-size:20px;margin:0 0 4px;}",
    ".sub{color:#888;font-size:13px;margin-bottom:16px;}",
    "table{border-collapse:collapse;width:100%;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.08);}",
    "th,td{padding:10px 12px;text-align:left;font-size:14px;border-bottom:1px solid #eee;}",
    "th{background:#fb7299;color:#fff;position:sticky;top:0;font-weight:600;}",
    "tbody tr:nth-child(even){background:#fafafa;}",
    "tbody tr:hover{background:#fff0f5;}",
    "td.num{text-align:right;font-variant-numeric:tabular-nums;}",
    "a{color:#fb7299;text-decoration:none;}",
    "a:hover{text-decoration:underline;}",
    ".rating{color:#fb7299;font-weight:600;}",
    "</style></head><body><div class='wrap'>",
    "<h1>少女乐队番 人气排行榜</h1>",
    f"<div class='sub'>共 {len(rows)} 部 · 按 B站播放量排序 · 由爬虫生成</div>",
    "<table><thead><tr>",
]
for h in headers:
    html.append(f"<th>{h}</th>")
html.append("</tr></thead><tbody>")

for idx, r in enumerate(rows):
    html.append("<tr>")
    for c in cols:
        v = r[c]
        if c == "url":
            html.append(f"<td><a href='{v}' target='_blank'>打开</a></td>")
        elif c == "cover":
            src = local_cover(v, idx)
            html.append(f"<td><img src='{src}' width='64' style='border-radius:4px' loading='lazy' onerror=\"this.onerror=null;this.src='{v}'\"></td>")
        elif c in ("follow", "danmaku", "view"):
            html.append(f"<td class='num'>{fmt(v)}</td>")
        elif c == "rating":
            html.append(f"<td class='rating'>{v}</td>")
        else:
            html.append(f"<td>{v}</td>")
    html.append("</tr>")

html.append("</tbody></table></div></body></html>")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(html))

print(f"已生成 {OUT}，{len(rows)} 行；封面存于 {COVERS_DIR}")
