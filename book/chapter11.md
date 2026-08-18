# Harness 的工作原理 {#ch-11}

## 从聊天助手到 Harness {#sec-11-1}

第 1 章那句“你好，请用一句话介绍你自己”，回复下面跟着一行“1 轮 · 1 步”；第 10 章让 DSH 去整理文件，同样是发一句话，那一行数字变成了“1 轮 · N 步”。都是打一句话回车，为什么有的只算一步，有的要算好几步。这道题的答案，就是理解 DSH 要迈的第一道门槛，DSH 跑的是一个循环。

聊天机器人的工作方式是一问一答，一次请求，一次回复，回复完这轮就彻底结束了。DSH 背后的模型多了一个选项，每次生成回复，除了直接说话，还可以选择“调用一个工具”。一旦模型选了调用工具，DSH 不会就此打住，而是先把工具真正执行了，把执行结果重新喂回给模型，让它再看一眼、再决定下一步。直到某一次它不再申请调用任何工具、只是把话说完，这一轮才算结束。这一整套“回复、执行、回填、再回复”反复打转的过程，就是 agent loop，也是“Agent”和“聊天机器人”之间唯一的分界线，聊天机器人的智能全在一次生成里，agent 的智能藏在这个循环转了几圈。

DSH 的文档给这个循环里的两个词下了精确定义（`docs/architecture.zh.md` 第 69 行）。一个**步骤**（step）是一次模型请求，加上这次请求申请调用的工具；一个**轮次**（turn）由零个或多个步骤组成，从领到第一条待处理的输入开始算起，一直到不再欠着任何工作才结束。界面统计行里的“轮 / 步”，说的就是这两个词，不是随口起的说法。“你好”那次，模型看到问题，直接组织语言回答，中间没有申请调用任何工具，一次模型请求就把这一轮的活干完，是 1 轮 1 步；整理桌面那次，模型第一次请求申请调用工具去看桌面上有什么，工具执行完把结果喂回去，模型看着这份结果再决定下一步该怎么整理，可能又申请调用一次工具。每一次“模型请求 + 它申请的工具”算一步，攒够了才关闭这一轮，步数自然就上去了。

定义里“零个步骤”那种情况是真会发生的。DSH 把一批输入送进模型之前，会先过一道 `agent/pre-step` 检查，插件在这里可以改写这批消息，也可以直接拒绝。一旦被拒绝，这一轮不会向模型发出任何请求，步数是零，但它照样先记了 `turn/start`、最后补上 `turn/end`，在会话日志里留下一条完整的轮次记录，只是这条记录没花掉任何一次模型调用（`docs/agent-lifecycle.zh.md` 的时序图里，被拒绝那条分支标着“该轮次不消耗任何步骤”，而 `turn/end` 画在分支之外，两条路都要经过它）。一件压根没发生的事也要老老实实记一笔，这个习惯 11.2 会讲清楚是为什么。

驱动这个循环的代码本身也是一个不算长的循环，核心类叫 `ReactLoopAgent`，跑起来之后一直在做的事就是一行代码，`while (await this.turn()) {}`（`packages/core/agent-loop/src/agent.ts:212`）。只要这一轮还没个了结，就接着跑下一轮，没有新输入、也没有欠着的工作了，循环才退出，跟本节的定义完全对应，不是另外一套东西。统计行里的“步数”，数的是 `step/end` 这个日志事件出现了几次。按气泡数，会把那些没吐出任何可见内容就失败或被取消的步骤漏掉；按事件数，一步不落（`packages/session/session-stats` 的说明文档原话）。

