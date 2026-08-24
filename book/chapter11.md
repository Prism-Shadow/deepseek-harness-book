# Harness 的工作原理 {#ch-11}

前几章已经用 dsh 完成了文件操作、多 Agent 协作等任务。本章暂时不再增加新的用法，而是打开 dsh 的内部工作过程，看看一次任务究竟怎样运行：模型如何在 agent loop 中反复调用工具，会话怎样被记录和恢复，工具调用如何经过权限检查，以及越来越长的上下文怎样被控制在模型窗口以内。理解这些机制以后，再看界面上的轮次、步骤、Session log、token 和上下文占用，就能知道它们分别在记录什么。

## 从聊天助手到 Harness {#sec-11-1}

回看我们在第 1 章向 dsh 打招呼时，模型直接回了一句话，状态栏显示“1 轮 · 1 步”。
后来我们又让 dsh 新建 `about-dsh.md`，消息流里则多出一张 Write 工具卡片。
文件写好以后，dsh 才给出回复。

在 dsh 的工作流程里，模型负责判断下一步，agent loop 负责推动任务继续。每一步开始时，agent loop 根据会话日志组装模型请求。模型可以直接回复，也可以提出工具调用。遇到 Write 调用，工具执行组件会运行 Write，把结果记进会话，agent loop 再进入下一步。模型随后读到这份结果，继续调用工具或给出最终回复。图 \ref{fig-11-1} 展示了这套循环。

```{=latex}
\begin{center}
\begin{minipage}{\linewidth}
\centering
\begin{tikzpicture}[node distance=9mm and 12mm, every node/.style={align=center, font=\sffamily\footnotesize}]
  \node[dshnode] (user) {用户输入};
  \node[dshaccentnode, right=of user] (model) {模型请求};
  \node[dshnodeflat, below=of model] (answer) {直接回复};
  \node[dshseam, right=of model] (call) {申请调用工具};
  \node[dshnode, right=of call] (result) {执行工具\\返回结果};
  \draw[dsharrow] (user) -- (model);
  \draw[dsharrow] (model) -- (answer);
  \draw[dsharrow] (model) -- (call);
  \draw[dsharrow] (call) -- (result);
  \draw[dsharrow] (result.south) to[out=-90, in=-90]
    node[dshlabel, below=0.5mm] {带着新结果再次请求} (model.south east);
\end{tikzpicture}
\captionof{figure}{模型与工具在 agent loop 中循环交接}
\label{fig-11-1}
\end{minipage}
\end{center}
```

turn 和 step 记的是两件不同的事。一个**轮次**（turn）对应 dsh 对一条用户消息的完整处理。
用户发出消息，轮次开始。dsh 完成这次任务，轮次结束。一个**步骤**（step）对应其中的
一次模型请求，以及这次请求触发的工具调用。一个轮次通常会经过一个或多个步骤，
特殊情况下也可能没有步骤。

第 1 章那次“你好”只请求了一次模型，也没有调用工具，所以显示“1 轮 · 1 步”。
整理文件仍是用户发出的同一个任务，因此始终算一个轮次。第一次请求中，模型可能会提出
查看目录。工具返回目录内容后，agent loop 再发起模型请求，让模型根据结果决定下一步。
每次模型请求都算一个新步骤，所以界面可能显示“1 轮 · 多步”。

用户发来消息后，dsh 会先开始一个轮次。正式请求模型之前，插件还有一次检查机会。
如果插件在这里叫停，dsh 就直接结束这个轮次，模型不会收到请求。源码把这个检查点
叫作 `agent/pre-step`。

步骤从请求模型时开始。因此，这次处理在内部生命周期中仍是一个 turn：日志里有
`turn/start` 和 `turn/end`，只是没有 `step/start`。界面统计行采用另一个口径，
只把至少完成过一个步骤的 turn 计入“轮”数。这里的内部 turn 用来划定一次处理的生命周期，
界面的“轮”用来统计实际进入模型循环的任务。

