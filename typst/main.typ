// 《从零开始玩转 DeepSeek Harness》Typst 版
//
// 排版基于 inelegant-note 模板，正文由 cmarker 从 book/*.md 直接载入，
// 部分与章节顺序读取 book/outline.md（全书目录的唯一依据）。

#import "@preview/inelegant-note:0.9.1": *
#import "markdown.typ": render-markdown

#let accent = rgb("#253A9B")
#let muted = rgb("#5B6478")

// 封面主图：沿用现有 PDF 封面「模型 — Harness — 工具」的关系示意。
#let cover-art = {
  set text(font: ("Source Han Sans SC",), fill: muted, weight: "bold")
  align(center + horizon)[
    #v(1fr)
    #text(size: 8.5pt, tracking: 2pt, fill: black)[DEEPSEEK HARNESS]
    #v(2fr)
    #grid(
      columns: (auto, 14mm, auto, 14mm, auto),
      align: horizon,
      text(size: 11pt)[MODEL],
      line(length: 100%, stroke: 0.8pt + muted),
      box(
        fill: accent,
        radius: 2mm,
        inset: (x: 6mm, y: 4mm),
        text(size: 11pt, fill: white)[DeepSeek Harness],
      ),
      line(length: 100%, stroke: 0.8pt + muted),
      text(size: 11pt)[TOOLS],
    )
    #v(3fr)
  ]
}

#cover-environment(
  title: [从零开始玩转 DeepSeek Harness],
  subtitle: "面向普通用户的 Agent 实践指南",
  author: "Prism-Shadow/dsh-book",
  cover-image: cover-art,
)

#show: overall

// 模板默认的代码字体是 Consolas，本机没有，换成等宽的 DejaVu Sans Mono，
// 中文仍由思源黑体兜底。
#show raw: set text(
  font: ((name: "DejaVu Sans Mono", covers: "latin-in-cjk"), "Source Han Sans SC"),
)

// 书稿用引用块承载提示词，给它一条主色竖线，和正文区分开。
#show quote.where(block: true): it => block(
  width: 100%,
  inset: (left: 1em, y: 0.6em),
  stroke: (left: 2pt + accent),
  it.body,
)

#front-matter[
  #render-markdown("/book/introduction.md", label-prefix: "intro-")

  #my-outline()
]

#show: main-matter

// 从 outline.md 解析「部分 / 章」的顺序。
#let book-plan = {
  let items = ()
  for line in read("/book/outline.md").split("\n") {
    let text = line.trim()
    if text.starts-with("# ") {
      let hit = text.slice(2).trim().match(regex("^第[^\\s　]+部分[\\s　]+(.+)$"))
      if hit != none {
        items.push((kind: "part", title: hit.captures.at(0)))
      }
    } else if text.starts-with("## ") {
      let hit = text.slice(3).trim().match(regex("^第([0-9]+)章"))
      if hit != none {
        items.push((kind: "chapter", number: int(hit.captures.at(0))))
      }
    }
  }
  items
}

#for item in book-plan {
  if item.kind == "part" {
    part-page(item.title)
  } else {
    // 模板的章标题里用 `counter(image)` 复位图表计数，在 Typst 0.15 上不生效，
    // 会让图号一路累加（图 9.78）。这里按章显式复位。
    counter(figure.where(kind: image)).update(0)
    counter(figure.where(kind: table)).update(0)
    counter(figure.where(kind: raw)).update(0)
    counter(math.equation).update(0)
    render-markdown(
      "/book/chapter" + str(item.number) + ".md",
      label-prefix: "ch" + str(item.number) + "-",
    )
  }
}
