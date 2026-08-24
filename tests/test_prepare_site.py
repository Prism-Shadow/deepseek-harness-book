from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from prepare_site import prepare_site, transform_markdown  # noqa: E402


class PrepareSiteTest(unittest.TestCase):
    def test_converts_latex_image_without_reencoding(self) -> None:
        source = r"""正文。

```{=latex}
\begin{figure}[H]
\includegraphics[width=0.82\textwidth]{assets/example.png}
\caption{示例截图}
\end{figure}
```
"""
        rendered = transform_markdown(source)
        self.assertIn("![示例截图](assets/example.png)", rendered)
        self.assertIn('style="width: 82%;"', rendered)
        self.assertNotIn("includegraphics", rendered)

    def test_removes_pdf_only_layout_command(self) -> None:
        source = "before\n\n```{=latex}\n\\Needspace{18\\baselineskip}\n```\n\nafter\n"
        rendered = transform_markdown(source)
        self.assertIn("before", rendered)
        self.assertIn("after", rendered)
        self.assertNotIn("Needspace", rendered)

    def test_preserves_figure_anchor_for_web_reference(self) -> None:
        source = r"""图 \ref{fig-1-1}。

```{=latex}
\includegraphics[width=0.8\textwidth]{assets/example.png}
\caption{示例截图}
\label{fig-1-1}
```
"""
        rendered = transform_markdown(source)
        self.assertIn("[图](#fig-1-1)", rendered)
        self.assertIn('id="fig-1-1"', rendered)

    def test_converts_known_tikz_diagram(self) -> None:
        source = r"""```{=latex}
\begin{tikzpicture}
\end{tikzpicture}
\captionof{figure}{用摘要替代较早历史，同时保留近期消息原文}
\label{fig-11-5}
```
"""
        rendered = transform_markdown(source)
        self.assertIn('id="fig-11-5"', rendered)
        self.assertIn("早期内容摘要", rendered)
        self.assertNotIn("tikzpicture", rendered)

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
            (book / "introduction.md").write_text("# 简介\n", encoding="utf-8")
            (book / "chapter1.md").write_text(
                "# 开始 {#ch-1}\n\n## 阅读 {#sec-1-1}\n\n"
                "![示例](assets/example.png)\n",
                encoding="utf-8",
            )
            site_assets = root / "site"
            site_assets.mkdir()
            output = root / "output" / "site-src"
            prepare_site(book, output, site_assets)
            self.assertEqual((output / "assets/example.png").read_bytes(), image)


if __name__ == "__main__":
    unittest.main()
