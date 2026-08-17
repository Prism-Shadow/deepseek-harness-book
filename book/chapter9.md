# DSH 的核心：Cordis {#ch-9}

第 8 章讲的那套循环，任何一个 agent harness 都绕不开。这一章讲的是 DSH 自己的那一半，它底下那个叫 Cordis 的框架，以及这个框架带来的一个不太常见的结果，产品里没有一块地板是不能撬开的。

## 一切皆插件：DSH 的模块化设计 {#sec-9-1}

第 2 章做了三件事。切标题栏那个“标准模式”下拉框，看到标准、PTC、极简、创造四个选项；用创造模式现场给界面挂了一个改主题色的插件，挂上之前还得在左下角的面板里点一下“允许”；最后把这个临时插件写成磁盘上的文件，塞进 `$DSH_HOME/profiles/web/cordis.patch.yml`，才算留住。切模式、装插件、改配置文件，这三件事是同一套机制在三个不同地方露出的痕迹。

DSH 的底层框架叫 Cordis，它对整个产品的定义只有一句话（`docs/architecture.zh.md` 第 11 行），**产品的每一部分都是插件**，模型适配器是插件，工具注册表是插件，会话日志是插件，就连 agent loop 本身也是插件。这句话要按字面意思读，**不存在一个“特权内核”，可以被谁打个补丁就改了行为**，扩展 DSH 的唯一方式，是把一个新插件挂到别的插件旁边，而不是钻进某个核心文件里改代码。第 2.2 节那个批准面板，正是这条规则在界面上的体现，DSH 现场“定义”了一个插件，但定义本身不会自动生效，得等一次显式的批准动作，插件才会真的挂载；插件的每一项注册，一段提示词、一个令牌覆盖、一个工具，都被当成一个可撤销的副作用，卸载插件或者进程重启，这些注册会按预期原样撤销。这也是为什么第 2.3 节实测“运行时插件重启就没了”是准的，它压根没有落盘，只是内存里一层临时的副作用。

一个插件长什么样，拆开看很朴素，一个带 `name`、可选 `inject`（声明自己依赖哪些别的服务）和 `apply(ctx)` 的对象或函数。第 2.3 节那份 `emerald-accent/client.js` 就是一个教科书式的例子。`inject: ['theme']` 声明它要用主题服务，`apply(ctx)` 里调用 `ctx.effect()` 包一层，注册一次令牌覆盖，这正是“插件是实现 Service 的对象、注册是可撤销副作用”这两条核心概念的真实代码，不是简化过的教学示例。跑一次 `dsh --profile web --dump-config`，能看到整棵插件树在配置层面长什么样。工具注册表、system prompt 组装、agent loop、DeepSeek 模型适配器，这些名字听起来分量完全不同的东西，在配置文件里是一模一样形状的几行，一个 `id`、一个 `name`、外加可选的 `config`。

```yaml
- id: agent-loop
  name: '@deepseek-ai/dsh-agent-loop'
  config:
    agents: []
- id: tool-todo
  name: '@deepseek-ai/dsh-tool-todo'
  config:
    allowParallelInProgress: true
  disabled: true
```

驱动整个 agent 循环的 `agent-loop`，和一个只是维护待办列表的小工具 `tool-todo`，在这棵树里是同一种公民，都是一行配置，都能被替换、被禁用、被另一个实现顶替。

第 2.3 节动手改的那两个文件，对应的正是这棵插件树是怎么叠出来的。DSH 启动时，配置是从一个空列表开始，一层一层往上叠，先按 profile 声明的顺序叠上各个组合包（比如 `dsh-base` 负责模型适配器、工具、持久化、沙箱这些基础设施，`dsh-web-app` 在此之上加一层浏览器应用），再叠 profile 自己的 `cordis.patch.yml`，再叠 home 目录级别那份，最后才是命令行传的 `--patch`（`docs/architecture.zh.md` 第 27 行）。第 2.3 节让翡翠绿主题“永久生效”的两步操作，往 `profiles/web/package.json` 加一条插件依赖、往 `profiles/web/cordis.patch.yml` 插一行，就是在这叠层里的“profile 自己的 patch”这一层上，多垒一层瓦。`dsh --profile web --dump-config` 打印出来的每一行，理论上都能被自己的 patch 顶替掉，这正是“没有特权内核”的直接推论，连官方随包发布的这些插件，也只是叠层里的普通一层，不是不能碰的地板。

