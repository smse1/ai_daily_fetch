# AI Daily Watch

一个可以直接放到 GitHub 的小项目：**每日抓取最新 AI 发展动态，自动生成日报，并把结果回写到仓库。**

适合用来做：
- 每日跟踪大模型公司官方动态
- 跟踪 AI 行业新闻与研究博客
- 给自己做一个长期的 AI 信息看板
- 后续扩展成邮件 / 飞书 / 企业微信推送机器人

---

## 1. 项目功能

当前版本已经包含：
- 多来源抓取（官方博客 + 行业媒体）
- 自动去重
- 本地 JSON 存储
- 每日 Markdown 日报生成
- GitHub Actions 定时任务（每天自动运行）
- 运行失败时不会整仓库崩掉，单个来源失败只告警

默认来源包括：
- OpenAI News
- Anthropic News
- Google DeepMind Blog
- Google Research Blog
- Hugging Face Blog
- MIT Technology Review AI
- TechCrunch AI

---

## 2. 项目结构

```bash
ai-daily-watch/
├─ .github/
│  └─ workflows/
│     └─ daily.yml           # GitHub Actions 每日自动运行
├─ config/
│  └─ sources.json          # 抓取源配置
├─ data/
│  ├─ articles.json         # 累计文章数据
│  └─ last_run.json         # 最近一次运行统计
├─ reports/
│  └─ 2026-04-05.md         # 每日生成的日报
├─ src/
│  ├─ __init__.py
│  ├─ fetch.py              # 抓取逻辑（RSS + HTML）
│  ├─ digest.py             # 日报生成逻辑
│  └─ utils.py              # 工具函数
├─ .gitignore
├─ main.py                  # 项目入口
├─ requirements.txt
└─ README.md
```

---

## 3. 本地运行

### 安装依赖

```bash
pip install -r requirements.txt
```

### 执行抓取

```bash
python main.py
```

运行后会生成：
- `data/articles.json`
- `data/last_run.json`
- `reports/当天日期.md`

---

## 4. 上传到 GitHub

先在 GitHub 上新建一个空仓库，比如：`ai-daily-watch`

然后在本地项目目录执行：

```bash
git init
git branch -M main
git add .
git commit -m "init: AI daily watch project"
git remote add origin 你的仓库地址
git push -u origin main
```

---

## 5. GitHub Actions 自动每日运行

项目已经自带：

```yaml
.github/workflows/daily.yml
```

作用：
- 每天定时执行 `python main.py`
- 自动提交更新后的 `data/` 和 `reports/`
- 你也可以手动点击 `Run workflow` 立即执行

默认定时是 **每天 UTC 01:00**，你可以自行改 cron。

常用时间换算：
- 新加坡时间 09:00 = UTC 01:00
- 北京时间 09:00 = UTC 01:00

---

## 6. 如何新增抓取源

编辑 `config/sources.json`。

### RSS 示例

```json
{
  "name": "Example RSS",
  "type": "rss",
  "url": "https://example.com/feed.xml",
  "limit": 10
}
```

### HTML 页面示例

```json
{
  "name": "Example Blog",
  "type": "html",
  "url": "https://example.com/blog/",
  "base_url": "https://example.com",
  "include_patterns": ["/blog/"],
  "exclude_patterns": ["/blog/"],
  "limit": 10
}
```

说明：
- `include_patterns`：链接路径中必须包含这些片段之一
- `exclude_patterns`：用于排除频道首页本身，避免把栏目页当文章抓进来

---

## 7. 后续可以继续增强的方向


### 方向一：中文总结
接入大模型 API，把每条新闻自动总结成 1~3 句中文。

### 方向二：消息推送
抓取后把日报推送到：
- 邮件
- 飞书机器人
- 企业微信机器人
- Telegram Bot
- Discord Webhook

### 方向三：更强筛选
给标题打标签，例如：
- 模型发布
- 融资并购
- 开源模型
- 安全政策
- Agent
- 多模态
- 芯片 / 基础设施

### 方向四：前端展示
后续可以加一个 Streamlit 页面，把历史日报做成可搜索的 AI 情报站。

---

## 8. 注意事项

- 某些站点页面结构变化后，HTML 抓取规则可能需要调整。
- GitHub Actions 的定时任务在仓库长期无活动时，可能会被 GitHub 暂停，需要重新启用。
- 如果某些媒体限制爬虫访问，可以优先使用 RSS 源，稳定性更高。

---

