# 使用 dsh 自进化 {#ch-14}

第 13 章介绍了四种扩展 dsh 的方法：编写 Skill、接入 MCP 服务器、安装社区插件，以及编写本地插件。本章继续讨论 dsh 如何检查和调整自身能力。

第 2 章已经展示过两个例子。2.1 节创建“技术编辑”preset 时，dsh 临时加载探针插件，查明 preset 服务的接口后再执行操作。2.2 节临时修改主题色时，浏览器等待用户批准后才运行客户端代码。第一节解释这两类操作背后的机制，第二节说明如何把项目规则写入指令文件，供后续会话继续使用。

## 使用 dsh 插件 Agent 实现自我进化 {#sec-14-1}

创造模式比标准模式多七个 Cordis 工具，其中三个用于检查，四个用于修改。

检查工具包括 `cordis_inspect_list`、`cordis_inspect_query` 和 `cordis_inspect_self`。`cordis_inspect_list` 列出当前 Host 中的检查提供方，同时返回用途、只读方法和输入输出 schema。`cordis_inspect_query` 按名称执行只读查询，可以查看服务方法签名、事件分发模式和工具 schema，也能读取主题令牌及浏览器中的插槽树。`cordis_inspect_self` 只检查当前会话定义的动态对象。这些工具都要求模型在编写代码前先查询实际接口，避免猜测名称和参数。2.1 节创建 preset 时的多个检查步骤，就来自这一过程。

修改工具包括 `cordis_define`、`cordis_run`、`cordis_stop` 和 `cordis_undefine`。`cordis_define` 保存定义，可能产生副作用的操作由 `cordis_run` 执行。

`cordis_define` 接收一个动态包。包中可以只有 host 部分或 client 部分，也可以同时包含两者。源码使用纯 JavaScript 函数体，dsh 不会转换 TypeScript、JSX 或 `import`。它先编译两部分代码以检查语法，此时不执行代码。检查通过后，dsh 分配一个 `dyn-<n>` id，并将定义保存在当前会话下。语法错误会在分配 id 之前返回，因此这一阶段不需要回滚已运行的代码。

每次 `define` 会为同一个 Plugin 追加一个不可变的 Package，不会覆盖旧版本。版本指针始终指向最新 Package，历史版本仍可查看。多次修改动态插件后，仍然可以按版本检查对应源码。

`cordis_run` 负责加载动态包。只有 host 部分时，代码会在当前进程的 `node:vm` 中求值并执行。包含 client 部分时，dsh 会向已连接的浏览器页面发送运行请求，然后等待用户允许或拒绝。2.2 节左下角的“Cordis 插件”面板就是这项审批的入口。面板提供“允许当前版本”“允许后续版本”和“拒绝”三种选择。

浏览器审批不设超时时间。如果没有页面可以应答，请求会保持等待，直到当前轮次被取消，并以 `cancelled` 结束。系统不会因等待超时自动允许请求。

广播事件只包含 id、名称和用途等元数据。client 源码会通过单独通道传给获得允许的页面，不会随广播发送。dsh 会先执行 host 部分；如果 host 执行失败，client 部分不会启动。

多个页面同时连接时，第一个有效应答决定运行结果，后续应答会被忽略。页面应答的版本如果已经失效，系统会拒绝该应答，避免加载已经停止分发的代码。

```{=latex}
\begin{figure}[H]
\centering
\begin{tikzpicture}[node distance=7mm and 11mm, every node/.style={align=center, font=\sffamily\footnotesize}]
  \node[dshnode] (def) {\texttt{cordis\_define}\\ 保存定义\\ \scriptsize 编译并检查语法};
  \node[dshseam, right=of def] (ask) {\texttt{cordis\_run}\\ 等待审批\\ \scriptsize 不设超时};
  \node[dshaccentnode, right=of ask] (live) {挂载生效\\ \scriptsize host 部分先执行};
  \node[dshnode, right=of live] (stop) {\texttt{cordis\_stop}\\ 停止当前分发\\ \scriptsize 保留定义};
  \node[dshnodeflat, below=8mm of live] (gone) {进程重启\\ \scriptsize 定义与运行状态一并清除};
  \draw[dsharrow] (def) -- (ask);
  \draw[dsharrow] (ask) -- node[dshlabel, above=0.5mm] {允许} (live);
  \draw[dsharrow] (live) -- (stop);
  \draw[dshmutedarrow] (stop.north) to[out=110, in=70] node[dshlabel, above=0.5mm] {停止后可再次运行} (ask.north);
  \draw[dshmutedarrow] (live) -- (gone);
\end{tikzpicture}
\caption{浏览器代码如何定义并运行，以及何时停止}
\end{figure}
```

