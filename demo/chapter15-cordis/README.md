# 第 15 章 Cordis 配套示例

本目录提供[第 15 章](../../book/chapter15.md)七组示例的完整 TypeScript 文件。每组目录中的代码对应正文第一次运行时的版本；修改问候语、填写错误配置、停用插件和增加执行监听，按正文继续操作。

## 准备环境

先准备一个用于练习的 deepseek-harness 源码副本，并按[开发指南](https://github.com/deepseek-ai/deepseek-harness/blob/5dda764ed3aa172535a7967b06ff95d9cbfe536a/docs/development.zh.md)安装源码依赖。本章核验使用源码提交 `5dda764ed3aa172535a7967b06ff95d9cbfe536a`、Node.js `24.20.0` 和该提交的依赖锁定文件。

把本书 `demo/` 下的整个 `chapter15-cordis` 文件夹复制到练习用源码副本根目录，保留目录名。复制后结构如下：

```text
deepseek-harness/
├── node_modules/
├── tsconfig.json
├── tsconfig.base.json
├── vendor/
│   └── cordis/bin.js
└── chapter15-cordis/
    ├── README.md
    ├── 01-first-plugin/     # hello.ts、cordis.yml
    ├── 02-lifecycle/        # lifecycle.ts、cordis.yml
    ├── 03-services/         # greeter.ts、consumer.ts、cordis.yml
    ├── 04-events/           # greeter.ts、consumer.ts、cordis.yml
    ├── 05-config/           # config-demo.ts、cordis.yml
    ├── 06-hmr/              # hello.ts、cordis.yml
    └── 07-tools/            # greet-demo.ts、cordis.yml
```

七组示例共用源码根目录的依赖与 TypeScript 路径配置，因此没有各自的 `package.json`。仅安装 dsh 命令行程序，或直接在书稿仓库的 Demo 目录执行下面的启动命令，都不具备所需环境。所有示例都不调用大模型，也不需要 API 密钥。

## 运行示例

从练习用 deepseek-harness 源码根目录进入第一组：

```bash
cd chapter15-cordis/01-first-plugin
node --import tsx ../../vendor/cordis/bin.js
```

终端输出 `Hello, Cordis!`。启动器读取当前目录的 `cordis.yml`；`../../vendor/cordis/bin.js` 从示例目录向上两层找到源码启动器。

其他各组使用相同启动命令，只需进入对应目录。切换示例前等待程序退出；HMR 示例会持续运行，按 Ctrl-C 停止。然后回到源码根目录，再进入另一组：

```bash
cd ../..
cd chapter15-cordis/02-lifecycle
node --import tsx ../../vendor/cordis/bin.js
```

| 示例目录 | 对应正文 | 第一次运行的观察点 |
| --- | --- | --- |
| `01-first-plugin` | 15.1 认识 Cordis | 打印 `Hello, Cordis!` |
| `02-lifecycle` | 15.2 插件如何加载和卸载 | 打印 tick，清理后停止；清理日志先于卸载完成日志 |
| `03-services` | 15.3 服务 | consumer 调用 greeter，打印 `Hello, world!` |
| `04-events` | 15.3 事件 | 事件监听日志先于调用方的返回值日志 |
| `05-config` | 15.3 配置 | 使用默认问候语，分别问候 alpha 和 beta |
| `06-hmr` | 15.3 热重载 | 打印问候语并开始监视当前目录 |
| `07-tools` | 15.4 Cordis 如何组装 dsh | 先打印工具结果观察日志，再打印调用方收到的内容块 |

## 继续练习

- 服务依赖：交换 `03-services/cordis.yml` 中两个插件的顺序，仍应正常问候；去掉提供方后，consumer 不会执行问候。
- 配置：按正文修改 `05-config/cordis.yml`，验证自定义值和错误类型；完成后恢复合法配置。
- 热重载：保持 `06-hmr` 运行，修改 `hello.ts` 并保存，再修改配置中的 `disabled`，观察卸载和重新加载。
- 工具执行监听：把正文“监听工具执行过程”中的监听代码加进 `07-tools/greet-demo.ts` 的 `apply` 内，放在工具注册之前，再次运行。

旧的三个 JavaScript 示例目录已由这些示例替换，旧版本可从 Git 历史查阅。
