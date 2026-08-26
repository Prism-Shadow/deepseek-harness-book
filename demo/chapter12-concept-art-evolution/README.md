# 第 12 章概念图自进化配套文件

本目录保存第 12 章“让 dsh 通过自进化画出概念图”案例的绘画侧文件，包括初始 Skill、演化后的 Skill、任务提示和两张 SVG 结果图。

目录分成三部分：

- `starter/` 是实验开始前的工作区，包含规则很少的 `animal-drawing` Skill 和对应的初始快照。
- `evolved/` 保存第 8 轮高分图，以及当时已经积累四条绘画策略的 Skill。
- `reuse/` 保存新会话读取最终 Skill 后生成的图片。

`evolution-prompt.md` 是本次实验使用的任务提示。运行前需要把 `{{ROUND_LIMIT}}` 替换为实际轮数，并准备一个位置固定、评分规则不变的评测命令。评测器属于实验环境，没有放进 dsh 工作区，本目录只保留绘画侧文件。

如果只想验证最终 Skill 是否可用，可以新建一个空工作区，将 `evolved/.dsh/` 复制进去，再把 `reuse-prompt.md` 交给 dsh。生成结果可以与 `evolved/high-score.svg` 和 `reuse/candidate.svg` 对照。