```{=latex}
\begin{center}
\begin{tikzpicture}[node distance=9mm and 12mm, every node/.style={align=center, font=\sffamily\footnotesize}]
  \node[dshnode] (u1) {用户\\一句话};
  \node[dshaccentnode, right=of u1] (m1) {模型\\第 1 次请求};
  \node[dshnodeflat, below=of m1] (chat) {直接回复\\（聊天机器人止步于此）};
  \node[dshseam, right=of m1] (tool) {申请\\调用工具};
  \node[dshnode, right=of tool] (exec) {执行工具\\结果回填};
  \draw[dsharrow] (u1) -- (m1);
  \draw[dsharrow] (m1) -- (chat);
  \draw[dsharrow] (m1) -- (tool);
  \draw[dsharrow] (tool) -- (exec);
  \draw[dsharrow] (exec.south) to[out=-90, in=-90] node[dshlabel, below=0.5mm] {第 2 次请求，再看一眼} (m1.south east);
\end{tikzpicture}
\end{center}
```

这个循环里，Harness（DSH 自己）和模型分工非常明确，模型只负责判断“接下来该说话还是该调用工具、调用哪个工具”，除此之外的一切都是 Harness 的活，拼好这次请求要发的内容（身份设定、工具清单、到目前为止的历史），真的把工具跑起来，把每一步、每一次调用原样记进日志，管住上下文不要爆掉。模型是循环里唯一的决策者，Harness 是循环本身、循环之外的一切基础设施，两者边界很干净。

> 深入一点。第 3 章用过的多 Agent 调研，看起来像是“另开了一个 AI”，但在这套循环模型里，子 agent 就是模型可以申请调用的一个工具（`docs/architecture.zh.md` 第 106 行）。调用它、等它跑完、把结果收回来，跟调用一个读文件的工具走的是同一条路径，只是这个“工具”内部自己又是一整个 agent loop。11.3 会具体讲工具调用这条路径，子 agent 这层实现细节留到讲插件扩展的章节。

**亲手验证**，给 DSH 一个必须动手改文件的任务，回复下面的统计行步数应该大于 1；切到“轨迹”标签页，数一数里面出现了几次完整的模型请求，应该正好和统计行报的步数对得上。这行数字是真的在数循环转了几圈，不是凭感觉估的。

## 消息与会话 {#sec-11-2}

第 1 章右上角有一个不起眼的按钮，叫“Session log”；第 1.3 节提过一句，说它能把整段记录导出成文件。当时没细讲的是，关掉 DSH 再重新打开，回到同一个工作区，那次对话居然还在，连当时的工具调用、耗时统计都分毫不差，是真的存在磁盘上了。一次对话在磁盘上到底是什么样子，值得打开看一眼。

打开这份导出文件会发现，里面是一行一个 JSON 对象、按时间顺序追加的事件流。会话开始时的一条 `session` 头信息，随后是权限模式、沙箱模式这些状态记录，再往下是 `turn/start`、`step/start`，然后才轮到对话内容本身，一条 `user/message`，几十条 `assistant/chunk`（模型逐字吐出的流式片段，用来保证界面回放和真实生成过程一致），一条汇总完的 `assistant/message`，如果这一步调用了工具，还会有 `tool/call` 和 `tool/result`，最后是 `step/end`、`turn/end`。DSH 的会话持久化目录（`docs/persistence-catalog.md`）里记录在案的事件类型有四十多种，绝大多数是像权限切换、审批询问、后台任务这类“记一笔账”的日志，跟模型这一轮说了什么没有关系。

这就是第一个要澄清的事实，**会话在磁盘上的真身，是一份只能追加、不能篡改的事件日志**，界面上看起来一问一答的消息列表，只是这份日志的一种呈现方式。模型每次请求看到的历史，是从这份日志里“投影”出来的。负责投影的函数叫 `deriveMessages()`，在 `session` 包的 `src/index.ts:726`。四十多种事件里，会被投影成一条模型可见消息的只有三种，`user/message`、`assistant/message`、`tool/result`，官方文档管这三种叫 surface（表面）事件。一条事件加入 surface 的方式只有两种。`append`，追加到末尾，这是绝大多数消息的路径；`replace`，把一段连续的旧 surface 节点整体换成一个新节点，第 11.4 节要讲的压缩就是靠这个操作实现的。旧的原始事件依然完整地躺在日志里，只是不再出现在模型看到的那份投影里。日志本身永远不重写、不删除。

