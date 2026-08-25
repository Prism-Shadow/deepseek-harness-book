# 第 12 章 Cordis 配套示例

本目录保存第 12 章使用的最小 Cordis 示例。读者可以复制整个目录，在副本中运行和修改。

```text
chapter12-cordis/
├── 12-2-lifecycle/
│   ├── cordis.yml
│   ├── hello.js
│   └── package.json
├── 12-3-relations/
│   ├── consumer.js
│   ├── cordis.yml
│   ├── greeter.js
│   └── package.json
└── 12-3-waterfall/
    ├── cordis.yml
    ├── package.json
    └── waterfall-demo.js
```

每个子目录都可以单独运行：

```bash
pnpm install
pnpm exec cordis
```

示例只用于观察 Cordis 的插件加载、Service 依赖和 waterfall 调用顺序，不依赖完整的 dsh 工作区。正文使用 TypeScript 片段讲解接口和类型，本目录中的 `.js` 文件保留相同运行逻辑，便于直接执行。
