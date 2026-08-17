# DSH Book

DeepSeek Harness 中文实战书稿与配套素材。

本书面向普通用户，从安装和第一次任务开始，通过桌面整理、深度调研、演示文稿、小游戏和个人网页等案例，带读者逐步掌握 DSH。后两部分介绍 DSH 的工作原理及 Skill、MCP、社区插件和自定义插件。

完整目录见 [`book/outline.md`](book/outline.md)。

## 仓库结构

```text
book/
  outline.md        全书目录
  introduction.md   内容简介
  chapter1.md       第1章正文
  ...
  chapter9.md       第9章正文
  assets/           截图和插图
  preamble.tex      PDF 排版主题
docs/
  writing-guide.md  协作写作规范
scripts/
  build_pdf.sh      PDF 构建入口
output/pdf/         本地构建产物
```

各章使用 Markdown 编写。正文以实战步骤和截图为主，文字负责说明操作、解释结果和提醒容易出错的地方。提交前请阅读 [`docs/writing-guide.md`](docs/writing-guide.md)。

本机的 `deepseek-harness/` 目录用于核对实现，不属于书稿仓库，也不会提交到 GitHub。

## 构建 PDF

在仓库根目录运行：

```bash
./scripts/build_pdf.sh
```

脚本会校验目录和章节标题，汇总 Markdown，并使用 Pandoc 与 XeLaTeX 生成 `output/pdf/DSH-Book-样章.pdf`。本机需要安装 Pandoc、XeLaTeX 和脚本提示的 TeX 组件。

每次推送和拉取请求都会触发 GitHub Actions。流水线会检查 Python 与 Shell 脚本、运行测试、构建 PDF，并上传 `dsh-book-pdf` 构建产物。
