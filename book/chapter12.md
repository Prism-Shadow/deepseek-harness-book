# dsh 的核心：Cordis {#ch-12}

上一章沿着一次任务的执行过程，介绍了模型、工具、会话和 Agent Loop 怎样配合完成任务。这些能力由不同插件分别提供，没有集中写在一个整体程序里。

Cordis 负责这些插件的运行时组织。程序启动时，它加载插件并建立插件之间的关系；配置或依赖发生变化时，它还会相应调整插件的运行状态。

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

这两层分别负责配置组合和插件运行：dsh 生成最终配置树，Cordis 的 Loader 根据这份配置加载插件。

下面几个概念会贯穿本章。这里先知道它们各自代表什么，后面再结合实际插件逐步展开。

| 概念    | 这里先这样理解                                 |
| ------- | ---------------------------------------------- |
| Context  | 插件运行时使用的上下文，也是访问其他能力的入口 |
| Plugin   | 可以被 Cordis 加载的一段功能定义               |
| Fiber    | Plugin 一次加载所产生的运行实例                |
| Loader   | 根据配置加载、更新和卸载插件                   |
| Service  | 一个插件向其他插件提供的能力                   |
| Event    | 插件之间发送通知或介入运行过程的机制           |
| Effect   | 与 Fiber 生命周期绑定、停止时需要清理的副作用  |

其中最需要先分清的是 Plugin 和 Fiber：

```text
Plugin          加载          Fiber
代码定义  ───────────────►  一次运行实例
```

同一个 Plugin 可以被多次加载，每次都会产生不同的 Fiber。

下一步回到 dsh，看看模型、工具、会话和 Agent Loop 等能力怎样出现在最终的插件配置树中。

### 看看 dsh 是怎样组装出来的

下面的命令会打印 Web profile 最终生成的配置树：

```bash
npx -y @deepseek-ai/dsh --profile web --dump-config
```

输出中可以找到 `agent-loop` 和 `tool-todo`。前者负责驱动 Agent Loop，后者提供待办事项工具。两者职责差别很大，但在最终配置中都表现为插件配置项，都有自己的 `id`、`name` 和 `config`。

![实际 dump-config 输出中 agent-loop 与 tool-todo 是平等插件](assets/chapter12/12-1-02-plugin-tree-proof.svg){width=88%}

这是前面配置组合机制在 Web profile 中的实际结果。模型适配器、工具、会话、沙箱和 Agent Loop 等能力，也都通过插件进入 Cordis 运行时。

![dsh 的各项能力通过 Cordis Context 协作](assets/chapter12/12-1-01-everything-is-plugin.svg){width=88%}

图中的 `Context` 表示插件共同使用的运行环境，箭头表示协作关系，不代表实际加载顺序。

下面把 Web profile 形成最终配置的过程对应到前面的 profile、bundle 和 patch：

![dsh 从组合包到用户补丁的分层装配](assets/chapter12/12-1-03-composition-layers.svg){width=88%}

**亲手验证。** 将 `--profile web` 换成自己正在使用的 profile，再执行一次 `--dump-config`。搜索模型适配器、`agent-loop` 和常用工具的名称，观察它们最终对应哪些插件配置项。如果预期的插件没有出现，可以先从 profile、bundle 和后续 patch 的组合关系开始排查。

至此可以划清 dsh 组合层与 Cordis 运行时的边界：**dsh 负责生成本次启动采用的最终配置，Cordis 则根据这份配置加载插件，并管理它们运行期间的协作和生命周期。**

## 插件如何加载和卸载 {#sec-12-2}

完整的 dsh 一次会加载许多插件，不容易看清其中一个插件从加载到退出经历了什么。本节先把环境缩到最小，只运行 Cordis 官方教程中的一个 `hello.ts` 插件。借助这个例子，可以单独观察 Loader 怎样读取配置、Plugin 怎样产生 Fiber，以及 Fiber 停止时怎样清理自己注册的资源。

### 从 Plugin 到 Fiber

先创建一个最简单的插件 `hello.ts`：

```ts
import type { Context } from '@deepseek-ai/cordis'

export const name = 'hello'

export function apply(ctx: Context) {
  console.log('hello from my first plugin')
}
```

这里的 `apply()` 是插件被加载时执行的入口。`ctx` 则是 Cordis 为这次插件运行提供的 `Context`，后面插件访问服务、监听事件和注册清理逻辑都要通过它完成。

