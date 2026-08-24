# dsh 的核心：Cordis {#ch-12}

上一章沿着一次任务的执行过程，介绍了模型、工具、会话和 Agent Loop 怎样配合完成任务。这些能力由不同插件分别提供，没有集中写在一个整体程序里。

把这些插件组织起来的是 Cordis。程序启动时，它负责加载插件并建立插件之间的关系；配置或依赖发生变化时，它还会相应调整插件的运行状态。

本章先从 dsh 实际使用的插件配置出发，再运行几个最小示例。我们会依次观察一份插件代码怎样开始运行、多个插件怎样建立依赖和通信，以及这些机制怎样支撑 dsh 中真实的工具调用。

## Cordis 如何组装 dsh {#sec-12-1}

### 先认识 Cordis

Cordis 是 dsh 使用的插件运行时框架。要理解它在 dsh 中的位置，可以先把启动过程分成两个层次：前一层负责决定“这次运行哪些插件”，后一层负责让这些插件真正运行起来。

启动时，dsh 先读取当前 profile。profile 描述这一次运行采用的配置，其中会按顺序引用一个或多个 bundle。这里可以先把 **bundle** 理解为一个可复用的插件配置层，它为 dsh 提供一批基础插件及其配置。

每个 bundle 通过 **patch** 把自己的配置加入已有结果。patch 可以插入新的插件配置项，也可以按 `id` 找到前面已经存在的配置项并覆盖它。profile 自己也可以提供 patch，在 bundle 的基础上继续修改配置。

dsh 按顺序应用这些 patch，后面的配置可以覆盖前面的配置，最终得到本次启动使用的插件配置树。随后，dsh 创建 Cordis 的根 `Context`，安装 Loader，由 Loader 根据这棵配置树加载插件。

```text
dsh 组合层

profile
  │
  ├── bundle 1 ──► patch 1
  ├── bundle 2 ──► patch 2
  └── profile patch
          │
          │  按顺序应用
          │  后面的配置可以覆盖前面的配置
          ▼
      最终插件配置树

Cordis 运行时

Root Context
     │
   Loader
     ├── Plugin X ──► Fiber X
     ├── Plugin Y ──► Fiber Y
     └── Plugin Z ──► Fiber Z
```

这两层解决的是不同问题。

**dsh 组合层决定“这次运行哪些插件，以及它们使用什么配置”**。profile 确定要采用的 bundle，并提供自己的调整；各层 patch 按顺序作用，最终形成一棵完整的插件配置树。

**Cordis 运行时负责“这些插件怎样真正运行起来”**。Loader 根据最终配置树加载插件。每次加载一个 Plugin，Cordis 都会创建一个 Fiber，表示这一次加载产生的运行实例。插件通过 `Context` 访问服务、监听事件，并登记需要随运行实例一起清理的副作用。

下面几个概念会贯穿本章。这里先知道它们各自代表什么，后面再结合实际插件逐步展开。

| **概念** | **这里先这样理解**                             |
| -------- | ---------------------------------------------- |
| Context  | 插件运行时使用的上下文，也是访问其他能力的入口 |
| Plugin   | 可以被 Cordis 加载的一段功能定义               |
| Fiber    | Plugin 一次加载所产生的运行实例                |
| Loader   | 根据配置加载、更新和卸载插件                   |
| Service  | 一个插件向其他插件提供的能力                   |
| Event    | 插件之间发送通知或介入运行过程的机制           |
| Effect   | 与 Fiber 生命周期绑定、停止时需要清理的副作用  |

其中最需要先分清的是 Plugin 和 Fiber：

```
Plugin          加载          Fiber
代码定义  ───────────────►  一次运行实例
```

Plugin 是可以反复加载的代码定义，Fiber 则对应其中某一次实际加载。同一个 Plugin 可以被加载多次，每次都会产生自己的 Fiber。

下一步回到 dsh，看看模型、工具、会话和 Agent Loop 等能力怎样出现在最终的插件配置树中。

### 看看 dsh 是怎样组装出来的

下面的命令不需要模型密钥。它会打印 Web profile 最终生成的配置树：

```sh
npx -y @deepseek-ai/dsh --profile web --dump-config
```

实际输出中，驱动 Agent 的 `agent-loop` 和维护待办事项的 `tool-todo` 具有相同的配置形状。

![实际 dump-config 输出中 agent-loop 与 tool-todo 是平等插件](assets/chapter12/12-1-02-plugin-tree-proof.svg)

配置树中的每一项都采用相同的插件结构。模型适配器、工具、会话、沙箱和 Agent Loop 虽然分工不同，在 Cordis 中都以插件身份参与运行。

