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


FIGURE_BLOCK = re.compile(
    r"(?P<open><figure\b)(?P<attributes>[^>]*)(?P<body>>.*?<figcaption>)"
    r"(?P<caption>.*?)(?P<close></figcaption>.*?</figure>)",
    flags=re.IGNORECASE | re.DOTALL,
)
HTML_ID = re.compile(r'\bid="([^"]+)"')
UNPUBLISHED_DEMO_LINK = re.compile(r"\[([^]]+)\]\(\.\./demo/[^)]+\)")
MARKDOWN_IMAGE = re.compile(
    r"^\s*!\[([^]]*)\]\(([^)]+)\)(?:\{([^}]*)\})?\s*$"
)
ATTRIBUTE_ID = re.compile(r"(?<!\S)#([A-Za-z][A-Za-z0-9._:-]*)")
FENCE_START = re.compile(r"^\s*(`{3,}|~{3,})")
INTRODUCTION_HEADING = re.compile(r"^# (导言\b.*)$", flags=re.MULTILINE)
INTRODUCTION_META_TITLE = re.compile(r"^title:[^\n]*\n", flags=re.MULTILINE)
EMPTY_FRONT_MATTER = re.compile(r"\A---\n\s*---\n")
README_DEMO_LINK = re.compile(r"\]\((demo/[^)]+)\)")
README_CHAPTER_LINK = re.compile(
    r"\]\(https://dshbook\.penguin\.ooo/(chapter\d+)/\)"
)




def safe_output_dir(book_dir: Path, output_dir: Path) -> None:
    """Reject broad or source-overlapping generated-output paths."""
    source = book_dir.resolve()
    target = output_dir.resolve()
    forbidden = {source, source.parent, Path.home().resolve(), Path("/").resolve()}
    if target in forbidden or source in target.parents:
        raise SystemExit(f"网站输出目录不安全: {target}")




def render_markdown_image(line: str) -> str | None:
    """Turn one standalone Markdown image into a visible web figure."""
    match = MARKDOWN_IMAGE.match(line)
    if match is None:
        return None

    caption, target, raw_attributes = match.groups()
    attributes = raw_attributes or ""
    identifier_match = ATTRIBUTE_ID.search(attributes)
    identifier = f' id="{identifier_match.group(1)}"' if identifier_match else ""
    if identifier_match:
        attributes = ATTRIBUTE_ID.sub("", attributes, count=1)

    image_attributes = attributes.split()
    if ".book-figure-image" not in image_attributes:
        image_attributes.insert(0, ".book-figure-image")
    if not any(attribute.startswith("loading=") for attribute in image_attributes):
        image_attributes.append('loading="lazy"')
    attribute_block = " ".join(image_attributes)

    rendered = [
        f'<figure class="book-figure"{identifier} markdown>',
        f"![{caption}]({target}){{ {attribute_block} }}",
    ]
    if caption:
        rendered.append(f"<figcaption>{html.escape(caption)}</figcaption>")
    rendered.append("</figure>")
    return "\n".join(rendered)


def render_markdown_figures(text: str) -> str:
    """Wrap source Markdown images, without touching code or existing figures."""
    output: list[str] = []
    fence: tuple[str, int] | None = None
    figure_depth = 0

    for line in text.splitlines():
        stripped = line.lstrip()
        fence_match = FENCE_START.match(line)
        if fence is not None:
            output.append(line)
            marker, length = fence
            if stripped.startswith(marker * length):
                fence = None
            continue
        if fence_match:
            token = fence_match.group(1)
            fence = (token[0], len(token))
            output.append(line)
            continue

        opens = len(re.findall(r"<figure\b", line, flags=re.IGNORECASE))
        closes = len(re.findall(r"</figure>", line, flags=re.IGNORECASE))
        if figure_depth > 0 or opens:
            output.append(line)
            figure_depth = max(0, figure_depth + opens - closes)
            continue

        rendered = render_markdown_image(line)
        output.extend(rendered.splitlines() if rendered else [line])

    return "\n".join(output)


