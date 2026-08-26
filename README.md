<div align="center">
  <h1>DeepSeek Harness 实战指南</h1>
  <h3>📘 《从零开始玩转 DeepSeek Harness》</h3>
  <p><em>从安装和第一次任务开始，带你学会让 DeepSeek Harness（简称 dsh）调用工具、读写文件，并把它扩展成自己的 Agent Harness。</em></p>

  <a href="https://dshbook.penguin.ooo/">
    <img src="https://img.shields.io/badge/在线阅读-dshbook.penguin.ooo-315EF5?style=flat&logo=gitbook&logoColor=white" alt="在线阅读：dshbook.penguin.ooo">
  </a>
  <img src="https://img.shields.io/badge/language-Chinese-2F855A?style=flat" alt="Language: Chinese">
  <a href="https://github.com/Prism-Shadow/dsh-book/stargazers">
    <img src="https://img.shields.io/github/stars/Prism-Shadow/dsh-book?style=flat&logo=github" alt="GitHub Stars">
  </a>
</div>

[在线阅读](https://dshbook.penguin.ooo/) ｜ [从第 1 章开始](https://dshbook.penguin.ooo/chapter1/)

## 📖 这本书写什么

DeepSeek Harness（简称 dsh）是一套由插件组装而成的 Agent Harness，用来组织模型、上下文、工具和任务运行过程。本书从安装和第一次任务讲起，通过调研、办公、内容创作、市场投研和代码审查等真实案例，带你逐步学会使用 dsh、扩展 dsh，并理解它的工作原理。关键步骤配有实际运行截图和示例文件，可以跟着正文操作。

## 🎯 你将学会什么

- 🚀 **快速上手：** 安装 dsh，接入模型，读懂任务结果和执行轨迹。
- 🔍 **调研办公：** 完成资料调研和市场投研，处理 Excel、Word、PPT、PDF 等常见文件。
- 🎨 **内容创作：** 生成海报、短剧分镜、求职材料和概念图。
- 🤝 **多人协作：** 接入飞书，并使用 AgentTeams 组织多个 Agent 完成代码审查。
- 🧩 **扩展能力：** 编写 Skill、接入 MCP，并安装或开发插件。
- ⚙️ **理解原理：** 掌握 Agent Harness、工具调用、上下文管理和 Cordis 插件系统。

## 🖼️ 书中案例

| [短剧画面](https://dshbook.penguin.ooo/chapter7/) | [活动海报](https://dshbook.penguin.ooo/chapter6/) | [自进化概念图](https://dshbook.penguin.ooo/chapter12/) |
| --- | --- | --- |
| [![dsh 生成短剧关键帧](book/assets/chapter7/7-2-07-frame-hook.png)](https://dshbook.penguin.ooo/chapter7/) | [![dsh 生成社区读书会海报](book/assets/chapter6/6-4-01-poster-final-export.png)](https://dshbook.penguin.ooo/chapter6/) | [![dsh 复用演化后的 Skill 生成概念图](book/assets/chapter12/12-2-07-skill-reuse.png)](https://dshbook.penguin.ooo/chapter12/) |

## 📚 内容导航

| 章节 | 主要内容 | 配套 Demo |
| --- | --- | --- |
| **第一部分　玩转 dsh** |  |  |
| [第 1 章 初识 dsh](https://dshbook.penguin.ooo/chapter1/) | 安装 dsh，接入模型，完成第一次任务。 |  |
| [第 2 章 定制自己的 dsh](https://dshbook.penguin.ooo/chapter2/) | 创建 AI 助手，用插件修改并保存主题。 |  |
| [第 3 章 让 dsh 完成一次调研](https://dshbook.penguin.ooo/chapter3/) | 拆分调研任务，核验材料并生成报告。 | [Demo](demo/chapter3-ai-code-assistant-research/) |
| [第 4 章 用 dsh 完成日常办公](https://dshbook.penguin.ooo/chapter4/) | 处理 Excel、Word、PPT 和 PDF。 | [Demo](demo/chapter4-office-workflow/) |
| [第 5 章 让 dsh 成为飞书里的数字秘书](https://dshbook.penguin.ooo/chapter5/) | 连接飞书，处理文档、任务、日程和审批。 | [Demo](demo/chapter5-feishu-assistant/) |
| [第 6 章 让 dsh 设计活动海报](https://dshbook.penguin.ooo/chapter6/) | 用 Design 插件生成并调整活动海报。 |  |
| [第 7 章 让 dsh 制作短剧](https://dshbook.penguin.ooo/chapter7/) | 编写剧本，生成分镜并制作短剧。 |  |
| [第 8 章 让 dsh 帮你找工作](https://dshbook.penguin.ooo/chapter8/) | 分析岗位，优化简历并进行模拟面试。 | [Demo](demo/chapter8-job-hunt/) |
| [第 9 章 用 dsh 构建市场投研助手](https://dshbook.penguin.ooo/chapter9/) | 定义信号，回测策略并生成市场报告。 | [Demo](demo/chapter9-a-share-research/) |
| [第 10 章 用 dsh 和 AgentTeams 组建 OPC 代码审查团队](https://dshbook.penguin.ooo/chapter10/) | 用 AgentTeams 并行审查仓库更新。 | [Demo](demo/chapter10-agentteams-repo-review/) |
| **第二部分　扩展 dsh** |  |  |
| [第 11 章 扩展 dsh 的能力](https://dshbook.penguin.ooo/chapter11/) | 使用 Skill、MCP 和插件扩展 dsh。 | [Demo](demo/chapter11-dsh-extensions/) |
| [第 12 章 让 dsh 通过自进化画出概念图](https://dshbook.penguin.ooo/chapter12/) | 通过多轮评分改进并复用绘画 Skill。 | [Demo](demo/chapter12-concept-art-evolution/) |
| **第三部分　拆解 dsh** |  |  |
| [第 13 章 Harness 的工作原理](https://dshbook.penguin.ooo/chapter13/) | 理解消息、会话、工具和上下文管理。 |  |
| [第 14 章 dsh 的核心：Cordis](https://dshbook.penguin.ooo/chapter14/) | 理解 Cordis 的插件加载、依赖和通信。 | [Demo](demo/chapter14-cordis/) |

## 👥 适合谁，怎么读

如果你第一次接触 dsh，建议从第 1 章开始顺序阅读。第 1 章会把安装、模型接入、任务结果和执行轨迹讲清楚，后面的案例都默认你已经知道这些基础操作。

如果你已经能正常使用 dsh，可以直接挑第一部分的实战案例。想做办公自动化，可以读第 4 章和第 5 章；想看多 Agent 调研和审查，可以读第 3 章和第 10 章；想做求职、投研或内容生产，可以读第 6 章到第 9 章。

如果你想把 dsh 改成更适合自己的工具，先读第 11 章。它会从 Skill 和 MCP 讲到插件开发。想理解内部机制，再读第 13 章和第 14 章。

## 🛠️ 本地构建

### 构建网站

在仓库根目录运行：

```bash
python3 -m pip install -r requirements-site.txt
python3 scripts/prepare_site.py
mkdocs serve
```

### 构建 PDF

本地安装 Pandoc、XeLaTeX 和脚本提示的 TeX 组件后，运行：

```bash
./scripts/build_pdf.sh
```

脚本会校验目录和章节标题，并在 `output/pdf/` 中生成 PDF。

## 🔗 相关链接

- [本书在线阅读](https://dshbook.penguin.ooo/)
- [DeepSeek Harness 官方介绍](https://www.deepseek.com/harness/)
- [DeepSeek Harness 官方源码](https://github.com/deepseek-ai/deepseek-harness)
