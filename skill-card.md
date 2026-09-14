## Description: <br>
一份素材进去，多种成品出来。输入文章/笔记/想法 → 11维内容画像 → 推荐跨媒介输出形态（PPT/信息图/漫画/短视频脚本/Newsletter/Skill封装）+ 适配度打分 → 生成调度提示词；支持批量扫描素材目录，输出「每篇该做成什么」的产出决策表。平台改写（公众号版/小红书版）交给 content-creator-skills，本技能只管「做成什么」。 <br>
This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
合尘猫 <br>

### License/Terms of Use: <br>
MIT <br>

## Use Case: <br>
素材/笔记库里积压了大量内容、却从没变成过成品的 AI 工作者。单篇给适配度推荐，批量给整库产出决策表。不是模板填空——11维内容画像 + 适配度归一打分（判据命中率），弱匹配如实提示不硬推。 <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: 画像不准导致推荐偏差（启发式判断） <br>
Mitigation: 支持手动修正画像维度后重新推荐 <br>

Risk: 跨Skill调度时部分分支不可用 <br>
Mitigation: 按优先级排列，不可用跳过并提示 <br>

## Skill Output: <br>
**Output Type(s):** 内容画像报告, 格式推荐, 多形态内容成品 <br>
**Output Format:** Markdown报告 + 对应格式产出文件 <br>