同一目录再创建 `cordis.yml`：

```yaml
- name: './hello.ts'
```

这份配置只有一个插件项，表示本次只需要加载 `hello.ts`。因此，相比完整的 dsh 配置，我们可以把 Loader 的行为集中在这一项上。

在官方源码仓库完成 `pnpm install` 后，进入 `tmp/cordis-tutorial`，运行：

```bash
node --import tsx ../../vendor/cordis/bin.js
```

终端会输出：

```text
hello from my first plugin
```

这行输出说明 `hello.ts` 已经被加载，`apply()` 也已经执行。

![官方最小插件从配置到输出的完整路径](assets/chapter12/12-1-04-official-loader-flow.svg){width=82%}

这里先记住一条主线：**配置选择 Plugin，加载产生 Fiber，`apply(ctx)` 在这个运行实例中执行。** 同一个 Plugin 可以被多次加载，每次都会产生自己的 Fiber。

### 在 apply 之前校验配置

插件通常需要从配置中读取参数，`cordis.yml` 中的插件条目可以带有 `config`，插件则可以导出一个名为 `Config` 的 Schema，规定这些参数允许什么类型、哪些可以省略，以及省略时使用什么默认值。

```typescript
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

这里有两个同名的 `Config`，`interface Config` 是 TypeScript 类型，用来描述代码中 `config` 应有的结构，`const Config` 则是运行时使用的 Schema，Cordis 会用它检查真正从配置文件读到的数据，并补上默认值。

例如，只配置 `targets`：

```yaml
- name: './config-demo.ts'
  config:
    targets: ['alpha', 'beta']
```

运行后得到：

```text
Hello, alpha!
Hello, beta!
```

配置中没有提供 `greeting`，Schema 因此补上默认值 `Hello`。等到 `apply(ctx, config)` 被调用时，传入的 `config` 已经完成校验和默认值补全。

如果把 `targets` 错写成字符串：

```yaml
config:
  targets: 'not-an-array'
```

这份配置不符合 Schema 对 `targets` 的约束，因此会在 `apply()` 执行之前校验失败。对应 Fiber 进入 `FAILED`，`apply()` 不会被调用。这样，错误配置会停在插件入口之外，不会作为不符合约定的数据继续进入插件逻辑。

### 让资源跟随 Fiber 清理

插件开始运行后，还可能创建定时器、连接或文件 watcher。这些资源如果比插件活得更久，就可能在插件卸载后继续运行，因此也需要跟随对应的 Fiber 一起清理。

Cordis 把这类需要随 Fiber 撤销的操作表示为 **Effect**。对于 Cordis 本身不知道怎样释放的资源，可以用 `ctx.effect()` 在创建资源的同时返回一个 disposer，说明卸载时怎样清理它：

```typescript
ctx.effect(() => {
  const timer = setInterval(() => console.log('tick'), 200)

  return () => {
    clearInterval(timer)
    console.log('heartbeat cleaned up')
  }
})
```

`ctx.effect()` 中的函数会立即执行，因此定时器在插件加载时开始工作；返回的 disposer 则被记录到当前 Fiber 上，等 Fiber 卸载时执行。

把这段逻辑放进 `heartbeat` 插件，再从另一个插件中挂载它。`ctx.plugin()` 会返回这次加载对应的 Fiber：

```typescript
const fiber = ctx.plugin(heartbeat)

ctx.effect(() => {
  const timer = setTimeout(async () => {
    await fiber.dispose()
    console.log('disposed')
  }, 700)

  return () => clearTimeout(timer)
})
```

这里外层的 `setTimeout` 也放进了 `ctx.effect()`。这样如果父插件先被卸载，尚未触发的定时任务也会一起取消，不会在已经停止的插件上继续执行。Cordis 官方教程同样采用这种写法。

运行后会先看到若干次：

```text
tick
```

大约 700 毫秒后出现：

```text
heartbeat cleaned up
disposed
```

`fiber.dispose()` 开始卸载 `heartbeat`。Cordis 会运行这个 Fiber 持有的 disposer，等包括异步清理在内的工作全部完成后，`dispose()` 才会结束。

Fiber 的主要状态包括：

```text
PENDING → LOADING → ACTIVE → UNLOADING → DISPOSED
                 ↘ FAILED