```{=latex}
\begin{center}
\begin{tikzpicture}[node distance=6mm, every node/.style={align=center, font=\sffamily\footnotesize}]
  \node[dshnodeflat, minimum width=90mm] (empty) {空列表};
  \node[dshnode, minimum width=90mm, below=of empty] (base) {dsh-base（模型、工具、持久化、沙箱……）};
  \node[dshnode, minimum width=90mm, below=of base] (webapp) {dsh-web-app（浏览器应用）};
  \node[dshaccentnode, minimum width=90mm, below=of webapp] (patch) {profiles/web/cordis.patch.yml（用户自己的补丁层）};
  \node[dshnodeflat, minimum width=90mm, below=of patch] (cli) {命令行 \texttt{-{}-patch}（可选）};
  \draw[dsharrow] (empty) -- (base);
  \draw[dsharrow] (base) -- (webapp);
  \draw[dsharrow] (webapp) -- (patch);
  \draw[dsharrow] (patch) -- (cli);
\end{tikzpicture}
\end{center}
```

标题栏那个“标准模式”下拉框，切开看是另一层叠加，叫 **agent preset**，一份预先写好、随包发布的插件组合，专门决定“这个会话能用哪些能力”。DSH 目前发四款。`minimal` 接近纯聊天，system prompt 整段锁死不能再拼接，只给持久 bash 和一个文本编辑工具，压缩也是关着的；`standard` 是完整的编码助手，第 1 章到现在用的都是它；`code`，也就是下拉框里的 PTC 模式，在 `standard` 的基础上只多挂了一个“把连续几步工具调用改写成一段 TypeScript 程序、一次执行”的展示层，官方注释原话是“一段本来要五次往返的操作，变成一次”；`cordis`，也就是创造模式，在 `standard` 之上另外开了运行时检查、插件实验和 preset 创作向导，第 2 章一直用它写人设、挂插件。翻一下这两份配置文件的行数就有直观感受，`minimal` 只有 62 行，`standard` 有 251 行，四倍的差距，基本就是“聊天”和“能读写文件、跑命令、管上下文压缩的完整 agent”之间的距离。

> 深入一点。Cordis 的完整概念还有两个本节没细讲，服务按 `inject`/依赖关系决定加载顺序，以及事件按 `emit`、`waterfall`、`parallel`、`serial` 四种模式分发，这两样是 9.2 的内容。想搞清楚一个具体插件内部是怎么写的、`ctx.effect()` 到底在管什么，`docs/cordis-primer.md` 是最短的入口；真要动手写一个插件，留给第 11 章。

**亲手验证**，跑 `npx @deepseek-ai/dsh --profile web --dump-config`（不需要配置任何密钥），在输出里搜 `agent-loop` 和 `tool-todo`，能看到两者是同样形状的配置行，一个决定了整个循环怎么转，一个只是个小工具，在配置层面待遇相同。再回到界面，把模式切到“极简模式”开一个新会话，让它做一件第 3 章那种要读文件、搜网页的任务，能明显感觉到它能用的手段比标准模式少了一大截，跟本节说的“minimal 只锁了两个工具、其余能力整段裁掉”对得上。四个模式在下拉框里挂着同样的名字长度，背后挂载的插件数量却天差地别，这正是“每一部分都是插件、都能按需增减”的直接体现。

## Cordis 的核心组成 {#sec-9-2}

9.1 说 DSH 的每一部分都是插件。这话要真站得住，还欠一个交代。一百多个互不相识的插件，凭什么能拼成一个跑得起来的产品，谁先启动谁后启动，一个插件想拦住另一个插件的行为又该从哪下手。Cordis 用五个概念回答这些问题，第 2.3 节那份十几行的 `emerald-accent/client.js` 里，已经有三个露过面了。

**插件是实现 Service 的对象**。它可以是一个带可选 `inject` 和 `apply(ctx)` 的函数，也可以是一个 `Service` 子类，挂载和卸载由 Cordis 管。翡翠绿那个插件是前一种，二十行不到，没有任何仪式感。

