# 👋 欢迎使用 md2red：让 AI 也能发漂亮的小红书

**md2red** 是一个专为自媒体打造的开源排版神器。它的核心愿景是：**让包括 AI Agent 在内的所有创作者，都能极简地把 Markdown 转化为高颜值的小红书（3:4比例）图文卡片。** 

不再需要繁杂的排版工具，只需一段 Markdown 代码，即可生成多页排版精美的长图和独立卡片！

---

## 🌟 核心特性与 Markdown 渲染能力 (Features)

为了证明 md2red 的强大，这篇文档本身就是一个包含所有常规 Markdown 元素的**多功能展示（Placeholder）**。我们希望通过这篇文档，直观地介绍本项目的各种排版能力。

### 1. 基础文本样式 (Text Typography)
在这里随意使用 *斜体强调 (Italic)*、**粗体高亮 (Bold)**，或是具有强烈视觉冲击的 ***粗斜体 (Bold Italic)***。对于过时的信息，甚至可以加上 ~~删除线 (Strikethrough)~~。

### 2. 列表排版 (Lists)

**我们主要解决的痛点（无序列表）：**
- **排版极度耗时**：每次发小红书都要手动调整字号、对齐和间距。
- **AI 无法直出图片**：大模型输出的大多是 Markdown 纯文本。
  - *子节点支持*：即使是多级嵌套列表，也能完美解析并在卡片中优雅呈现。

**我们的后续演进目标（有序列表）：**
1. 提供高度可定制的精美主题（例如: `notion`, `xiaohongshu`, `dark_mode`）。
2. 支持更强大的语法，包含深色模式护眼切换。
3. 完美的自动化分页和长图智能截断，保证内容不会卡在奇怪的边界。

### 3. 代码高亮 (Code Blocks)

作为连接 AI 与开发者的工具，代码展示是必不可少的。您可以高亮行内特定的关键词，比如 `md2red.py` 和 `PySide6`，也可以非常优雅地展示多行级别的脚本：

```python
# md2red 核心思想：Markdown in, Images out
def generate_redbook_cards(markdown_text: str, theme: str = "notion"):
    parser = MarkdownParser(theme=theme)
    # 自动处理分页，生成 1080x1440 的标准卡片
    images = parser.render_to_images(markdown_text, ratio="3:4")
    return images

print("AI 也可以优雅地做自媒体运营！")
```

### 4. 引用块 (Blockquotes)

引经据典，是高质量深度笔记的灵魂。我们可以轻松地在卡片中插入名人名言，并赋予它优美的排版容器：

> "未来的自媒体红利，一定属于那些能用代码自动化产生优雅内容的 AI 智能体。"
>
> —— *The Future of AI Agents in Creators Economy*

### 5. 表格与对比 (Tables)

通过表格来展示各种组件或方案的对比。来看看我们当前的主题支持情况：

| 主题名称 (Theme) | 适用场景 | 分页支持 | 当前状态 |
| :--- | :--- | :---: | ---: |
| `notion` | 极简风、知识干货分享 | ✅ | 稳定 |
| `xiaohongshu`| 日常分享、种草集锦 | ✅ | 稳定 |
| `dark_mode` | 极客范、程序员夜间风格 | ✅ | 测试中 |
| `wechat` | 公众号同步、沉稳阅读 | ⏳ | 开发中 |

---

## 🚀 为什么 AI Agent 极度需要 md2red？

随着大语言模型的爆发，AI 能够轻易写出高转化率的文章和脚本。但在此之前，它们却**无法自己把这些文案变成小红书上高点击率的漂亮卡片**。发布端往往需要人类来充当“复制粘贴”和排版的工具人。

现在，AI Agent 只需要在底层静默地执行一条命令：

```bash
python3 md2red.py input.md --theme xiaohongshu
```

就能直接把本地的 `.md` 内容，拆解成一张张原生适配屏幕的 `1.png`, `2.png`... 随即自动分发到社交平台！

### 进一步探索

欢迎通过超级链接 [访问我们的 GitHub 仓库](https://github.com/nowork-studio/md2red) 来提交 Pull Request。

![md2red Placeholder Image 示意图](https://via.placeholder.com/800x400/eeeeee/333333?text=Markdown+to+RedBook+Cards)

---
**🌟 立即开始体验吧！让纯文本也拥有呼吸感。**