```

`LOADING` 表示插件正在加载，`ACTIVE` 表示已经正常运行；卸载时进入 `UNLOADING`，所有清理完成后成为 `DISPOSED`。配置校验或插件启动过程抛出异常时，则进入 `FAILED`。`PENDING` 与 Service 依赖有关，留到下一节解释。

很多时候不需要亲自调用 `ctx.effect()`。`ctx.on()`、`ctx.plugin()` 和 Service 注册本身就会把对应的清理操作挂到当前 Fiber 上；dsh 中的 `ctx.tools.register()` 也采用相同机制。只有定时器、外部连接、文件 watcher 等 Cordis 无法自行理解如何释放的资源，才需要显式提供 disposer。

## 插件如何依赖、通信和更新 {#sec-12-3}

前面只看了一个插件从加载到卸载的生命周期。真实的 dsh 中，插件很少完全独立运行：工具插件可能要使用工具运行时，Agent Loop 需要模型、会话等服务，其他插件还可能监听某个过程，或者在其中插入自己的处理逻辑。

Cordis 主要用两套机制处理这些关系：

```text
需要长期使用另一项能力
         │
         ▼
  Service + inject

某件事发生时需要通知、观察或介入
         │
         ▼
       Event
```

**Service** 是插件向运行时提供的一项可复用能力，其他插件可以通过 `Context` 访问它；**inject** 用来声明当前插件运行所依赖的 Service，并让 Cordis 在依赖尚未满足时暂缓启动。

**Event** 则面向某一次发生的过程。插件不需要直接依赖事件的发送方，只要监听相应事件，就可以在事件发生时得到通知，或者在允许的情况下介入处理。

这两种关系还会影响插件更新：Service 出现、消失或被替换时，依赖它的 Fiber 可能需要重新计算运行状态；事件监听则会随着所属 Fiber 一起注册和撤销。后面分别来看这两种机制。

### 用 Service 和 `inject` 建立依赖

Service 是插件向其他插件提供的一项具名能力，并通过 `Context` 暴露。例如，可以定义一个名为 `greeter` 的服务：

```typescript
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

这里有两件事需要分开看。`declare module` 只告诉 TypeScript：`Context` 上存在一个 `ctx.greeter`，它不负责运行时注册。真正创建 `GreeterService` 时，`super(ctx, 'greeter')` 才把当前实例注册为名为 `greeter` 的 Service；`ctx.plugin(GreeterService)` 则负责把这个 Service 类作为子插件加载。这里的 `export const name` 只是插件的名称，与 Service 名称不是同一个概念，只是这个例子恰好都写成了 `greeter`。

另一个插件需要使用这项能力时，可以声明：

```typescript
import type { Context } from '@deepseek-ai/cordis'

export const name = 'consumer'
export const inject = ['greeter']

export function apply(ctx: Context) {
  console.log(ctx.greeter.greet('world'))
}
```

`inject = ['greeter']` 声明：这个插件只有在 `greeter` Service 可用时才能运行。因此进入 `apply()` 时，Cordis 已经保证 `ctx.greeter` 就绪。

在 `cordis.yml` 中组合两个插件：

```yaml
- name: './greeter.ts'
- name: './consumer.ts'
```

运行后会看到：

```text
Hello, world!
```

`inject` 把 Service 是否可用变成消费方 Fiber 的运行条件，`cordis.yml` 中的书写顺序不决定插件何时开始运行。如果 `consumer` 准备启动时 `greeter` 尚不可用，它会停在 `PENDING`；等 `greeter` 出现后，再继续进入 `LOADING`，执行 `apply()`，成功后成为 `ACTIVE`。

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

消费方依赖的是 Service 的能力约定，具体实现可以由不同插件提供。这条稳定的能力边界可以看作一条 **seam（替换缝）**：只要新的提供方保持接口兼容，消费方就不需要修改。

![同一个能力 seam 可以接入不同提供方](assets/chapter12/12-2-03-capability-seam.svg){width=88%}

dsh 因此可以在本机、沙箱和远程实现之间替换能力提供方，而不必让上层插件随之修改。

### 用 Event 观察或介入运行过程

Service 适合插件明确调用一项长期存在的能力。还有一类协作围绕“某件事情正在发生”：一个插件发出事件，其他插件可以监听它。监听器既可以只是观察并记录，也可以根据事件采用的分发方式参与处理，甚至影响后续结果。

Cordis 用 Event 处理这类关系。事件发出方只需要按照约定发出事件，不需要知道有多少插件正在监听，也不需要知道监听器来自哪里。