一条消息的结构也比看上去简单，`role` 只有 `system`、`user`、`assistant` 三种，内容由若干个块拼成，常见的有文本块、推理块（对应第 1 章回复里那一行“Think”）、图片块、工具调用块、工具结果块。这里有一个容易反直觉的设计，**工具执行的结果，在消息层面是一条 `role: 'user'` 的消息**（`packages/llm/llm/src/message.ts:150-156` 明确把 `ToolResultMessage` 定义成 `role: 'user'`）。从模型的视角看，它自己动手执行的工具产生的结果，跟人类在输入框里打字发过来的东西，走的是同一条“外界发生了什么”的通道。模型分不出，也不需要分出这条消息是人打的还是工具返回的，它只知道“轮到我看新情况了”。

DSH 的文档里把这条设计原则称为铁律，**模型可见即已记录**（`docs/architecture.zh.md:100`）。任何进入模型请求的内容，都必须能从日志重建出来，这是一条由运行时强制检查的不变量，不是约定俗成。这条铁律还带来一个实际的好处，进程意外退出也不会丢内容。重新打开一个会话时，如果 DSH 发现日志里有一个 `turn/start` 没等到配对的 `turn/end`，就知道上次是在这一轮中途被打断的，会补一条 `reason: { kind: 'interrupted' }` 的 `turn/end` 把这一轮正式收尾，日志既不截断也不需要人工修复（`docs/subsystems/persistence.md` “Crash recovery preserves an interrupted turn”）。

```{=latex}
\begin{center}
\begin{tikzpicture}[node distance=13mm, every node/.style={align=center}]
  \node[dshnodeflat, minimum width=118mm] (log) {会话事件日志（只增不改）\\[0.6mm] \scriptsize\ttfamily turn/start\ \ step/start\ \ user/message\ \ assistant/chunk*\\ \scriptsize\ttfamily assistant/message\ \ tool/call\ \ tool/result\ \ step/end\ \ turn/end};
  \node[dshseam, below=of log, minimum width=70mm] (surface) {surface 投影：append / replace\\ \footnotesize 只挑 user/message、assistant/message、tool/result};
  \node[dshaccentnode, below=of surface, minimum width=55mm] (messages) {模型看到的历史\\ \footnotesize deriveMessages()};
  \draw[dsharrow] (log) -- (surface);
  \draw[dsharrow] (surface) -- (messages);
\end{tikzpicture}
\end{center}
```

**亲手验证**，找一个自己之前做过的任务，比如第 1.2 节那次新建 `about-dsh.md`，打开对应会话，点右上角的“Session log”导出。导出的是解压好的纯文本，一行一个 JSON，直接用文本编辑器打开就能读。原始存档文件本身其实是 zstd 压缩过的（后缀是 `.jsonl.zstd`），Session log 按钮的作用之一就是替你把这层压缩摘掉。在导出的文本里，从头往下找。第一行是 `session` 头，往下能找到一条 `user/message`（就是当时打的那句任务描述），一串 `assistant/chunk`，如果 DSH 当时调用过工具，会有配对的 `tool/call` 和 `tool/result`，最后一条回复文本落在一条 `assistant/message` 里。把这几行跟本节的事件表对一遍，能对上，就说明“会话是事件日志、消息是投影出来的”这件事不是纸上谈兵。

> 深入一点。会话事件的完整目录、每个字段的类型和来源文件，都在 `docs/persistence-catalog.md` 里，这份文档由脚本从源码类型定义直接生成，跟代码不会脱节。想搞清楚某个具体字段（比如 `tool/result` 里的 `meta`）是干什么用的，去那里查最快。

## 工具调用与结果返回 {#sec-11-3}

第 1.3 节点开过一张工具卡片，看到过一次完整的文件差异；后面几章里，输入框旁边那个“Workspace Write”下拉框也一直挂在那，偶尔会跳出一个权限确认弹窗。模型说“我要读一下这个文件”“我要执行这条命令”的时候，从它开口到结果回到它眼前，中间这条路上站着哪些环节，是这一节要拆开的东西。

