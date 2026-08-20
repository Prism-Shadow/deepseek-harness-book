# 第 10 章提示词

这里保存第 10 章真实仓库审查案例使用的提示词。

- [`repository-review-prompt.md`](repository-review-prompt.md)：使用 dsh 和 AgentTeams 审查 `penguin-harness` 最近两周更新的完整提示词。

进入已经固定版本的仓库目录后，可以直接把提示词内容交给 dsh：

```bash
dsh --profile headless "$(cat /path/to/repository-review-prompt.md)"
```

提示词中的日期、基线提交和截止提交属于本章案例。审查其他仓库时，需要先替换这些边界。
