#!/usr/bin/env python3
"""Render the canonical three-part outline as LaTeX front matter."""

from __future__ import annotations

import argparse
from pathlib import Path

from prepare_book import parse_outline, read_headings


CHINESE_PART_NUMBERS = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]


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


def collect_identifiers(paths: list[Path]) -> set[str]:
    identifiers: set[str] = set()
    for path in paths:
        for _level, _title, identifier, _line_number in read_headings(path):
            if not identifier:
                continue
            if identifier in identifiers:
                raise SystemExit(f"{path}: 重复的标题 ID: {identifier}")
            identifiers.add(identifier)
    return identifiers


def render_outline(outline: Path, actual: list[Path], output: Path) -> None:
    plans = parse_outline(outline)
    identifiers = collect_identifiers(actual)
    result = [r"\begin{hhplannedoutline}"]
    if "content-intro" in identifiers:
        result.append(r"\hhplanfront{导言}{content-intro}")

    active_part = ""
    part_number = 0
    for chapter in plans:
        if chapter.part_title != active_part:
            active_part = chapter.part_title
            part_number += 1
            result.append(
                rf"\hhplanpart{{第{CHINESE_PART_NUMBERS[part_number - 1]}部分}}"
                rf"{{{latex_escape(active_part)}}}"
            )
        chapter_label = f"ch-{chapter.number}" if f"ch-{chapter.number}" in identifiers else ""
        result.append(
            rf"\hhplanchapter{{{chapter.number}}}{{{latex_escape(chapter.title)}}}{{{chapter_label}}}"
        )
        for section in chapter.sections:
            identifier = f"sec-{chapter.number}-{section.number}"
            label = identifier if identifier in identifiers else ""
            result.append(
                rf"\hhplansection{{{chapter.number}.{section.number}}}"
                rf"{{{latex_escape(section.title)}}}{{{label}}}"
            )

    result.append(r"\end{hhplannedoutline}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(result) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("sources", type=Path, nargs="+")
    args = parser.parse_args()
    render_outline(args.outline, args.sources, args.output)


if __name__ == "__main__":
    main()