![dsh 的各项能力通过 Cordis Context 协作](assets/chapter12/12-1-01-everything-is-plugin.svg)

这棵树从空列表开始生成。dsh 依次应用 profile 指定的 bundles、profile 自己的 `cordis.patch.yml`、home 级补丁和命令行 `--patch`。后应用的补丁可以根据稳定 `id` 替换前面的配置项。替换时，整块 `config` 会被覆盖，其中的键不会继续深度合并。

![dsh 从组合包到用户补丁的分层装配](assets/chapter12/12-1-03-composition-layers.svg)

**亲手验证。** 将 `--profile web` 换成自己正在使用的 profile，再执行一次 `--dump-config`。搜索模型适配器、`agent-loop` 和常用工具的名称。它们应当出现在同一棵配置树中；某项能力没有出现时，应先检查 profile 和补丁，而不是到 Cordis 源码里寻找开关。

至此可以划清 dsh 与 Cordis 的边界。dsh 负责生成本次启动采用的配置树，Cordis 负责让树中的插件运行起来。

## 插件如何加载和卸载 {#sec-12-2}

完整的 dsh 一次会加载许多插件，很难直接看清单个插件经历了什么。下面运行官方 Cordis 教程中的最小组合，只加载一份 `hello.ts`。这样便能沿着 Loader 的执行过程，观察 Plugin 怎样成为 Fiber，以及 Fiber 卸载时怎样清理资源。

### 从 Plugin 到 Fiber

官方教程先创建 `hello.ts`：

```ts
import type { Context } from '@deepseek-ai/cordis'

export const name = 'hello'

export function apply(ctx: Context) {
  console.log('hello from my first plugin')
}
```

同一目录下的 `cordis.yml` 只选择要加载的模块：

```yaml
- name: './hello.ts'
```

在官方源码仓库完成 `pnpm install` 后，进入 `tmp/cordis-tutorial`，运行：

```sh
node --import tsx ../../vendor/cordis/bin.js
```

终端会输出：

```console
hello from my first plugin
```

![官方最小插件从配置到输出的完整路径](assets/chapter12/12-1-04-official-loader-flow.svg)

终端出现这行文字，说明整条加载路径已经走通。启动器先创建根 Context 并挂载 Loader。Loader 读取 `cordis.yml`，解析 `hello.ts`，为它创建 Fiber，随后 Cordis 调用 `apply(ctx)`。文件里的 `apply` 属于 Plugin 定义，运行中的 Fiber 才拥有状态和清理责任。

### 在 apply 之前校验配置

插件通常需要从配置中读取参数。`cordis.yml` 中的每个插件条目都可以带有 `config`，插件则可以导出同名的 `Config` Schema，规定这些参数应当是什么类型、哪些可以省略，以及省略后使用什么默认值。

```{=latex}
\Needspace{0.32\textheight}
```

```ts
export interface Config {
  greeting: string
  targets: string[]
}

export const Config: Schema<Config> = Schema.object({
  greeting: Schema.string().default('Hello'),
  targets: Schema.array(String).default(['world']),
})

export function apply(ctx: Context, config: Config) {
  for (const target of config.targets) {
    console.log(`${config.greeting}, ${target}!`)
  }
}
```

例如，只配置 `targets`：

```yaml
- name: './config-demo.ts'
  config:
    targets: ['alpha', 'beta']
```

运行后得到：

```console
Hello, alpha!
Hello, beta!
```

这里没有提供 `greeting`，Schema 自动补上了默认值 `Hello`。进入 `apply` 的配置已经完成校验和补全。

如果把 `targets` 错写成字符串：

```yaml
config:
  targets: 'not-an-array'
```

Schema 会在 `apply` 执行前拒绝这份配置。对应 Fiber 进入 `FAILED`，插件逻辑不会继续运行。配置错误会在插件开始工作之前暴露，不符合约定的数据也不会继续进入插件内部。

### 让资源跟随 Fiber 清理

插件开始运行后，还可能创建定时器、连接或文件 watcher。这些资源需要在插件停止运行时一起停止。

Cordis 用 Effect 表达这种生命周期关系。对于 Cordis 尚未管理的资源，可以用 `ctx.effect()` 同时写下怎样创建和怎样撤销：

```ts
ctx.effect(() => {
  const timer = setInterval(() => console.log('tick'), 200)

  return () => {
    clearInterval(timer)
    console.log('heartbeat cleaned up')
  }
})
```

把这段逻辑写进 `heartbeat` 插件，再保留挂载它时返回的 Fiber：

