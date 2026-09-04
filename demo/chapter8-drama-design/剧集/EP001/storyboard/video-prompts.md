# EP001 · 视频提示词

> 来源：`motion-specs.jsonl` 的已接受记录
> 配方：`motion-generic@1.0`
> 范围：本文件仅提供提示词，不触发媒体服务；实际视频生产交 `$short-drama-produce`

## `SHOT-001` · 开场钩子：湿猫隔玻璃望热气

- **运动规格**：`MOTION-001`
- **起始帧**：`KEY-001`
- **参考图用途**：`REF-001 / order 1 / start_frame` 只决定起始构图与可见状态；不得导入尚未发生的动作与终点；检查状态 `unverified`（关键帧为文本规格、尚未生成参考图，无像素检查证据）
- **时长（只读）**：`5s`
- **边界核对**：`end match`
- **声音引用**：`BLK-EP001-SC001-P02（SFX 雨点敲玻璃 + 关东煮咕嘟）`
- **注意**：字幕「雨夜 · 23:47」为后期叠层，不进视频提示词；参考图未生成，正式生产前需先产出关键帧并做像素检查

### 可复制通用提示词

> 3D cartoon animation, Pixar-style render: rounded cute character shapes, soft volumetric lighting, high-saturation warm colors, stylized soft shadows. A soaked orange cat with a round face, white chest and belly, large amber eyes and a fluffy tail curls on the doormat in front of a convenience-store glass door, lower-right of frame, wet fur plastered flat. Start: the cat is curled still, gaze low, tail hanging into a puddle. 0-1s: the cat stays curled while rain keeps pattering and oden steam fogs the glass. 1-2.5s: the cat slowly raises its head, amber eyes aiming through the glass at the steaming oden pot inside. 2.5-4s: the cat shuffles one paw-length forward and leans in, nose nearly touching the bottom edge of the glass, gaze locked on the steam. 4-5s: the cat holds the leaning pose, tail giving one slow sway in the puddle. Camera: locked wide shot, three-quarter angle from the storefront side, at cat-eye height about 40cm, no movement. Lighting: cold blue rainy night as the base tone, warm convenience-store light spilling through the glass door, steam glistening on the glass. Sound: rain pattering on glass and the oden pot bubbling throughout. Final frame: the soaked cat leaning toward the glass, gaze fixed on the steam. No readable text in the frame.

### 只读结束报告

- **位置/姿态**：前倾贴近玻璃门、重心在前爪 → 来源：`end_boundary`：匹配
- **目光/双手/持物**：望向店内热气；无手部/持物 → 来源：匹配
- **可见状态**：毛发湿透贴服、热气凝水珠 → 来源：匹配
- **下一镜**：仅比较 `SHOT-002/start_boundary`（店员货架前持货），未改写

---

## `SHOT-002` · 心疼被看见：店员停手侧头

- **运动规格**：`MOTION-002`
- **起始帧**：`KEY-002`
- **参考图用途**：`REF-002 / order 1 / start_frame` 只决定起始构图与可见状态；不得导入尚未发生的停手侧头；检查状态 `unverified`
- **时长（只读）**：`5s`
- **边界核对**：`end match`
- **声音引用**：`BLK-EP001-SC002-P01（SFX 门外短促猫叫）`
- **注意**：无

### 可复制通用提示词

> 3D cartoon animation, Pixar-style render: rounded cute character shapes, soft volumetric lighting, high-saturation warm colors. A young convenience-store clerk with a high ponytail and a warm-colored apron over a store uniform stands at the shelves on the left third of frame, both hands holding items mid-restock. Start: she faces the shelves, gaze down on the goods, relaxed stance. 0-1s: a short cat meow sounds from outside the door; her hands stop mid-motion. 1-2s: she turns her head about thirty degrees toward the glass door on the right. 2-3.5s: she looks through the glass at the cat on the doormat outside, brows loosening slightly. 3.5-5s: she holds the look, goods still in her hands, body still. Camera: locked medium shot, three-quarter angle from inside the store on the interior side of the axis, eye-level, no movement. Lighting: warm interior light filling the store, cold blue rainy night visible through the glass door on the right. Sound: one short cat meow at the start, muffled rain through the glass, oden pot bubbling in the left background. Final frame: the clerk standing still, gaze fixed on the cat outside. No readable text in the frame.

### 只读结束报告

- **位置/姿态**：站姿静止、仍在货架前 → 来源：匹配
- **目光/双手/持物**：望向门外猫；双手仍持商品 → 来源：匹配
- **可见状态**：店内暖光、门外冷蓝 → 来源：匹配
- **下一镜**：仅比较 `SHOT-003/start_boundary`（店员门边手搭门把），未改写

