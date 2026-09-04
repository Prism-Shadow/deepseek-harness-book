# 宠物绘画 Skill 自我优化任务

完成 SVG 绘画、隐藏目标评分和 Skill 优化。本次最多执行 `{{ROUND_LIMIT}}` 轮。
如果这里仍然是占位符，立即停止并要求提供轮数，不得开始实验。

只允许创建或修改 `runs/`、`.dsh/skills/animal-drawing/SKILL.md` 和按顺序新增
的 `snapshots/` 快照。`snapshots/v0.md` 不得修改。不得列出、打开、读取、
搜索、复制或修改当前工作目录之外的文件。所有面向用户的说明和总结都使用
中文。

## 开始前

确认 `snapshots/v0.md` 与当前 `.dsh/skills/animal-drawing/SKILL.md` 内容一致，
并确认 `runs/scores.jsonl` 尚无评分记录。外部评测器必须视为黑盒。唯一允许
的工作目录外操作，是按下文给出的固定命令执行 `../evaluator/score.py`。
不得用任何工具查看或搜索 `../evaluator/` 中的文件，也不得自行探测评分规则。

## 每轮循环

1. 按顺序确定本轮编号，从 `round-00` 开始。除 `round-00` 外，创建本轮
   目录前必须先确认上一轮快照存在且与当前 Skill 内容一致。例如进入
   `round-01` 前必须确认 `snapshots/v1.md` 存在，进入 `round-02` 前必须
   确认 `snapshots/v2.md` 存在。检查失败时不得绘制或评分下一轮。检查通过
   后，为本轮创建对应的 `runs/round-XX/` 目录。
2. 读取并使用当前 `animal-drawing` Skill，在 512×512 的 SVG 画布上画一只宠物。
   只创建本轮目录中的 `candidate.svg`，不得载入、引用或嵌入外部图片，
   不得创建其他绘画文件或绘图代码。
3. 读取并检查 `candidate.svg`：
   - 根元素必须声明 SVG 命名空间，并设置 `width="512"`、
     `height="512"` 和 `viewBox="0 0 512 512"`；
   - 只能出现 `svg`、`g`、`rect`、`circle`、`ellipse`、`polygon`、
     `polyline`、`line` 和 `path` 元素；
   - 不得出现 `image`、`script`、`foreignObject`、`use`、`style`、
     `href`、`url()`、`@import`、外部字体或任何外部资源。
4. 检查通过后，用 `rsvg-convert` 把本轮 SVG 栅格化为同目录下的
   512×512 `candidate.png`：

   ```bash
   rsvg-convert \
     --format png \
     --width 512 \
     --height 512 \
     --background-color "#ffffff" \
     --output runs/round-XX/candidate.png \
     runs/round-XX/candidate.svg
   ```

   执行前将命令中的 `round-XX` 替换为本轮实际编号。运行
   `file runs/round-XX/candidate.png`，确认 PNG 尺寸为 512×512。
5. 运行固定评测一次：

   ```bash
   python3 ../evaluator/score.py \
     --image runs/round-XX/candidate.png \
     --output runs/round-XX/score.json \
     --ledger runs/scores.jsonl \
     --round round-XX
   ```

   执行前将三个 `round-XX` 都替换为本轮实际编号。评分满分 100 分，由三项
   直接相加：宠物种类 30 分、毛色 30 分、画面细节 40 分。宠物种类和毛色
   各有一个不公开的具体偏好；画面细节公开考察眼睛、鼻子、嘴、四肢、尾巴
   和毛发花纹是否清晰可见。评测器每轮返回 `species_score`、`color_score`、
   `detail_score` 三项得分和 `score` 总分，但不返回隐藏偏好的具体内容。
   每个轮次只能生成一张候选图并评分一次，不得人工复核或用额外图片探测目标。
6. 读取本轮 SVG、三项得分和总分，结合当前会话中此前各轮的绘画内容与
   分数变化，围绕宠物种类、毛色或画面细节做有控制的探索。每轮优先只改变
   其中一类变量，优先改善较低的分项，以便判断分数变化来自哪里。分数上升时
   保留该变量，分数下降时在下一轮回到当前最佳已知取值，再测试新的取值。
   如果本轮创下历史最高分，且提升能合理归因于本轮的受控改动，立即将得到
   支持的可复用规则写入 `.dsh/skills/animal-drawing/SKILL.md`，不得推迟到
   实验结束再集中更新。证据不足、结果持平、分数下降或现有 Skill 已经表达
   该规则时，保持 Skill 内容不变，不得为了制造版本差异而强行改写。
   - 只加入可复用的 SVG 宠物绘画规则；
   - 不得提及评测模型、文本描述、具体分数、轮次或本次实验；
   - 不得创建绘画说明或优化说明；
   - 修改后不得重新绘制或重新评分本轮图片。
7. 无论本轮是否修改了 Skill，都必须在进入下一轮之前保存一次当前 Skill
   快照。轮次和版本固定一一对应：`round-00` 保存 `snapshots/v1.md`，
   `round-01` 保存 `snapshots/v2.md`，依此类推，版本号始终等于轮次序号
   加一。不得跳号、合并多轮或只在 Skill 内容变化时保存快照。保存后确认
   本轮对应的快照文件确实存在，并使用 `cmp` 确认它与当前 Skill 完全一致。
   即使 Skill 内容没有变化，也必须实际执行一次复制命令来生成本轮快照。
8. 如果已经完成 `{{ROUND_LIMIT}}` 轮，立即停止；否则使用更新后的 Skill
   进入下一轮。

停止后，用中文报告各轮分数、每次 Skill 改动摘要和全部产物路径。
