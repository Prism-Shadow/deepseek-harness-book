# 第二部分《理解 DSH》写作规划

状态：**已执行完毕，仅作存档**。2026-08-18 最新目录把第二部分收拢为两章，安全边界章移出正文，Cordis 部分合并为三节。本文记录的是此前的规划思路和源码出处，章号、节号均已不对应正文。
源码版本基准：`@deepseek-ai/dsh-root` 0.1.0-rc.5（本机 `deepseek-harness/` checkout）。

## 总体思路

第二部分与第一部分的关系是"解剖读者已经用过的东西"。第一部分留下了一批读者亲眼见过但没解释的界面元素，第 8 章每一节都从其中一个出发，讲完机制后回到一个读者能亲手验证的现象上。截图基本不用（少数复用第一部分的），改用 TikZ 示意图和少量公式。

每节的固定结构：

1. 现象。第一部分见过的一个界面元素或数字。
2. 机制。讲清楚它背后发生了什么，配一张图。
3. 亲手验证。一个不花钱或花很少钱的实验（看文件、跑命令、观察统计行）。
4. 深挖入口。一句话指向 DSH 自带文档，给想继续钻的读者留路。

### 三条可用的外部依托

- **DSH 源码自带文档**（双语，部分由源码生成并有 CI 门禁保证不漂移）：
  `docs/architecture.md`（总架构）、`docs/agent-lifecycle.md`（一轮对话 Mermaid 时序图）、
  `docs/tool-execution-pipeline.md`（工具管线流程图）、`docs/persistence-catalog.md`（全部会话事件目录）、
  `docs/cordis-primer.md`（插件框架五概念）、`docs/subsystems/`（约 45 个子系统页）。
  书里的图可以参照这些重画（简化到读者粒度），事实断言全部可对照核验。
- **learn-deepseek-harness**（github.com/Prism-Shadow/learn-deepseek-harness）：十课渐进式构建迷你 harness，
  三大支柱（一切皆插件 / Session Log 是唯一真相 / 对 KV Cache 极度敏感）与 DSH 设计一致。
  借它两样东西：支柱作为第 8 章的暗线；"用可观测数字验证理论"的教学法（如切换 append/prepend 看缓存命中率）。
  不照搬它的"动手造"路线，我们的读者是用户不是实现者。
- **免费验证入口**（不需要 API Key、不花钱）：
  `dsh --profile web --dump-config`（看真实插件树）、直接查看 `~/.dsh/sessions/**/session.jsonl`、
  UI 统计行与 Session log 按钮。花钱极少的：多轮对话看缓存命中率、`/compact`。

### 图和公式的排版约定

