# -*- coding: utf-8 -*-
"""
内容路由器 · Content Router MCP Server
======================================
把「这份素材该做成什么」从凭感觉，变成一道可计算的问题：
**11 维内容画像 → 跨媒介形态推荐（带适配度与理由）→ 调度提示词**。

双通道:
  本地 stdio   :  python server.py
  远程 HTTP    :  python server.py --transport http --host 127.0.0.1 --port 8769

暴露工具:
  - analyze_content       11 维画像 + 形态推荐（一次给全，最常用）
  - recommend_formats     只出排序推荐（适配度% + 理由）
  - get_dispatch_prompt   为指定形态生成调度提示词（交给任意 Agent 执行）
  - list_formats          6 种跨媒介输出形态的定义与适用内容
  - profile_schema        11 维画像的口径与取值

自检(不走协议,直接打工具):  python server.py --selftest
"""
import argparse
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

# 工具注解：纯读、幂等、不接触外部世界，统一声明为 RO_ANN。
try:
    from mcp.types import ToolAnnotations
except ImportError:  # 老版本 SDK 无该类型时降级为 dict，行为一致
    ToolAnnotations = dict

# mcp 2.x 把 FastMCP 更名为 MCPServer；兼容 1.x，避免 SDK 升级打断通道。
try:  # mcp >= 2.x
    from mcp.server.mcpserver import MCPServer as _MCPServer
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP as _MCPServer

# 公网部署必需：SDK 默认开启 DNS-rebinding 防护，只放行 localhost，
# 外部以真实域名访问会被拒成 421「Invalid Host header」。这里改为白名单放行。
try:
    from mcp.server.transport_security import TransportSecuritySettings
except ImportError:  # 老版本 SDK 无此模块
    TransportSecuritySettings = None

from engine import (  # noqa: E402
    profile_content,
    recommend_formats as _recommend,
    get_dispatch_prompt as _dispatch,
    format_profile_report,
    format_recommendation,
    STRUCTURE_TYPES,
    DEPTH_LEVELS,
    EMOTION_TYPES,
)

# 端口一律用 host:* 通配——写死端口后，任何换端口的探活（本地测试 / CI /
# 目录站的容器构建测试）都会吃 421，而报错只有一句 Invalid Host header。
DEFAULT_ALLOWED_HOSTS = [
    "savantcat.cn", "savantcat.cn:443", "savantcat.cn:*",
    "www.savantcat.cn", "www.savantcat.cn:443", "www.savantcat.cn:*",
    "127.0.0.1", "127.0.0.1:*", "localhost", "localhost:*",
]

FORMATS = [
    {"name": "PPT演示文稿", "适合": "方法论、层级框架、教学", "工作流": "ppt-director-workflow"},
    {"name": "信息图", "适合": "并列对比、概念梳理", "工作流": "baoyu-infographic"},
    {"name": "60秒短视频脚本", "适合": "热点、情绪型短内容", "工作流": "beat-plan-video-workflow"},
    {"name": "漫画/视觉故事", "适合": "案例、故事、有人物对白", "工作流": "baoyu-comic"},
    {"name": "Newsletter", "适合": "深度 + 私密语感", "工作流": ""},
    {"name": "结构化Skill封装", "适合": "方法论、可复用工作流", "工作流": ""},
]
_FORMAT_NAMES = [f["name"] for f in FORMATS]

PROFILE_SCHEMA = [
    {"维度": "① 字数", "取值": "短 / 中 / 长"},
    {"维度": "② 信息密度", "取值": "有效信息点占比（0-1）"},
    {"维度": "③ 结构类型", "取值": " / ".join(STRUCTURE_TYPES)},
    {"维度": "④ 视觉潜力", "取值": "低 / 中 / 高"},
    {"维度": "⑤ 深度等级", "取值": " / ".join(DEPTH_LEVELS)},
    {"维度": "⑥ 情感色彩", "取值": " / ".join(EMOTION_TYPES)},
    {"维度": "⑦ 叙事张力", "取值": "低 → 高"},
    {"维度": "⑧ 视觉叙事潜力", "取值": "低 / 中 / 高（能否改编漫画）"},
    {"维度": "⑨ 信息图解潜力", "取值": "低 / 高（核心观点 ≤8 个？）"},
    {"维度": "⑩ 实战可操作性", "取值": "低 / 中 / 高"},
    {"维度": "⑪ 时效性", "取值": "永久 / 时效"},
]