模型申请调用一个工具，靠的是回复里带的一个“工具调用块”，工具名加一段 JSON 参数，仅此而已。模型对每个工具的了解也仅限于此。工具的名字、一句描述、参数长什么样，这三样东西被称为 schema，是唯一进入提示词、喂给模型的信息（`packages/core/tools/src/index.ts` 的 `schemaOf()` 只挑这三个字段）。工具执行要多久超时、允不允许跟别的工具同时跑、内部要不要重试，这些全是宿主（Harness）自己知道、模型完全看不到的私有信息。这是一个刻意的设计，模型只负责“决定调用什么”，至于这次调用安不安全、划不划算，判断权全部留在 Harness 这一侧。

一次调用从请求发出到结果回填，要走一条固定的流水线。模型的回复一解析出工具调用块，DSH 立刻把这次调用记一条 `tool/call` 落进会话日志。注意，是**先记日志、再执行**，这样即使执行过程中进程崩了，重新打开也能从日志里看出“上次正做到哪一步”。落完日志才进入裁决，一连串权限、沙箱、钩子策略依次表态，给出允许、拒绝或者“问一下人类”三种结果之一；选择“问”的会转给审批服务弹出确认框，如果当前环境根本没有审批渠道（比如无人值守的自动化任务），策略上直接按拒绝处理。没有人能回答的问题，答案默认是“不行”，这是一条一以贯之的保守默认。裁决通过之后才执行工具本体，执行完再走一轮后处理，最终结果同样先落一条 `tool/result` 日志，再回填给模型看下一步该干什么。

```{=latex}
\begin{center}
\begin{tikzpicture}[node distance=8mm and 6mm, every node/.style={align=center, font=\footnotesize}]
  \node[dshnode] (call) {模型发起\\ 工具调用};
  \node[dshnodeflat, right=of call] (log1) {落日志\\ tool/call};
  \node[dshseam, right=of log1] (gate) {裁决\\ 允许 / 拒绝 / 询问};
  \node[dshaccentnode, right=of gate] (exec) {执行\\ 工具本体};
  \node[dshnodeflat, right=of exec] (log2) {落日志\\ tool/result};
  \node[dshnode, right=of log2] (back) {回填给\\ 模型};
  \draw[dsharrow] (call) -- (log1);
  \draw[dsharrow] (log1) -- (gate);
  \draw[dsharrow] (gate) -- (exec);
  \draw[dsharrow] (exec) -- (log2);
  \draw[dsharrow] (log2) -- (back);
  \draw[dshmutedarrow] (gate.south) to[out=-60, in=-120] node[dshlabel, below=0.5mm] {询问但无人应答 $\Rightarrow$ 拒绝} (log1.south);
\end{tikzpicture}
\end{center}
```

裁决这一环在图上只是一个方框，实际展开是一整套边界。输入框旁边那个“Workspace Write”是一个**权限预设**，一个名字背后绑着两个各自独立的旋钮，一个管文件这层能碰到什么，一个管裁决为“问一下”时是弹窗还是直接放行。这两个旋钮各自有几档、拦得住什么拦不住什么、找不到人应答时为什么答案总是“不行”，共同构成了 DSH 的权限与安全边界。这里先记住一件事：裁决站在执行之前，任何一次工具调用都得先过这一关。

并发执行上，DSH 同样采用不出错就不并行的策略，只有工具自己明确声明“我在并发环境下是安全的”（`isConcurrencySafe: true`），调度器才会把它和别的调用一起并行跑；这个声明缺失、抛错，或者返回值不是严格的 `true`，一律按独占对待，宁可慢一点也不冒险。