- 图用 TikZ 写在 Markdown 的 ```` ```{=latex} ```` 原生块里，构建管线已支持；用 preamble 里已有的品牌色。
  建议在 preamble 增加几个统一样式（如 `dshnode`、`dshseam`、`dsharrow`），第 8 章约 7 张图风格一致。
- 公式用 pandoc 数学语法，每个公式后必须跟一句白话解释。只在 8.5 集中出现，其他节不硬塞。
- "深入一点"的旁注框复用现有 quote 样式（左侧蓝竖线框）。

---

## 8.1 从聊天助手到 Agent Harness

**现象锚点**：第 1 章"你好"对话统计行显示"1 轮 · 1 步"；第 3 章整理桌面时同一位置是"1 轮 · N 步"。同样是发一句话，为什么步数不一样。

**机制内容**：
- 聊天机器人 = 一次请求一次回答；Agent = 一个循环。模型每次回答可以选择"直接说话"或"调用工具"，调了工具就把结果喂回去再来一轮，直到模型不再调工具。
- 正式术语（源码定义，`docs/architecture.md:65`）：**step = 一次模型请求加上它调用的工具；turn = 零个或多个 step**。统计行的"轮/步"就是这两个词（`session-stats` 包，README 解释了为什么数 `step/end` 事件而不是数回复条数）。
- Harness 的职责清单：组装请求（system prompt + 工具表 + 历史）、执行工具、记录日志、管理上下文。模型只负责"下一步说什么/调什么"。
- 循环真身：`packages/core/agent-loop/src/agent.ts` 的 `ReactLoopAgent`，`kick()` 里就是 `while (await this.turn()) {}`，可以引这一行。
- 旁注框：第 4 章用过的多 Agent 调研，本质是"子 agent 被当成一个工具"（`docs/architecture.md:102`），细讲留给 8.4。

**图**：
1. 聊天 vs Agent 循环对比图（左右两栏流程图）。
2. 一轮对话时序图（用户 → Harness → 模型 → 工具 → 模型 → 回复），参照 `docs/agent-lifecycle.md` 重画简化版。

**亲手验证**：给 DSH 一个必须动文件的小任务，看统计行步数 > 1；切到轨迹 tab 数一数模型请求次数，对上 step 定义。

## 8.2 一切皆插件：DSH 的模块化设计

**现象锚点**：第 2 章读者已经用动态插件换过主题；界面上"标准模式"那个下拉框。

**机制内容**：
- 核心论断（`docs/architecture.md:11-13`，可直接翻译引用）：产品的每个部分都是插件，包括模型适配器、工具注册表、会话日志、agent loop 本身，全部可以从配置替换，"没有特权核心可以打补丁"。
- 插件长什么样：一个带 `name` / `inject`（声明依赖）/ `apply(ctx)` 的函数（`docs/cordis-primer.md:9-13` 五个概念，挑三个讲：插件、context 服务仓库、typed events）。
- 证据：`packages/bundle/base/cordis.patch.yml:420-451` 里，`tools`（工具注册表）、`system-prompt`、`agent-loop`、`llm-deepseek`（模型适配器）和小小的 `tool-todo` 是长得一模一样的配置行。
- 组装顺序（`docs/architecture.md:27`）：空列表 → base bundle → web-app bundle → 用户的 `~/.dsh/cordis.patch.yml` → 命令行 `--patch`。用户改主题、换模型，本质都是在往这个叠层里加一行。
- "标准模式"的真身：agent preset，随包发布四个（minimal / standard / code / cordis，`apps/cli/config/agent-presets/`）。minimal 接近纯聊天（完整锁死的 system prompt、只有两个工具、无压缩），standard 是完整 coding agent，两者 YAML 对比就是"从聊天到 Agent"最直观的教材。code preset 只比 standard 多一行，效果是模型改写 TypeScript 程序批量调工具（引其注释"五次往返变一次"）。
- 与第 9 章分工：本节讲"是什么、为什么"，写插件的"怎么做"全部留给第 9 章。

**图**：配置叠层组装图（几层 patch 依次叠加成运行时插件树）。

**亲手验证**：跑 `dsh --profile web --dump-config`（不需要 key），在输出里找到 agent-loop 和 tool-todo 各一行；打开 minimal 和 standard 两个 preset 的 YAML 对比行数。

## 8.3 消息与会话

**现象锚点**：第 1 章界面右上角的 Session log 按钮；关掉 DSH 重开，会话还在。

**机制内容**：
- 一条消息的结构：`role` 只有 system / user / assistant 三种，内容是块（text / reasoning / image / tool-call / tool-result）。有个反直觉的设计值得点破：**工具结果是一条 user 消息**（`packages/llm/llm/src/message.ts:152-156`），从模型视角看，工具输出和用户输入一样都是"外界发生的事"。第 1 章截图里的 Think 行就是 reasoning 块。
- 会话不是消息数组，是**只增不改的事件日志**：`turn/start`、`user/message`、`assistant/chunk`、`tool/call`、`tool/result` 等 15 种核心事件（完整目录在 `docs/persistence-catalog.md`），一行一个存在 `~/.dsh/sessions/<项目目录>/<会话>/session.jsonl`。
- 模型看到的历史是从日志**投影**出来的（surface 机制，`deriveMessages()`，`packages/core/session/src/index.ts:726` 附近注释可引）：只有三种事件上表面（user/message、assistant/message、tool/result），表面操作只有 append 和 replace 两种。这为 8.5 的压缩埋伏笔。
- 铁律（`docs/architecture.md:96`）："**模型可见的必然被记录**"，任何进入模型请求的东西都能从日志重建。
- 崩溃恢复：重新加载时发现 `turn/start` 没有配对的 `turn/end`，就补一条 `interrupted` 结尾，日志永不截断。

**图**：事件日志 → surface 投影 → 模型可见消息的三层图（标出 append 与 replace）。

**亲手验证**：打开自己昨天那个会话的 `session.jsonl`，认出第一行 header、一条 `user/message`、一串 `assistant/chunk` 和最终的 `assistant/message`；对照书里的事件表。这是全章最有"祛魅"效果的实验。

## 8.4 工具调用与结果返回

**现象锚点**：第 1.3 节看过的工具卡片；权限确认弹窗；输入框旁的 Workspace Write 下拉。

**机制内容**：
- 模型是怎么"调工具"的：回复里带一个 tool-call 块（工具名 + JSON 参数），Harness 解析执行，把结果作为 tool/result 回填，模型再看一眼决定下一步。模型对每个工具知道的只有三样：name、description、parameters（`schemas()` 白名单投影，`packages/core/tools/src/index.ts:1234`），超时、并发安全性等全是宿主私有。
- 一次调用的完整管线（参照 `docs/tool-execution-pipeline.md` 重画）：`tool/call` 先落日志 → pre-execute 裁决（allow / deny / ask）→ ask 走人类审批 → 守卫链 → 执行 → post-execute → `tool/result` 落日志 → 回填。强调两个设计：调用在执行**之前**就记日志（崩溃后可知道"正做到哪"）；审批只影响结果，模型看不到审批过程本身。
- 权限的三层拼装："Workspace Write" 是一个**权限预设**，一个名字绑定两个旋钮：沙箱模式（read-only / workspace-write / danger-full-access，只管文件效果）+ 审批策略（ask / never）（`packages/interaction/permission-presets/src/index.ts:168-175`）。
- 并行与保守默认：只有工具显式声明 `isConcurrencySafe: true` 才允许并行，声明缺失、抛错、返回非 true 一律按独占处理，fail-closed（`packages/core/tools/src/index.ts:256-269`）。同样的保守设计还有：没有审批服务时 ask 自动变 deny。
- 旁注框 1：超时和"复读机"保护（timeout-policy 按工具自报预算掐表；repeat-tool-reminder 数连击在 3/5/8 次时劝告模型，但不强制）。
- 旁注框 2：子 agent 也是工具（呼应第 4 章），一个 `ctx.subagents` 接口后面从进程内 fork 到 Claude Code 都能挂。

**图**：工具调用时序图（模型 → 日志 → 裁决/审批 → 执行 → 日志 → 模型），把权限分层画成管线上的闸门。

**亲手验证**：让 DSH 写一个文件，在 Session log 里找到 `tool/call` 与 `tool/result` 两条事件并注意先后顺序；把权限切到 read-only 再让它写文件，观察拒绝长什么样。

## 8.5 上下文管理（公式集中在这一节）

**现象锚点**：第 1 章统计行"输入 7.7K tok · 缓存命中 0%"。两个当时没解释的数字，这节全部讲清。

**机制内容**，四块递进：

1. **一次请求里有什么**。上下文组装剖面：system prompt（分段按 order 拼接，从 harness 身份到各工具指引）+ 工具表 + 历史消息 + 运行时注入快照（第 1 章"上下文注入"卡片的真身，本质是一条特殊的 user 消息，内容变了才重新注入）。7.7K token 的来源就此拆开。
2. **token 怎么数**。给出 DSH 的估算公式（`packages/llm/token-meter/src/estimate.ts`，全文 88 行）：
   $t(\text{文本}) = \lceil \text{字符数}/4 \rceil + 4$，消息、工具调用、整个请求逐层累加；
   provider 返回真实用量后校准替换估算值。顺带解释上下文窗口 $W$ 是硬预算。
3. **缓存命中率为什么重要**。前缀缓存一条规则：从第一个 token 起逐字节一致的前缀免于重算，一处变动其后全部失效。由此推出 DSH 的纪律：只在末尾追加、工具表用与机器无关的固定排序、system prompt 保持稳定。命中率 = 缓存命中 token / 输入 token，直接影响首 token 延迟和费用。观察：第 1 轮 0%，第 2 轮起大幅上升。
4. **上下文满了怎么办**。三级手段按成本递进：
   - spill：超过 50KB 的工具输出直接落文件，给模型一个定位符（免进上下文）；
   - 剪枝：超预算的旧工具结果改写成"头 4096 字符 + 省略标记 + 尾部"（免模型调用）;
   - 压缩：总量超过阈值才花一次模型调用做摘要。触发公式（`packages/compaction/compaction-basic/src/config.ts`）：
     $\text{触发} = \lfloor 0.8 \cdot W \rfloor$，$\text{保留尾部} = \lfloor 0.16 \cdot W \rfloor$；
     先免费剪枝再复测，仍超阈值才摘要（两道门）。摘要骑在一条带 replace 操作的 user 消息上，
     旧事件仍完整留在日志里，呼应 8.3 的"日志只增不改"。
   所有默认值标注"当前版本默认，可配置"。

**图**：
1. 上下文组装剖面图（一根竖条从上到下：system 各段 → 工具表 → 历史 → 注入快照，旁边标 token 计数）。
2. 压缩前后对比图（`[u1, a2, …, u9, a10]` → `[S, u9, a10]`，参照 learn-deepseek-harness L06 的例子）。

**亲手验证**：连续聊五轮，看缓存命中率逐轮变化；跑一个长任务后执行 `/compact`，对比统计行输入 token 变小，再去 session.jsonl 里找 `compaction/start` / `summary` / `end` 三条事件。

---

## 落地注意事项

- **事实纪律不变**：本规划里所有数字（4:1 估算、0.8、0.16、50000、8192/4096、3/5/8）和行为断言都有源码出处（见各节括号内路径），成文时逐条复核当时版本，正文标注"默认值，可配置"。DSH 处于 rc 阶段，交稿前需要 diff 一次源码确认没漂移。
- **preamble 需要的小改动**：增加统一的 TikZ 图样式宏；确认 pandoc 数学公式在当前管线渲染正常（理论上开箱即用，写 8.5 前先构建验证一次）。
- **写作顺序建议**：8.3 → 8.4 → 8.5 → 8.2 → 8.1。中间三节是硬机制，先写；8.2 需要统摄性最强放后面写更稳；8.1 是导言性质，最后写才知道该预告什么。
- **篇幅预估**：8.5 最重（四块内容 + 两图 + 全部公式），8.1 最轻。如果 8.5 写爆了，spill/剪枝可以并成一小段。
- **第 9 章边界**：8.2 不出现任何"写插件"的操作步骤；Skill / MCP 在第 8 章只在需要处一笔带过。
