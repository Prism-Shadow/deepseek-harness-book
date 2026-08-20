# 4.2 编写 Word 报告提示词

## 安装 Word Skill

```text
请将下面的 Word Skill 安装到当前工作区的
.agents/skills/minimax-docx：

https://github.com/MiniMax-AI/skills/tree/main/skills/minimax-docx

安装完成后检查 SKILL.md、scripts 和 references 是否齐全，
并告诉我安装位置。先不要生成报告。
```

## 生成费用复盘报告

```text
请使用 minimax-docx Skill，读取：

4-1-excel/output/产品发布会费用整理结果.xlsx
4-2-word/source/报告写作要求.md

生成一份《产品发布会费用复盘报告》。

要求：
1. 金额和异常事项以 Excel 为准，不补造数据；
2. 包含项目概况、预算执行、分类费用分析、异常事项和后续建议；
3. 使用表格展示主要费用数据；
4. 采用简洁、正式的办公报告风格；
5. 检查标题层级、分页、表格宽度和中文排版；
6. 将文件保存为
4-2-word/output/产品发布会费用复盘报告.docx；
7. 生成页面预览并检查排版。

完成后说明生成了哪些文件，以及报告中的主要结论。
```
