#!/usr/bin/env python3
"""Validate the manuscript and prepare a web-only MkDocs source tree."""

from __future__ import annotations

import argparse
import html
import re
import shutil
from pathlib import Path

from prepare_book import (
    discover_chapters,
    parse_outline,
    validate_chapter,
    validate_images,
)


RAW_LATEX_START = "```{=latex}"
FENCE_END = "```"
INCLUDEGRAPHICS = re.compile(
    r"\\includegraphics(?:\[([^]]*)\])?\{([^}]+)\}"
)
CAPTION = re.compile(r"\\caption(?:of\{figure\})?\{(.+?)\}(?:\n|$)")
LABEL = re.compile(r"\\label\{([^}]+)\}")
REFERENCE = re.compile(r"图\s*\\ref\{(fig-[A-Za-z0-9._:-]+)\}")
UNPUBLISHED_DEMO_LINK = re.compile(r"\[([^]]+)\]\(\.\./demo/[^)]+\)")
LATEX_COMMAND = re.compile(r"\\(?:Needspace|newpage|clearpage)\b")


DIAGRAMS: dict[str, str] = {
    "使用 dsh 开展深度调研的五个步骤。第三步包含三个并行研究方向，完成后再进入核验和报告生成。": """
<div class="diagram-flow diagram-flow-vertical">
  <div class="diagram-node">1. 创建调研项目</div><span class="diagram-arrow">↓</span>
  <div class="diagram-node">2. 制定研究计划</div><span class="diagram-arrow">↓</span>
  <div class="diagram-node diagram-node-accent">3. 使用子代理并行调研</div>
  <div class="diagram-branches">
    <div class="diagram-node diagram-node-flat">效果与成本</div>
    <div class="diagram-node diagram-node-flat">产品与技术适配</div>
    <div class="diagram-node diagram-node-flat">安全与落地</div>
  </div>
  <span class="diagram-arrow">↓</span><div class="diagram-node">4. 核验研究结果</div>
  <span class="diagram-arrow">↓</span><div class="diagram-node">5. 生成决策报告并继续完善</div>
</div>""",
    "主会话与三个子代理的文件分工。每个子代理只负责一个研究方向，并写入自己的文件。": """
<div class="diagram-flow diagram-flow-vertical">
  <div class="diagram-node diagram-node-accent">主会话</div>
  <div class="diagram-branches">
    <div class="diagram-stack"><div class="diagram-node">效果与成本<br>子代理</div><span>↓</span><div class="diagram-node diagram-node-flat">任务一-效果与成本.md</div></div>
    <div class="diagram-stack"><div class="diagram-node">产品与技术适配<br>子代理</div><span>↓</span><div class="diagram-node diagram-node-flat">任务二-产品与技术适配.md</div></div>
    <div class="diagram-stack"><div class="diagram-node">安全与落地<br>子代理</div><span>↓</span><div class="diagram-node diagram-node-flat">任务三-安全与落地.md</div></div>
  </div>
</div>""",
    "模型与工具在 Agent Loop 中循环交接": """
<div class="diagram-flow diagram-flow-row">
  <div class="diagram-node">用户输入</div><span class="diagram-arrow">→</span>
  <div class="diagram-node diagram-node-accent">模型请求</div><span class="diagram-arrow">→</span>
  <div class="diagram-node diagram-node-seam">申请调用工具</div><span class="diagram-arrow">→</span>
  <div class="diagram-node">执行工具<br>返回结果</div><span class="diagram-loop">↩ 带着新结果再次请求</span>
</div>
<div class="diagram-note">模型也可以直接回复并结束循环</div>""",
    "dsh 从会话日志中整理下一次模型请求所需的历史": """
<div class="diagram-flow diagram-flow-vertical">
  <div class="diagram-node diagram-node-flat diagram-node-wide">只追加的会话事件日志<br><code>turn/start · step/start · user/message · assistant/message · tool/call · tool/result · step/end · turn/end</code></div>
  <span class="diagram-arrow">↓</span>
  <div class="diagram-node diagram-node-seam">当前 surface<br><small>用户消息 · assistant 消息 · 工具结果 · 注入并记录的状态</small></div>
  <span class="diagram-arrow">↓</span>
  <div class="diagram-node diagram-node-accent">下一次模型请求<br><code>deriveMessages()</code></div>
</div>""",
    "dsh 处理一次工具调用的过程": """
<div class="diagram-flow diagram-flow-row">
  <div class="diagram-node">模型给出<br>工具名和参数</div><span class="diagram-arrow">→</span>
  <div class="diagram-node diagram-node-flat">记录调用<br><code>tool/call</code></div><span class="diagram-arrow">→</span>
  <div class="diagram-node diagram-node-seam">权限与 hook<br>用户确认</div><span class="diagram-arrow">→</span>
  <div class="diagram-node diagram-node-accent">按工具自身的<br>执行约束运行</div><span class="diagram-arrow">→</span>
  <div class="diagram-node diagram-node-flat">记录结果<br><code>tool/result</code></div><span class="diagram-arrow">→</span>
  <div class="diagram-node">下一次模型请求</div>
</div>
<div class="diagram-note">拒绝时生成拒绝结果，同样写入 <code>tool/result</code></div>""",
    "一次模型请求中的主要上下文": """
<div class="diagram-context">
  <div class="diagram-node">系统说明 <small>dsh 的身份与工作方式</small></div>
  <div class="diagram-node diagram-node-flat">工具描述 <small>名称、用途和参数格式</small></div>
  <div class="diagram-node">消息历史 <small>用户消息、模型回复、工具结果</small></div>
  <div class="diagram-node diagram-node-flat">其中还可以包含 <small>权限状态和插件注入的信息</small></div>
  <div class="diagram-context-label"><span>相对稳定</span><span>随任务推进增长</span></div>
</div>""",
    "用摘要替代较早历史，同时保留近期消息原文": """
<div class="diagram-compare">
  <div class="diagram-compare-label">压缩前</div><div class="diagram-node diagram-node-flat">多条早期消息</div><div class="diagram-node diagram-node-flat">多条近期消息</div>
  <div class="diagram-compare-label">压缩后</div><div class="diagram-node diagram-node-accent">早期内容摘要</div><div class="diagram-node diagram-node-flat">多条近期消息</div>
</div>""",
    "概念图生成、评分与 Skill 更新循环，深蓝框中的结果会传给下一轮": """
<div class="diagram-flow diagram-flow-row">
  <div class="diagram-node">读取当前 Skill</div><span class="diagram-arrow">→</span>
  <div class="diagram-node">生成 SVG 概念图</div><span class="diagram-arrow">→</span>
  <div class="diagram-node">渲染并查看图片</div><span class="diagram-arrow">→</span>
  <div class="diagram-node">取得三个分项得分</div><span class="diagram-arrow">→</span>
  <div class="diagram-node">比较前后得分</div><span class="diagram-arrow">→</span>
  <div class="diagram-node diagram-node-accent">更新或保留 Skill</div><span class="diagram-loop">↩ 下一轮</span>
</div>""",
}