> 深入一点。只要日志已经写入 `step/start`，这一步就会计数。`ReactLoopAgent` 会在
> 步骤结束时写入 `step/end`，中途失败或被取消也一样。界面根据 `step/end` 计算步数，
> 因此有些没有显示回复的步骤仍会被计入。当前轮次结束后，外层循环再判断是否还有消息
> 需要处理。第 3 章用过的多 Agent 调研，在主 agent 看来也是一种工具调用；工具内部可以
> 再运行一套 agent loop，主 agent 只接收最终结果。

**亲手验证。** 给 dsh 一个需要读取并修改文件的任务。任务结束后查看统计行，再打开 Session log。
日志中 `step/end` 的数量应当与界面步数一致。
这里不应按聊天气泡计数，因为失败或取消的步骤可能没有可见气泡。

## 消息与会话 {#sec-11-2}

完成一次任务后，退出 dsh，过一会儿再打开同一个会话，前面的消息为什么还能恢复？
这是因为 dsh 会在任务进行时，把消息、模型输出和工具调用依次写进会话日志。
恢复会话时，它自动重新读取这份记录，不需要用户另点“保存”。

要想查看原始记录，可以点击右上角的“Session log”。下载得到的是一个 ZIP 归档，
解压后先看顶层的 `session.jsonl`。子 agent 的日志位于 `subagents/<id>/`，
会话引用过的图片则放在 `media/`。磁盘上的日志默认使用 zstd 压缩，
导出的 `session.jsonl` 已经解码，可以直接用文本编辑器打开。

`session.jsonl` 的每一行都是一条事件。一个轮次从 `turn/start` 开始，随后可能经过
一个或多个步骤。每个步骤都有 `step/start` 和 `step/end`，用户消息记为
`user/message`。模型流式生成内容时，日志会连续写入 `assistant/chunk`，再用
`assistant/message` 保存完整回复。工具调用还会产生 `tool/call` 和 `tool/result`。
所有步骤结束后，这个轮次才以 `turn/end` 收尾。

日志里的许多事件只用来记录运行过程，例如轮次的开始与结束，以及模型流式生成的内容。
下一次请求模型时，dsh 不会把所有事件原样发给模型，而是从日志中取出当前的 surface。
surface 主要由用户消息、模型的完整回复和工具结果组成，还可以包含 dsh 或插件注入并记录的
运行状态。这些消息按原来的顺序组成模型看到的历史。

会话继续时，新消息接在 surface 末尾，日志中把这种操作记为 `append`。
对话太长需要压缩时，dsh 会用一条摘要代替一段旧消息，后续请求只带上摘要，
对应的操作叫作 `replace`。被替换的事件仍然保留在日志里，界面回放和导出不会因此缺失。
图 \ref{fig-11-2} 展示了 dsh 怎样从会话日志中整理出模型需要的历史。

```{=latex}
\begin{center}
\begin{minipage}{\linewidth}
\centering
\begin{tikzpicture}[node distance=11mm, every node/.style={align=center, font=\sffamily\footnotesize}]
  \node[dshnodeflat, minimum width=112mm] (log)
    {只追加的会话事件日志\\[0.5mm]
     \scriptsize\ttfamily turn/start\quad step/start\quad user/message\quad assistant/chunk*\\
     \scriptsize\ttfamily assistant/message\quad tool/call\quad tool/result\quad step/end\quad turn/end};
  \node[dshseam, below=of log, minimum width=84mm] (surface)
    {筛选出的模型消息\\\footnotesize 用户消息 · assistant 消息 · 工具结果\\
     \footnotesize 注入状态等};
  \node[dshaccentnode, below=of surface, minimum width=55mm] (messages)
    {下一次请求中的历史\\\footnotesize deriveMessages()};
  \draw[dsharrow] (log) -- (surface);
  \draw[dsharrow] (surface) -- (messages);
\end{tikzpicture}
\captionof{figure}{dsh 从会话日志中整理出模型需要的消息历史}
\label{fig-11-2}
\end{minipage}
\end{center}
```

每条消息都有 `role` 和具体内容。`role` 只有 `system`、`user` 和 `assistant` 三种，
内容则可以是文本、图片或工具调用等不同类型的块。工具结果也使用 `role: 'user'`，
但它的内容是 `tool-result` 块，并带有对应工具调用的 `callId`。dsh 和模型据此识别工具结果，
不会把它当成用户在输入框中发来的普通消息。

