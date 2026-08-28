// 全书 PDF 封面。

#import "@preview/inelegant-note:0.9.1": page-all, sans-font

#let ink = rgb("#1C2530")
#let muted = rgb("#667085")
#let accent = rgb("#4D6BFE")
#let accent-dark = rgb("#253A9B")
#let rule-colour = rgb("#D9DEEF")

#let repository-url = "https://github.com/Prism-Shadow/deepseek-harness-book"

#let fish-mark(width: 10mm) = image("/book/assets/fish-mark.svg", width: width)

#let github-mark(width: 4.2mm) = image("/book/assets/github-mark.svg", width: width)

// 在指定坐标上竖直居中放置内容。
#let _at(dx: 0mm, dy: 0mm, height: 10mm, body) = place(
  top + center,
  dx: dx,
  dy: dy - height / 2,
  box(height: height, align(horizon, body)),
)

#let cover-page(lead: [], brand: [], subtitle: []) = {
  set page(
    width: page-all.width,
    height: page-all.height,
    margin: 0mm,
    numbering: none,
    header: none,
    footer: none,
  )
  set text(font: sans-font, fill: ink)

  // 页眉的品牌签名：鱼形标记 + 字标 + 分隔线。
  place(top + left, dx: 22mm, dy: 20mm, fish-mark(width: 10mm))
  place(
    top + left,
    dx: 36mm,
    dy: 20mm,
    box(height: 10mm, align(horizon, text(size: 8.5pt, weight: "bold", tracking: 0.15em)[
      DEEPSEEK HARNESS
    ])),
  )
  place(
    top + left,
    dx: 22mm,
    dy: 38mm,
    line(length: page-all.width - 44mm, stroke: 0.7pt + rule-colour),
  )

  // 书名：主书名沿用 DSHInk，产品名沿用品牌主色 DSHAccent。
  place(top + center, dy: 59mm, text(size: 29pt, weight: "bold", lead))
  place(top + center, dy: 91mm, text(size: 39pt, weight: "bold", fill: accent, brand))
  place(top + center, dy: 132mm, text(size: 16pt, fill: muted, subtitle))

  // 模型 — Harness — 工具的关系示意，中心距页底 69mm。
  let axis = page-all.height - 69mm
  let label(body) = text(size: 12pt, weight: "bold", fill: muted, body)
  _at(dx: -53mm, dy: axis, label[MODEL])
  _at(dx: 53mm, dy: axis, label[TOOLS])
  for dx in (-29.5mm, 29.5mm) {
    place(top + center, dx: dx, dy: axis, line(length: 11mm, stroke: 1pt + rule-colour))
  }
  for dx in (-35mm, 35mm) {
    _at(dx: dx, dy: axis, height: 2.7mm, circle(radius: 1.35mm, fill: accent, stroke: none))
  }
  _at(
    dy: axis,
    height: 15mm,
    box(
      width: 48mm,
      height: 15mm,
      fill: accent,
      radius: 2mm,
      align(center + horizon, text(size: 12pt, weight: "bold", fill: white)[DeepSeek Harness]),
    ),
  )

  // 页脚的 GitHub 仓库入口。
  place(
    bottom + center,
    dy: -28mm,
    text(size: 13pt, fill: muted)[本书后续更新内容请关注 GitHub 仓库],
  )
  place(
    bottom + center,
    dy: -18mm,
    link(repository-url)[
      #box(baseline: 0.8mm, github-mark())
      #h(2mm)
      #text(size: 11.5pt, fill: accent-dark, repository-url)
    ],
  )
}
