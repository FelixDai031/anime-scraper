# B站番剧排行榜爬虫（二次元主题 · 第一个爬虫项目）

这是一个**真实能跑**的入门爬虫，用来抓 B站「番剧 / 国创」排行榜，
把排名、评分、追番数、弹幕数存成 CSV，并打印评分 Top10。

代码在 `anime_scraper.py`，每个函数都有中文注释，建议对照着读。

---

## 一、在你自己电脑上跑起来（5 步）

> 这个环境里我已经帮你跑通验证过了，数据是真的。你本机照下面做就行。

**1. 装 Python（如果还没装）**
- 去 https://www.python.org/downloads/ 下最新版
- 安装时**务必勾选 "Add python.exe to PATH"**（最下面那行小字）
- 装完打开 `cmd`（Win+R → 输入 cmd → 回车），输入 `python --version` 看到版本号就成功

**2. 把项目文件夹放到本地**
- 把整个 `anime-scraper` 文件夹复制到比如 `D:\code\anime-scraper`

**3. 打开终端进到目录**
```bat
cd D:\code\anime-scraper
```

**4. 装依赖（只需要 requests 这一个库）**
```bat
pip install -r requirements.txt
```

**5. 运行**
```bat
python anime_scraper.py
```
跑完会生成 `anime_ranking.csv`，用 Excel 双击就能打开看。

---

## 二、代码地图（对照文件看）

| 函数 | 作用 | 对应知识点 |
|------|------|-----------|
| `fetch_ranking()` | 发 HTTP 请求拿 JSON | `requests.get` / 参数 / 状态码 |
| `parse_item()` | 从一大坨数据里挑字段 | 字典取值 / 类型转换 / 异常处理 |
| `save_to_csv()` | 写 CSV 文件 | 文件 IO / `csv` 模块 / 编码 |
| `analyze()` | 按评分排 Top10 | `sorted` + `lambda` 排序 |
| `main()` | 把上面串起来 | 程序入口 / 循环 / 流程控制 |

**必记的一个点**：`if __name__ == "__main__":` 表示"只有直接运行这个文件时才执行"，
被别的文件 import 时不会跑——这是 Python 项目的标准写法。

---

## 三、改着玩（练手）

1. 改 `main()` 里的 `[("番剧", 1), ("国创", 4)]`，只抓一种试试
2. 把 `analyze()` 改成按「追番数 follow」排 Top10
3. 加一列「弹幕率 = danmaku / follow」，看看哪部番弹幕最密
4. 试试 `day=7` 抓周榜（改 `fetch_ranking` 的默认参数）

---

## 四、下一步往哪走（接上之前聊的路线）

- **阶段三（动态页）**：爬 B站视频的**弹幕**（需要抓 `api.bilibili.com/x/v1/dm/list.so` 接口，是 XML）
- **阶段四（框架）**：把逻辑改写成 Scrapy 爬虫，练工程化
- **AI 线**：用这份 CSV 做番剧推荐（协同过滤），或按 `badge`/评分做简单分类
- **UI 线**：用 HTML/CSS 把这个 CSV 做成一个「番剧排行榜展示页」

---

## 五、规矩（爬取红线）

- 这是**公开 API**，只做学习用途，别高频狂刷（代码里已 `time.sleep(1)` 限速）
- 别把数据拿去商用
- 真要爬需要登录的站点（如 Pixiv），用 cookie，控制频率，尊重 robots.txt
