# 第 7 章短剧案例配套文件

本目录保存第 7 章《让 dsh 制作短剧》案例《纸箱小屋》的完整制作产物与提示词。案例使用 [drama-skills](https://github.com/worldwonderer/drama-skills) 配合 dsh，从一句话故事开始，完成剧本、资产设定、分镜、视频提示词，确认后逐镜生成视频，再合成发布。所有视频均由火山方舟 Seedance 2.0 mini 真实生成。

## 目录结构

```text
chapter7-drama-design/
├── README.md                  本说明
├── prompts/                   各环节实际发送给 dsh 的消息（按步骤编号）
│   ├── 01-初始化项目.md
│   ├── 02-写剧本.md
│   ├── 03-接受剧本并拆解资产.md
│   ├── 04-接受资产并拆分镜.md
│   ├── 05-接受分镜并写视频提示词.md
│   ├── 06-接受提示词并进入生产.md
│   └── 07-合成成片.md
├── short-drama.json           项目 manifest（标题、语言、画幅、权威决策）
├── 创作者决策/                创作者决策记录（制作形态、视觉方向、集长目标）
├── 设定集/                    角色、造型、场景、视图、道具与状态
├── 剧集/EP001/                第 1 集全部制作产物
```

`剧集/EP001/` 内部：

```text
剧集/EP001/
├── episode-card.json          单集卡
├── beats.jsonl                因果节拍（6 拍）
├── screenplay.md              剧本（8 场，0 台词，4 处字幕）
├── screenplay-index.jsonl     剧本索引（派生文件）
├── assets/                    资产出现、决策与连续性记录
├── storyboard/                分镜（coverage/shots/keyframes）、
│                              视频提示词（motion-specs/video-prompts）
└── 制作成果/
    ├── videos/                8 段分镜视频（SHOT-001.mp4 ~ SHOT-008.mp4）
    ├── final/                 拼接成片 last-order.mp4 与拼接清单
    └── release/               发布目录：成片《纸箱小屋》.mp4 与发布说明 README.md
```

## 关键产物位置

| 内容 | 路径 |
|---|---|
| 剧本 | `剧集/EP001/screenplay.md` |
| 分镜（8 镜） | `剧集/EP001/storyboard/shots.jsonl` |
| 视频提示词 | `剧集/EP001/storyboard/video-prompts.md` |
| 8 段分镜视频 | `剧集/EP001/制作成果/videos/` |
| 成片 | `剧集/EP001/制作成果/release/《纸箱小屋》.mp4`（40.7 秒，720p） |
| 发布说明 | `剧集/EP001/制作成果/release/README.md` |

## 说明

- `prompts/` 中的消息是本书实际操作时发送给 dsh 的原文，生产确认码与项目一一绑定，仅作记录，不可复用。
- 项目状态可用 drama-skills 的命令查看：`python <技能目录>/scripts/project_tool.py status demo/chapter7-drama-design`。
- `prompts/` 保留了实际操作时使用的原始项目路径 `demo/chapter7`；在本仓库中复用时，请按当前存档目录调整路径。
- 本目录不包含任何 API Key 或个人路径；密钥只在生成时从用户主目录的 `.ark-key` 读取。
