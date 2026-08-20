# 4.1 整理 Excel 表格提示词

## 安装 Excel Skill

```text
请将下面的 Excel Skill 安装到当前工作区的
.agents/skills/minimax-xlsx：

https://github.com/MiniMax-AI/skills/tree/main/skills/minimax-xlsx

安装完成后检查文件是否齐全，并告诉我安装位置。先不要处理表格。
```

## 整理费用表

```text
请使用已安装的 minimax-xlsx Skill，整理
4-1-excel/source/产品发布会费用明细.xlsx。

要求：
1. 保留原始文件，不要覆盖；
2. 统一日期和费用类别；
3. 删除完全重复的记录；
4. 保留场地押金退回这笔负数记录；
5. 标出类别缺失、凭证缺失等需要人工确认的问题；
6. 生成“整理后明细”“费用汇总”和“异常记录”三个工作表；
7. 在汇总表中统计总费用及各类别费用；
8. 调整列宽、表头、金额格式和重点数据的样式；
9. 将结果保存为
4-1-excel/output/产品发布会费用整理结果.xlsx。

完成后说明发现了哪些问题、做了哪些修改，并给出整理后的费用总额。
```
