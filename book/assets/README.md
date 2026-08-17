# 图片目录

各章截图分别放在 `chapter1/` 至 `chapter9/` 子目录中。文件名使用 `章-节-序号-内容.png`，正文通过相对路径引用。

提交截图前，检查图片中没有 API Key、访问令牌、个人路径、内部网址和其他敏感信息。

封面、目录和篇章页上的鲸鱼标识不是图片文件：它是从 DSH 源码（`packages/client/ui-primitives/src/FishLogo.tsx`）里的官方矢量路径抄来的，直接用 TikZ 画在 `book/preamble.tex` 的 `\DSHFishMark` 命令里，缩放到任何尺寸都不会糊。