首先声明一个统计事件：

```ts
import type { Context } from '@deepseek-ai/cordis'

declare module '@deepseek-ai/cordis' {
  interface Events {
    'stats/report'(name: string, count: number): void
  }
}
```

这里的 `Events` 为事件定义名称和参数类型。这样，发送和监听 `stats/report` 时，TypeScript 都可以检查事件名以及参数是否匹配。

一个插件可以发出这项事件：

```ts
ctx.emit('stats/report', name, count)
```

其他插件则可以监听：

```ts
ctx.on('stats/report', (name, count) => {
  console.log(`[stats] ${name} -> ${count}`)
})
```

对于这种只负责通知的事件，可以先把关系理解成：

```text
                 ┌──► listener B
plugin A ──Event─┤
                 └──► listener C
```

发出事件的插件不需要知道监听器的数量或来源。以后增加一个新的监听插件，原来的发送方也不需要修改。

事件监听同样受到 Fiber 生命周期管理。`ctx.on()` 注册监听器时，会把相应的撤销操作记录到当前 Fiber；Fiber 卸载后，这个监听器也会自动移除，不需要插件另外维护清理代码。

Event 不只有一种执行方式。不同的分发模式决定监听器怎样执行、是否等待异步结果，以及监听器能不能影响整个处理过程。

| 模式        | 行为                                                         |
| ----------- | ------------------------------------------------------------ |
| `emit`      | 同步调用所有监听器，不等待异步结果，也不使用返回值           |
| `parallel`  | 并行执行所有监听器，并等待它们全部完成                       |
| `serial`    | 按顺序执行监听器，遇到第一个有效返回值后停止                 |
| `bail`      | `serial` 的同步版本                                          |
| `waterfall` | 监听器组成处理链，可以继续调用下游，也可以包装或截断后续处理 |

`emit` 和 `parallel` 更偏向通知，`serial` 和 `bail` 可以提前给出结果；下面重点看能够形成处理链的 `waterfall`。

Service 用来调用一项长期存在的能力，Event 用来围绕一次过程观察或参与。在 `waterfall` 中，监听器调用 `next()` 会继续执行下游，直接返回则会截断后续处理。

创建 `waterfall-demo.ts`：

```typescript
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

```text
HELLO
** BLOCKED **
```

输入 `hello` 时，两条监听器都调用 `next()`，默认结果返回后被第一条监听器转成 `HELLO`。输入包含 `blocked` 时，第二条监听器直接返回替代文本，默认处理被截断，最终得到 `** BLOCKED **`。

两种事件关系可以这样区分：

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
默认处理
   │
   ▼
  结果
```

因此，写 waterfall 监听器时有一条重要规则：**只要不打算截断后续处理，就必须调用 `next()`。** 如果一个本来只想记录日志或包装结果的监听器忘记调用 `next()`，它也会意外阻断后面的监听器和默认处理。

dsh 会把这种机制用在需要插件共同参与的关键处理链上。例如，`agent/request` 允许插件介入模型请求，`approval/request` 让不同提供方参与审批决策；工具执行还依次经过 `tools/pre-execute`、`tools/execute` 和 `tools/post-execute` 等 waterfall。后面回到 dsh 的实际执行过程时，我们会沿着一次工具调用继续观察这些扩展点。

### 依赖变化时重新加载

如果一个 Service 的提供方消失，依赖它的消费方也会停止并清理自己的 Effect；Service 恢复后，消费方重新加载。

```text
Provider 消失
      │
      ▼
Consumer 停止并清理 Effects
      │
      │ Provider 恢复
      ▼
Consumer 重新加载
      │
      ▼
ACTIVE
```

这种变化既可能来自源码 HMR，也可能来自配置调整。Loader 根据稳定的 `id` 识别发生变化的配置项，只重新处理受影响的插件。

Effect 可以理解为插件“做了什么”，退出时需要撤销；Service 与 `inject` 描述插件“需要什么”，依赖变化时重新计算运行关系。下面的图把两者概括为时间可组合性和空间可组合性。

![时间可组合性与空间可组合性](assets/chapter12/12-2-02-spatiotemporal.svg){width=88%}

这些机制让很多变化可以在插件级处理，无需重启整个进程。Cordis 只能自动撤销纳入其生命周期管理的资源；外部写入和安全隔离等问题，仍需要事务、补偿或独立沙箱处理。