模型看到的历史来自会话日志，进入模型请求的内容也必须事先写入日志。
dsh 把这条规则概括为“模型可见即已记录”。这样一来，恢复会话或回放任务时，
dsh 才能从日志中还原模型当时看到的内容。

进程异常退出也可能留下一个没有正常结束的轮次。重新加载时，dsh 会保留已经完整写入的事件。
日志中有未完成的工具调用时，它会补上一条说明中断情况的 `tool/result`。
如果步骤也没有结束，再补上 `step/end`，最后用 `turn/end {interrupted}` 结束这个轮次。
日志末尾如果有一条只写了一半的记录，这段不完整内容会被丢弃。

**亲手验证。** 打开一个做过文件操作的会话，点击“Session log”并解压下载的 ZIP。
在根目录的 `session.jsonl` 中搜索 `tool/call`，再用其中的 `callId` 查找对应的
`tool/result`。两条记录应当使用相同的 `callId`，并位于同一组 `step/start` 与
`step/end` 之间。

## 工具调用与结果返回 {#sec-11-3}

模型需要使用工具时，会在回复中给出工具名和一组 JSON 参数。它之所以知道该选哪个工具，
是因为 dsh 在请求中附上了当前可用的工具表。表中有名称、用途说明和参数格式。

当收到工具调用后，dsh 不会立刻执行。它先把调用写入会话日志，再交给权限规则和 hook 检查。
检查结果可以是放行、拒绝，也可以是请用户确认。通过检查后，工具还要按照自身的执行环境
和权限约束运行。文件和 Shell 工具会应用相应的沙箱策略，其他工具则遵循各自的执行约束。

无论工具执行是否成功，dsh 都会整理出一条工具结果，写入日志，再放进下一次模型请求。
因此，模型能看到工具执行结果，如果工具执行被拒绝，也能根据拒绝原因调整调用方式。
图 \ref{fig-11-3} 展示了这条路径。

```{=latex}
\begin{center}
\begin{minipage}{\linewidth}
\centering
\begin{tikzpicture}[node distance=10mm and 14mm, every node/.style={align=center, font=\sffamily\footnotesize}]
  \node[dshnode] (call) {模型给出\\工具名和参数};
  \node[dshnodeflat, right=of call] (log1) {记录调用\\tool/call};
  \node[dshseam, right=of log1] (gate) {权限与 hook\\用户确认};
  \node[dshaccentnode, below=of gate] (exec) {按工具自身的\\执行约束运行};
  \node[dshnodeflat, left=of exec] (log2) {记录结果\\tool/result};
  \node[dshnode, left=of log2] (back) {下一次\\模型请求};
  \node[dshnodeflat, right=of exec] (deny) {生成拒绝结果};
  \draw[dsharrow] (call) -- (log1);
  \draw[dsharrow] (log1) -- (gate);
  \draw[dsharrow] (gate) -- node[dshlabel, right] {放行} (exec);
  \draw[dshmutedarrow] (gate) -- node[dshlabel, right] {拒绝} (deny);
  \draw[dsharrow] (exec) -- (log2);
  \draw[dshmutedarrow] (deny.south) -- ++(0,-6mm) -| (log2.south);
  \draw[dsharrow] (log2) -- (back);
\end{tikzpicture}
\captionof{figure}{dsh 处理一次工具调用的过程}
\label{fig-11-3}
\end{minipage}
\end{center}
```

输入框旁的“Workspace Write”决定工具可以在哪里写文件。在这个模式下，工具可以改动当前工作区
和指定的临时目录。操作需要访问其他位置时，dsh 会先询问用户。切换到“Read Only”后，
同一个写文件请求就会被拒绝。

模型一次也可能提出多个工具调用。dsh 通常逐个执行，只有工具明确说明本次调用可以并发时，
才会让它与其他调用同时运行。无法确定是否安全时，调用仍按顺序执行。

如果模型连续用相同参数调用同一个工具，它可能没有利用上一次返回的结果。
调用连续出现第 3、5、8 次时，dsh 会在下一次模型请求中加入提醒，
请模型重新考虑是否还要继续。工具不会因此自动取消，执行前仍要经过原来的权限检查。