> 深入一点。连续调用同一个工具、参数几乎不变，是模型卡壳的常见信号。DSH 内置一个“复读机”提醒（repeat-tool-reminder），在连续第 3、5、8 次重复同样的调用时往上下文里加一句提醒，但只是劝，不会强行拦截或者篡改调用，它相信这类判断最终还是该留给模型自己。另外，第 3 章用过的多 Agent 调研功能，在这条流水线上就是一个特殊的“工具”，背后统一走 `ctx.subagents` 这个接口，进程内的子 agent、外部的 Claude Code，都是插在同一个接口后面的不同实现，这种“同一个接口后面挂着一排实现”的结构，12.3 会讲清楚它叫什么、为什么到处都是。

**亲手验证**，让 DSH 写一个新文件，完成后展开消息流里对应的工具行，能看到一次调用先后落了 `tool/call` 和 `tool/result` 两条记录，顺序永远是先请求后结果。接着把 Workspace Write 切到 Read Only（设置里能找到这个选项），再让它写同一个文件，这次会被拒绝，回复里能读到具体是哪一层挡下来的，是沙箱本身，还是审批环节。两次对比一下，比单看一次拒绝更容易看出这套裁决链条分了几层。

## 上下文管理 {#sec-11-4}

第 1 章那行统计数据里有两个当时没解释的数字，“输入 7.7K tok · 缓存命中 0%”。7.7K 是怎么数出来的，命中率又为什么第一轮总是 0%，这两个问题，加上“聊得越久 DSH 会不会记不住”，是本节要讲透的三件事。

### 一次请求里装了什么

DSH 发给模型的每一次请求，是四块内容拼起来的一份文本。分若干段、按固定顺序拼接的 system prompt（从 Harness 的身份说明，到当前工作目录，到各个已启用工具各自的使用提示，一段接一段）；工具表，也就是每个可调用工具的名字、描述和参数 schema；到目前为止投影出来的历史消息（11.2 讲过的那份 surface 投影）；以及运行时注入的快照，也就是第 1 章“上下文注入”卡片的真身，一条特殊的 `user` 消息，只有内容真的变了（比如切换了工作目录、多了一条 skill 说明）才会重新注入一次，没变就不重复占位置。7.7K token，就是这四块内容加总的结果。

### token 怎么数出来的

模型服务商按 token 计费和计量，但请求发出去之前，DSH 得自己先估一个数，用来判断要不要触发下面要讲的压缩。估算公式在 `packages/llm/token-meter/src/estimate.ts` 里，逻辑不复杂，一段文本块的估算 token 数是

$$t(\text{文本}) = \left\lceil \dfrac{\text{字符数}}{4} \right\rceil + 4$$

也就是“每 4 个字符算 1 个 token，再加 4 个块开销”。4 字符约等于 1 token 是英文场景下的经验值，中文场景会偏保守（一个汉字常常就吃掉不止一个 token），所以这本来就是一个刻意留了余量的粗估，不是精算。一条消息由多个块拼成，最终还要在块的总和上再加一份固定的角色开销。这些数字全部只在第一次请求前用来打预算；DeepSeek 官方接口一旦返回真实用量，DSH 立刻拿真实值替换掉估算值，统计行显示的从第二次响应起就是服务商报的准确数字，不再是估的。上下文窗口 $W$（当前默认的 DeepSeek-V4-Flash / V4-Pro 都是 1,000,000 token）是这份预算的硬上限，后面压缩阈值都是拿它当分母算出来的。注意这里的 $W$ 是模型适配器登记的真实上下文容量，跟统计行旁边“最大输出”设置的那个 token 数是两码事，后者只管这次回复最多能吐多长。

### 缓存命中率为什么值得盯着看

缓存命中率这行数字，看着像个无关紧要的性能指标，实际上直接决定这一轮回复要等多久、这一轮要花多少钱。背后的规则很朴素，大模型服务商的前缀缓存只认“从第一个字节开始逐字节完全一致的前缀”，只要这段前缀在中途某个位置发生过一次改动，那个位置之后的所有内容全部要重新计算，缓存一分钱都不省。DSH 为了不白白浪费这份缓存，给自己定了几条纪律。历史消息只在末尾追加，绝不在中间插入或者重排；工具表按照与运行环境无关的固定顺序排列，同一批工具无论在哪台机器上跑，序列化出来都是逐字节相同的文本；system prompt 一旦拼好就不轻易改。命中率的计算很直接。