def safe_output_dir(book_dir: Path, output_dir: Path) -> None:
    """Reject broad or source-overlapping generated-output paths."""
    source = book_dir.resolve()
    target = output_dir.resolve()
    forbidden = {source, source.parent, Path.home().resolve(), Path("/").resolve()}
    if target in forbidden or source in target.parents:
        raise SystemExit(f"网站输出目录不安全: {target}")


def extract_caption(body: str) -> str:
    match = CAPTION.search(body)
    return match.group(1).strip() if match else ""


def image_width(options: str | None) -> str | None:
    if not options:
        return None
    match = re.search(r"width\s*=\s*([0-9.]+)\\(?:textwidth|linewidth)", options)
    if not match:
        return None
    value = float(match.group(1)) * 100
    return f"{value:g}%"


def render_image_block(body: str, caption: str) -> str:
    images = INCLUDEGRAPHICS.findall(body)
    rendered: list[str] = []
    grid_class = " book-figure-grid" if len(images) > 1 else ""
    label = LABEL.search(body)
    identifier = f' id="{label.group(1)}"' if label else ""
    rendered.append(
        f'<figure class="book-figure{grid_class}"{identifier} markdown>'
    )
    for options, target in images:
        width = image_width(options)
        attrs = [".book-figure-image", 'loading="lazy"']
        if width and len(images) == 1:
            attrs.append(f'style="width: {width};"')
        rendered.append(
            f"![{caption}]({target}){{ {' '.join(attrs)} }}"
        )
    if caption:
        rendered.append(f"<figcaption>{html.escape(caption)}</figcaption>")
    rendered.append("</figure>")
    return "\n".join(rendered)