**亲手验证。** 先在 Workspace Write 下让 dsh 新建一个文件，随后展开对应的工具记录。
日志中应先出现 `tool/call`，再出现带相同 `callId` 的 `tool/result`。切换到 Read Only 后，
再次请求写入。第二次仍会留下工具结果，但内容会说明写入被拒绝。

## 上下文管理 {#sec-11-4}

任务越长，模型每次需要回看的内容越多。工具说明、先前消息和刚刚得到的工具结果，
都要占用上下文窗口。窗口有上限，dsh 因而需要决定每次请求带上什么，历史太长时又该怎样缩短。

### 一次请求包含的内容

一次模型请求主要有三部分。最前面是 system prompt，用来说明 dsh 的身份和工作方式。
接着是当前可用的工具描述。第三部分是消息历史，也就是 11.2 节提到的 surface。

运行过程中会变化的信息，例如当前权限模式或插件补充的环境状态，也会进入消息历史。
dsh 先把它记成带来源的消息，再随 surface 一起发给模型。内容没有变化时，
不会在每一步重复添加。图 \ref{fig-11-4} 展示了一次模型请求的组成关系。

```{=latex}
\begin{center}
\begin{minipage}{\linewidth}
\centering
\begin{tikzpicture}[node distance=2.5mm, every node/.style={align=left, font=\sffamily\footnotesize}]
  \node[dshnode, minimum width=82mm, anchor=west] (sys) at (0,0)
    {系统说明\quad dsh 的身份与工作方式};
  \node[dshnodeflat, minimum width=82mm, anchor=west, below=of sys] (tools)
    {工具表\quad 名称、用途和参数格式};
  \node[dshnode, minimum width=82mm, anchor=west, below=of tools] (history)
    {消息历史\quad 用户消息、模型回复、工具结果};
  \node[dshnodeflat, minimum width=64mm, anchor=west, below=of history,
    xshift=9mm] (context)
    {其中包含\quad 当前权限和插件补充的状态};
  \draw[dshmutedarrow] ([xshift=2mm]sys.east) -- ++(11mm,0)
    node[dshlabel, right] {稳定前缀};
  \draw[dshmutedarrow] ([xshift=2mm]history.east) -- ++(11mm,0)
    node[dshlabel, right] {通常只在末尾增长};
\end{tikzpicture}
\captionof{figure}{一次模型请求的组成}
\label{fig-11-4}
\end{minipage}
\end{center}
```

### 如何统计 token 数

模型服务商只会在请求完成后返回实际使用的 token 数。如果等到这时再检查，
system prompt、工具表和消息历史可能已经超过模型一次能够接收的 token 上限，
请求也会随之失败。因此，每次请求发出前，dsh 都会先估算这些内容有多大。
快到上限时，它可以先压缩历史，再请求模型。
对于文本块，估算公式如下。

$$t(\text{文本}) = \left\lceil \dfrac{\text{字符数}}{4} \right\rceil + 4$$

也就是每 4 个字符折算成 1 个 token，再加 4 个 token 的块开销。工具调用会分别估算
工具名和 JSON 参数，工具结果则继续估算其中的内容块。每条消息还有 `role` 等结构信息，
dsh 会再加 4 个 token，估算这些内容占用的空间。

这套算法适合在请求前快速检查，却不是模型真正使用的分词器，尤其容易低估中文和
JSON schema。请求成功后，dsh 会记下服务商返回的实际用量。下一次估算时，
它以这个数字为基准，只估算后来新增或替换的内容。

聊天统计行把每次模型请求的用量加在一起。一个任务如果走了五步，统计行就会累计
五次请求的输入量和缓存用量。它表示这个会话到目前为止一共使用了多少 token。

上下文占用面板只看下一次准备发给模型的内容，用来判断当前上下文还剩多少空间。
面板会分别估算 system prompt、工具表和消息历史的大小。因此，统计行可能随着步骤不断增长，
上下文占用则只反映下一次请求，两处数字不会相等。

### 如何计算缓存命中率

统计行按下面的公式计算缓存命中率。