$$\text{命中率} = \dfrac{\text{缓存命中的 token 数}}{\text{这次请求的输入 token 数}}$$

第一次请求时缓存里什么都没有，命中率自然是 0%，这就是第 1 章“你好”那一行“缓存命中 0%”的来历。那一次是这台机器上打给模型的第一句话，7687 个输入 token 一个都省不掉，全得从头算。

纪律有没有生效，看后面的请求就知道。第 1.2 节那次新建文件的任务，用的是同一份 system prompt 和同一张工具表，这段前缀在“你好”那次已经被服务商缓存下来了，所以这次任务第一步只新送了 28 个 token，另外 7680 个整段命中，命中率 99.6%。这个任务一共八步，每一步都只是在上一步的末尾追加工具结果和新回复，新增部分都不大，最后一步只多了 54 个新 token、命中 16896 个，命中率 99.7%。八步加总，界面统计行报的是“缓存命中 92%、输入 99.6K tok”。八步跑下来近十万 token 的输入，真正重算的不到八千，剩下九万多全靠缓存白拿，这就是“只追加、不改历史”这条纪律换来的东西。

```{=latex}
\begin{center}
\begin{tikzpicture}[node distance=2mm, every node/.style={align=left, font=\sffamily\footnotesize}]
  \node[dshnode, minimum width=68mm, anchor=west] (sys) at (0,0) {system prompt（按 order 分段拼接）};
  \node[dshnodeflat, minimum width=68mm, anchor=west, below=of sys] (tools) {工具表（固定顺序，逐字节稳定）};
  \node[dshnode, minimum width=68mm, anchor=west, below=of tools] (hist) {历史消息（11.2 的 surface 投影，只追加）};
  \node[dshnodeflat, minimum width=68mm, anchor=west, below=of hist] (inject) {运行时注入快照（变了才重新出现的一条 user 消息）};
  \draw[dshmutedarrow] ([xshift=2mm]sys.east) -- ++(10mm,0) node[dshlabel, right] {\shortstack{可复用的\\缓存前缀}};
  \draw[dshmutedarrow] ([xshift=2mm]hist.east) -- ++(10mm,0) node[dshlabel, right] {\shortstack{末尾追加，\\不改前面}};
\end{tikzpicture}
\end{center}
```

### 上下文快满了怎么办

一次任务跑得足够久，历史迟早会逼近 $W$ 这条硬上限。DSH 按代价从低到高安排了三道手段。第一道最便宜，单次工具输出如果超过 50000 字节，直接整段落盘存成文件，回填给模型的只是一个定位符，连进入上下文的资格都不给，这一步不花一次模型调用，纯粹是省地方。第二道稍微精细一点，一条已经超出预算的旧工具结果，会被改写成“开头 4096 字符 + 一个省略标记 + 结尾 1024 字符”，模型多数时候只需要头尾就能判断这条历史大致说了什么，同样不用请模型出面。前两道手段都免费，也都先跑一遍。只有跑完之后重新一测，总量还是超标，才会动用第三道花钱的手段，压缩。

压缩的触发和保留量都是按上下文窗口 $W$ 的比例算的。

$$\text{触发阈值} = \lfloor 0.8 \times W \rfloor \qquad \text{压缩后保留尾部} = \lfloor 0.16 \times W \rfloor$$

意思是历史总量摸到 $W$ 的 80% 就要开始处理，处理完之后只留最近这一段、大约相当于 $W$ 的 16%，把中间那一大段换成一条摘要。走到摘要这一步，会实打实花一次模型调用去总结被替换掉的那一段对话，换来的这条摘要会以本节前面提过的 `replace` 操作接在历史里；被替换的那些原始事件不会消失，只是不再出现在模型看到的投影里，跟 11.2 讲的“日志只增不改”完全对得上。

