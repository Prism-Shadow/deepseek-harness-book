from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from prepare_book import assemble, parse_outline  # noqa: E402


OUTLINE = """# 第一部分　使用 DSH

## 第1章　初识 DSH

### 1.1 安装 DSH

# 第二部分　理解 DSH

## 第2章　工作原理

### 2.1 消息与会话
"""


class PrepareBookTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.book = Path(self.temp.name) / "book"
        self.book.mkdir()
        (self.book / "outline.md").write_text(OUTLINE, encoding="utf-8")
        (self.book / "introduction.md").write_text(
            "# 内容简介 {.unnumbered #content-intro}\n\n正文。\n",
            encoding="utf-8",
        )
        (self.book / "chapter1.md").write_text(
            "# 初识 DSH {#ch-1}\n\n## 安装 DSH {#sec-1-1}\n",
            encoding="utf-8",
        )
        (self.book / "chapter2.md").write_text(
            "# 工作原理 {#ch-2}\n\n## 消息与会话 {#sec-2-1}\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_outline_preserves_parts_and_chapter_numbers(self) -> None:
        plans = parse_outline(self.book / "outline.md")
        self.assertEqual([plan.part_title for plan in plans], ["使用 DSH", "理解 DSH"])
        self.assertEqual([plan.number for plan in plans], [1, 2])

    def test_assembly_inserts_part_pages(self) -> None:
        output = Path(self.temp.name) / "book.md"
        assemble(self.book, self.book / "outline.md", output)
        rendered = output.read_text(encoding="utf-8")
        self.assertIn(r"\part{使用 DSH}", rendered)
        self.assertIn(r"\part{理解 DSH}", rendered)
        self.assertLess(rendered.index("# 初识 DSH"), rendered.index("# 工作原理"))

    def test_wrong_section_id_fails(self) -> None:
        (self.book / "chapter2.md").write_text(
            "# 工作原理 {#ch-2}\n\n## 消息与会话 {#sec-2-9}\n",
            encoding="utf-8",
        )
        with self.assertRaises(SystemExit):
            assemble(self.book, self.book / "outline.md", Path(self.temp.name) / "book.md")


if __name__ == "__main__":
    unittest.main()