```ts
const fiber = ctx.plugin(heartbeat)

setTimeout(async () => {
  await fiber.dispose()
  console.log('disposed')
}, 700)
```

运行后会先看到若干次：

```console
tick
```

大约 700 毫秒后出现：

```console
heartbeat cleaned up
disposed
```

`fiber.dispose()` 开始卸载插件。卸载过程中，Cordis 找到这个 Fiber 持有的 Effect，并调用其中的 disposer，定时器随之停止。

Fiber 的主要状态包括：

```text
PENDING → LOADING → ACTIVE → UNLOADING → DISPOSED
                 ↘ FAILED
```

`LOADING` 表示插件正在加载，`ACTIVE` 表示已经正常运行；卸载时进入 `UNLOADING`，所有清理完成后成为 `DISPOSED`。如果配置校验或 `apply` 执行失败，则进入 `FAILED`。

这里暂时不解释 `PENDING`。它表示插件还缺少运行所需的依赖，下一节讨论多个插件之间的关系时再回来处理。

许多 Cordis 注册操作本身已经属于 Effect，例如 `ctx.on()`、`ctx.plugin()`、Service 注册，以及 dsh 中的 `ctx.tools.register()`。它们都会跟随所属 Fiber 自动撤销。定时器、外部连接和文件 watcher 等资源，Cordis 不知道怎样清理，才需要显式使用 `ctx.effect()`。

如果多个异步清理操作存在严格的先后关系，应把它们放在同一个 disposer 中依次 `await`，不能依赖多个 disposer 之间的执行顺序。

## 插件如何依赖、通信和更新 {#sec-12-3}

到目前为止，我们只研究了一个插件自身怎样运行。真实的 dsh 中，大多数插件都需要与其他插件发生关系。工具插件需要工具运行时，Agent Loop 需要模型和会话，其他插件还可能观察或介入这些过程。

这里先关注两种基本的协作方式：

```text
需要使用另一项能力
        │
        ▼
 Service + inject

希望通知、观察或介入一次过程
        │
        ▼
      Event
```

Service 表达“我需要谁提供能力”；Event 表达“某件事发生时，谁愿意参与”。

### 用 Service 和 `inject` 建立依赖

Service 是挂在 `Context` 上的一项具名能力。例如，可以定义一个名为 `greeter` 的服务：

```ts
import { Service, type Context } from '@deepseek-ai/cordis'

declare module '@deepseek-ai/cordis' {
  interface Context {
    greeter: GreeterService
  }
}

export class GreeterService extends Service {
  constructor(ctx: Context) {
    super(ctx, 'greeter')
  }

  greet(who: string) {
    return `Hello, ${who}!`
  }
}

export const name = 'greeter'

export function apply(ctx: Context) {
  ctx.plugin(GreeterService)
}
```

`super(ctx, 'greeter')` 把当前实例注册为名为 `greeter` 的 Service。`declare module` 只在 TypeScript 中声明 `ctx.greeter` 的类型，不负责运行时注册。`apply` 中的 `ctx.plugin(GreeterService)` 负责在运行时把这个 Service 作为插件挂载起来。

另一个插件如果需要这项能力，可以声明：

```ts
import type { Context } from '@deepseek-ai/cordis'

export const name = 'consumer'
export const inject = ['greeter']

export function apply(ctx: Context) {
  console.log(ctx.greeter.greet('world'))
}
```

在 `cordis.yml` 中组合两个插件：

```yaml
- name: './greeter.ts'
- name: './consumer.ts'
```

运行后会看到：

```console
Hello, world!
```

`inject` 声明服务依赖。Cordis 会等到 `greeter` 可用后，再运行消费方的 `apply`。`cordis.yml` 中两个插件的书写顺序不会决定它们实际开始工作的顺序。

只要 `greeter` 尚未准备好，消费方就停在 `PENDING`；Service 可用后，它才继续加载并进入 `ACTIVE`。

```text
greeter 不可用
      │
      ▼
consumer: PENDING
      │
      │ greeter 出现
      ▼
consumer: LOADING → ACTIVE
```

依赖关系在插件启动以后仍然有效。如果 `greeter` 的提供方被卸载，消费方也会随之卸载；新的 `greeter` 出现后，消费方会再次加载。

消费方依赖能力名称及其接口，不导入提供方的具体实现。因此，同一个 `shell` Service 可以由本机 Shell 提供，也可以换成远程沙箱；只要接口保持一致，消费方不需要修改。

![同一个能力 seam 可以接入不同提供方](assets/chapter12/12-2-03-capability-seam.svg)

### 用 Event 观察或介入运行过程

Service 适合一个插件明确调用另一项能力。某件事情发生后，插件也可以只把它通知出去，让感兴趣的插件自行处理。这时可以使用 Event。

