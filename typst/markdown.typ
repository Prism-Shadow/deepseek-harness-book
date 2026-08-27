// 用 cmarker 把 book/*.md 载入 Typst。
//
// 书稿正文是 Pandoc 风味的 Markdown，其中三处扩展语法 CommonMark 不认识：
//   1. 标题尾部的 `{#ch-1}` / `{#sec-1-1}` 锚点；
//   2. 图片尾部的 `{width=68%}` / `{.book-technical-figure width=72%}` 属性；
//   3. YAML front matter（只有 introduction.md 有）。
// 这里先把它们规范成 cmarker 支持的写法，再交给 cmarker 转换。

#import "@preview/cmarker:0.1.10"
#import "@preview/mitex:0.2.7": mitex
#import "@preview/zebraw:0.6.1": zebraw

// 书稿根目录，图片路径都相对于它。
#let book-root = "/book/"

#let _escape-attr(value) = value
  .replace("&", "&amp;")
  .replace("\"", "&quot;")
  .replace("<", "&lt;")
  .replace(">", "&gt;")

// 去掉 YAML front matter。
#let _strip-front-matter(src) = src.replace(
  regex("(?s)^---\r?\n.*?\r?\n---\r?\n"),
  "",
)

// 去掉标题尾部的 `{#id}`、`{.class}` 属性。
// 全书没有 `](#id)` 形式的交叉引用，这些锚点只服务于网页版，直接丢弃即可。
#let _strip-heading-attrs(src) = src.replace(
  regex("(?m)^(#{1,6}[ \t]+\\S.*?)[ \t]*\\{[#.][^}\n]*\\}[ \t]*$"),
  m => m.captures.at(0),
)

// 独占一行的图片：把 `{width=68%}` 之类的属性转成 `<img>`，cmarker 认识宽高。
#let _rewrite-images(src) = src.replace(
  regex("(?m)^!\\[([^\\]]*)\\]\\(([^)\\s]+)\\)(\\{[^}\n]*\\})?[ \t]*$"),
  m => {
    let alt = m.captures.at(0)
    let path = m.captures.at(1)
    let attrs = m.captures.at(2)
    let extra = ""
    if attrs != none {
      for key in ("width", "height") {
        let hit = attrs.match(regex(key + "[ \t]*=[ \t]*\"?([0-9.]+%?)\"?"))
        if hit != none {
          extra += " " + key + "=\"" + hit.captures.at(0) + "\""
        }
      }
    }
    "<img src=\"" + _escape-attr(path) + "\" alt=\"" + _escape-attr(alt) + "\"" + extra + ">"
  },
)

// --- Pandoc 原始 LaTeX 块 -----------------------------------------------
//
// 书稿里有 22 处 ```{=latex} 块，只有三种形态：
//   * \Needspace{..}：给 XeLaTeX 的分页提示，Typst 自己分页，直接丢弃；
//   * 单图 figure：\includegraphics + \caption；
//   * minipage 拼图：多张图并排，每张下面一行小字，整组共用一个 \caption。
// 这里把它们翻译成 `<!--raw-typst -->` 块，交给下面的 latex-figure 渲染。

#let _typst-str(value) = "\"" + value.replace("\\", "\\\\").replace("\"", "\\\"") + "\""

// `0.96\textwidth` -> 96%，`\linewidth` -> 100%
#let _tex-width(value) = {
  let hit = value.match(regex("^([0-9.]+)"))
  let ratio = if hit == none { 1.0 } else { float(hit.captures.at(0)) }
  str(calc.round(ratio * 100, digits: 2)) + "%"
}