---

## `SHOT-003` · 犹豫成立：开门惊猫

- **运动规格**：`MOTION-003`
- **起始帧**：`KEY-003`
- **参考图用途**：`REF-003 / order 1 / start_frame` 只决定起始构图与可见状态；不得导入尚未发生的开门与猫后退；检查状态 `unverified`
- **时长（只读）**：`5s`
- **边界核对**：`end match`
- **声音引用**：门把转动与门开合一声轻响（环境层，SC003 无 SFX 标签）
- **注意**：无

### 可复制通用提示词

> 3D cartoon animation, Pixar-style render: rounded cute character shapes, soft volumetric lighting, high-saturation warm colors. A young convenience-store clerk with a high ponytail and a warm-colored apron stands at the glass door in the center of frame, leaning forward, right hand on the door handle. Outside on the doormat at the lower-right, a soaked orange cat with a round face, white chest and belly, amber eyes and a clamped fluffy tail crouches low. Start: the door is closed, the clerk watching the cat through the glass. 0-1s: she presses the handle down and the door opens a crack. 1-2s: the cat flinches, retreating two steps back into the rain, crouching into a tight ball. 2-3.5s: the clerk releases the handle at once; the door swings slowly shut while she keeps watching through the glass. 3.5-5s: the cat creeps back onto the doormat; the clerk's fingers loosen and tighten on the handle again, gaze staying on the cat. Camera: locked medium shot, near-frontal from inside the store, eye-level, no movement. Lighting: warm interior light from the left, cold blue rainy night through the glass with a sharp warm-cold boundary at the door edge. Sound: a soft door-handle click and door movement, rain briefly louder while the gap is open. Final frame: the cat back on the doormat, the clerk's hand frozen on the handle. No readable text in the frame.

### 只读结束报告

- **位置/姿态**：店员门内站姿前倾；猫回门垫 → 来源：匹配
- **目光/双手/持物**：隔玻璃看猫；右手在门把上松开又握紧 → 来源：匹配
- **可见状态**：门合拢、猫毛湿透 → 来源：匹配
- **下一镜**：仅比较 `SHOT-004/start_boundary`（店员蹲姿托空纸箱），未改写

---

## `SHOT-004` · 心软转折：纸箱小屋落位

- **运动规格**：`MOTION-004`
- **起始帧**：`KEY-004`
- **参考图用途**：`REF-004 / order 1 / start_frame` 只决定起始构图与可见状态；不得导入尚未发生的推箱垫报纸；检查状态 `unverified`
- **时长（只读）**：`5s`
- **边界核对**：`end match`
- **声音引用**：`BLK-EP001-SC004-P02（SFX 纸箱沿地面摩擦）`
- **注意**：字幕「先住一晚吧。」为后期叠层，不进视频提示词；干报纸文字 policy `graphic_only`，画面无需可辨文字

### 可复制通用提示词

> 3D cartoon animation, Pixar-style render: rounded cute character shapes, soft volumetric lighting, high-saturation warm colors. A young convenience-store clerk with a high ponytail and a warm-colored apron crouches inside the store door, center-right of frame, both hands holding an empty open-top corrugated cardboard box at chest height; a half sheet of dry newspaper lies on the counter at the left. Start: she crouches facing the closed glass door, gaze on the box. 0-1s: she pushes the door open a gap with her right hand, wide enough for the box. 1-2.5s: she slides the box flat through the gap onto the eave floor, its opening facing the store light; the box scrapes along the ground. 2.5-3.5s: she reaches for the dry newspaper, takes it from the counter, and pads it into the box bottom. 3.5-4.5s: she pats the box lightly, pulls back inside the store, and gently closes the door. 4.5-5s: she watches the little house through the glass, holding still. Camera: locked medium shot, three-quarter angle from inside the store, at crouch height about 70cm, no movement. Lighting: warm interior light filling the store, cold blue night glowing through the door gap. Sound: the dry scraping of cardboard on the ground, muffled rain outside. Final frame: the clerk standing inside, gazing at the cardboard house under the eave. No readable text in the frame.

### 只读结束报告

- **位置/姿态**：店员退回门内站姿；小屋在门外屋檐下 → 来源：匹配
- **目光/双手/持物**：隔玻璃看小屋；双手空 → 来源：匹配
- **可见状态**：小屋箱口朝店内灯光、干报纸垫底 → 来源：匹配
- **下一镜**：仅比较 `SHOT-005/start_boundary`（猫站门垫嗅闻），未改写