$$\text{命中率} =
\dfrac{\text{缓存读取 token 数}}
{\text{未缓存输入 + 缓存读取 + 缓存写入 token 数}}$$

这里的缓存是模型服务商提供的前缀缓存，与 dsh 保存会话日志不是一回事。
如果两次请求开头有一大段内容完全相同，服务商就有机会复用上一次的计算结果。

dsh 会固定 system prompt 和工具表的排列顺序，消息历史通常也只在末尾增长。
第一次请求还没有旧前缀可用，命中率可能是 0%。后续请求沿用相同开头时，命中率便会上升。
统计行显示的是整段任务的累计值，因此还包含第一次建立前缀的成本。

切换模型、改变工具集合或压缩较早的历史，都会改变请求前缀，命中率也可能随之下降。

### 上下文过长时的处理

把上下文窗口记为 $W$。本章所用版本将 DeepSeek-V4-Flash 和 DeepSeek-V4-Pro 的窗口登记为
1,000,000 token。这个数字决定一份请求最多能装多少内容。“最大输出”是另一项限制，
只约束一次回复最多生成多少 token。

dsh 按三层顺序处理过长的上下文。工具刚返回超大文本时，dsh 先把全文保存到 spill（溢出）
文件，只把开头、结尾和取回方法交给模型。整段历史接近窗口上限后，它继续裁剪较早的大型
工具结果。如果仍然腾不出足够空间，dsh 才会请模型概括较早的消息，同时保留近期消息原文。

前两层都优先处理体积大的工具结果，避免一段命令输出挤满后续请求。裁剪和摘要改变的是
模型随后看到的 surface，原始 `tool/result` 和旧消息仍在会话日志中。图 \ref{fig-11-5}
用一个缩小的例子表示摘要前后的变化。

```{=latex}
\begin{center}
\begin{minipage}{\linewidth}
\centering
\begin{tikzpicture}[node distance=7mm and 9mm, every node/.style={align=center, font=\sffamily\footnotesize}]
  \node[dshlabel, anchor=east] (before) {压缩前};
  \node[dshnodeflat, right=5mm of before] (early) {多条早期消息};
  \node[dshnodeflat, right=7mm of early] (recent) {多条近期消息};
  \node[dshlabel, anchor=east, below=14mm of before] (after) {压缩后};
  \node[dshaccentnode, right=5mm of after] (summary) {早期内容摘要};
  \node[dshnodeflat, right=7mm of summary] (recent2) {多条近期消息};
  \draw[dsharrow] (early.south) -- (summary.north);
  \draw[dshmutedarrow] (recent.south) -- (recent2.north);
\end{tikzpicture}
\captionof{figure}{压缩较早历史，保留近期消息原文}
\label{fig-11-5}
\end{minipage}
\end{center}
```

**本版本默认值。** 这些设置可以由 profile 或模型策略修改。

| 设置 | 默认值 |
|---|---|
| 工具结果 spill | 文本超过 50,000 个 UTF-8 字节 |
| 较早工具结果裁剪 | 文本超过 8192 个 Unicode 码点；保留前 4096 个、后 1024 个 |
| 历史摘要 | 占用达到 $0.8W$；近期原文约 $0.16W$ |

**亲手验证。** 找一个历史较长的 Web 会话，在输入框中执行 `/compact`。
压缩成功后，界面会显示本次压缩了多少条历史。导出 Session log，搜索
`compaction/start`、`compaction/summary` 和 `compaction/end`，可以看到完整的压缩过程。
摘要替换了较早的消息，下一次请求能够复用的前缀可能变短，缓存命中率也可能下降。
上下文占用面板中的预计用量则应减少。如果界面提示 `No compactable history yet.`，
说明当前还没有适合压缩的历史，可以继续对话几轮后再试。

自动压缩会在下一次模型请求发出前检查上下文占用。这项检查采用的是估算值。
估算尚未达到压缩阈值时，服务商仍可能认为实际请求超过了模型的上下文窗口。
遇到这种错误，dsh 会在当前步骤中压缩历史。压缩确实让上下文变短后，
它会重新请求模型，步骤和轮次都不会重新开始。没有腾出空间，原来的错误就会返回。
