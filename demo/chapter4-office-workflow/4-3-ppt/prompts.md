# 4.3 设计并生成 PPT 演示文稿提示词

## 检查 ModLens 配置

```text
请使用 ModLens 阅读下面这张页面预览：

4-2-word/output/preview/预览-第1页.png

只根据图片内容，告诉我页面标题、费用预算、实际总费用和预算执行率。
```

## 安装 PPT Skill

```text
请将下面的 PPT Skill 安装到当前工作区的
.agents/skills/pptx-generator：

https://github.com/MiniMax-AI/skills/tree/main/skills/pptx-generator

安装完成后检查 SKILL.md 和 references 是否齐全，
并告诉我安装位置。先不要生成演示文稿。
```

## 生成并检查演示文稿

```text
请使用 pptx-generator Skill，读取：

4-1-excel/output/产品发布会费用整理结果.xlsx
4-2-word/output/产品发布会费用复盘报告.docx
4-3-ppt/source/演示文稿制作要求.md

生成一套《产品发布会费用复盘》演示文稿。

要求：
1. 严格按照制作要求生成 6 页、16:9 的幻灯片，
2. 金额、比例和异常事项必须与 Excel、Word 报告一致，
3. 采用深蓝、浅蓝为主，橙色突出异常事项，
4. 使用大数字、图表和简短列表，避免大段文字，
5. 生成可以继续编辑的 PPTX，并保留生成源文件，
6. 生成每页预览，使用 ModLens 检查文字溢出、重叠、对齐和风格一致性，
7. 发现问题后直接修正并重新检查，
8. 将最终文件保存为：
4-3-ppt/output/产品发布会费用复盘.pptx。

缺少运行依赖时请自行安装。完成后说明生成了哪些文件，
以及检查和修改了哪些问题。
```