**上下文是服务的容器**。每个服务占住一个固定的 `ctx.<key>`，`ctx.tools` 是工具注册表，`ctx.llm` 是模型适配器，`ctx.sessions` 是会话存储。别的插件要用它，靠的是这个 key，而不是 import 某个具体实现的文件（`docs/cordis-primer.zh.md` 第 10 行）。这一条读起来最平淡，却是下一节整节的前提。

**依赖靠 `inject` 声明**。`inject: ['theme']` 那一行的意思是“主题服务就位之前我不启动”。加载顺序是这么表达出来的，不是谁在配置文件里写得靠前谁先跑。`--dump-config` 打印出来的行有确定的书写次序，但一个插件的 `apply` 什么时候真的执行，取决于它等的那些服务什么时候到齐。

**通信靠类型化事件**。服务声明自己会发哪些事件，别的插件挂监听器上去。事件的分发方式有四种，是公开约定的一部分，不能随便换。

| 模式 | 是否等待 | 顺序 | 有无返回值 |
|---|---|---|---|
| `emit` | 否 | 按注册顺序观察 | 无 |
| `waterfall` | 否 | 按注册顺序观察 | 有 |
| `parallel` | 是 | 全部并行观察 | 无 |
| `serial` | 是 | 按注册顺序观察 | 有 |

第 8 章反复出现的那些“拦下来”，用的都是表里的 `waterfall`。`agent/pre-step` 能拒绝一整批还没发出去的消息，`tools/pre-execute` 能把一次工具调用挡在执行之前，机制是同一个。waterfall 是环绕中间件，每个监听器拿到的参数末尾多一个 `next`，调用 `next()` 就把决定权交给下游，不调用直接返回就是短路。文档把这条规矩写得很清楚，握有决定权的策略监听器可以短路，只做标注和观察的必须往下委托（`docs/cordis-primer.zh.md` 第 34 至 38 行）。8.3 讲的那条“允许、拒绝、询问”的裁决链，落到实现上就是一串挂在 `tools/pre-execute` 上的监听器，谁认为这次调用归自己管，谁就不再往下传。

**注册是可撤销的副作用**。提示词片段、工具 schema、模型适配器、监听器，这些东西都通过 `ctx.effect()` 或者 `ctx.on()` 装上去，插件卸载或者重载时按预期原样撤销。翡翠绿插件里 `ctx.effect()` 包的那一层，撤销的就是那次令牌覆盖。Cordis 的实践规则要求每一次注册都配一个对应的清理函数，要么由 `ctx.effect()` 返回，要么用框架提供的辅助方法自动处理。

还有一条不在五个概念里、但读配置时一定会撞见的东西。`--dump-config` 输出中的 `tool-bash` 那一行写着 `disabled: !!js process.platform === 'win32'`，`!!js` 后面跟的是一个表达式，loader 在每次做挂载决策时才求值。同一份配置在 Windows 和在 Linux 上装出来的插件树因此并不相同，Windows 上启用的是 `tool-pwsh` 那一行，条件正好反过来。

**亲手验证**，打开第 2.3 节自己写的那份 `emerald-accent/client.js`，对着上面五条逐个认领，`inject: ['theme']` 是第三条，`apply(ctx)` 是第一条，`ctx.effect()` 是第五条，二十行代码里坐实了三条。再跑一次 `npx @deepseek-ai/dsh --profile web --dump-config`，在输出里搜 `tool-bash`，能看到那行 `disabled: !!js process.platform === 'win32'`，这是“配置项是表达式、按你这台机器的环境求值”的现场证据。

## 能力 Seam：一整类能力如何被替换 {#sec-9-3}

8.3 的旁注里埋过一句话，进程内的子 agent 和外部的 Claude Code，是插在同一个接口后面的不同实现。这句话背后是 DSH 用得最多的一个结构，官方管它叫 **seam**，直译是接缝。

一条 seam 由三个角色组成（`docs/architecture.zh.md` 第 104 行）。**Service Definition** 声明接口，规定这类能力必须能回答哪些问题；**Service Provider** 实现它；**Consumer** 使用它，通常是一个面向模型的工具。一个包可以同时扮演多个角色，但只有一个角色单独存在时不构成 seam。添加一项能力，意味着这三样要一起设计。

