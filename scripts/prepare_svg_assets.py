#!/usr/bin/env python3
"""Convert Markdown SVG images to temporary vector PDFs for XeLaTeX."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path


IMAGE = re.compile(r"(!\[[^]]*]\()([^\s)]+)((?:\s+['\"][^'\"]*['\"])?\))")


def convert(markdown: Path, book_dir: Path, output_dir: Path) -> int:
    converter = shutil.which("rsvg-convert")
    if converter is None:
        raise SystemExit(
            "书稿引用了 SVG，但缺少 rsvg-convert。macOS 可运行：brew install librsvg"
        )

    converted: dict[str, Path] = {}

    def replace(match: re.Match[str]) -> str:
        target = match.group(2)
        if "://" in target or target.startswith("data:"):
            return match.group(0)
        if Path(target).suffix.lower() != ".svg":
            return match.group(0)

        source = (book_dir / target).resolve()
        if not source.is_file():
            raise SystemExit(f"SVG 图片不存在：{source}")
        try:
            relative = source.relative_to(book_dir.resolve())
        except ValueError as error:
            raise SystemExit(f"SVG 图片必须位于 book/ 目录：{source}") from error

        destination = (output_dir / relative).with_suffix(".pdf")
        if target not in converted:
            destination.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                [converter, "--format=pdf", f"--output={destination}", str(source)],
                check=True,
            )
            converted[target] = destination
        return f"{match.group(1)}{destination.resolve()}{match.group(3)}"

    text = markdown.read_text(encoding="utf-8")
    markdown.write_text(IMAGE.sub(replace, text), encoding="utf-8")
    return len(converted)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--book-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    count = convert(args.markdown, args.book_dir, args.output_dir)
    if count:
        print(f"SVG 矢量转译：{count} 张")


if __name__ == "__main__":
    main()
