# -*- coding: utf-8 -*-
"""把 anime_ranking_full.csv 渲染成带【本地封面图】的 HTML 表格，输出到 site/ 用于部署
封面会从 B站图床下载到 site/covers/，避免公开页被防盗链挡住。
运行： cd anime-scraper && py csv_to_html.py
"""
import csv
import os
import re
import hashlib
import requests

SRC = "anime_ranking_full.csv"
OUT_DIR = "site"
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
    "danmaku_rate": "弹幕率", "cover": "封面", "type": "类型", "url": "链接",
}
headers = [cn.get(c, c) for c in cols]

# 哪些列可点表头排序：num=数值(去千分位比较), str=文本, none=不排序
SORTABLE = {
    "rank": "num", "rating": "num", "follow": "num", "danmaku": "num",
    "view": "num", "danmaku_rate": "num", "title": "str", "type": "str",
    "cover": "none", "url": "none",
}

def local_cover(url, idx):
    """下载封面到本地，用「图片网址哈希」命名，保证同一部番永远对应同一张图
    （不依赖行号，避免榜单顺序变化导致封面错位）。失败则返回原外链兜底。"""
    if not url:
        return url
    key = hashlib.md5(url.encode("utf-8")).hexdigest()[:16]
    for ext in ("jpg", "png", "webp"):
        if os.path.exists(os.path.join(COVERS_DIR, f"{key}.{ext}")):
            return f"covers/{key}.{ext}"
    try:
        r = requests.get(url, headers=HEADERS_REQ, timeout=15)
        if r.status_code == 200 and len(r.content) > 500:
            # 按文件头判断真实格式，避免把 PNG 存成 .jpg 导致裂图
            if r.content[:3] == b"\xff\xd8\xff":
                ext = "jpg"
            elif r.content[:4] == b"\x89PNG":
                ext = "png"
            elif r.content[:4] == b"RIFF" and r.content[8:12] == b"WEBP":
                ext = "webp"
            else:
                ext = "jpg"
            with open(os.path.join(COVERS_DIR, f"{key}.{ext}"), "wb") as imgf:
                imgf.write(r.content)
            return f"covers/{key}.{ext}"
    except Exception:
        pass
    return url

html = [
    "<!DOCTYPE html>", "<html lang='zh-CN'>", "<head>",
    "<meta charset='utf-8'>",
    "<meta name='viewport' content='width=device-width, initial-scale=1'>",
    "<title>二次元番剧排行榜</title>", "<style>",
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
    "th.sortable{cursor:pointer;user-select:none;}",
    "th.sortable:hover{filter:brightness(1.08);}",
    "th .arrow{font-size:11px;margin-left:4px;}",
    "</style></head><body><div class='wrap'>",
    "<h1>二次元番剧排行榜（B站周榜）</h1>",
    f"<div class='sub'>共 {len(rows)} 部 · 数据源 api.bilibili.com · 由爬虫生成</div>",
    "<table><thead><tr>",
]
for c, h in zip(cols, headers):
    stype = SORTABLE.get(c, "none")
    if stype in ("num", "str"):
        html.append(f"<th class='sortable' data-type='{stype}' onclick='sortBy(this)'>{h}<span class='arrow'></span></th>")
    else:
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

html.append("</tbody></table></div>")
html.append("""
<script>
function sortBy(th){
  var table = th.closest('table');
  var tbody = table.tBodies[0];
  var rows = Array.from(tbody.rows);
  var idx = Array.from(th.parentNode.children).indexOf(th);
  var type = th.getAttribute('data-type');
  var asc = th.getAttribute('data-dir') !== 'asc';   // 第一次点升序，再点降序
  rows.sort(function(a,b){
    var va = a.children[idx].textContent.trim();
    var vb = b.children[idx].textContent.trim();
    if(type === 'num'){
      va = parseFloat(va.replace(/,/g,'')) || 0;
      vb = parseFloat(vb.replace(/,/g,'')) || 0;
      return asc ? va - vb : vb - va;
    } else {
      return asc ? va.localeCompare(vb,'zh') : vb.localeCompare(va,'zh');
    }
  });
  rows.forEach(function(r){ tbody.appendChild(r); });
  Array.from(th.parentNode.children).forEach(function(h){
    h.removeAttribute('data-dir');
    var ar = h.querySelector('.arrow'); if(ar) ar.textContent='';
  });
  th.setAttribute('data-dir', asc ? 'asc' : 'desc');
  var arrow = th.querySelector('.arrow'); if(arrow) arrow.textContent = asc ? '▲' : '▼';
}
</script>
</body></html>""")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(html))

print(f"已生成 {OUT}，{len(rows)} 行；封面存于 {COVERS_DIR}")