拿沙箱这条 seam 对照最省事，因为三个角色在 `--dump-config` 里就是挨着的三行。`sandbox` 是接口，`sandbox-local` 是本机的实现，`bash-sandbox` 是消费方，也就是那个真正拿着命令去 spawn 的家伙。消费方交出即将执行的确切 argv，提供方按这次调用的策略把它包起来再还回去。消费方从头到尾不知道自己跑在 bwrap、Landlock 还是 Seatbelt 上。

```{=latex}
\begin{center}
\begin{tikzpicture}[node distance=8mm and 10mm, every node/.style={align=center, font=\sffamily\footnotesize}]
  \node[dshnode] (consumer) {Consumer\\ 消费方\\ \scriptsize tool-bash};
  \node[dshseam, right=of consumer, minimum height=12mm] (def) {Service Definition\\ 接口 \texttt{ctx.shell}};
  \node[dshaccentnode, right=of def, minimum width=28mm] (p1) {bash-local};
  \node[dshnode, below=4mm of p1, minimum width=28mm] (p2) {bash-sandbox};
  \node[dshnodeflat, below=4mm of p2, minimum width=28mm] (p3) {pwsh-local};
  \draw[dsharrow] (consumer) -- (def);
  \draw[dsharrow] (def) -- (p1);
  \draw[dshmutedarrow] (def.east) -- (p2.west);
  \draw[dshmutedarrow] (def.east) -- (p3.west);
  \node[dshlabel, below=1mm of p3] {同一个接口，换一行配置就换一个实现};
\end{tikzpicture}
\end{center}
```

DSH 并不打算把所有东西都做成 seam。生成出来的能力图里，56 个有服务声明的包分成三类，26 个是可替换的 seam，29 个是核心主干，剩下一个是组合点（`docs/capability-seams.zh.md` 的服务表，这张表由脚本从源码声明里扫出来，配了完整性守卫，不会跟代码脱节）。主干那一类是会话日志、工具注册表、系统提示词组装这些东西，它们没有替换点，因为换掉其中一个基本等于换一个产品。这条分界线本身就是设计决定，值得看一眼那张表，你会发现凡是跟“怎么执行”有关的几乎都是 seam，凡是跟“怎么记录”有关的几乎都是主干。

seam 真正的威力在于替换一个提供方就能改变整个产品的行为。文件系统和进程这两个提供方共享同一个执行世界，把它们一起指向远程沙箱，Bash、持久终端和语言服务器就一并搬了过去，不需要给每个消费方单独分叉一份（`docs/architecture.zh.md` 第 106 行）。子 agent 那条 seam 的落差更夸张，仓库的 `packages/subagent/` 下并排放着六个实现，进程内新建、进程内 fork、ACP、Codex、Claude Code，以及通过 DSH 自己的 SDK 委派出去。第 4 章那次多 Agent 调研用的是其中最朴素的一个，你现在跑的这棵 web 插件树里挂着的也只有 `spawn` 和 `fork` 两个提供方，另外四个躺在包里等着被配置换上去。

替换要真的成立，接口就得管住自己。`ctx.lsp` 那条 seam 的说明里有句话值得抄下来，这条 seam 不提供协议逃生口，后端必须把自己的东西翻译成标准化的请求和结果。一旦允许某个提供方从接口的缝隙里漏出协议细节，消费方迟早会依赖上那些细节，接缝也就名存实亡了。

**亲手验证**，在 `--dump-config` 的输出里连着找三行，`- id: sandbox` 后面跟的名字是 `@deepseek-ai/dsh-sandbox-local`，这是接口位上装了本机实现；再往下找 `- id: bash-sandbox`，这是消费方。然后搜 `subagent`，能看到 `subagent-spawn-in-process` 和 `subagent-fork-in-process` 两行，各自的 `config` 里写着 `providerName: spawn` 和 `providerName: fork`，一个接口位上并排注册着两个具名提供方，这就是 seam 在配置层面长的样子。

## Cordis 的设计原理 {#sec-9-4}

前面三节讲的是这套结构是什么样，这一节讲它为什么值得这么麻烦。

代价是明摆着的。加一项能力要同时设计三个角色，每一次注册都得配一个清理函数，任何一个想拦截别人的插件都得老老实实调用 `next()` 往下传。相比之下，在一个核心文件里加个 `if` 分支快得多。DSH 换来的东西，是一句写在架构文档开头的话，不存在需要打补丁的特权内核，扩展它的方式是把插件挂到别的插件旁边（`docs/architecture.zh.md` 第 13 行）。

