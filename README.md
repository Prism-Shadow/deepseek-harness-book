# DSH Book

DeepSeek Harness 中文实战书稿与配套素材。

本书面向普通用户，从安装和第一次任务开始，通过桌面整理、深度调研、演示文稿、小游戏和个人网页等案例，带读者逐步掌握 DSH。后两部分介绍 DSH 的工作原理及 Skill、MCP、社区插件和自定义插件。

完整目录见 [`book/outline.md`](book/outline.md)。

## 当前分工

目前先推进第一部分。

| 作者 | 负责内容 |
| --- | --- |
| 徐意哲 | 第1、2章 |
| 余彦可 | 第3、4章 |
| 周雷骏 | 第5章 |
| 刘志豪 | 第6章 |
| 翟翔 | 第7章 |

## 仓库结构

```text
book/
  outline.md        全书目录
  chapter1.md       第1章正文
  ...
  chapter9.md       第9章正文
  assets/           截图和插图
docs/
  writing-guide.md  协作写作规范
```

各章使用 Markdown 编写。正文以实战步骤和截图为主，文字负责说明操作、解释结果和提醒容易出错的地方。提交前请阅读 [`docs/writing-guide.md`](docs/writing-guide.md)。

本机的 `deepseek-harness/` 目录用于核对实现，不属于书稿仓库，也不会提交到 GitHub。