例如，一个插件发出统计事件：

```ts
ctx.emit('stats/report', name, count)
```

其他插件可以监听：

```ts
ctx.on('stats/report', (name, count) => {
  console.log(`[stats] ${name} -> ${count}`)
})
```

发出事件的插件不需要知道监听器的数量，也不需要知道它们来自哪些插件。

```text
                 ┌──► listener B
plugin A ──Event─┤
                 └──► listener C
```

`ctx.on()` 本身就是 Effect，因此监听器会跟随所属 Fiber 一起卸载，不需要另外手工移除。

`emit` 是 Cordis 的一种事件分发方式。不同模式规定了监听器怎样执行，以及它们能否影响结果：

| 模式 | 行为 |
|---|---|
| `emit` | 同步通知所有监听器，不收集返回值 |
| `parallel` | 并行执行监听器，并等待全部完成 |
| `serial` | 按顺序执行，遇到第一个有效返回值后停止 |
| `bail` | `serial` 的同步版本 |
| `waterfall` | 监听器组成处理链，可以继续、包装或截断后续处理 |

这里重点看 `waterfall`。创建 `waterfall-demo.ts`：

```{=latex}
\Needspace{0.72\textheight}
```

```ts
import type { Context } from '@deepseek-ai/cordis'

declare module '@deepseek-ai/cordis' {
  interface Events {
    'demo/transform'(
      input: string,
      next: () => Promise<string>,
    ): Promise<string>
  }
}

export const name = 'waterfall-demo'

export function apply(ctx: Context) {
  ctx.on('demo/transform', async (input, next) => {
    const downstream = await next()
    return downstream.toUpperCase()
  })

  ctx.on('demo/transform', async (input, next) => {
    if (input.includes('blocked')) return '** blocked **'
    return next()
  })

  void (async () => {
    console.log(await ctx.waterfall(
      'demo/transform',
      'hello',
      async () => 'hello',
    ))
    console.log(await ctx.waterfall(
      'demo/transform',
      'blocked words',
      async () => 'blocked words',
    ))
  })()
}
```

让 `cordis.yml` 只加载这个文件：

```yaml
- name: './waterfall-demo.ts'
```

运行后得到：

```console
HELLO
** BLOCKED **
```

第一条监听器先调用 `next()`，等后续处理完成后，再把结果改成大写。第二条监听器发现输入中有 `blocked` 时直接返回，没有调用 `next()`，因此默认行为不会继续执行。它返回的替代文本随后经过第一条监听器，最终变成大写的 `** BLOCKED **`。

两种情况可以这样区分：

```text
emit
发生了一件事
    │
    ├──► 观察者
    └──► 观察者

waterfall
开始一次处理
    │
 listener A
    │ next()
 listener B
    │ next()
 默认行为
    │
    ▼
   结果
```

只负责观察或包装结果的 waterfall 监听器必须调用 `next()`。只有明确希望截断后续处理时，才不调用它。

dsh 利用这种机制给关键执行过程留下扩展点。模型请求、审批决策和工具执行中都有 waterfall。最后一节回到 dsh 时，我们会沿着一次工具调用继续观察这条处理链。

### 依赖变化时重新加载

Cordis 的热更新（HMR）把前两节的机制连在一起。提供方代码发生变化时，旧 Fiber 先卸载，所属 Effects 随之清理；依赖它的消费者进入 `PENDING`。新提供方加载完成后，消费者再次进入 `ACTIVE`。

```text
Provider 消失
      ↓
Consumer → PENDING
      ↓
旧 Effects 清理
      ↓
Provider 恢复
      ↓
Consumer → ACTIVE
```

Loader 依靠稳定 `id` 比较新旧配置，只更新发生变化的条目。`disabled: true` 可以卸载插件而保留配置项，改回 `false` 后再重新挂载。

![时间可组合性与空间可组合性](assets/chapter12/12-2-02-spatiotemporal.svg)

Effect 记录插件创建了哪些需要清理的资源，并在退出时撤销；`inject` 记录插件需要哪些能力，并随依赖变化调整 Fiber。Cordis 论文分别把它们称为时间可组合性和空间可组合性。

这些能力有明确边界。Cordis 可以撤销由 Context 管理的注册，已经发出的消息和写入外部系统的数据不会随 Fiber 卸载消失。依赖声明也不提供安全隔离。不可信代码仍需放进单独进程、WebAssembly 或虚拟机等隔离环境。

![Cordis 管理插件实例的恢复，同时保留系统边界](assets/chapter12/12-3-01-problem-scenes-boundary.svg)