---

## `SHOT-005` · 信任突破：猫入住小屋

- **运动规格**：`MOTION-005`
- **起始帧**：`KEY-005`
- **参考图用途**：`REF-005 / order 1 / start_frame` 只决定起始构图与可见状态；不得导入尚未发生的试探钻入；检查状态 `unverified`
- **时长（只读）**：`5s`
- **边界核对**：`end match`
- **声音引用**：`BLK-EP001-SC005-P01（SFX 钻箱窸窣 + 低呼噜）`
- **注意**：无

### 可复制通用提示词

> 3D cartoon animation, Pixar-style render: rounded cute character shapes, soft volumetric lighting, high-saturation warm colors. A soaked orange cat with a round face, white chest and belly, amber eyes and a fluffy tail stands on the doormat at the lower-left, ears pricked up, one front paw slightly lifted; a corrugated cardboard box house sits under the eave at the lower-right, its opening facing warm store light. Start: the cat stands still, nose sniffing the air toward the box. 0-1s: the cat stays put, ears swiveling, sniffing. 1-2.5s: the cat circles the box sniffing its edge, reaches a front paw into the opening, and pulls it back. 2.5-4s: the cat slips inside the box and turns around, rustling the dry newspaper lining. 4-5s: the cat curls into a ball, fluffy tail over its nose, amber eyes closing to slits, a soft purr rising. Camera: locked medium shot, three-quarter angle from outside the store, at cat-eye height about 40cm, no movement. Lighting: cold blue rainy night base, warm light spilling from the box opening and the glass door, reflecting on the wet ground. Sound: rain easing to eave dripping, rustling of the box, then a low purr. Final frame: the cat curled inside the box, tail over its nose. No readable text in the frame.

### 只读结束报告

- **位置/姿态**：猫蜷在小屋箱内、尾巴盖鼻尖 → 来源：匹配
- **目光/双手/持物**：眯起琥珀色眼睛；无持物 → 来源：匹配
- **可见状态**：毛仍湿、箱口透暖光 → 来源：匹配
- **下一镜**：仅比较 `SHOT-006/start_boundary`（深夜猫在箱口探头、毛已蓬松），未改写

---

## `SHOT-006` · 温暖延续：深夜探头望灯光

- **运动规格**：`MOTION-006`
- **起始帧**：`KEY-006`
- **参考图用途**：`REF-006 / order 1 / start_frame` 只决定起始构图与可见状态；不得导入尚未发生的眯眼望灯；检查状态 `unverified`
- **时长（只读）**：`5s`
- **边界核对**：`end match`
- **声音引用**：`BLK-EP001-SC006-P02（SFX 雨声渐弱、屋檐滴水）`
- **注意**：毛已干燥（LOOK-CAT-BASE）为连续性兑现点，起点状态必须保持蓬松干燥

### 可复制通用提示词

> 3D cartoon animation, Pixar-style render: rounded cute character shapes, soft volumetric lighting, high-saturation warm colors. Deep night. A dry, fluffy orange cat with a round face, white chest and belly and big amber eyes pokes half its head out of a corrugated cardboard box house at the lower-right of frame, front paws resting on the box edge, body still inside, warm store light spilling from the box opening and outlining the cat in a soft warm rim light against cold blue night tones. Start: the cat holds the peeking pose, eyes toward the store light. 0-1s: the cat stays still, one ear swiveling. 1-3s: the cat slowly squints its amber eyes into slits, gazing at the warm light inside the store through the glass door. 3-4.5s: the cat holds the gaze while its tail sways gently inside the box. 4.5-5s: the cat holds the pose as eave dripping slows. Camera: locked medium shot, near-frontal from outside the store, at cat-eye height about 40cm, no movement. Lighting: cold blue deep-night tones, warm light from the box opening and the store as the only warm sources. Sound: rain fading to slow eave drips, quiet night. Final frame: the fluffy cat peeking from the box, eyes squinting at the warm light. No readable text in the frame.

### 只读结束报告

- **位置/姿态**：探头姿态、前爪搭箱口 → 来源：匹配
- **目光/双手/持物**：望向店内灯光；无持物 → 来源：匹配
- **可见状态**：毛蓬松干燥、箱口透暖光 → 来源：匹配
- **下一镜**：仅比较 `SHOT-007/start_boundary`（清晨猫叼鱼干在小屋门口），未改写

---

## `SHOT-007` · 惊喜：清晨鱼干谢礼

