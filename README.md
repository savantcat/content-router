# 🔀 内容路由器 · Content Router

### 一份素材进去，多种成品出来。

写一次，改四次 —— 这是多平台创作者最耗命的地方。
内容路由器把「这篇该做成什么」变成一道**可计算**的问题：**11 维内容画像 → 智能推荐 → 一键调度**。

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-green.svg)](engine.py)
[![Deps](https://img.shields.io/badge/dependencies-zero-success.svg)](requirements.txt)

---

## 🚧 先说边界：它管「做成什么」，不管「发到哪」

这是两件事，别混：

| 你的问题 | 该用谁 |
|:---|:---|
| 这篇素材**该做成什么**？PPT、信息图、漫画还是短视频？ | **内容路由器**（本仓库） |
| 文章写完了，怎么改成**知乎版 / CSDN 版 / 小红书版**？ | [`content-creator-skills`](https://gitee.com/savantcat/content-creator-skills) 里的 `multi-platform-rewrite` |

- **路由器**推荐的是**跨媒介形态**——媒介变了：文字 → 图表 / 视频 / 漫画 / PPT / 可复用技能。
- **平台改写**是**同媒介换平台**——还是文章，只换读者、语气和钩子。

两者的关系是**上下游**：**先路由，再改写**。路由器告诉你这篇值不值得做成视频，改写技能负责把它写成视频号能发的样子。
本仓库**不碰**平台改写，那条线交给 `content-creator-skills`。

## 😩 你是不是也这样

同一份素材，公众号写完，知乎版、CSDN 版、小红书版**还得从头再改一遍**，一晚上没了。

但比这更亏的是**另一种累**：你花了两天把一篇深度长文做成 60 秒短视频，结果它根本没有叙事张力，讲出来像念说明书；
另一篇随手记的案例，其实天生就是一张信息图，你却把它硬写成了长文。

**你根本不知道这篇最适合做成什么。** 凭感觉选，一半力气花在错的形态上。

## ✨ 它怎么解决

```
一篇素材  ──▶  ① 11维画像  ──▶  ② 匹配推荐（带分数+理由）  ──▶  ③ 生成调度提示词
                字数/结构/密度           PPT ⭐⭐⭐                 交给你的 Agent 执行
                视觉潜力/叙事张力…        信息图 ⭐⭐⭐
                                        短视频脚本 ⭐⭐
```

**不是模板填空。** 先给内容做体检，再基于体检结果匹配形态，最后才谈转换。

## 📐 11 维内容画像

| 维度 | 判定 | 维度 | 判定 |
|:---|:---|:---|:---|
| ① 字数 | 短 / 中 / 长 | ⑦ 叙事张力 | 低 → 高 |
| ② 信息密度 | 有效信息点占比 | ⑧ 视觉叙事潜力 | 能否改编漫画 |
| ③ 结构类型 | 线性/并列/层级/碎片/流程 | ⑨ 信息图解潜力 | 核心观点 ≤8 个？ |
| ④ 视觉潜力 | 可否图表化 | ⑩ 实战可操作性 | 读者要不要动手 |
| ⑤ 深度等级 | 入门 / 中级 / 深度 | ⑪ 时效性 | 永久 → 时效 |
| ⑥ 情感色彩 | 客观/积极/反思/警示 | | |

## 🎯 6 种跨媒介输出形态

| 形态 | 适合什么内容 | 对应工作流 |
|:---|:---|:---|
| 📊 PPT 演示文稿 | 方法论、层级框架、教学 | `ppt-director-workflow` |
| 🎬 60 秒短视频脚本 | 热点、情绪型短内容 | `beat-plan-video-workflow` |
| 📊 信息图 | 并列对比、概念梳理 | `baoyu-infographic` |
| 🎨 漫画 / 视觉故事 | 案例、故事、有人物对白 | `baoyu-comic` |
| 📧 Newsletter | 深度 + 私密语感 | — |
| 🛠️ Skill 封装 | 方法论、可复用工作流 | — |

> 以上都是**媒介发生改变**的形态。公众号版、小红书版这类**同媒介换平台**的改写，不在本仓库职责内，
> 请用 [`content-creator-skills`](https://gitee.com/savantcat/content-creator-skills)。两件事分开做，才不会互相打架。

> 上表的「对应工作流」是 Hermes Agent 生态内的私有技能，**未随本仓库开源**。
> 但**不影响使用**：`route()` 只产出 `dispatch_prompt` 与目标技能名，你自己接上任意 Agent 或手工执行都行 —— 本仓库可独立运行，**零强制依赖**。

## 🚀 30 秒跑起来

```bash
git clone https://gitee.com/savantcat/content-router.git
cd content-router
python engine.py analyze README.md
```

输出：

```
📐 内容画像报告
========================================
字数:      1,551 字（中文）
密度:      ░░░░░░░░░░ 0.09
结构:      流程步骤
视觉潜力:  ███    高
深度等级:  入门
叙事张力:  █      低
情感色彩:  客观
实战性:    █      低
信息图解:  低
漫画潜力:  中
时效性:    永久

🏆 推荐输出（按适配度排序）
----------------------------------------
🥇 信息图           ⭐⭐  适配 44%  核心点10个+视觉高+图解低
🥈 PPT演示文稿       ⭐⭐  适配 38%  结构流程步骤+视觉高+内容入门
🥉 漫画/视觉故事       ⭐  适配 29%  漫画潜力中+张力低
4. 结构化Skill封装    ⭐  适配 29%  实战低+结构流程步骤+深度入门
5. 60秒短视频脚本      ⭐  适配 14%  张力低+情感客观+非时效
```

## 📦 批量路由：素材库 → 产出决策表

单篇分析只是玩具，**批量**才是刚需 —— 素材囤了一堆，一篇篇问太慢，也永远问不完。

```bash
python engine.py batch ./我的素材库 --out 产出决策表.md
```

一张表告诉你**每篇素材该做成什么**，直接当工作计划用（实测输出）：

| # | 素材 | 字数 | 结构 | 首推形态 | 适配度 | 次选 |
|:--|:--|--:|:--|:--|:--|:--|
| 1 | 知识星球_专享版.md | 863 | 并列观点 | **信息图** | 100% | PPT演示文稿 / 60秒短视频脚本 |
| 2 | 百家号_粘贴版.md | 1,010 | 碎片集合 | **信息图** | 67% | 60秒短视频脚本 / PPT演示文稿 |
| 3 | 公众号_AI客服国标MCP.md | 1,199 | 并列观点 | **60秒短视频脚本** | 57% | 信息图 / PPT演示文稿 |
| 4 | CSDN_技术版_MCP服务端实战.md | 1,243 | 并列观点 | **信息图** | 56% | PPT演示文稿 / 60秒短视频脚本 |

```
📦 扫描到 7 篇素材
**形态分布**：信息图 ×4、60秒短视频脚本 ×3
**最值得先做的 5 篇**：
- 知识星球_专享版.md → **信息图**（适配 100%）
- 百家号_粘贴版.md → **信息图**（适配 67%）
...
```

**适配度 = 判据命中率**（该形态得分 ÷ 该形态满分），跨形态可比。
首推 <40% 时它会直接告诉你「**这篇还没有明显适合的形态，别急着动手**」——不硬推，这是它可信的原因。

## 🧩 当库用

```python
from engine import profile_content, recommend_formats, format_profile_report, format_recommendation
from engine import ContentRouter

text = open("我的文章.md", encoding="utf-8").read()

profile = profile_content(text)
print(format_profile_report(profile))
recs = recommend_formats(profile)          # [{"format": ..., "score": ..., ...}]
print(format_recommendation(recs))

# 一键调度：为选中形态生成 dispatch 提示词 + 落盘 JSON 报告
router = ContentRouter(output_dir="./router_output")
result = router.route("我的文章.md", target_formats=["PPT演示文稿", "信息图"])
```

## 🔌 作为 MCP 服务调用

`server.py` 把引擎包成标准 **MCP server** —— 别人的 Agent 可以直接调这几个工具，不必读源码、不必抄公式。

```bash
pip install "mcp>=2.1"

python server.py                                # 本地 stdio（Claude Desktop / Cursor / 任意 MCP 客户端）
python server.py --transport http --port 8769   # 远程 streamable-http
python server.py --selftest                     # 不走协议，直接遍历打全部工具
```

| 工具 | 作用 |
|:---|:---|
| `analyze_content` | 11 维画像 + 形态推荐（一次给全，最常用） |
| `recommend_formats` | 只出排序推荐：适配度% + 命中的判据 |
| `get_dispatch_prompt` | 为指定形态生成调度提示词（交给任意 Agent 执行） |
| `list_formats` | 6 种跨媒介输出形态的定义与适用内容 |
| `profile_schema` | 11 维画像的口径与取值范围 |

客户端配置（stdio）：

```json
{ "mcpServers": { "content-router": { "command": "python", "args": ["server.py"] } } }
```

服务端为**纯计算、纯读**：5 个工具的四个 annotation hint 全部声明（`readOnlyHint=true` / `destructiveHint=false` / `idempotentHint=true` / `openWorldHint=false`），不写盘、不发起任何外部请求、不需要 API Key。

## 💻 命令行

```bash
# 分析 + 推荐
python engine.py analyze 我的文章.md

# 分析 + 推荐 + 调度
python engine.py route 我的文章.md --formats PPT演示文稿,信息图,60秒短视频脚本

# 批量：整个素材目录 → 产出决策表（最实用的一步）
python engine.py batch ./我的素材库 --top 20 --out 产出决策表.md
```

## 🛡️ 已知风险与规避

| 风险 | 规避 |
|:---|:---|
| 画像不准 | 支持手动修正画像维度后重新推荐 |
| 推荐偏差 | 永远给多个候选 + 理由，把决定权交回给你 |
| 跨 Skill 调度 | 按优先级排列，不可用的分支跳过并提示 |
| 长文超 token | 自动分段摘要后再画像 |

## 📁 项目结构

```
engine.py          单文件核心引擎（画像 / 推荐 / 调度 / CLI），纯标准库
server.py          MCP 服务端（5 个工具，双通道 stdio / streamable-http）
server.json        MCP 元数据（官方 Registry 格式）
SKILL.md           Agent 技能定义 + 完整 API 说明
skill-card.md      技能卡片（用途 / 输出 / 风险）
_meta.json         元信息
```

## 🔗 相关仓库

- [`content-creator-skills`](https://gitee.com/savantcat/content-creator-skills) —— 平台改写三件套（多平台改写 / 去 AI 味 / 旧文变选题），负责**「发到哪」**。
- [`savantcat-portfolio`](https://gitee.com/savantcat/savantcat-portfolio) —— 全部开源项目索引。

## 📄 License

MIT — 见 [LICENSE](LICENSE)。

## 👤 作者

合尘猫 · AI 落地实践 · <https://savantcat.cn>