## Cordis 如何支撑 dsh 的工具调用 {#sec-12-4}

前三节使用独立的小例子观察 Cordis。这一节回到 dsh 的 `tools` Service，把同一套 Plugin、Fiber、Service、Event 和 Effect 放进一次真实工具调用。示例由代码直接调用工具执行接口，不需要模型密钥。插件的打包、安装和长期使用留到下一章完成。

### 向 tools Service 注册工具

官方教程创建 `greet-tool.ts`，先声明对 `tools` 的依赖：

```ts
export const inject = ['tools']
```

`apply` 通过 `ctx.tools.register()` 注册工具：

```ts
ctx.tools.register(defineTool({
  name: 'greet',
  description: 'Greet the named person.',
  parameters: {
    name: { type: 'string', required: true },
  },
  output: {
    schema: { type: 'string' },
    render: (_args, value) => [{ type: 'text', text: value }],
  },
  async execute(args) {
    return `Hello, ${args.name}!`
  },
}))
```

这里的 `ctx.tools` 是 Service，`inject` 保证它已经可用。`register()` 产生的清理动作会附着到当前 Fiber。插件卸载时，`greet` 也会从工具表中移除。

### 让真实工具流水线执行一次

教程用代码代替模型，直接发起调用：

```ts
const result = await ctx.tools.execute({
  callId: CallId('demo-1'),
  name: 'greet',
  arguments: { name: 'Cordis' },
  signal: new AbortController().signal,
})
```

这次调用会经过 dsh 的工具执行扩展点：

```text
ctx.tools.execute()
        ↓
tools/pre-execute
        ↓
tools/execute
        ↓
greet.execute()
        ↓
校验返回值并执行 output.render
        ↓
tools/post-execute
        ↓
finalizeContent
        ↓
tools/result
```

`tools/pre-execute` 可以处理权限和沙箱，`tools/execute` 可以包裹超时、重试或指标记录。工具返回值经过 Schema 校验和 `output.render` 后进入 `tools/post-execute`，监听器可以接受、阻止或替换结果。工具自己的 `finalizeContent` 完成最后一次内容调整，`tools/result` 随后通知观察者。

### 观察工具结果

另一个插件监听 `tools/result`：

```ts
export function apply(ctx: Context) {
  ctx.on('tools/result', (exec, result) => {
    const text = result.content
      .map(block => block.type === 'text' ? block.text : '')
      .join('')
    console.log(`[tool-logger] ${exec.name} -> ${text}`)
  })
}
```

组合需要 dsh 的 system prompt 和 tools 插件：

```yaml
- name: '@deepseek-ai/dsh-system-prompt'
- name: '@deepseek-ai/dsh-tools'
- name: './tool-logger.ts'
- name: './greet-tool.ts'
```

运行后会看到：

```console
[tool-logger] greet -> Hello, Cordis!
tool replied: [{"type":"text","text":"Hello, Cordis!"}]
```

logger 先打印，因为 `tools/result` 在 `ctx.tools.execute()` 返回结果之前发出。两个自定义插件没有互相导入，它们通过 `ctx.tools` 和事件系统接入同一条执行流程。

把这次调用对应回前三节，可以看到每个概念都有具体位置。

| Cordis 概念 | 在 dsh 工具系统中的位置 |
|---|---|
| Service | `ctx.tools` 提供工具注册和执行能力 |
| `inject` | 工具插件声明自己依赖 `tools` |
| Effect | `ctx.tools.register()` 随所属 Fiber 卸载而撤销 |
| Event | `tools/result` 等事件允许插件观察或介入执行过程 |
| Plugin | tools、logger 和策略都可以由独立插件提供 |
| Fiber | 上述插件被加载后各自形成运行实例 |

### 区分实时事件和会话记录

`tools/result` 与 `tool/result` 名字接近，承担的工作不同。

| 名称 | 类型 | 用途 |
|---|---|---|
| `tools/result` | Cordis Event | 插件实时观察一次工具执行的最终结果 |
| `tool/result` | Session Event | 把工具结果写入会话日志，供恢复、重放和下一轮模型请求使用 |

本节直接调用 `ctx.tools.execute()`，看到的是 Cordis 工具流水线。完整 Agent 还会由 agent loop 记录 `tool/call` 和 `tool/result`，再把这些持久记录整理成下一轮模型消息。

回看本章，Context 提供运行环境，Loader 按配置加载 Plugin，Plugin 运行成 Fiber。Fiber 通过 Service 建立依赖，通过 Event 参与运行过程，并用 Effect 保证卸载时完成清理。dsh 的插件树就运行在这套机制上。
