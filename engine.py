#!/usr/bin/env python3
"""
内容路由器 — 核心引擎
输入素材 → 11维内容画像 → 推荐最优输出形态 → 调度执行
"""

import re
import json
import os
import datetime
from pathlib import Path
from typing import Optional


# ── 维度常量 ──────────────────────────────────────────

STRUCTURE_TYPES = ["线性叙事", "并列观点", "层级框架", "碎片集合", "流程步骤"]
DEPTH_LEVELS = ["入门", "中级", "深度"]
EMOTION_TYPES = ["客观", "积极", "反思", "警示"]


# ── 内容画像 ──────────────────────────────────────────

def profile_content(text: str) -> dict:
    """11维内容画像分析"""
    if not text or not text.strip():
        return {"error": "空内容"}

    # ① 字数
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    total_chars = len(text.strip())
    
    if chinese_chars < 500:
        word_level = "短"
    elif chinese_chars < 3000:
        word_level = "中"
    else:
        word_level = "长"

    # ② 信息密度：有效信息点（数字/专名/结论句）占比
    info_points = len(re.findall(r'\d+[.%]?|\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text))
    sentences = len(re.split(r'[。！？\n]', text))
    info_density = min(1.0, info_points / max(sentences, 1) / 3)

    # ③ 结构类型判定
    # 检测是否是列表/编号/小标题结构
    has_bullets = bool(re.search(r'^[*-]\s', text, re.MULTILINE))
    has_numbers = bool(re.search(r'^\d+[\.\、\．]', text, re.MULTILINE))
    has_headers = bool(re.search(r'^#{1,4}\s', text, re.MULTILINE))
    has_steps = bool(re.search(r'步骤|第[一二三四五六七八九十]步|流程|Stage', text))
    has_story = bool(re.search(r'有一天|曾经|有一次|记得|那年|当时|突然', text))

    if has_steps:
        structure_type = "流程步骤"
    elif has_bullets or has_numbers:
        structure_type = "并列观点"
    elif has_headers and chinese_chars > 1000:
        structure_type = "层级框架"
    elif has_story:
        structure_type = "线性叙事"
    else:
        structure_type = "碎片集合"

    # ④ 视觉潜力：包含可图表化元素
    visual_keywords = ['对比', '关系', '趋势', '结构', '流程', '分类', '组成', '阶段',
                       'vs', 'VS', '比例', '分布', '增长', '下降', '变化']
    visual_score = sum(1 for kw in visual_keywords if kw in text) / len(visual_keywords)
    visual_potential = "高" if visual_score > 0.15 else ("中" if visual_score > 0.05 else "低")

    # ⑤ 深度等级
    depth_keywords = ['本质上', '底层', '原理', '机制', '规律', '范式', '逻辑', '框架',
                      '系统', '结构', '本质', '核心矛盾']
    depth_score = sum(1 for kw in depth_keywords if kw in text)
    depth_level = "深度" if depth_score > 5 else ("中级" if depth_score > 2 else "入门")

    # ⑥ 情感色彩
    positive_words = ['好', '棒', '牛', '厉害', '惊喜', '收获', '成功', '值得', '推荐']
    reflective_words = ['反思', '遗憾', '可惜', '没想到', '原来', '教训', '错误', '问题']
    warning_words = ['注意', '警惕', '避免', '千万别', '危险', '不要', '小心', '提醒']

    pos_score = sum(1 for w in positive_words if w in text)
    ref_score = sum(1 for w in reflective_words if w in text)
    warn_score = sum(1 for w in warning_words if w in text)

    if warn_score > pos_score and warn_score > ref_score:
        emotion = "警示"
    elif ref_score > pos_score:
        emotion = "反思"
    elif pos_score > 3:
        emotion = "积极"
    else:
        emotion = "客观"

    # ⑦ 叙事张力：矛盾/冲突/转折检测
    tension_words = ['但是', '然而', '反而', '出乎意料', '没想到', '却', '可悲', '讽刺',
                     '矛盾', '冲突', '两难', '纠结', '挣扎']
    tension_score = sum(1 for w in tension_words if w in text)
    narrative_tension = "高" if tension_score > 5 else ("中" if tension_score > 2 else "低")

    # ⑧ 视觉叙事潜力（漫画改编）：有人物+对话+场景
    has_characters = bool(re.search(r'[我你他她它]说|人物|角色|对话|场景|地方|来到|走进', text))
    comic_potential = "高" if (has_characters and tension_score > 3) else ("中" if has_characters else "低")

    # ⑨ 信息图解潜力：核心观点数估计
    # 根据段落数和标题数估算核心观点数
    para_count = len(re.split(r'\n\n+', text.strip()))
    core_points = min(para_count, 10) if has_headers else min(para_count // 2 + 1, 8)
    infographic_potential = "高" if core_points <= 8 else "低"

    # ⑩ 实战可操作性
    action_keywords = ['打开', '点击', '输入', '设置', '创建', '下载', '安装', '运行',
                       '复制', '粘贴', '按以下', '步骤', '方法一', '方法二', '教程']
    action_score = sum(1 for kw in action_keywords if kw in text)
    actionable = "高" if action_score > 8 else ("中" if action_score > 4 else "低")

    # ⑪ 时效性
    time_keywords = ['2026', '2025', '今年', '本月', '本周', '最新', '刚刚', '近日',
                     '昨日', '今日', '正在', '即将']
    time_sensitive = bool(re.search(r'202[5-9]', text) or
                          any(kw in text for kw in time_keywords))
    timeliness = "时效" if time_sensitive else "永久"

    return {
        "word_count": chinese_chars,
        "total_chars": total_chars,
        "word_level": word_level,
        "info_density": round(info_density, 2),
        "structure_type": structure_type,
        "visual_potential": visual_potential,
        "depth_level": depth_level,
        "emotion": emotion,
        "narrative_tension": narrative_tension,
        "comic_potential": comic_potential,
        "infographic_potential": infographic_potential,
        "actionable": actionable,
        "timeliness": timeliness,
        "core_points_est": core_points,
    }


# ── 格式推荐引擎 ──────────────────────────────────────

def recommend_formats(profile: dict) -> list[dict]:
    """基于内容画像推荐最优输出形态"""
    if "error" in profile:
        return []

    scores = []

    # PPT: 层级框架 + 方法论 + 视觉潜力高 + 字数中长
    ppt_score = 0
    if profile["structure_type"] == "层级框架":
        ppt_score += 3
    if profile["visual_potential"] in ("高", "中"):
        ppt_score += 2
    if profile["word_level"] in ("中", "长"):
        ppt_score += 1
    if profile["depth_level"] == "深度":
        ppt_score += 1
    if profile["actionable"] == "高":
        ppt_score += 1
    scores.append({"format": "PPT演示文稿", "score": ppt_score,
                   "reason": f"结构{profile['structure_type']}+视觉{profile['visual_potential']}+内容{profile['depth_level']}"})

    # 信息图: 并列观点 + 核心点≤8 + 视觉潜力高
    infographic_score = 0
    if profile["structure_type"] == "并列观点":
        infographic_score += 3
    if profile["infographic_potential"] == "高":
        infographic_score += 3
    if profile["visual_potential"] in ("高", "中"):
        infographic_score += 2
    if profile["core_points_est"] <= 8:
        infographic_score += 1
    scores.append({"format": "信息图", "score": infographic_score,
                   "reason": f"核心点{profile['core_points_est']}个+视觉{profile['visual_potential']}+图解{profile['infographic_potential']}"})

    # 公众号文章: 深度分析 + 字数长 + 叙事型
    article_score = 0
    if profile["depth_level"] == "深度":
        article_score += 3
    if profile["word_level"] in ("中", "长"):
        article_score += 2
    if profile["structure_type"] in ("线性叙事", "层级框架"):
        article_score += 1
    if profile["narrative_tension"] in ("高", "中"):
        article_score += 1
    scores.append({"format": "公众号文章", "score": article_score,
                   "reason": f"深度{profile['depth_level']}+字数{profile['word_level']}+张力{profile['narrative_tension']}"})

    # 小红书图文: 短(<500) + 情感强 + 叙事张力高
    xhs_score = 0
    if profile["word_level"] == "短":
        xhs_score += 3
    else:
        xhs_score += 1
    if profile["emotion"] in ("积极", "反思"):
        xhs_score += 2
    if profile["narrative_tension"] == "高":
        xhs_score += 1
    scores.append({"format": "小红书图文", "score": xhs_score,
                   "reason": f"字数{profile['word_level']}+情感{profile['emotion']}+张力{profile['narrative_tension']}"})

    # 短视频脚本: 叙事张力高 + 情感强 + <1500字
    video_score = 0
    if profile["narrative_tension"] == "高":
        video_score += 3
    elif profile["narrative_tension"] == "中":
        video_score += 1
    if profile["emotion"] in ("反思", "警示"):
        video_score += 2
    if profile["word_level"] in ("短", "中"):
        video_score += 1
    if profile["timeliness"] == "时效":
        video_score += 1
    scores.append({"format": "60秒短视频脚本", "score": video_score,
                   "reason": f"张力{profile['narrative_tension']}+情感{profile['emotion']}+{'时效' if profile['timeliness']=='时效' else '非时效'}"})

    # 漫画: 视觉叙事潜力高 + 叙事张力高 + 有人物
    comic_score = 0
    if profile["comic_potential"] == "高":
        comic_score += 4
    elif profile["comic_potential"] == "中":
        comic_score += 1
    if profile["narrative_tension"] in ("高", "中"):
        comic_score += 2
    if profile["visual_potential"] in ("高", "中"):
        comic_score += 1
    scores.append({"format": "漫画/视觉故事", "score": comic_score,
                   "reason": f"漫画潜力{profile['comic_potential']}+张力{profile['narrative_tension']}"})

    # Newsletter: 深度+字数多+结构完整
    nl_score = 0
    if profile["depth_level"] == "深度":
        nl_score += 2
    if profile["word_level"] == "长":
        nl_score += 3
    if profile["structure_type"] in ("层级框架", "线性叙事"):
        nl_score += 2
    scores.append({"format": "Newsletter", "score": nl_score,
                   "reason": f"深度{profile['depth_level']}+字数{profile['word_level']}+结构{profile['structure_type']}"})

    # Skill封装: 方法论+实战性高+流程步骤
    skill_score = 0
    if profile["actionable"] == "高":
        skill_score += 3
    if profile["structure_type"] in ("流程步骤", "层级框架"):
        skill_score += 2
    if profile["depth_level"] == "深度":
        skill_score += 2
    scores.append({"format": "结构化Skill封装", "score": skill_score,
                   "reason": f"实战{profile['actionable']}+结构{profile['structure_type']}+深度{profile['depth_level']}"})

    # 按评分排序
    scores.sort(key=lambda x: x["score"], reverse=True)
    return scores


# ── 调度执行 ──────────────────────────────────────────

def get_dispatch_prompt(format_name: str, source_text: str, profile: dict) -> str:
    """获取对应格式的调度提示词"""
    prompts = {
        "PPT演示文稿": f"""请基于以下内容生成PPT制作简报：
内容字数：{profile['word_count']}字
内容结构：{profile['structure_type']}
内容深度：{profile['depth_level']}

要求：
1. 提取3-5个核心观点，每页一个
2. 为每页设计标题和要点
3. 建议配图/图表类型
4. 适合演讲的节奏（每页1-2分钟）

请用 `ppt-director-workflow` skill执行。

源内容：
{source_text[:2000]}
""",
        "信息图": f"""请基于以下内容生成信息图设计稿：
内容字数：{profile['word_count']}字
核心观点数：约{profile['core_points_est']}个

要求：
1. 用一张图呈现所有核心观点
2. 建议配色方案
3. 确定信息层级（主标题→副标题→正文）
4. 适合分享到朋友圈/社群的尺寸

请用 `baoyu-infographic` skill执行。

源内容：
{source_text[:2000]}
""",
        "公众号文章": f"""请基于以下内容生成公众号文章优化简报：
内容字数：{profile['word_count']}字
叙事类型：{profile['structure_type']}
情感色彩：{profile['emotion']}

要求：
1. 给出优化后的标题建议（3个候选）
2. 建议分段和插图位置
3. 需要补充的钩子/金句
4. 末尾引导关注话术

请用 `hechenmao-writing-framework` skill的六大角色流水线执行。

源内容：
{source_text[:2000]}
""",
        "小红书图文": f"""请基于以下内容生成小红书图文简报：
内容字数：{profile['word_count']}字
情感色彩：{profile['emotion']}

要求：
1. 提取最有传播力的1-2个观点
2. 设计6-8张图文卡片的标题
3. 适合小红书的语气（口语化、有情绪）
4. 配图风格建议

请用 `content-matrix` skill执行。

源内容：
{source_text[:2000]}
""",
        "60秒短视频脚本": f"""请基于以下内容生成60秒短视频分镜脚本：
内容字数：{profile['word_count']}字
叙事张力：{profile['narrative_tension']}

要求：
1. 按60秒（约180字口播）设计脚本
2. 前3秒钩子
3. 分镜标注（画面/口播/字幕）
4. 适合数字人口播

请用 `beat-plan-video-workflow` skill执行。

源内容：
{source_text[:1500]}
""",
    }

    return prompts.get(format_name, f"将以下内容转化为{format_name}格式\n\n{source_text[:2000]}")


# ── 报告生成 ──────────────────────────────────────────

def format_profile_report(profile: dict) -> str:
    """格式化输出内容画像报告"""
    lines = []
    lines.append("📐 内容画像报告")
    lines.append("=" * 40)
    lines.append(f"字数:      {profile['word_count']:,} 字（{profile['word_level']}文）")
    lines.append(f"密度:      {'█' * int(profile['info_density'] * 10)}{'░' * (10 - int(profile['info_density'] * 10))} {profile['info_density']}")
    lines.append(f"结构:      {profile['structure_type']}")
    lines.append(f"视觉潜力:  {'█' * (3 if profile['visual_potential']=='高' else (2 if profile['visual_potential']=='中' else 1)) :<6s} {profile['visual_potential']}")
    lines.append(f"深度等级:  {profile['depth_level']}")
    lines.append(f"叙事张力:  {'█' * (3 if profile['narrative_tension']=='高' else (2 if profile['narrative_tension']=='中' else 1)) :<6s} {profile['narrative_tension']}")
    lines.append(f"情感色彩:  {profile['emotion']}")
    lines.append(f"实战性:    {'█' * (3 if profile['actionable']=='高' else (2 if profile['actionable']=='中' else 1)) :<6s} {profile['actionable']}")
    lines.append(f"信息图解:  {profile['infographic_potential']}")
    lines.append(f"漫画潜力:  {profile['comic_potential']}")
    lines.append(f"时效性:    {profile['timeliness']}")
    return "\n".join(lines)


def format_recommendation(scores: list[dict]) -> str:
    """格式化推荐结果"""
    if not scores:
        return "暂无推荐"

    medals = ["🥇", "🥈", "🥉"]
    lines = ["\n🏆 推荐输出（按适配度排序）"]
    lines.append("-" * 40)
    for i, rec in enumerate(scores[:5]):
        medal = medals[i] if i < 3 else f"{i+1}."
        stars = "⭐" * min(rec["score"], 5)
        lines.append(f"{medal} {rec['format']:12s}  {stars}  {rec['reason']}")
    return "\n".join(lines)


# ── 路由执行 ──────────────────────────────────────────

class ContentRouter:
    """内容路由器主类"""

    def __init__(self, output_dir: str = "./router_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def analyze(self, text: str) -> dict:
        """分析内容并返回完整画像+推荐"""
        profile = profile_content(text)
        recs = recommend_formats(profile)
        return {"profile": profile, "recommendations": recs}

    def route(self, source_path: str, target_formats: Optional[list[str]] = None) -> dict:
        """分析并调度执行"""
        with open(source_path, "r", encoding="utf-8") as f:
            text = f.read()

        result = self.analyze(text)

        if target_formats:
            selected = [r for r in result["recommendations"] if r["format"] in target_formats]
        else:
            selected = result["recommendations"][:3]

        # 记录调度结果
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.output_dir / f"router_{timestamp}.json"

        dispatch = []
        for rec in selected:
            prompt = get_dispatch_prompt(rec["format"], text, result["profile"])
            dispatch.append({
                "format": rec["format"],
                "score": rec["score"],
                "dispatch_prompt": prompt,
                "target_skill": {
                    "PPT演示文稿": "ppt-director-workflow",
                    "信息图": "baoyu-infographic",
                    "公众号文章": "hechenmao-writing-framework",
                    "小红书图文": "content-matrix",
                    "60秒短视频脚本": "beat-plan-video-workflow",
                    "漫画/视觉故事": "baoyu-comic",
                }.get(rec["format"], ""),
            })

        output = {
            "timestamp": timestamp,
            "source": source_path,
            "profile": result["profile"],
            "dispatch": dispatch,
        }

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        return output


# ── CLI 入口 ──────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="内容路由器")
    sub = parser.add_subparsers(dest="command", required=True)

    analyze_parser = sub.add_parser("analyze", help="分析内容并推荐输出形态")
    analyze_parser.add_argument("file", help="内容文件路径")

    route_parser = sub.add_parser("route", help="分析+调度执行")
    route_parser.add_argument("file", help="内容文件路径")
    route_parser.add_argument("--formats", help="指定输出格式（逗号分隔）")

    args = parser.parse_args()

    if args.command == "analyze":
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
        profile = profile_content(text)
        print(format_profile_report(profile))
        recs = recommend_formats(profile)
        print(format_recommendation(recs))

    elif args.command == "route":
        router = ContentRouter()
        result = router.route(args.file,
                              args.formats.split(",") if args.formats else None)
        print(f"✅ 路由完成，已调度 {len(result['dispatch'])} 个分支")
        print(f"📄 报告保存至: {router.output_dir / f'router_{result['timestamp']}.json'}")
        for d in result["dispatch"]:
            print(f"  {d['format']:12s} → 匹配skill: {d['target_skill']}")


if __name__ == "__main__":
    main()