def _transport_security():
    if TransportSecuritySettings is None:
        return None
    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,   # 保留防护，用白名单而非关闭
        allowed_hosts=DEFAULT_ALLOWED_HOSTS,
        allowed_origins=["*"],                  # 公开只读服务：允许任意来源 Agent 调用
    )


def _with_fit(recs):
    """补上跨形态可比的适配度（判据命中率 = 得分 / 该形态满分）。"""
    out = []
    for r in recs:
        item = dict(r)
        mx = item.get("max") or 0
        item["fit"] = round(100.0 * item.get("score", 0) / mx) if mx else 0
        out.append(item)
    return out


def _blank(text):
    return not text or not str(text).strip()


# ---------------------------------------------------------------- MCP Server
SERVER_VERSION = "1.0.0"

mcp = _MCPServer(
    "content-router",
    title="内容路由器 · Content Router",
    description=(
        "11 维内容画像 → 跨媒介输出形态推荐（PPT/信息图/短视频/漫画/Newsletter/Skill 封装），"
        "并给出可直接执行的调度提示词。纯计算、零依赖、不落盘。"
    ),
    version=SERVER_VERSION,
    website_url="https://savantcat.cn/mcp-content-router",
    instructions=(
        "内容路由器把「这份素材该做成什么」变成可计算的问题：先给内容做 11 维体检"
        "（字数/密度/结构/视觉潜力/深度/情感/叙事张力/漫画潜力/图解潜力/实操性/时效性），"
        "再基于体检结果匹配跨媒介输出形态并给出适配度与理由。它管「做成什么形态」，"
        "不管「同媒介换哪个平台」——后者是平台改写，不在本服务职责内。"
        "推荐永远给多个候选 + 理由，把决定权交回调用方。"
    ),
)

RO_ANN = ToolAnnotations(readOnlyHint=True, destructiveHint=False,
                         idempotentHint=True, openWorldHint=False)


@mcp.tool(annotations=RO_ANN)
def analyze_content(text: str) -> str:
    """给一段内容做 11 维画像，并推荐最适合的跨媒介输出形态（一次给全）。

    适合「这篇到底该做成什么」这类问题。返回画像明细 + 排序推荐（含适配度%
    与命中的判据），可直接当决策依据。

    Args:
        text: 原文全文（中英文均可）。建议 200 字以上；过短画像不稳，
              长文超过 8000 字会自动截断后画像。
    """
    if _blank(text):
        return json.dumps({"error": "内容为空", "hint": "请传入待分析的正文文本"},
                          ensure_ascii=False)
    src = str(text)
    truncated = len(src) > 8000
    if truncated:
        src = src[:8000]
    profile = profile_content(src)
    if "error" in profile:
        return json.dumps({"error": profile["error"]}, ensure_ascii=False)
    recs = _with_fit(_recommend(profile))
    top = recs[0] if recs else None
    return json.dumps({
        "profile": profile,
        "profile_report": format_profile_report(profile),
        "recommendations": recs,
        "recommend_report": format_recommendation(_recommend(profile)),
        "top": top["format"] if top else None,
        "top_fit": top["fit"] if top else 0,
        "note": ("首推适配度 <40% 说明这篇还没有明显适合的形态，不建议急着动手。"
                 "换形态前先想清楚要动哪一维画像。"),
        "truncated": truncated,
    }, ensure_ascii=False, indent=1)