`cordis_stop` 停止当前分发，移除处理器，并等待 host 部分的 fiber 停止，但会保留定义。之后仍可通过 `cordis_run` 再次加载。`cordis_undefine` 会同时删除定义。

这组操作可能返回六类未执行结果：定义不存在、host 执行失败、client 执行失败、用户拒绝、轮次被取消，或没有正在运行的分发。其中，用户拒绝、轮次被取消和无运行中分发属于状态反馈，不表示系统内部故障。

动态定义属于创建它的会话。其他会话查询该定义时，系统会按不存在处理，从而避免会话之间泄漏动态对象。

动态包保存在 dsh 进程的共享内存中，可以跨轮次使用，也可能影响同一进程中的其他会话。`cordis_stop` 只清除运行状态，`cordis_undefine` 还会删除定义；卸载工具集或重启进程则会清除两者。这些操作不会生成插件文件、安装依赖或改动个人与项目配置，也不会自动将动态包转换为持久插件（`packages/extensions/tool-cordis/README.md`）。需要保留实验结果时，应按照第 13.4 节的方法编写本地插件。这也解释了第 2.3 节中临时插件为何会在重启后消失。

> `node:vm` 提供的全局对象隔离不能作为安全边界。host 辅助方法可能使代码离开隔离环境，插件获得的服务也会作用于正在运行的 dsh。官方文档建议将这组工具按 shell 执行权限对待。因此，创造模式应只在可信环境中使用，并认真检查待运行的代码和审批请求。

要验证这套机制，先切换到创造模式，让 dsh 列出当前进程中注册的工具。这项只读任务会调用 `cordis_inspect_list` 和 `cordis_inspect_query`，不会弹出运行审批。然后重复第 2.2 节的翡翠绿主题实验。插件生效后，输入“停止刚才的插件”，界面颜色应恢复默认；再输入“重新运行刚才的插件”，主题色应再次变为翡翠绿。这一过程可以确认 `stop` 会保留定义，供后续重新运行。

一个 agent preset 对应磁盘上的一个目录。目录中包含 `agent.cordis.yml` 和元数据文件，分别记录插件组合与显示信息。标题栏中的标准、PTC、极简和创造模式，都来自这样的 preset 目录。

dsh 从两个根目录发现 preset。随安装包发布的目录只读，其中的条目带有 `system` 信任。`$DSH_HOME/.agent-presets` 是用户可写目录，用于保存自定义 preset。Web 应用的配置将这个目录视为与 shell 执行同级的信任边界（`packages/bundle/web-app/cordis.patch.yml` 第 410 行起）。preset 会决定新会话启动时加载哪些工具，因此只应允许可信的用户或进程写入该目录。

创建 preset 时，服务接收源 id、目标 id 和可选的显示名称，然后将源 preset 整个复制到第一个可写的根目录。复制内容包括组合文件、元数据、Skill 目录和附带资源。接口不直接接收组合文本，新 preset 因而从一份可加载的现有组合开始。

复制前，服务会检查目标 id 的格式、是否已占用，以及源 preset 是否存在。id 必须符合 `[a-z0-9][a-z0-9-]*`，因此 `../escape`、`a/b` 和绝对路径都无法通过 id 检查。复制中途失败时，服务会回滚未完成的目录。2.1 节创建的“技术编辑”保存在 `$DSH_HOME/.agent-presets/tech-editor/`。

无法解析的 preset 仍会出现在列表中，同时显示失败原因。如果直接忽略这类目录，目录占用的 id 仍然存在，用户却无法从界面找到它。显示错误可以避免“创建失败后又提示重名”的困惑。

preset 只能在会话尚未产生内容时切换。已经开始的会话会收到 `agent-preset-locked`。preset 决定模型可见的工具 schema 和提示词段落，中途切换会使日志中的既有工具调用无法在新组合中重放。

切换成功后，dsh 会向会话日志追加 `agent-preset/selected` 事件。会话头信息只记录初始 preset，当前 preset 需要根据后续日志计算。恢复会话、fork 和生成列表摘要时，dsh 都会解析该事件，保证会话使用切换后的工具组合重建。

子 Agent 会加入父 Agent 已经运行的组合，不会再按 id 挂载一次 preset。这样可以保证父子 Agent 使用同一份组合，即使父 Agent 启动后配置文件被修改，或对应 preset 已被删除，子 Agent 仍然可以加入现有运行时。

