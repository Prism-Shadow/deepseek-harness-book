// 封面，移植自 book/preamble.tex 里的 \maketitle。
//
// LaTeX 版和本模板的开本都是 185×260mm，所以坐标 1:1 沿用。品牌色、鱼形标记
// 的路径数据和仓库地址都直接从 preamble.tex 读，两版共用一份定义，改一处即可。

#import "@preview/inelegant-note:0.9.1": page-all, sans-font

#let _preamble = read("/book/preamble.tex")

#let _tex-value(pattern) = {
  let hit = _preamble.match(regex(pattern))
  assert(hit != none, message: "book/preamble.tex 里找不到：" + pattern)
  hit.captures.at(0)
}

// \definecolor{DSHAccent}{HTML}{4D6BFE}
#let brand-color(name) = rgb(
  "#" + _tex-value("\\\\definecolor\\{" + name + "\\}\\{HTML\\}\\{([0-9A-Fa-f]{6})\\}"),
)

#let ink = brand-color("DSHInk")
#let muted = brand-color("DSHMuted")
#let accent = brand-color("DSHAccent")
#let accent-dark = brand-color("DSHAccentDark")
#let rule-colour = brand-color("DSHRule")

#let repository-url = _tex-value("\\\\newcommand\\{\\\\DSHRepositoryURL\\}\\{([^}]*)\\}")

// dsh 官方鱼形标记，viewBox 0 0 23.16 17.04，路径数据取自 preamble.tex。
#let _fish-path = _tex-value("\\\\newcommand\\{\\\\DSHFishPathData\\}\\{([^}]*)\\}")

#let fish-mark(width: 10mm, fill: accent) = image(
  bytes(
    "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 23.16 17.04\">"
      + "<path d=\"" + _fish-path + "\" fill=\"" + fill.to-hex() + "\"/>"
      + "</svg>"
  ),
  format: "svg",
  width: width,
)

#let github-mark(width: 4.2mm) = image("/book/assets/github-mark.svg", width: width)

// 竖直居中地放一段内容：TikZ 的 anchor=west / anchor=center 对应到这里。
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
  place(top + left, dx: 22mm, dy: 20mm, fish-mark(width: 10mm, fill: ink))
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
