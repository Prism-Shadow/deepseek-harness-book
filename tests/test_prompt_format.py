from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book"
PROMPT_TITLE = '> <span class="prompt-title">提示词内容：</span>'


class PromptFormatTest(unittest.TestCase):
    def test_all_prompt_titles_use_the_standard_blockquote(self) -> None:
        count = 0
        for path in sorted(BOOK.glob("chapter*.md")):
            lines = path.read_text(encoding="utf-8").splitlines()
            for index, line in enumerate(lines):
                if "提示词内容：" not in line:
                    continue
                count += 1
                self.assertEqual(line, PROMPT_TITLE, f"{path.name}:{index + 1}")
                self.assertLess(index + 2, len(lines), f"{path.name}:{index + 1}")
                self.assertEqual(lines[index + 1], ">", f"{path.name}:{index + 2}")
                self.assertTrue(
                    lines[index + 2].startswith("> "),
                    f"{path.name}:{index + 3}",
                )
        self.assertGreater(count, 0)


if __name__ == "__main__":
    unittest.main()
