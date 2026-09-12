# 🔀 内容路由器 · Content Router

### 一份素材进去，多种成品出来。

写一次，改四次 —— 这是多平台创作者最耗命的地方。
内容路由器把「这篇该做成什么」变成一道**可计算**的问题：**11 维内容画像 → 智能推荐 → 一键调度**。

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-green.svg)](engine.py)
[![Deps](https://img.shields.io/badge/dependencies-zero-success.svg)](requirements.txt)

---

## 😩 你是不是也这样

公众号写完了，知乎版、CSDN 版、小红书版、PPT 版**还得从头再改一遍**，一晚上没了。

更冤的是：**你根本不知道这篇最适合做成什么。**
有的内容天生适合做 PPT，有的适合一张信息图讲完，有的只适合压成 6 张卡片 —— 凭感觉选，一半力气花在错的形态上。

## ✨ 它怎么解决

```
一篇素材  ──▶  ① 11维画像  ──▶  ② 匹配推荐（带分数+理由）  ──▶  ③ 生成调度提示词
                字数/结构/密度           PPT ⭐⭐⭐                 交给你的 Agent 执行
                视觉潜力/叙事张力…        信息图 ⭐⭐⭐
                                        公众号 ⭐⭐
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

## 🎯 8 种输出形态

| 形态 | 适合什么内容 | 对应工作流 |
|:---|:---|:---|
| 📊 PPT 演示文稿 | 方法论、层级框架、教学 | `ppt-director-workflow` |
| 📱 小红书图文 | 短评、情绪、个人感悟 | `content-matrix` |
| 📝 公众号文章 | 深度分析、叙事、复盘 | `hechenmao-writing-framework` |
| 🎬 60 秒短视频脚本 | 热点、情绪型短内容 | `beat-plan-video-workflow` |
| 📊 信息图 | 并列对比、概念梳理 | `baoyu-infographic` |
| 🎨 漫画 / 视觉故事 | 案例、故事、有人物对白 | `baoyu-comic` |
| 📧 Newsletter | 深度 + 私密语感 | — |
| 🛠️ Skill 封装 | 方法论、可复用工作流 | — |

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
📐 内容画像报告: README.md
字数:      1,842 字
结构:      并列观点
视觉潜力:  ████████░░ 高
实战性:    ████████░░ 高

🏆 推荐输出（按适配度排序）
1. 信息图       ⭐⭐⭐  结构化信息+核心点≤8
2. 公众号文章   ⭐⭐    深度分析+字数充裕
```

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

## 💻 命令行

```bash
# 分析 + 推荐
python engine.py analyze 我的文章.md

# 分析 + 推荐 + 调度
python engine.py route 我的文章.md --formats PPT演示文稿,信息图,公众号文章
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
SKILL.md           Agent 技能定义 + 完整 API 说明
skill-card.md      技能卡片（用途 / 输出 / 风险）
_meta.json         元信息
```

## 📄 License

MIT — 见 [LICENSE](LICENSE)。

## 👤 作者

合尘猫 · AI 落地实践 · <https://savantcat.cn>