```{=latex}
\begin{center}
\begin{tikzpicture}[node distance=7mm and 9mm, every node/.style={align=center, font=\sffamily\footnotesize}]
  \node[dshnodeflat] (u1) {u1};
  \node[dshnodeflat, right=4mm of u1] (a2) {a2};
  \node[dshnodeflat, right=4mm of a2] (dots1) {\dots};
  \node[dshnodeflat, right=4mm of dots1] (u9) {u9};
  \node[dshnodeflat, right=4mm of u9] (a10) {a10};
  \node[dshlabel, above=1mm of u1, anchor=south west, xshift=-1mm] {压缩前：};
  \node[dshaccentnode, below=13mm of a2, xshift=8mm] (s) {摘要 S};
  \node[dshnodeflat, right=6mm of s] (u9b) {u9};
  \node[dshnodeflat, right=4mm of u9b] (a10b) {a10};
  \node[dshlabel, anchor=south west] at (u1.west |- s.north) {压缩后：};
  \draw[dsharrow] ($(u1.south)!0.5!(dots1.south)$) -- (s.north);
\end{tikzpicture}
\end{center}
```

以上这些数字，50000 字节、4096/1024 字符、0.8 和 0.16 的比例，都是当前版本代码里的默认配置，可以通过配置整体替换，不是写死不能改的规则；本节引用的每一处都对应着仓库里一份具体的配置文件，版本升级之后这些数字本身可能会调整，但“先免费剪、再花钱摘要，摘要走 replace、原始日志永不删除”这套结构性设计不太会变。

**亲手验证**，连续跟 DSH 聊几轮，观察统计行里缓存命中率的变化。第一次请求必然是 0%，只要中途没有切换工作区或者大幅改动上下文，从第二次起命中率应该显著跳高。实测连续问了 7 轮简单问题，命中率是这样爬升的，第 1 轮 0%，第 2 轮 98.6%，第 3 轮 98.4%，第 4 轮 98.2%，第 5 轮到第 7 轮稳定在 99% 以上。只要历史一直在末尾追加、不做任何中间改动，命中率会一直维持在高位，不会随着聊天变长而衰减。

想亲眼看到压缩发生，有个绕不开的前提要先说清楚。当前这个版本里，Web 界面默认打包的插件树并没有装载 `compaction-basic` 和 `command-compact`（跑一次 `dsh --profile web --dump-config`，能看到这两行明确标着 `disabled: true`）。也就是说，本节前面讲的自动压缩和 `/compact` 命令，在你第 1 章装的这个 Web 应用里眼下是不生效的，这是当前 rc 阶段的真实状态，不是本节写错了。想亲手看一遍完整流程，换成用命令行跑一次无头任务，`npx @deepseek-ai/dsh --profile headless "……"`，`headless` 这个 profile 的默认插件树里两者都是启用的。实测跑一个会用掉不少历史的多步任务，再追加一句“帮我 /compact 一下”触发压缩，几秒钟后收到“Compacted 14 history items (~369 tokens)”的执行结果，会话的 Session log 里能看到严丝合缝的一串记录，`compaction/start` 开始、`compaction/summary` 带着摘要正文和“这次替换掉了哪个范围的历史”，`compaction/end` 收尾，跟 11.2 讲的“任何操作先落日志”是同一个套路。压缩之后再发一条新消息，统计行会看到一个不算意外的副作用，这一次输入 token 数量涨回 6000+、缓存命中率跌到 20% 出头。`replace` 操作换掉了请求前缀的一部分，旧的缓存自然对不上号了，压缩换来的是上下文变小，不是免费的午餐，下一次请求要重新攒一遍缓存。

> 深入一点。本节前面说的“压缩”，实际上有两条触发路径。一条是防患于未然，DSH 在发起下一次模型请求之前，会预先算一遍历史体积，摸到阈值就提前处理，请求还没发出去，就已经不会超限；另一条是兜底，万一还是撞上了服务商返回的“上下文超限”错误，会在那个失败步骤之后立刻补救。两条路径走的是同一套“先剪枝、再摘要”的逻辑，只是触发时机一个在前一个在后。