> 创造模式将配置分为 HOST 组合和 AGENT PRESET 两个平面。HOST 组合保存注册表和跨会话共享服务，包括持久化、沙箱与审批栈、模型路由和子 Agent 后端。AGENT PRESET 保存单个会话贡献的工具、persona 和提示词段落。发布服务的配置应放入 HOST 组合。随安装包发布的 preset 不应直接编辑或删除：升级会覆盖其内容，损坏 `cordis` preset 还会使创造模式无法启动。需要调整时，应先复制一份用户副本。

要验证 preset 的发现和锁定规则，可以打开 `$DSH_HOME/.agent-presets/tech-editor/`，修改 `preset.yml` 中的说明文字并保存。新建会话后，模式下拉框会显示新说明，无需重启 dsh，因为 preset 列表每次都会重新读取目录。然后在一个已经产生内容的会话中尝试切换模式，界面应拒绝操作，对应 `agent-preset-locked` 规则。

## 让 Agent 记住每次犯错的历史 {#sec-14-2}

13.1 节中的 Skill 用来保存可按需加载的方法，例如周报结构和日期格式。项目规则则需要在每个会话中持续生效，例如仓库使用哪条测试命令、哪些目录禁止修改，以及配置文件应遵循什么格式。dsh 使用指令文件保存这类约束。

dsh 通过 agent-instructions 插件读取 `AGENTS.md` 风格的指令文件。插件先读取 `$DSH_HOME/AGENTS.md`，再从项目根目录逐层查找到当前工作目录。每一层目录都会先检查基础候选 `AGENTS.md` 和 `CLAUDE.md`，再检查本地覆盖候选 `AGENTS.local.md` 和 `CLAUDE.local.md`（`packages/context/agent-instructions/src/config.ts` 第 12 至 13 行）。同一目录中的候选文件去掉首尾空白后，如果内容逐字节相同，只会保留一份，避免重复注入。全部指令的内容上限为 64KB，对应配置项 `maxBytes: 65536`。

插件把指令内容注入为持久的用户角色消息，并用 `<system-reminder>` 标签包裹。标签内的固定说明会交代指令的适用方式和优先级：具体指令优先于宽泛指令，指令文件不能覆盖系统、开发者或用户直接提出的要求。每段内容前还会注明来源文件，便于定位和修改。每个会话第一次满足条件的 `agent/pre-step` 会收集指令基线，并把它加入同一批模型消息，位置紧接用户的第一条消息。因此，新会话从第一个执行步骤起就能获得当前范围内的全部项目规则。

会话进行中，插件还会跟踪成功的 `read`、`write` 和 `edit` 工具结果。每次文件操作完成后，它会检查新进入的目录以及此前加载过的范围。指令文件新增、修改、删除，或因内容重复而被折叠时，插件会分别发送新增、替换或移除通知。插件不会跟随 shell 工具中的目录切换，因为每次调用都会启动独立进程，无法可靠地通过任意 shell 语法判断当前目录。如果在会话中新增或修改 `AGENTS.md`，后续只要成功读写该范围内的文件，插件就会发现变化，无需重新创建会话。

Skill 适合保存按需加载的方法，指令文件适合保存需要持续生效的项目约束。两者都是磁盘上的纯文本文件，可以随代码库进行版本管理。

dsh 不会自动把执行中的错误写入指令文件。用户需要明确要求它把新规则补充到 `AGENTS.md`，也可以要求它在任务结束时整理本次工作中需要长期保留的约束。因此，本节所说的“记住”是把经验写入每个会话都会读取的位置，具体记录哪些内容仍需由用户决定。

源码还预留了跨会话引入上下文的接口，由部署方选择是否接入。当前 Web 插件树没有挂载该能力，在 `--dump-config` 输出中也找不到对应配置。本节介绍的做法只依赖指令文件，不要求启用跨会话上下文。

验证时，可以在项目根目录创建 `AGENTS.md`，写入一条容易观察的规则，例如“本仓库的所有新建文件都以一行注释开头，注明创建日期”。新建会话并要求 dsh 创建文件，检查它是否遵守这条规则。随后把规则修改为“注释中还要注明文件用途”，再让 dsh 读取同一范围内的其他文件，以触发一次成功的文件操作，最后创建第二个文件。第一个文件用于验证会话开始时的基线注入，第二个文件用于验证会话中的动态发现。