def number_web_figures(text: str, chapter_number: int) -> str:
    """Number rendered figures in reading order without changing source captions."""
    figure_index = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal figure_index
        figure_index += 1
        number = f"{chapter_number}.{figure_index}"
        expected_id = f"fig-{chapter_number}-{figure_index}"
        attributes = match.group("attributes")
        identifier_match = HTML_ID.search(attributes)
        if identifier_match:
            identifier = identifier_match.group(1)
            if identifier.startswith("fig-") and identifier != expected_id:
                raise SystemExit(
                    f"图片 {number} 的锚点应为 {expected_id}，实际为 {identifier}"
                )
        else:
            identifier = expected_id
            attributes += f' id="{identifier}"'

        caption = match.group("caption")
        numbered_caption = (
            f'<span class="book-figure-number">图 {number}</span> {caption}'
        )
        return (
            match.group("open")
            + attributes
            + match.group("body")
            + numbered_caption
            + match.group("close")
        )

    return FIGURE_BLOCK.sub(replace, text)


def transform_markdown(text: str, chapter_number: int | None = None) -> str:
    """Prepare canonical Markdown for the website."""
    if "```{=latex}" in text:
        raise SystemExit("书稿不再支持 LaTeX 原始块")

    rendered_text = render_markdown_figures(text).rstrip() + "\n"
    if chapter_number is not None:
        rendered_text = number_web_figures(rendered_text, chapter_number)

    rendered_text = UNPUBLISHED_DEMO_LINK.sub(lambda match: match.group(1), rendered_text)
    return rendered_text


def transform_introduction(text: str) -> str:
    """Prepare the book introduction as a regular website page."""
    rendered = transform_markdown(text)
    rendered, title_count = INTRODUCTION_META_TITLE.subn("", rendered, count=1)
    rendered, front_matter_count = EMPTY_FRONT_MATTER.subn("", rendered, count=1)
    heading_count = len(INTRODUCTION_HEADING.findall(rendered))
    if title_count != 1:
        raise SystemExit("网页导言缺少标题元数据")
    if front_matter_count != 1:
        raise SystemExit("网页导言的元数据块不是预期结构")
    if heading_count != 1:
        raise SystemExit("网页导言缺少“导言”标题")
    metadata = (
        "---\n"
        "title: 导言\n"
        "source_edit_path: book/introduction.md\n"
        "---\n\n"
    )
    return metadata + rendered


def transform_readme(text: str, repository_url: str) -> str:
    """Prepare the repository README as the website homepage."""
    rendered = transform_markdown(text)
    rendered = rendered.replace("(book/assets/", "(assets/")
    rendered = README_CHAPTER_LINK.sub(
        lambda match: f"]({match.group(1)}.md)", rendered
    )
    rendered = rendered.replace(
        "](https://dshbook.penguin.ooo/)", "](index.md)"
    )
    repository = repository_url.rstrip("/")
    rendered = README_DEMO_LINK.sub(
        lambda match: f"]({repository}/tree/main/{match.group(1).rstrip('/')})",
        rendered,
    )
    metadata = (
        "---\n"
        "title: DeepSeek Harness 实战指南\n"
        "source_edit_path: README.md\n"
        "---\n\n"
    )
    return metadata + rendered


def prepare_site(
    book_dir: Path,
    output_dir: Path,
    site_assets: Path,
    readme_path: Path | None = None,
    repository_url: str = "https://github.com/Prism-Shadow/dsh-book",
) -> list[Path]:
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
    readme = readme_path or book_dir.parent / "README.md"
    if not readme.is_file():
        raise SystemExit(f"网站首页缺少 README: {readme}")

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)
    shutil.copytree(book_dir / "assets", output_dir / "assets")
    for directory in ("assets", "javascripts", "stylesheets"):
        source = site_assets / directory
        if source.is_dir():
            shutil.copytree(source, output_dir / directory, dirs_exist_ok=True)

    generated: list[Path] = []
    index_path = output_dir / "index.md"
    index_path.write_text(
        transform_readme(readme.read_text(encoding="utf-8"), repository_url),
        encoding="utf-8",
    )
    validate_images(index_path)
    generated.append(index_path)

    introduction_path = output_dir / "introduction.md"
    introduction_path.write_text(
        transform_introduction(introduction.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    generated.append(introduction_path)

    for number, source in chapters:
        target = output_dir / source.name
        target.write_text(
            transform_markdown(
                source.read_text(encoding="utf-8"), chapter_number=number
            ),
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
    parser.add_argument("--readme", type=Path, default=Path("README.md"))
    parser.add_argument(
        "--repository-url",
        default="https://github.com/Prism-Shadow/dsh-book",
    )
    args = parser.parse_args()
    generated = prepare_site(
        args.book_dir,
        args.output_dir,
        args.site_assets,
        args.readme,
        args.repository_url,
    )
    print(
        "网页正文："
        + "、".join(path.name for path in generated)
    )


if __name__ == "__main__":
    main()
