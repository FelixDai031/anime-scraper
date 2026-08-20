# 把 anime-scraper 推上 GitHub（Day4 最后一步）

本地仓库已经建好（`git init` + 首次 commit 完成），只剩「建远程仓库 + push」两步。
这两步需要你自己的 GitHub 账号和凭证，我在本机帮不了——按下面照做即可。

---

## 步骤 1：GitHub 网页建仓库（空仓库）

1. 登录 https://github.com （用 `daihaotian874@gmail.com`）
2. 右上角 **+** → **New repository**
3. Repository name 填：`anime-scraper`
4. 选 **Public**（公开，想要第一个公开仓库）或 Private 都行
5. ⚠️ **不要**勾选 "Add a README file" / "Add .gitignore" / "Add a license"
   （保持空仓库，否则远程有初始 commit，push 会冲突）
6. 点 **Create repository**

建好后页面会显示一个地址，形如：
`https://github.com/FelixDai031/anime-scraper.git`

---

## 步骤 2：生成 Personal Access Token（只需一次）

> 你没配 SSH 密钥，所以走 **HTTPS + Token**。密码栏填的是 token，不是 GitHub 登录密码。

1. 右上头像 → **Settings**
2. 左侧最底 **Developer settings** → **Personal access tokens** → **Tokens (classic)**
3. **Generate new token (classic)**
4. Note 填：`anime-scraper-push`
5. Expiration 选 `90 days`（或自选）
6. 勾选 **repo**（这一组全勾上，管仓库读写）
7. 拉到底 **Generate token**
8. 复制那串 `ghp_xxxxxxxx` —— **只显示这一次，存到备忘录**

---

## 步骤 3：本机 push（在 VSCode 终端 / Git Bash 执行）

```bash
# 把本地 master 改名为 main，对齐 GitHub 默认分支（建议做）
git branch -M main

# 关联远程仓库（URL 换成你刚才建的那个）
git remote add origin https://github.com/FelixDai031/anime-scraper.git

# 首次推送并设置上游
git push -u origin main
```

弹窗要账号密码时：
- 用户名：`FelixDai031`
- 密码栏：**粘贴刚才的 token**（不是 GitHub 登录密码）

> `credential.helper=manager` 已配好，token 会缓存，下次 push 不用再输。

---

## 验证

刷新 https://github.com/FelixDai031/anime-scraper ，能看到 12 个文件
（`.gitignore`、README.md、各 `.py`、两个排行页 html 等）即成功。

如果 push 报 `failed to push`，把完整红色报错发我，我帮你对着调。
