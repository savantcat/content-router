# 内容路由器

一份素材进去，多种成品出来。11维内容画像 → 智能推荐 → 调度执行。

## 快速使用

```bash
# 分析一篇文章
python engine.py analyze 我的文章.md

# 分析+指定输出格式
python engine.py route 我的文章.md --formats PPT,信息图,公众号文章
```

## 特性

- ✅ 11维内容画像（字数/结构/密度/潜力等）
- ✅ 8种输出形态自动推荐
- ✅ 智能匹配算法（不是随机或模板填空）
- ✅ 兼容现有 Hermes Skill 生态
- ✅ 支持手动指定输出格式

## 输出的8种形态

| 形态 | 对应Skill | 适合内容 |
|:----|:---------|:---------|
| 📊 PPT演示文稿 | ppt-director-workflow | 方法论/层级框架 |
| 📱 小红书图文 | content-matrix | 短评/情绪/感悟 |
| 📝 公众号文章 | hechenmao-writing-framework | 深度分析/叙事 |
| 🎬 60秒短视频脚本 | beat-plan-video-workflow | 热点/情绪/短内容 |
| 📊 信息图 | baoyu-infographic | 概念梳理/对比 |
| 🎨 漫画/视觉故事 | baoyu-comic | 案例/故事 |
| 📧 Newsletter | — | 深度+私密语感 |
| 🛠️ Skill封装 | — | 方法论/工作流 |

## 许可证

MIT
