#!/usr/bin/env python3
"""Validate the three-part outline and assemble the Markdown build input."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path


CHAPTER_FILE = re.compile(r"chapter([1-9][0-9]*)\.md$")
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
ATTRIBUTE = re.compile(r"\s+\{([^}]*)\}\s*$")
EXPLICIT_ID = re.compile(r"(?:^|\s)#([A-Za-z0-9:._-]+)(?:\s|$)")
PART_TITLE = re.compile(r"^第[^\s　]+部分[\s　]+(.+)$")
CHAPTER_TITLE = re.compile(r"^第([1-9][0-9]*)章[\s　]+(.+)$")
SECTION_TITLE = re.compile(r"^([1-9][0-9]*)\.([1-9][0-9]*)\s+(.+)$")
IMAGE = re.compile(r"!\[[^]]*]\(([^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)")


@dataclass
class SectionPlan:
    number: int
    title: str


@dataclass
class ChapterPlan:
    number: int
    title: str
    part_title: str
    sections: list[SectionPlan] = field(default_factory=list)


def split_heading(line: str) -> tuple[int, str, str | None] | None:
    match = HEADING.match(line)
    if not match:
        return None
    text = match.group(2)
    identifier = None
    attrs = ATTRIBUTE.search(text)
    if attrs:
        id_match = EXPLICIT_ID.search(attrs.group(1))
        identifier = id_match.group(1) if id_match else None
        text = text[: attrs.start()].rstrip()
    return len(match.group(1)), text, identifier


def read_headings(path: Path) -> list[tuple[int, str, str | None, int]]:
    headings: list[tuple[int, str, str | None, int]] = []
    fenced = False
    fence = ""
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            marker = stripped[:3]
            if not fenced:
                fenced, fence = True, marker
            elif marker == fence:
                fenced = False
            continue
        if fenced:
            continue
        parsed = split_heading(line)
        if parsed:
            headings.append((*parsed, line_number))
    return headings


def parse_outline(path: Path) -> list[ChapterPlan]:
    chapters: list[ChapterPlan] = []
    current_part = ""
    current_chapter: ChapterPlan | None = None

    for level, title, _identifier, line_number in read_headings(path):
        if level == 1:
            match = PART_TITLE.fullmatch(title)
            if not match:
                raise SystemExit(f"{path}:{line_number}: 一级标题应为第 N 部分")
            current_part = match.group(1)
            current_chapter = None
        elif level == 2:
            if not current_part:
                raise SystemExit(f"{path}:{line_number}: 章标题前缺少部分标题")
            match = CHAPTER_TITLE.fullmatch(title)
            if not match:
                raise SystemExit(f"{path}:{line_number}: 二级标题应为第 N 章")
            number = int(match.group(1))
            if number != len(chapters) + 1:
                raise SystemExit(f"{path}:{line_number}: 章编号应为 {len(chapters) + 1}")
            current_chapter = ChapterPlan(number, match.group(2), current_part)
            chapters.append(current_chapter)
        elif level == 3:
            if current_chapter is None:
                raise SystemExit(f"{path}:{line_number}: 节标题前缺少章标题")
            match = SECTION_TITLE.fullmatch(title)
            if not match:
                raise SystemExit(f"{path}:{line_number}: 三级标题应以 N.M 开头")
            chapter_number = int(match.group(1))
            section_number = int(match.group(2))
            expected_section = len(current_chapter.sections) + 1
            if chapter_number != current_chapter.number or section_number != expected_section:
                raise SystemExit(
                    f"{path}:{line_number}: 节编号应为 "
                    f"{current_chapter.number}.{expected_section}"
                )
            current_chapter.sections.append(SectionPlan(section_number, match.group(3)))
        else:
            raise SystemExit(f"{path}:{line_number}: 全书目录只允许一至三级标题")

    if not chapters:
        raise SystemExit(f"{path}: 全书目录没有章标题")
    return chapters


def discover_chapters(book_dir: Path) -> list[tuple[int, Path]]:
    found: list[tuple[int, Path]] = []
    for path in book_dir.glob("chapter*.md"):
        match = CHAPTER_FILE.fullmatch(path.name)
        if not match:
            raise SystemExit(f"{path}: 章节文件必须命名为 chapterN.md")
        found.append((int(match.group(1)), path))
    found.sort()
    if not found:
        raise SystemExit(f"{book_dir}: 至少需要一个 chapterN.md")
    return found


def validate_images(path: Path) -> None:
    for target in IMAGE.findall(path.read_text(encoding="utf-8")):
        if "://" in target or target.startswith("data:"):
            continue
        if not (path.parent / target).is_file():
            raise SystemExit(f"{path}: 图片不存在: {target}")


def validate_chapter(number: int, path: Path, plans: list[ChapterPlan]) -> None:
    if number > len(plans):
        raise SystemExit(f"{path}: 第 {number} 章未出现在 outline.md")
    plan = plans[number - 1]
    headings = read_headings(path)
    if not headings:
        raise SystemExit(f"{path}: 缺少章标题")

    level, title, identifier, line_number = headings[0]
    if level != 1 or title != plan.title or identifier != f"ch-{number}":
        raise SystemExit(
            f"{path}:{line_number}: 章标题应为 # {plan.title} {{#ch-{number}}}"
        )

    seen: list[str] = []
    for level, title, identifier, line_number in headings[1:]:
        if level != 2:
            continue
        index = len(seen)
        if index >= len(plan.sections) or title != plan.sections[index].title:
            raise SystemExit(f"{path}:{line_number}: 二级标题与 outline.md 不一致: {title}")
        expected_id = f"sec-{number}-{index + 1}"
        if identifier != expected_id:
            raise SystemExit(f"{path}:{line_number}: 标题 ID 应为 {expected_id}")
        seen.append(title)

    if len(seen) != len(plan.sections):
        raise SystemExit(f"{path}: 二级标题数量与 outline.md 不一致")
    validate_images(path)


def latex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
    return "".join(replacements.get(char, char) for char in text)


def assemble(book_dir: Path, outline: Path, output: Path) -> list[Path]:
    introduction = book_dir / "introduction.md"
    if not introduction.is_file():
        raise SystemExit(f"缺少 {introduction}")

    plans = parse_outline(outline)
    chapters = discover_chapters(book_dir)
    if [number for number, _path in chapters] != list(range(1, len(plans) + 1)):
        raise SystemExit(f"{book_dir}: chapterN.md 必须完整覆盖目录中的所有章节")
    for number, path in chapters:
        validate_chapter(number, path, plans)
    validate_images(introduction)

    parts = [introduction.read_text(encoding="utf-8").rstrip()]
    active_part = ""
    for number, path in chapters:
        plan = plans[number - 1]
        if plan.part_title != active_part:
            active_part = plan.part_title
            parts.extend(
                ["", "```{=latex}", rf"\part{{{latex_escape(active_part)}}}", "```", ""]
            )
        parts.extend(
            [
                "",
                "```{=latex}",
                rf"\setcounter{{chapter}}{{{number - 1}}}",
                "```",
                "",
                path.read_text(encoding="utf-8").rstrip(),
            ]
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(parts) + "\n", encoding="utf-8")
    return [introduction, *(path for _number, path in chapters)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--book-dir", type=Path, required=True)
    parser.add_argument("--outline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sources = assemble(args.book_dir, args.outline, args.output)
    print("正文顺序：" + "、".join(path.name for path in sources))


if __name__ == "__main__":
    main()