- **运动规格**：`MOTION-007`
- **起始帧**：`KEY-007`
- **参考图用途**：`REF-007 / order 1 / start_frame` 只决定起始构图与可见状态；不得导入尚未发生的放鱼干与跑开；检查状态 `unverified`
- **时长（只读）**：`5s`
- **边界核对**：`end match`
- **声音引用**：`BLK-EP001-SC007-P01（转场：雨声隐去、鸟鸣接上）`
- **注意**：字幕「谢谢你。」为后期叠层，不进视频提示词；冷暖切换（冷蓝→暖阳）在本镜开头完成

### 可复制通用提示词

> 3D cartoon animation, Pixar-style render: rounded cute character shapes, soft volumetric lighting, high-saturation warm colors. Early morning. A dry, fluffy orange cat with a round face, white chest and belly and big amber eyes stands at the entrance of a cardboard box house at the lower-right, holding a small curved dried fish in its mouth, head lowered toward the doormat; morning sunlight streams from the upper-left, dew glistening on the box edges. Start: the cat stands still, gaze on the center of the doormat. 0-1s: the cat holds still, fixing the landing spot. 1-2.5s: the cat places the dried fish neatly at the center of the doormat and draws its mouth back. 2.5-3.5s: the cat looks up toward the store interior through the glass door. 3.5-5s: the cat turns and runs off, stops at the street corner on the left, and looks back over its shoulder toward the store. Camera: locked medium shot, three-quarter angle from outside the store, at cat-eye height about 40cm, no movement. Lighting: warm morning sunlight from the upper-left, lighting the eave, the doormat and the dew. Sound: rain fading out, morning birdsong taking over, light cat footsteps near the end. Final frame: the cat looking back from the corner, the dried fish sitting centered on the doormat. No readable text in the frame.

### 只读结束报告

- **位置/姿态**：猫在街角四足站定回头 → 来源：匹配
- **目光/双手/持物**：回望玻璃门方向；鱼干已放下 → 来源：匹配
- **可见状态**：小鱼干端放门垫正中、阳光铺满门口 → 来源：匹配
- **下一镜**：仅比较 `SHOT-008/start_boundary`（店员门内推门、猫街角回望），未改写

---

## `SHOT-008` · 治愈落点：店员推门见谢礼

- **运动规格**：`MOTION-008`
- **起始帧**：`KEY-008`
- **参考图用途**：`REF-008 / order 1 / start_frame` 只决定起始构图与可见状态；不得导入尚未发生的推门拾鱼干；检查状态 `unverified`
- **时长（只读）**：`5s`
- **边界核对**：`end match`
- **声音引用**：`BLK-EP001-SC008-P02（SFX 门铃轻响 + 明亮猫叫）`
- **注意**：字幕「早安。」为后期叠层，不进视频提示词；末镜，下一集尚未建立，交接以 `next_start_locator（EP002 provisional）` 为准

### 可复制通用提示词

> 3D cartoon animation, Pixar-style render: rounded cute character shapes, soft volumetric lighting, high-saturation warm colors. Early morning. A young convenience-store clerk with a high ponytail and a warm-colored apron pushes the glass door open from inside, appearing in the door frame on the right; a few steps away at the left, an orange cat with a round face, white chest and belly and a fluffy tail stands at the street corner, looking back over its shoulder; the cardboard box house sits under the eave at the lower-right with dew on its edges. Start: the clerk leans forward pushing the door, gaze down at the ground. 0-1s: the door opens, a bell chimes, and morning light floods out through the opening. 1-2.5s: she steps out, looks down, sees the dried fish centered on the doormat, and freezes for a moment. 2.5-3.5s: she crouches, picks up the fish, and stands back up, the fish now in her right hand. 3.5-5s: she looks up at the cat at the corner, smiles, and gives the fish a gentle little wave toward the cat; sunlight fills the little house and her face. Camera: locked medium shot, frontal from outside the store facing the door, eye-level, no movement. Lighting: warm morning sunlight from the upper-left mixing with warm interior light at the door edge. Sound: a soft doorbell chime at the start, then one short bright cat call near the end, morning birdsong around. Final frame: the smiling clerk holding up the dried fish, the cat watching from the corner, sunlight on the little house. No readable text in the frame.

### 只读结束报告

- **位置/姿态**：店员门外门垫前站姿、面朝猫方向 → 来源：匹配
- **目光/双手/持物**：看向街角的猫；右手拿小鱼干 → 来源：匹配
- **可见状态**：阳光照小屋与店员脸上、猫在街角回望 → 来源：匹配
- **下一镜**：`EP002` 尚未建立（`next_start_locator provisional`），未改写