@mcp.tool(annotations=RO_ANN)
def recommend_formats(text: str) -> str:
    """只出形态推荐表：按适配度排序，每个形态给出得分、适配度% 和命中理由。

    需要画像明细时用 analyze_content。

    Args:
        text: 原文全文。建议 200 字以上。
    """
    if _blank(text):
        return json.dumps({"error": "内容为空"}, ensure_ascii=False)
    profile = profile_content(str(text)[:8000])
    if "error" in profile:
        return json.dumps({"error": profile["error"]}, ensure_ascii=False)
    recs = _with_fit(_recommend(profile))
    return json.dumps({
        "count": len(recs),
        "recommendations": recs,
        "top": recs[0]["format"] if recs else None,
        "report": format_recommendation(_recommend(profile)),
    }, ensure_ascii=False, indent=1)


@mcp.tool(annotations=RO_ANN)
def get_dispatch_prompt(text: str, format_name: str) -> str:
    """为指定输出形态生成「调度提示词」——一段可直接交给 Agent 执行的指令。

    先 recommend_formats 挑形态，再用本工具取该形态的执行口令。

    Args:
        text: 原文全文。
        format_name: 目标形态，必须是 list_formats 里的名字之一：
                     PPT演示文稿 / 信息图 / 60秒短视频脚本 / 漫画/视觉故事 /
                     Newsletter / 结构化Skill封装
    """
    if _blank(text):
        return json.dumps({"error": "内容为空"}, ensure_ascii=False)
    name = (format_name or "").strip()
    if name not in _FORMAT_NAMES:
        return json.dumps({
            "error": "未识别的输出形态: %s" % name,
            "available_formats": _FORMAT_NAMES,
            "hint": "形态名必须与 list_formats 返回的 name 完全一致",
        }, ensure_ascii=False)
    src = str(text)[:8000]
    profile = profile_content(src)
    if "error" in profile:
        return json.dumps({"error": profile["error"]}, ensure_ascii=False)
    recs = _with_fit(_recommend(profile))
    hit = next((r for r in recs if r["format"] == name), None)
    skill = next((f["工作流"] for f in FORMATS if f["name"] == name), "")
    return json.dumps({
        "format": name,
        "fit": hit["fit"] if hit else None,
        "reason": hit["reason"] if hit else "",
        "target_skill": skill,
        "dispatch_prompt": _dispatch(name, src, profile),
        "note": "target_skill 是作者本地的同名技能名，未随本仓库开源；"
                "dispatch_prompt 自带完整上下文，接任意 Agent 或手工执行均可。",
    }, ensure_ascii=False, indent=1)


@mcp.tool(annotations=RO_ANN)
def list_formats() -> str:
    """列出 6 种跨媒介输出形态：名字、适合什么内容、对应工作流。

    注意：这里都是**媒介发生改变**的形态（文字 → 图表/视频/漫画/PPT/技能）。
    公众号版、小红书版这类**同媒介换平台**的改写不在本服务职责内。
    """
    return json.dumps({
        "count": len(FORMATS),
        "formats": FORMATS,
        "boundary": "本服务管「做成什么形态」，不管「发到哪个平台」。",
    }, ensure_ascii=False, indent=1)


@mcp.tool(annotations=RO_ANN)
def profile_schema() -> str:
    """列出 11 维内容画像的口径与取值范围（用于理解/修正画像结果）。"""
    return json.dumps({
        "count": len(PROFILE_SCHEMA),
        "dimensions": PROFILE_SCHEMA,
        "structure_types": STRUCTURE_TYPES,
        "depth_levels": DEPTH_LEVELS,
        "emotion_types": EMOTION_TYPES,
    }, ensure_ascii=False, indent=1)


