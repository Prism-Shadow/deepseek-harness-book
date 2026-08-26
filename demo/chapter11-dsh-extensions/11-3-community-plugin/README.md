# 安装社区插件

第 11 章使用下面的命令安装 `dsh-find-plugin`：

```bash
dsh plugin --profile web add dsh-find-plugin
```

安装命令会修改 web profile 的依赖与插件列表。安装前应检查 npm 包信息和源码；安装后需要重启 dsh，新的工具才会加载。