def render_diagram(body: str, caption: str) -> str:
    diagram = DIAGRAMS.get(caption)
    if diagram is None:
        label = LABEL.search(body)
        identifier = label.group(1) if label else "无标签"
        raise SystemExit(f"网页端缺少 TikZ 图转换: {identifier} {caption}")
    label = LABEL.search(body)
    identifier = f' id="{label.group(1)}"' if label else ""
    return (
        f'<figure class="book-diagram"{identifier} role="img" '
        f'aria-label="{html.escape(caption, quote=True)}">\n'
        f"{diagram.strip()}\n"
        f"<figcaption>{html.escape(caption)}</figcaption>\n"
        "</figure>"
    )


def render_latex_block(body: str) -> str:
    caption = extract_caption(body)
    if INCLUDEGRAPHICS.search(body):
        return render_image_block(body, caption)
    if "\\begin{tikzpicture}" in body:
        return render_diagram(body, caption)
    if not body.strip() or LATEX_COMMAND.search(body):
        return ""
    raise SystemExit("网页端遇到未支持的 LaTeX 块")


def transform_markdown(text: str) -> str:
    """Convert Pandoc-only blocks while leaving the canonical Markdown untouched."""
    lines = text.splitlines()
    output: list[str] = []
    index = 0
    while index < len(lines):
        if lines[index].strip() != RAW_LATEX_START:
            output.append(lines[index])
            index += 1
            continue

        start = index + 1
        index += 1
        block: list[str] = []
        while index < len(lines) and lines[index].strip() != FENCE_END:
            block.append(lines[index])
            index += 1
        if index == len(lines):
            raise SystemExit(f"第 {start} 行开始的 LaTeX 块没有闭合")
        rendered = render_latex_block("\n".join(block))
        if rendered:
            output.extend(rendered.splitlines())
        index += 1

    rendered_text = "\n".join(output).rstrip() + "\n"
    rendered_text = REFERENCE.sub(lambda match: f"[图](#{match.group(1)})", rendered_text)
    rendered_text = UNPUBLISHED_DEMO_LINK.sub(lambda match: match.group(1), rendered_text)
    if RAW_LATEX_START in rendered_text:
        raise SystemExit("网页稿仍包含 LaTeX 原始块")
    return rendered_text


def prepare_site(book_dir: Path, output_dir: Path, site_assets: Path) -> list[Path]:
    safe_output_dir(book_dir, output_dir)
    outline = book_dir / "outline.md"
    plans = parse_outline(outline)
    chapters = discover_chapters(book_dir)
    if [number for number, _ in chapters] != list(range(1, len(plans) + 1)):
        raise SystemExit("chapterN.md 必须完整覆盖 outline.md 中的所有章节")

    for number, path in chapters:
        validate_chapter(number, path, plans)
    introduction = book_dir / "introduction.md"
    validate_images(introduction)

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)
    shutil.copytree(book_dir / "assets", output_dir / "assets")
    for directory in ("assets", "stylesheets"):
        source = site_assets / directory
        if source.is_dir():
            shutil.copytree(source, output_dir / directory, dirs_exist_ok=True)

    generated: list[Path] = []
    index_path = output_dir / "index.md"
    index_path.write_text(
        transform_markdown(introduction.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    generated.append(index_path)

    for _number, source in chapters:
        target = output_dir / source.name
        target.write_text(
            transform_markdown(source.read_text(encoding="utf-8")),
            encoding="utf-8",
        )
        validate_images(target)
        generated.append(target)

    return generated


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--book-dir", type=Path, default=Path("book"))
    parser.add_argument("--output-dir", type=Path, default=Path("output/site-src"))
    parser.add_argument("--site-assets", type=Path, default=Path("site"))
    args = parser.parse_args()
    generated = prepare_site(args.book_dir, args.output_dir, args.site_assets)
    print("网页正文：" + "、".join(path.name for path in generated))


if __name__ == "__main__":
    main()
