# 第 12 章扩展案例配套文件

这里放的是第 12 章“扩展 dsh 的能力”用到的示例文件。每个子目录对应正文中的一个小节，可以单独使用。

## 12.1 周报 Skill

`12-1-weekly-report/` 用来复现项目级 Skill 生成周报的案例。新建一个空工作区，将下面两项复制进去：

```text
本周工作草记.md
.dsh/
```

`.dsh/skills/weekly-report/SKILL.md` 是本节使用的 Skill，`本周工作草记.md` 是交给 dsh 整理的原始材料。复制完成后，按照正文提示新建会话并生成周报。

`expected/周报-2026-08-28.md` 保存了一份实测结果，只用于对照自己的输出，复现时不需要复制到工作区。

## 12.2 文件系统 MCP

`12-2-mcp-filesystem/` 用来复现 MCP 读取工作区外文件的案例。`notes/` 中有一份数据库断连排查笔记，可以把这个目录复制到工作区外的任意位置。

打开 `cordis.patch.example.yml`，将下面的示例路径替换为 `notes/` 所在目录的绝对路径：

```text
/absolute/path/to/dsh-mcp-notes
```

改好路径后，将示例中的 MCP 配置加入当前 web profile 的 `cordis.patch.yml`，原文件中的其他配置继续保留。

## 12.3 社区插件

`12-3-community-plugin/README.md` 保存本章实测使用的社区插件安装命令：

```bash
dsh plugin --profile web add dsh-find-plugin
```

安装前先检查 npm 包信息和源码，确认插件来源与权限符合自己的使用要求。安装完成后重启 dsh，新工具才会加载。

## 12.4 自定义插件

`12-4-tool-decide/` 保存随机选择工具的插件源码和两份配置片段。按照下面的顺序操作：

1. 将 `tool-decide/` 复制到 `$DSH_HOME/profiles/web/plugins/`。
2. 将 `profile-package.fragment.json` 中的依赖项加入 web profile 的 `package.json`。
3. 将 `cordis.patch.example.yml` 中的插件配置加入 web profile 的 `cordis.patch.yml`。
4. 进入 web profile 目录运行 `pnpm install`，然后重启 dsh。

重启后，`tool-decide` 会注册一个名为 `pick_one` 的工具，用来从多个选项中随机选出一个。