#let _rewrite-latex-blocks(src) = src.replace(
  regex("(?ms)^```\\{=latex\\}\r?\n(.*?)\r?\n```[ \t]*$"),
  m => {
    let body = m.captures.at(0)
    let pieces = ()
    for hit in body.matches(regex(
      "\\\\includegraphics\\[width=([^\\]]*)\\]\\{([^}]*)\\}"
        + "(?:[ \t]*\r?\n[ \t]*\\\\par\\\\smallskip\\\\sffamily\\\\footnotesize[ \t]*([^\r\n]*))?"
    )) {
      let note = hit.captures.at(2)
      pieces.push(
        "("
          + "path: " + _typst-str(hit.captures.at(1)) + ", "
          + "width: " + _tex-width(hit.captures.at(0)) + ", "
          + "note: " + (if note == none { "none" } else { _typst-str(note.trim()) })
          + ")"
      )
    }
    if pieces.len() == 0 {
      // 只剩 \Needspace 之类的排版提示，Typst 用不上。
      return ""
    }
    let caption = body.match(regex("\\\\caption\\{([^}]*)\\}"))
    (
      "<!--raw-typst #latex-figure("
        + "caption: "
        + (if caption == none { "none" } else { _typst-str(caption.captures.at(0)) })
        + ", ("
        + pieces.join(", ")
        + (if pieces.len() == 1 { ",)" } else { ")" })
        + ") -->"
    )
  },
)

#let normalize(src) = _rewrite-images(_rewrite-latex-blocks(_strip-heading-attrs(_strip-front-matter(src))))

// --- 渲染 ---------------------------------------------------------------

// 图片路径相对 book/ 解析；正文里的图片都独占一行，统一渲染成带题注的图。
#let _plain-image(path, ..args) = image(
  if path.starts-with("/") or path.contains("://") { path } else { book-root + path },
  ..args,
)

#let _image(path, alt: none, ..args) = {
  let body = _plain-image(path, ..args)
  if alt == none or alt == "" {
    align(center, body)
  } else {
    figure(body, caption: alt)
  }
}

// 由 `_rewrite-latex-blocks` 生成的调用：单图直接排，多图按两列拼。
#let _latex-figure(items, caption: none) = {
  let cell(it) = {
    align(center)[
      #_plain-image(it.path, width: it.width)
      #if it.note != none [
        #v(0.4em, weak: true)
        #text(font: ("Source Han Sans SC",), size: 0.85em, it.note)
      ]
    ]
  }
  let body = if items.len() == 1 {
    cell(items.first())
  } else {
    grid(columns: (1fr, 1fr), column-gutter: 4mm, row-gutter: 4mm, ..items.map(cell))
  }
  if caption == none { align(center, body) } else { figure(body, caption: caption) }
}

// 代码块用模板自带的 zebraw 显示，行内代码保持默认。
//
// 书稿里有 21 个代码块的最长行超过版心宽度（最长 92 字符），Typst 不会折行，
// 所以先量一下自然宽度，超宽的块整块按比例缩小字号。
#let code-width = 145mm // = page-all.width - 2 * page-all.mar-x
#let _raw(body, block: false, ..args) = {
  let it = raw(body, block: block, ..args)
  if not block { return it }
  context {
    let avail = code-width - 4mm // 留出 zebraw 的内边距
    let natural = measure(it).width
    if natural > avail {
      show raw: set text(size: (avail / natural) * 1em)
      zebraw(numbering: false, it)
    } else {
      zebraw(numbering: false, it)
    }
  }
}

// 书稿里用 `<span class="prompt-title">提示词内容：</span>` 标注提示词块的抬头。
#let _span(attrs, body) = {
  if attrs.at("class", default: "") == "prompt-title" {
    strong(body)
  } else {
    body
  }
}

/// 渲染一个 Markdown 文件。
/// - path: 相对仓库根目录的路径，例如 `/book/chapter1.md`
/// - label-prefix: 标题标签前缀，避免各章同名小节的标签互相冲突
#let render-markdown(path, label-prefix: "") = cmarker.render(
  normalize(read(path)),
  // 正文含大量 `--flag`、`"路径"` 等技术写法，关掉智能标点以免被改写。
  smart-punctuation: false,
  math: mitex,
  set-document-title: false,
  label-prefix: label-prefix,
  html: (span: _span),
  scope: (
    image: _image,
    raw: _raw,
    latex-figure: _latex-figure,
  ),
)