# ---------------------------------------------------------------- 自检
SAMPLE = """# 用 AI 客服把重复咨询压下去：我们踩过的五个坑

## 一、先量化到底有多少重复

上线前先做了一件事：把过去三个月的咨询记录导出来，按问题类型打标。
结果是话务高峰期超过 60% 的进线都在问同样的十几件事。

## 二、五个坑

1. 一上来就买大模型 API，没先做知识库 —— 结果答得又快又错。
2. 知识库只喂了产品手册，没喂工单记录 —— 客户问法跟手册写法完全对不上。
3. 没设兜底转人工 —— 答不上来就硬答，反而更伤。
4. 没做回归验收 —— 改一次知识库就悄悄坏一处，没人发现。
5. 老板只看"接住了多少"，不看"解决率" —— 指标错了，动作就全错。

## 三、可复用的做法

按以下步骤做：打开后台 → 导出近三个月工单 → 按问题类型打标 → 抽 top20 建 FAQ 基线 →
上线后每周做一次解决率回归，低强度条目自动归档。
配置路径是 ./kb/config.json，运行 python check.py 做验收。
2026 年这套流程已经跑通三个项目。
"""


def _selftest():
    r = json.loads(analyze_content(SAMPLE))
    print("[1] analyze_content    -> 维度=%d 推荐=%d 首推=%s(适配%d%%)" % (
        len(r.get("profile", {})), len(r.get("recommendations", [])),
        r.get("top"), r.get("top_fit", 0)))
    assert r.get("top"), "analyze_content 未给出首推形态"

    r = json.loads(recommend_formats(SAMPLE))
    print("[2] recommend_formats  -> count=%d top=%s" % (r["count"], r["top"]))
    assert r["count"] == 6, "推荐形态数应为 6"

    r = json.loads(list_formats())
    print("[3] list_formats       -> count=%d names=%s" % (r["count"], [f["name"] for f in r["formats"]]))

    r = json.loads(profile_schema())
    print("[4] profile_schema     -> count=%d" % r["count"])

    r = json.loads(get_dispatch_prompt(SAMPLE, "信息图"))
    print("[5] get_dispatch_prompt-> %s 提示词=%d字 target_skill=%s" % (
        r["format"], len(r.get("dispatch_prompt") or ""), r.get("target_skill")))
    assert r.get("dispatch_prompt"), "调度提示词为空"

    r = json.loads(get_dispatch_prompt(SAMPLE, "不存在的形态"))
    print("[6] 容错(形态)         -> %s available=%d" % (r.get("error"), len(r.get("available_formats", []))))
    assert r.get("available_formats"), "容错未回可选形态"

    r = json.loads(analyze_content(""))
    print("[7] 容错(空内容)       -> %s" % r.get("error"))

    r = json.loads(analyze_content("短句。"))
    print("[8] 短文本             -> 首推=%s(适配%d%%)" % (r.get("top"), r.get("top_fit", 0)))

    print("\n✅ 8/8 工具自检通过")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--transport", default="stdio",
                    choices=["stdio", "http", "streamable-http", "sse"])
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8769)
    ap.add_argument("--path", default="/mcp")
    ap.add_argument("--stateless", action="store_true",
                    help="无状态模式（反代/公网部署更稳，不依赖会话粘滞）")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        _selftest()
        return

    t = "streamable-http" if args.transport == "http" else args.transport
    if t == "stdio":
        mcp.run()
        return
    sys.stderr.write("[content-router] serving on %s:%d%s (%s, stateless=%s)\n"
                     % (args.host, args.port, args.path, t, args.stateless))
    ts = _transport_security()
    kw = {} if ts is None else {"transport_security": ts}
    try:  # mcp 2.x：run() 直收 kwargs
        mcp.run(transport=t, host=args.host, port=args.port,
                streamable_http_path=args.path,
                stateless_http=args.stateless,
                max_request_body_size=1024 * 1024,
                **kw)
    except TypeError:  # mcp 1.x：kwargs 不被接受，走 settings
        s = getattr(mcp, "settings", None)
        if s is not None:
            for k, v in (("host", args.host), ("port", args.port)):
                try:
                    setattr(s, k, v)
                except Exception:
                    pass
        try:
            mcp.run(transport=t, **kw)
        except TypeError:
            mcp.run(transport=t)


if __name__ == "__main__":
    main()
