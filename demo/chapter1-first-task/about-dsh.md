# About DSH（DeepSeek Harness）

DSH（DeepSeek Harness）是 DeepSeek 推出的开源 AI 智能体（Agent）开发与运行框架，基于插件化架构构建，以 MIT 协议发布。`dsh` 是它的命令行启动器：核心思想是"profile"——把若干插件组合包（bundle）的配置层按顺序叠加，再叠加用户自己的覆盖配置（`cordis.patch.yml`），最终组装出一个可运行的完整应用。内置的 `web` 和 `headless` 两个 profile 首次使用即可自动初始化。

DSH 能做什么：通过 `dsh web` 可以启动一个浏览器图形界面，与 AI 助手进行多轮对话并协作完成实际任务，例如读写文件、执行 Shell 命令、调用各种工具、搜索网页、管理长时目标与后台任务等；通过 `dsh --profile headless "任务描述"` 则可以在无界面环境下运行一次性会话，直接输出最终答案后退出。整个运行过程支持会话持久化、状态压缩、沙箱权限控制等能力。

DSH 的扩展性也很强：可以自定义 profile、通过 `dsh plugin` 安装和管理插件、用 patch 层按需覆盖默认行为。因此它既能作为开箱即用的个人 AI 助手，也能作为搭建定制化多智能体工作流的底层框架。
