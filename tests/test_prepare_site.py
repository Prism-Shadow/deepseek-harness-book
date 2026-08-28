from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from prepare_site import (  # noqa: E402
    prepare_site,
    transform_markdown,
    transform_readme,
)


class PrepareSiteTest(unittest.TestCase):
    def test_prepares_readme_as_web_homepage(self) -> None:
        source = """# 示例

![图片](book/assets/example.png)

[在线阅读](https://dshbook.penguin.ooo/)
[开始](https://dshbook.penguin.ooo/chapter1/)
[Demo](demo/example/)
"""
        rendered = transform_readme(source, "https://github.com/example/book")
        self.assertIn("title: DeepSeek Harness 实战指南", rendered)
        self.assertIn("source_edit_path: README.md", rendered)
        self.assertIn("![图片](assets/example.png)", rendered)
        self.assertIn("[在线阅读](index.md)", rendered)
        self.assertIn("[开始](chapter1.md)", rendered)
        self.assertIn(
            "[Demo](https://github.com/example/book/tree/main/demo/example)",
            rendered,
        )

    def test_adds_visible_caption_to_standalone_markdown_image(self) -> None:
        source = (
            "正文。\n\n"
            "![示例截图](assets/example.png){#fig-example width=82%}\n"
        )
        rendered = transform_markdown(source)
        self.assertIn(
            '<figure class="book-figure" id="fig-example" markdown>',
            rendered,
        )
        self.assertIn(
            "![示例截图](assets/example.png)"
            '{ .book-figure-image width=82% loading="lazy" }',
            rendered,
        )
        self.assertIn("<figcaption>示例截图</figcaption>", rendered)

    def test_does_not_rewrap_images_in_code_or_existing_figure(self) -> None:
        source = """```markdown
![代码示例](assets/code.png)
```

<figure class="book-figure" markdown>
![已有图片](assets/existing.png)
<figcaption>已有说明</figcaption>
</figure>
"""
        rendered = transform_markdown(source)
        self.assertEqual(rendered.count('<figure class="book-figure"'), 1)
        self.assertNotIn("<figcaption>代码示例</figcaption>", rendered)
        self.assertEqual(rendered.count("<figcaption>已有说明</figcaption>"), 1)

    def test_preserves_and_numbers_image_grid(self) -> None:
        source = """<figure class="book-figure book-figure-grid" markdown>

<div class="book-figure-item" markdown>
![第一张图](assets/one.png){.book-figure-image width=88%}
<span class="book-figure-note">第一张图的说明</span>
</div>

<div class="book-figure-item" markdown>
![第二张图](assets/two.png){.book-figure-image width=88%}
<span class="book-figure-note">第二张图的说明</span>
</div>

<figcaption>两张示例图</figcaption>
</figure>
"""
        rendered = transform_markdown(source, chapter_number=3)
        self.assertIn('class="book-figure book-figure-grid"', rendered)
        self.assertIn('id="fig-3-1"', rendered)
        self.assertIn("第一张图的说明", rendered)
        self.assertIn(
            '<figcaption><span class="book-figure-number">'
            "图 3.1</span> 两张示例图</figcaption>",
            rendered,
        )

    def test_rejects_raw_latex_block(self) -> None:
        source = "```{=latex}\n\\Needspace{18\\baselineskip}\n```\n"
        with self.assertRaisesRegex(SystemExit, "不再支持 LaTeX 原始块"):
            transform_markdown(source)

    def test_copies_assets_byte_for_byte(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            book = root / "book"
            assets = book / "assets"
            assets.mkdir(parents=True)
            image = b"\x89PNG\r\n\x1a\nunchanged"
            (assets / "example.png").write_bytes(image)
            (book / "outline.md").write_text(
                "# 第一部分　示例\n\n## 第1章　开始\n\n### 1.1 阅读\n",
                encoding="utf-8",
            )
            (book / "introduction.md").write_text(
                "---\ntitle: 示例书\n---\n\n# 导言\n",
                encoding="utf-8",
            )
            (book / "chapter1.md").write_text(
                "# 开始 {#ch-1}\n\n## 阅读 {#sec-1-1}\n\n"
                "![示例](assets/example.png)\n",
                encoding="utf-8",
            )
            (root / "README.md").write_text(
                "# 示例首页\n\n![示例](book/assets/example.png)\n",
                encoding="utf-8",
            )
            site_assets = root / "site"
            site_assets.mkdir()
            output = root / "output" / "site-src"
            prepare_site(book, output, site_assets)
            self.assertEqual((output / "assets/example.png").read_bytes(), image)
            self.assertIn("示例首页", (output / "index.md").read_text())
            self.assertIn("# 导言", (output / "introduction.md").read_text())
            self.assertIn(
                "source_edit_path: book/introduction.md",
                (output / "introduction.md").read_text(),
            )


if __name__ == "__main__":
    unittest.main()
