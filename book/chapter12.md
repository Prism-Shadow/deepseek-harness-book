# dsh 的核心：cordis {#ch-12}

模型决定 Agent 能想多远，harness 决定它能做什么。Cordis 是 dsh 的装配层：让模型、工具、沙箱、会话和 Agent Loop 都成为可替换的插件，并负责它们的挂载、卸载与依赖关系。

![一图读懂 Cordis 的能力、问题、场景与未来](assets/chapter12/12-0-01-cordis-overview.svg)

## 一切皆插件：dsh 的模块化设计 {#sec-12-1}

“一切皆插件”要按字面理解。模型适配器、工具注册表、会话日志、沙箱、存储、界面，甚至决定下一步的 Agent Loop，都以插件形式进入同一个 Cordis Context。Cordis 只负责装配，能力留在插件里。

![dsh 的各项能力通过 Cordis Context 协作](assets/chapter12/12-1-01-everything-is-plugin.svg)

这解决了传统扩展系统的一个限制：开发者不必等待核心项目预留扩展点，也不必 fork 一份源码。换模型、换沙箱或增加工具，都可以通过换插件或叠加配置完成。

### 亲手看见插件树

下面的命令不需要模型密钥。它会打印当前 profile 最终装配出的配置树。

```sh
dsh --profile web --dump-config
```

实际输出中，驱动整个循环的 `agent-loop` 和维护待办列表的 `tool-todo` 具有相同的配置形状。

![实际 dump-config 输出中 agent-loop 与 tool-todo 是平等插件](assets/chapter12/12-1-02-plugin-tree-proof.svg)

配置树不是一份不可动的默认配置。dsh 从空列表开始，依次叠加组合包、profile 补丁、home 补丁和命令行补丁。后面的层可以替换前面的条目。

![dsh 从组合包到用户补丁的分层装配](assets/chapter12/12-1-03-composition-layers.svg)

四种运行模式也是同一机制：Standard、Code、Minimal 和 Creator 只是四套不同的插件组合。切换模式，本质上是在给会话换一组能力。

## cordis 的核心组成 {#sec-12-2}

Cordis 可以压缩成五个概念。

![Cordis 的五个核心概念](assets/chapter12/12-2-01-five-concepts.svg)

- **Plugin** 用 `apply(ctx)` 贡献能力。
- **Context** 用稳定的 `ctx.<key>` 保存服务。
- **inject** 声明依赖，服务未就绪时插件不会启动。
- **Event** 让插件协作；`waterfall` 事件还能拦截请求或工具执行。
- **Effect** 记录注册动作及其清理函数，卸载时自动撤销。

### 两种可组合性

论文把动态组合拆成两个正交问题：组件退出后，做过的修改能否撤销；依赖出现、消失或换实现后，其他组件能否自动调整。

![时间可组合性与空间可组合性](assets/chapter12/12-2-02-spatiotemporal.svg)

**时间可组合性**把副作用和逆操作放在一起。插件注册工具、监听器或服务时，Cordis 同时记下如何撤销；卸载时按相反顺序清理。

**空间可组合性**把依赖写进 `inject`。提供方出现，消费者激活；提供方要离开，消费者先停用并撤销自己的副作用，再允许提供方退出。

### 用 seam 替换能力

dsh 把可替换能力称为 **seam**（接缝）。一条 seam 由接口定义、提供方和消费者组成。消费者只认稳定接口，不知道背后是本机、沙箱、远程服务，还是另一个 Agent 产品。

![同一个能力 seam 可以接入不同提供方](assets/chapter12/12-2-03-capability-seam.svg)

这带来几类直接场景：

- 固定工具和循环，只替换模型，用于可重复评测；
- 把文件系统和进程后端一起换成远程沙箱；
- 在同一子 Agent 接口后接入进程内 Agent、ACP、Codex 或 Claude Code；
- 运行时更换存储、模型路由或权限策略，而不改消费方。

## cordis 的设计原理 {#sec-12-3}

传统插件系统常把模块问题推给进程重启：插件卸载不干净，就重启整个宿主；依赖变化难处理，就拆成服务交给容器编排。Cordis 把治理粒度降回组件本身。

![Cordis 从整机重启转向模块级恢复，同时保留系统边界](assets/chapter12/12-3-01-problem-scenes-boundary.svg)

这里有两条重要边界。

第一，Cordis 只能撤销被 Context 纳入管理的副作用。已经发出的消息、写入外部系统的数据或完成的付款，不会因为插件卸载而自动消失；这类动作仍需延迟提交或补偿操作。

第二，依赖声明不是安全沙箱。恶意插件如果能直接访问 Node.js 或原生系统接口，仍可能绕过 Context；不可信代码需要进程、WebAssembly、虚拟机等隔离边界。

### X 上的三种判断

截至 2026 年 8 月 18 日，公开讨论主要集中在三个方向：

- Pi Agent 作者 Armin Ronacher 认为，dsh 虽不完美，却是少见的、让他愿意重新审视自身 harness 设计的开源项目（[原帖](https://x.com/mitsuhiko/status/2088189145952731317)）。
- 早期体验者关注 Creator 模式展示出的自修改能力：Agent 能生成并挂载插件，但内存插件重启后消失，距离持续自演化还有一步（[报道转述](https://en.shuziqushi.com/new417069.html)）。
- 谨慎意见集中在 Node.js 工具链门槛、插件兼容、界面复杂度和安全治理；这些问题决定 Cordis 能否从开发者框架走向普通用户产品（[报道转述](https://en.shuziqushi.com/new417069.html)）。

### 未来不是“插件更多”

Cordis 已在 Koishi 的 4000 多个社区插件中证明了动态装配可以支撑真实生态；dsh 则把这套机制带进 Agent harness。论文同时明确：**持续由 Agent 生成、替换和回滚自身组件，仍是未来验证方向，不是已经完成的结论。**

![从 Koishi 生产验证到自演化 harness 的下一步](assets/chapter12/12-3-02-community-future.svg)

接下来的关键，不只是让 Agent “会改自己”，而是回答五个问题：外部动作如何补偿，不可信插件如何隔离，依赖接口如何做版本兼容，频繁重组的运行成本多高，以及谁来批准和审计长期自演化。

> 本章资料截至 2026 年 8 月 18 日。dsh 仍处于 Developer Preview，插件 API 可能发生破坏性变化。核心事实以 [DeepSeek Harness 官方仓库](https://github.com/deepseek-ai/deepseek-harness)、[Cordis 仓库](https://github.com/cordiverse/cordis) 和论文 [A Programming Paradigm for Spatiotemporal Composability](https://github.com/cordiverse/paper) 为准；[HelmCode 的架构导读](https://helmcode.com/deepseek-harness/cordis)用于辅助核对信息结构。
