#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BOOK_DIR="$ROOT_DIR/book"
OUTPUT_DIR="$ROOT_DIR/output/pdf"
BUILD_DIR="$ROOT_DIR/tmp/pdfs/elegant-build"
OUTPUT_PDF="$OUTPUT_DIR/DSH-Book-样章.pdf"
OUTLINE_TEX="$BUILD_DIR/planned-outline.tex"
BOOK_MARKDOWN="$BUILD_DIR/book.md"

if ! command -v pandoc >/dev/null 2>&1; then
  echo "缺少 pandoc。macOS 可运行：brew install pandoc" >&2
  exit 1
fi

if command -v xelatex >/dev/null 2>&1; then
  XELATEX_BIN="$(command -v xelatex)"
elif [ -x "/Library/TeX/texbin/xelatex" ]; then
  XELATEX_BIN="/Library/TeX/texbin/xelatex"
elif [ -x "$HOME/Library/TinyTeX/bin/universal-darwin/xelatex" ]; then
  XELATEX_BIN="$HOME/Library/TinyTeX/bin/universal-darwin/xelatex"
else
  echo "缺少 XeLaTeX。请安装 TinyTeX 或 BasicTeX。" >&2
  exit 1
fi

TEX_BIN_DIR="$(dirname "$XELATEX_BIN")"
export PATH="$TEX_BIN_DIR:$PATH"
export TEXINPUTS="$BOOK_DIR//:$ROOT_DIR//:${TEXINPUTS:-}"

REQUIRED_TEX_FILES=(
  elegantbook.cls
  anyfontsize.sty
  titlesec.sty
  microtype.sty
  needspace.sty
  ragged2e.sty
  fvextra.sty
  setspace.sty
  csquotes.sty
  logreq.sty
  comment.sty
  colortbl.sty
  mwe.sty
  enumitem.sty
  esint.sty
  footmisc.sty
  mathrsfs.sty
  multirow.sty
  makecell.sty
  lipsum.sty
  hologo.sty
  listings.sty
  tocloft.sty
  tikz.sty
  tcolorbox.sty
  tikzfill.image.sty
  pdfcol.sty
  fixtounicode.sty
  ctex.sty
  FandolSong-Regular.otf
  TeXGyreTermesX-Regular.otf
  texgyreheros-regular.otf
  texgyrecursor-regular.otf
  bbding.sty
  manfnt.sty
  adforn.sty
)

for tex_file in "${REQUIRED_TEX_FILES[@]}"; do
  if ! kpsewhich "$tex_file" >/dev/null 2>&1; then
    echo "缺少 TeX 排版依赖：$tex_file" >&2
    echo "TinyTeX 可运行：tlmgr install elegantbook anyfontsize titlesec newtx tex-gyre ctex fandol needspace ragged2e fvextra setspace csquotes logreq comment colortbl mwe enumitem esint footmisc jknapltx multirow makecell lipsum hologo listings tocloft tcolorbox tikzfill pdfcol fixtounicode pgf microtype caption bbding manfnt adforn" >&2
    exit 1
  fi
done

mkdir -p "$OUTPUT_DIR" "$BUILD_DIR"

python3 "$SCRIPT_DIR/prepare_book.py" \
  --book-dir "$BOOK_DIR" \
  --outline "$BOOK_DIR/outline.md" \
  --output "$BOOK_MARKDOWN"

python3 "$SCRIPT_DIR/generate_outline_tex.py" \
  --outline "$BOOK_DIR/outline.md" \
  --output "$OUTLINE_TEX" \
  "$BOOK_MARKDOWN"

pandoc "$BOOK_MARKDOWN" \
  --from markdown+lists_without_preceding_blankline \
  --output "$OUTPUT_PDF" \
  --pdf-engine="$XELATEX_BIN" \
  --top-level-division=chapter \
  --number-sections \
  --metadata has-frontmatter=true \
  --metadata title="从零开始玩转 DeepSeek Harness" \
  --metadata subtitle="面向普通用户的 Agent 实践指南" \
  --metadata title-meta="从零开始玩转 DeepSeek Harness" \
  --metadata author-meta="" \
  -V documentclass=elegantbook \
  -V classoption=lang=cn \
  -V classoption=nofont \
  -V classoption=color=black \
  -V classoption=device=normal \
  -H "$BOOK_DIR/preamble.tex" \
  --include-before-body="$OUTLINE_TEX" \
  --highlight-style=kate \
  --resource-path="$ROOT_DIR:$BOOK_DIR" \
  --columns=80

echo "已生成：$OUTPUT_PDF"
