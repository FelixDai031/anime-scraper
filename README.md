# 🎬 二次元番剧排行榜爬虫 · anime-scraper

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

一个**真实可运行**的 Python 入门爬虫项目：抓取 B 站「番剧榜」与「少女乐队专题」排行榜，
输出 CSV 数据与可视化网页。代码带详细中文注释，适合新手对照学习，也是本人第一个开源项目。

> 技术栈：`Python 3` · `requests` · 纯前端 `HTML/JS` · `Git`

---

## ✨ 项目特性

- **真实数据**：调用 B 站公开 API，抓取真实番剧的排名、评分、追番数、播放量、弹幕数
- **弹幕率分析**：额外计算「弹幕率 = 弹幕数 / 追番数」，找出弹幕最密集的作品
- **本地化封面**：自动下载封面图到本地 `site/covers/`，避免公开网页被防盗链拦截
- **纯前端排序**：生成的网页支持「点表头按播放量 / 弹幕率排序」（无需后端服务器）
- **配套练习**：内含 Python 基础练习脚本（`list` / `dict` / `set` / 推导式）

---

## 📁 项目结构

```
anime-scraper/
├── anime_scraper_done.py     # 主爬虫：抓取番剧榜 → 输出 anime_ranking_full.csv
├── anime_scraper_band.py     # 少女乐队专题爬虫
├── csv_to_html.py            # 把 CSV 渲染为 site/index.html（含封面 + 排序）
├── csv_to_html_band.py       # 少女乐队版展示页生成
├── practice_list_dict.py     # Python 基础练习（list/dict/set/推导式）
├── anime_scraper.py          # 基础教学版（简化示例，适合入门先读）
├── anime_scraper_tutorial.py # 教程配套代码
├── requirements.txt          # 依赖：requests
├── PUSH_GUIDE.md             # 把本项目推送到 GitHub 的步骤记录
├── README.md
└── .gitignore
```

> 运行爬虫后还会生成 `*.csv`（数据）与 `site/`（网页），这些已被 `.gitignore` 忽略，
> 不会进仓库——克隆后先运行脚本即可重新生成。

---

## 🚀 快速开始

```bash
# 1. 安装依赖（只需 requests）
pip install -r requirements.txt

# 2. 运行主爬虫：抓取番剧榜 → 生成 anime_ranking_full.csv
python anime_scraper_done.py

# 3. 生成可视化网页：输出 site/index.html（含封面）
python csv_to_html.py

# 4. 查看网页：用浏览器打开 site/index.html
```

> 环境要求：Python 3.8+。Windows 下用 `python` 或 `py` 均可。
> CSV 默认以 `utf-8-sig` 编码保存，Excel / WPS 直接打开中文不乱码。

---

## 📊 数据字段说明

| 字段 | 含义 |
|------|------|
| `rank` | 排行榜名次 |
| `title` | 番剧名称 |
| `score` | 评分（满分 10） |
| `follow` | 追番人数 |
| `view` | 播放量 |
| `danmaku` | 弹幕总数 |
| `danmaku_rate` | 弹幕率 = `danmaku / follow` |

---

## 🧭 学习路线

这是本人「准大二暑期冲刺计划」中的一个环节，完整路线：

```
爬虫入门 → Python 专项 → C 语言专项 → Git/GitHub → 数据分析(NumPy)
→ 线性代数 → 神经网络入门 → UI 设计 → 整合为个人作品集
```

`practice_list_dict.py` 是 Python 基础练习；`anime_scraper.py` 是给新手先读的简化版。

---

## ⚖️ 爬虫伦理

- 本项目调用的是 **B 站公开 API**，仅用于学习，代码中已加 `time.sleep(1)` 限速
- 请勿高频请求、请勿将数据用于商业用途
- 爬取需登录的站点时，注意隐私与 `robots.txt`，控制频率

---

## 📄 许可

本项目以 [MIT License](LICENSE) 开源，仅供学习交流。番剧封面版权归原版权方所有。
