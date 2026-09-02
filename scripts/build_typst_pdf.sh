#!/usr/bin/env bash
# 用 Typst 构建全书 PDF：inelegant-note 模板 + cmarker 直接载入 book/*.md。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_DIR="$ROOT_DIR/output/pdf"
OUTPUT_PDF="$OUTPUT_DIR/DeepSeek Harness 实战指南.pdf"

if ! command -v typst >/dev/null 2>&1; then
  echo "缺少 typst。可从 https://github.com/typst/typst/releases 下载后放进 PATH。" >&2
  exit 1
fi

# 模板 inelegant-note 指定思源宋体 / 思源黑体，缺字体会退化成默认字体。
for family in "Source Han Serif SC" "Source Han Sans SC"; do
  if ! typst fonts | grep -x "$family" >/dev/null; then
    echo "缺少中文字体：$family" >&2
    echo "可从 Adobe 下载后解压到 ~/.local/share/fonts 并运行 fc-cache -f：" >&2
    echo "  https://github.com/adobe-fonts/source-han-serif/releases (09_SourceHanSerifSC.zip)" >&2
    echo "  https://github.com/adobe-fonts/source-han-sans/releases  (09_SourceHanSansSC.zip)" >&2
    exit 1
  fi
done

mkdir -p "$OUTPUT_DIR"

# 编译前检查目录、章节标题和图片引用。
python3 "$SCRIPT_DIR/prepare_book.py" \
  --book-dir "$ROOT_DIR/book" \
  --outline "$ROOT_DIR/book/outline.md"

# --root 指到仓库根目录，正文里的 /book/... 路径才能解析。
typst compile --root "$ROOT_DIR" "$ROOT_DIR/typst/main.typ" "$OUTPUT_PDF"

echo "已生成：$OUTPUT_PDF"
