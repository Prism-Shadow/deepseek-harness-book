#import "@preview/inelegant-note:0.9.1": *
#import "markdown.typ": render-markdown
#import "cover.typ": accent, cover-page

#set document(title: "从零开始玩转 DeepSeek Harness")

#cover-page(
  lead: [从零开始玩转],
  brand: [DeepSeek Harness],
  subtitle: [面向普通用户的 Agent 实践指南],
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
