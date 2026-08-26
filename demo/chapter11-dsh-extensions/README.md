# 第 11 章扩展案例配套文件

本目录保存第 11 章“扩展 dsh 的能力”使用的示例文件，分别对应周报 Skill、文件系统 MCP、社区插件和自定义插件。

## 11.1 周报 Skill

`11-1-weekly-report/` 中包含原始草记、项目级 Skill 和一份实测生成结果。复现时，新建一个空工作区，将 `本周工作草记.md` 与 `.dsh/` 复制进去，再按照正文提示新建会话。`expected/` 只用于比较结果，不需要复制到工作区。

## 11.2 文件系统 MCP

`11-2-mcp-filesystem/notes/` 是 MCP 服务器需要读取的工作区外目录。将它复制到自选位置，把 `cordis.patch.example.yml` 中的示例路径替换为该目录的绝对路径，再将配置合并到当前 web profile 的 `cordis.patch.yml`。不需要用示例文件覆盖已有配置。

## 11.3 社区插件

`11-3-community-plugin/README.md` 保存本章实测使用的安装命令。第三方插件源码和 `node_modules` 不在本目录重复保存，安装前仍应自行检查插件来源与权限。

## 11.4 自定义插件

将 `11-4-tool-decide/tool-decide/` 复制到 `$DSH_HOME/profiles/web/plugins/`，再把两个示例配置中的内容分别合并到 profile 的 `package.json` 和 `cordis.patch.yml`。完成后在 profile 目录运行 `pnpm install`，并重启 dsh。