这句话有两个维度上的具体含义，时间上的和空间上的。

时间上，挂载和卸载是对称的。一个插件在 `apply` 里做的每一件事，注册一个工具、加一段提示词、覆盖一个主题令牌、挂一个监听器，都被当成副作用记着账，插件走的时候按账本原样撤销。第 2.3 节那个实验之所以结论那么干脆，运行时挂上去的插件重启就没了，正是因为这套账本从来不打算落盘，它记的是内存里这一份运行时的欠账。

空间上，依赖关系是活的。`inject` 声明的不只是启动顺序，还有存续条件。一个插件依赖的服务如果消失了，它自己也跟着停下来，而不是抱着一个失效的引用继续跑。所以“换掉一个提供方”这件事在运行时是有确定语义的，旧的一批注册撤销，依赖它的那些跟着重来一遍。

```{=latex}
\begin{center}
\begin{tikzpicture}[node distance=7mm and 14mm, every node/.style={align=center, font=\sffamily\footnotesize}]
  \node[dshaccentnode] (plug) {一个插件的 \texttt{apply(ctx)}};
  \node[dshnode, right=of plug] (reg) {注册一个工具\\ 加一段提示词\\ 覆盖一个令牌\\ 挂一个监听器};
  \node[dshnodeflat, right=of reg] (off) {卸载 / 重启};
  \draw[dsharrow] (plug) -- node[dshlabel, above=0.5mm] {装上} (reg);
  \draw[dsharrow] (reg) -- node[dshlabel, above=0.5mm] {逐条撤销} (off);
  \draw[dshmutedarrow] (off.south) to[out=-120, in=-60] node[dshlabel, below=0.5mm] {回到装之前的样子} (plug.south);
\end{tikzpicture}
\end{center}
```

有了这两条，扩展点就不必是恩赐，而可以是清单。架构文档末尾直接列了一张“新行为的归属位置”表，18 行，左边是你想干的事，右边是它该挂在哪。加一个模型提供方，在 `ctx.llm` 上注册适配器；加一个模型能用的能力，在 `ctx.tools` 上注册，它的 schema 会自动进提示词组装；想让某个会话拥有一套不同的能力集合，组装一个 agent preset；想拦住请求、工具或者整个轮次，用对应的 `agent/*` 或 `tools/*` 事件。表里没有任何一行写着“改核心代码”。这张表配着 `dsh --profile web --dump-config` 一起看，是这一章最实在的收获，前者告诉你新东西该往哪挂，后者告诉你已经挂了什么。

事件域的选择是大多数改动的第一个决定，文档把它分成三类（`docs/architecture.zh.md` 第 59 行）。会话事件是追加进日志的持久事实，一件事重新加载之后还得在，就用它；`agent/*` 事件携带活着的 agent，要观察或者拦截正在进行的工作，就用它；能力事件挂在某条 seam 上，`fs/*`、`tools/*` 这些，用来附加策略和适配器，好处是不需要反过来 import 那个循环。

最后一条纪律是收口用的。**模型可见即已记录**，任何抵达模型请求的东西都必须能从会话日志重建，这不是一句口号，DSH 用一个运行时不变量服务去断言它（`packages/runtime-diagnostics/invariants`，每个包用自己的 npm 名字注册自己那部分检查，失败时报错会指名道姓说是哪个包违约了）。8.2 讲过的日志只增不改，9.1 讲过的没有特权内核，在这条纪律上合成了一件事，产品的每一部分都可以被换掉，但换成什么都得把话说清楚、记下来。

**亲手验证**，跑 `npx @deepseek-ai/dsh --profile web --dump-config`，把输出里以 `# ==` 开头的注释行找出来，它们标着下面每一段配置是从哪一层来的。第 2 章和后面几章做过操作的机器上，能看到 `@deepseek-ai/dsh-base`、`dsh-base` 被 `dsh-web-app` 打过补丁的那一段、`@deepseek-ai/dsh-web-app`，最后是你自己那份 `~/.dsh/profiles/web/cordis.patch.yml`。自己的补丁排在最后一层，这就是 9.1 那张叠层图的实物。想验证“可撤销”，把自己 patch 里第 2.3 节加的那行注释掉，重启 DSH，主题色会退回默认，再把注释去掉重启，它又回来，装上和撤下走的是同一本账。