## Cordis 如何支撑 dsh 的工具调用 {#sec-12-4}

前三节使用独立的小例子观察 Cordis。这一节回到 dsh 的 `tools` Service，把同一套 Plugin、Fiber、Service、Event 和 Effect 放进一次真实工具调用。示例由代码直接调用工具执行接口，不需要模型密钥。插件的打包、安装和长期使用留到下一章完成。

### 向 tools Service 注册工具

官方教程创建 `greet-tool.ts`，先声明对 `tools` Service 的依赖：

```ts
export const inject = ['tools']
```

`apply()` 再通过 `ctx.tools.register()` 注册工具：

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

这里的 `ctx.tools` 是前面介绍过的 Service，`inject` 保证插件运行时这项能力已经可用。`ctx.tools.register()` 注册的工具也受 Fiber 生命周期管理：插件卸载后，`greet` 会自动从工具表中移除。

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
  允许 / 拒绝 / 询问
        ↓
registered guards
        ↓
tools/execute
  超时 / 重试 / 指标
        ↓
greet.execute()
        ↓
规范化工具结果
        ↓
tools/post-execute
        ↓
finalizeContent
        ↓
tools/result
```

`tools/pre-execute` 负责执行前的检查，可以允许、拒绝或要求审批；随后 guard 继续约束这次调用。`tools/execute` 包住真正的工具执行，适合加入超时、重试和指标统计。

工具返回后，dsh 会校验并渲染结果，再经过 `tools/post-execute` 和 `finalizeContent` 做最后处理，最终通过 `tools/result` 通知观察者。

### 观察工具结果

另一个插件可以监听 `tools/result`，观察已经完成的工具调用：

```typescript
export function apply(ctx: Context) {
  ctx.on('tools/result', (exec, result) => {
    const text = result.content
      .map(block => block.type === 'text' ? block.text : '')
      .join('')
    console.log(`[tool-logger] ${exec.name} -> ${text}`)
  })
}
```

再把 logger 和前面的 `greet` 工具一起加入配置：

```yaml
- name: '@deepseek-ai/dsh-system-prompt'
- name: '@deepseek-ai/dsh-tools'
- name: './tool-logger.ts'
- name: './greet-tool.ts'
```

运行后会看到：

```text
[tool-logger] greet -> Hello, Cordis!
tool replied: [{"type":"text","text":"Hello, Cordis!"}]
```

`tools/result` 会在 `ctx.tools.execute()` 返回之前发出，因此 logger 先收到并打印结果。`greet-tool` 和 `tool-logger` 没有直接依赖彼此：前者通过 `ctx.tools` 注册能力，后者通过 Event 观察执行结果，两者在同一条工具流水线中协作。

把这次调用对应回前面几节，Cordis 的几个核心概念都有了具体位置：

| **Cordis 概念** | **在 dsh 工具系统中的位置**                                  |
| --------------- | ------------------------------------------------------------ |
| Service         | `ctx.tools` 提供工具注册和执行能力                           |
| `inject`        | 工具插件声明自己依赖 `tools`                                 |
| Effect          | `ctx.tools.register()` 和 `ctx.on()` 随所属 Fiber 一起撤销   |
| Event           | `tools/result` 用于观察结果；执行前后的 waterfall 事件可以介入处理 |
| Plugin          | tools、工具、logger 和策略都可以由独立插件提供               |
| Fiber           | 每个 Plugin 加载后形成自己的运行实例                         |

### 区分运行时事件和会话记录

`tools/result` 与 `tool/result` 名字接近，承担的工作不同。

| 名称           | 属于          | 作用                                                   |
| -------------- | ------------- | ------------------------------------------------------ |
| `tools/result` | Cordis Event  | 在运行时通知插件一次工具执行已经得到最终结果           |
| `tool/result`  | Session Event | 把工具结果写入会话日志，供恢复、回放和后续模型请求使用 |

本节直接调用 `ctx.tools.execute()`，因此观察的是工具运行时内部的 Cordis 流水线。完整的 Agent 工具调用还会由 Agent Loop 把 `tool/call` 和 `tool/result` 写入 Session log，再从这些持久记录中整理出后续模型请求需要的消息。

dsh 先生成最终插件配置，Cordis 再由 Loader 把其中的 Plugin 加载为 Fiber。工具系统展示了 Service、Event 和 Effect 怎样共同工作，同一套机制也支撑模型、会话、沙箱和 Agent Loop 等其他能力。
