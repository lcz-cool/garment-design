# 图片提示词配方

两类图的目标完全不同，提示词结构也必须不同。**用英文写提示词**，结构描述按「上衣到裙摆」或「正面到背面」的物理顺序，AI 对顺序敏感。

---

## 一、效果图 Lookbook

### 目标
一张时装编辑风的全身照：能看出廓形比例、面料垂坠、颜色气质。不是商品白底图，也不是秀场抓拍。

### 结构公式

```
[① 镜头与体裁] + [② 服装全描述] + [③ 模特与姿态] + [④ 背景] + [⑤ 光线] + [⑥ 质感与否定]
```

**① 镜头与体裁**
`Full-body editorial fashion photograph` / `Lookbook photograph, full figure in frame`

画幅必须写死：`vertical 2:3 portrait format`。不写就每次比例不同，版面跟着抖，系列之间也不好排。

**② 服装全描述** —— 逐项，缺一项 AI 就自由发挥
品类 → 廓形 → 领型 → 袖型 → 长度（具体到身体位置）→ 门襟 → 细节 → 面料质感 → 颜色

长度必须落到身体位置：`mid-calf`、`just above the knee`、`hitting at the hip bone`、`floor-length`。
不要写 `long` —— AI 会理解成拖地。

**穿法要配视觉事实**（三次实测全部失效：`untucked` 仍被塞进裤子、`flat front` 仍出前褶、`worn open` 仍拉上拉链）。
所有「穿法动词」（tucked / untucked / worn open / rolled cuffs）都必须补一句**可验证的画面**：

- 不塞下摆 → `shirt hem hanging below the belt line, belt not visible`
- 敞开穿 → `jacket unzipped, zip pull resting at the bottom, ribbed hem band visible below, inner layer visible down the chest`
- 卷袖 → `sleeve cuffs rolled twice, forearm visible`

规律：**状态词（open / tucked）几乎不生效，可见部件（unzipped、zip pull、hem band）才生效**。写「敞开」不如写「拉链头停在最下方、下摆罗纹露在外面」。

**长度要双锚定**（实测过：只写一次 `mid-calf` 会失效，图会滑到及踝）：
正向写落点 + 反向排除，如 `hem ending at mid-calf, well above the ankle, not floor-length`。
衣长描述尽量配合「露出小腿」这类可验证的视觉事实：`calf visible below the hem`。

**③ 模特与姿态** —— 按性别取模板，不要把 woman 写死在男装任务里

- **女装**：`a woman with a low bun, standing in a three-quarter turn, weight on the back leg, one hand relaxed at her side`
- **男装**：`a man with short hair and clean grooming, standing with shoulders square, hands relaxed at his sides`
- **中性 / unisex**：`an androgynous model, minimal styling, upright neutral stance`

通用规则：

- 姿态优先 `three-quarter turn` / `walking` / `back view with head turned`
- 面部越正面越容易崩，侧身能规避大部分问题
- 不要描述具体长相（年龄与体态之外，细节会抢戏）
- **男装额外要求**（见下文「男装拍摄要点」）

### 男装拍摄要点

男装的判断依据是版型与比例，不是情绪。三点必须在提示词里落实：

1. **全身带鞋** —— 男装看的是「裤长 + 鞋」的整体比例。必须写 `full body including shoes, shoes visible in frame`。鞋被裁掉，裤长就废了。
2. **肩线必须清晰** —— 肩是男装廓形的起点。写 `shoulders square, shoulder seam clearly visible, upright posture`，姿态避免驼背、侧身过度、手臂抬举遮挡肩部。
3. **裤装完整入镜** —— 写 `trousers fully visible from waist to hem, trouser hem and shoe interaction visible`。裤口翻边与否、堆积量多少，全在这一段里。

补充：

- 男装姿态更克制：站直、手自然下垂或单手握拳、一手插袋。**不要走动摆臂** —— 会遮住廓形。
- 镜头可以稍远，`full figure with generous headroom and floor visible`，留出鞋与地面。
- 若服装描述本身有中性歧义（如「衬衫」），在提示词开头加 `menswear, men's garment` 明确否定女装倾向，否则容易画成女装衬衫。

**④ 背景 —— 按风格取预设，别每次现编**

背景是 lookbook 的编排底色。同一个系列里换背景，等于把一组图变成一堆积图。按下表选一个，然后**同一系列全部沿用**：

| 风格锚点 | 背景预设 |
|---|---|
| 静奢 / 90 年代极简 / 意式西装 | `seamless warm-grey studio backdrop, paper floor seam` |
| 法式复古 / 芭蕾风 / 新中式 | `sunlit plaster wall, soft window shadow, pale linen curtain edge` |
| 常春藤 / Clean Fit / 老钱风 | `quiet stone courtyard wall, even overcast light` |
| 阿美咔叽 / 日系工装 / Gorpcore | `weathered concrete street surface, muted daylight` |
| City Boy / Y2K / Blokecore | `muted city pavement, shallow depth of field, no signage` |

**不要写具体地名、招牌、人群** —— 会带出文字水印与路人。

**⑤ 光线**
`large softbox from camera left with gentle fill, subtle floor shadow` / `soft directional window light, warm`

**⑥ 质感与否定**
`85mm lens, f/2.8, eye level, full figure with headroom` + `quiet luxury, subtle film grain` + `no text, no logo, no watermark`

### 完整示例（可直接改写）

> Full-body editorial fashion photograph of a woman wearing a long A-line dress in ivory silk crepe de chine: square neckline, voluminous puffed elbow-length sleeves gathered at the shoulder, fitted waist seam, full gathered skirt falling to mid-calf, hidden back zip. A woman with a low bun stands in a three-quarter turn, weight on the back leg, one hand relaxed at her side. Seamless warm-grey studio backdrop, large softbox from camera left with gentle fill, subtle floor shadow. 85mm lens at f/2.8, eye level, full figure in frame with headroom, quiet luxury, subtle film grain, no text, no logo.

### 男装示例（早秋 · 牛津纺纽扣领衬衫）

> Full-body lookbook photograph of menswear: a man wearing a light-blue oxford button-down shirt, regular fit, button-down collar, single chest pocket, barrel cuffs, worn untucked over stone chinos with flat front and plain hem, white leather sneakers. A man with short hair and clean grooming stands with shoulders square, hands relaxed at his sides, torso angled slightly to camera-left. Seamless warm-grey studio backdrop, large softbox from camera left with gentle fill, subtle floor shadow. 85mm lens at f/2.8, eye level, full figure including shoes with floor visible, crisp cotton texture with visible oxford weave, natural film grain, no text, no logo.

与女装示例有三处关键差别：开头用 `menswear` 定调、姿态换成 `shoulders square`、结尾强制 `including shoes with floor visible`。

### 常见失败与对策

| 现象 | 原因 | 对策 |
|---|---|---|
| 面料像廉价化纤／塑料 | 只写了颜色没写材质 | 补具体面料名 + hand-feel 词（matte, fluid, crisp, slubby） |
| 裙长/衣长不对 | 用了 long / short 这类模糊词 | 改成身体锚点：mid-calf、above knee |
| 廓形塌掉，看不出 A 型 | 模特姿态遮挡或面料描述矛盾 | 换站姿、补 `structured, holds shape` |
| 手指/脸崩 | 全身正脸特写 | 改侧身、背身、或手插袋 |
| 冒出水印或文字 | 未否定 | 结尾固定加 `no text, no logo, no watermark` |
| 颜色偏离色板 | 只给色名没给参照 | 用具体色名（ivory、oatmeal、sage）+ 必要时加 hex 描述 |
| 男装被画成女装 | 品类中性（衬衫 / 大衣 / 卫衣）+ 未标注性别 | 提示词开头加 `menswear, men's garment`，并把模特换成 `a man` |
| 男装裤长看不出 | 全身图裁掉了鞋 | 加 `full figure including shoes with floor visible` |
| 男装肩部塌、看不出廓形 | 模特驼背或手臂遮挡 | 改 `shoulders square, upright posture, arms not raised` |

---

## 二、款式平面图 Technical Flat

### 目标

一张看得懂结构的**沟通用款式图**：正背面对应、白底、无人体、结构线和工艺位置清晰。

**它不是什么**：不是能直接打版放码的 CAD。位图线稿没有尺寸标注、不能量取、不能放码，左右对称性还要靠提示词和核对勉强守住。给工厂的尺寸依据永远是设计稿 06 节。要真打版，得另行出矢量图。

**画幅**：`horizontal 3:2 landscape format`，与效果图的竖构图互补。

### 硬禁忌：不能出现颜色词

平面图提示词里**一个颜色词都不能有**。写 `burgundy jacket` 就会得到深色填充图，线稿压在深底上几乎看不清；写 `white shirt` 会得到白色填充，看起来像没画完。

颜色只属于效果图和设计稿的色板。平面图只描述结构，靠 `black line art, no color fill` 兜底。

### 结构公式

```
[① 体裁断言] + [② 视图与布局] + [③ 服装结构复述] + [④ 绘制风格] + [⑤ 否定清单]
```

**① 体裁断言**（必须放最前，权重最高）
`Technical flat fashion CAD drawing` / `Technical fashion illustration, flat sketch`

**② 视图与布局**
`front view and back view side by side, garment alone, flat lay, centered, generous white margin`

**③ 服装结构复述** —— 与效果图逐项一致
`square neckline, puffed elbow-length sleeves, fitted waist seam, gathered A-line skirt to mid-calf, concealed back zip`

**④ 绘制风格**
`pure white background, uniform black line weight, visible seam lines and topstitching, construction details drawn precisely, symmetrical`

**⑤ 否定清单**（这一步决定成败）
`no body, no mannequin, no model, no shading, no gradient, no fabric texture, no cast shadow, no background elements, no text labels`

### 完整示例

> Technical flat fashion CAD drawing of a long A-line dress: square neckline, puffed elbow-length sleeves gathered at the shoulder, fitted waist seam, full gathered skirt falling to mid-calf, concealed back zip. Front view and back view side by side, garment alone with no body and no mannequin, flat lay, centered with generous white margin. Pure white background, uniform black line weight, visible seam lines and topstitching, construction details drawn precisely, symmetrical. No shading, no gradient, no fabric texture, no cast shadow, no background elements, no text labels.

### 常见失败与对策

| 现象 | 原因 | 对策 |
|---|---|---|
| 画成了效果图／有人穿着 | 否定词不足 | 把 `no body, no mannequin` 提到靠前位置 |
| 出现灰底或渐变 | 默认渲染习惯 | 加 `pure white background, no gradient, no shading` |
| 只有正面，缺背面 | 未强调视图 | 明确 `front view AND back view side by side` |
| 加了一堆不存在的口袋/褶皱 | 结构复述不全，AI 脑补 | 复述里补 `no pockets, no extra details` |
| 线太细看不清 | 未指定线宽 | 加 `uniform bold line weight, clear outlines` |
| 加了色块但不是线稿 | 混入色彩描述 | 删除颜色词，只留结构；需要彩色 flat 时单独指定 `flat color fill, no shading` |
| 整张被深色填充、线稿看不清 | 提示词里写了服装颜色（如 `burgundy jacket`） | 删掉所有颜色词，加 `black line art, no color fill` |
| 袖口或下摆末端出现尖角畸形 | 罗纹收口被误读成锥形 | 加 `clean straight sleeve openings, no pointed or tapered ends` |

### 下装平面图补充

裤装与半裙的 flat 与上装不同，结构线集中在腰头以下：

- 视图：正面 + 背面，必要时加侧视（裤装侧缝和裤口形状在侧视最清楚）
- 必须画出的线：腰头、门襟（拉链或纽扣）、前褶（无褶 / 单褶 / 双褶要画出褶量）、侧缝、后袋、裤口（翻边与否）
- 提示词追加：`trousers technical flat, front view and back view, waistband, fly, front pleat, rear welt pockets, hem detail clearly drawn`

---

## 三、两张图的一致性校验

**平面图的提示词必须从已生成的效果图反推，而不是重新描述最初的需求。** 这一步不能省 —— 效果图一旦出图就是既成事实，平面图的任务是复现它，不是复现你想画的。

实测教训：省掉反推、凭最初描述重写一遍，会得到一件「看起来像、处处不同」的衣服 —— 领片小一号、袋盖从斜变平、落肩变成高袖山装袖、罗纹宽度翻倍。

### 核对清单（12 项，逐项过）

| # | 项 | 常见偏移 |
|---|---|---|
| 1 | 领型大类 | 翻领 / 立领 / 驳领 |
| 2 | 领片大小与领角角度 | 大尖角 vs 小圆角 |
| 3 | 领口开度 | 闭合到领座 vs 敞开成 V |
| 4 | 肩型与袖山 | 正肩装袖 / 落肩低袖山 |
| 5 | 袖身宽窄与袖口处理 | 窄顺垂 vs 宽收锥 |
| 6 | 门襟位置、扣数、拉链长度 | |
| 7 | 口袋有无、位置、袋形 | 贴袋 / 带盖 / 斜置 / 水平 |
| 8 | 腰线高度与分割位置 | |
| 9 | 衣长落点 | |
| 10 | 下摆形态与罗纹宽度 | 窄罗纹 vs 宽罗纹 |
| 11 | 整体宽高比 | 横宽短款 vs 接近正方 |
| 12 | 左右对称性与多余细节 | 单侧多出拉链、笔插、线迹 |

前五项最容易漏 —— 「口袋有无」查了，「袋盖角度」没查；「领型形状」查了，「领片大小和开度」没查。

### 左右必须严丝合缝

平面图是给版师用的，同一高度的两个对称部件必须完全一致。AI 有个稳定的坏习惯：**在单侧加笔**，比如左边胸袋多一条竖向下垂的拉链、右边袖口多一道线迹。肉眼扫一眼不会发现，但它直接让平面图失去可用性 —— 版师会以为你要做不对称设计。

提示词写法：

`exactly two matching chest pockets, identical in size and position, perfectly symmetrical about the center line, no vertical zip or pen slot inside the pockets`

核对时**把左右单独比一遍**，不要只确认「有没有口袋」。

### 不一致怎么办

重生成平面图，不要改效果图。把每处差异写进平面图提示词，用**可量化的相对描述**：

- 领口 → `deep open neckline with spread collar points`
- 袋盖 → `flaps angled diagonally, outer corners higher than inner corners`
- 肩袖 → `dropped shoulder with low armhole, wide slightly tapered sleeve`
- 比例 → `body width close to its body length`
- 罗纹 → `narrow ribbed hem band`

---

## 四、整套 look

### 结构公式

```
[① 体裁] + [② 外层（最完整）] + [③ 内层·只写露出部分] + [④ 下装] + [⑤ 鞋] + [⑥ 配饰] + [⑦ 模特] + [⑧ 场景光线] + [⑨ 否定]
```

与单件的差别只有一条：**按穿着层次从外到内写**，不按从上到下写。

### 内层只写露出的部分

这是整套最容易翻车的地方。完整描述内搭，AI 会把它画到外套外面，或者让外套直接消失。

- 错：`a black turtleneck with ribbed collar and fitted body, merino wool`（内层描述过满）
- 对：`underneath, a black turtleneck, only the ribbed collar visible at the neck`

内层的完整信息放到设计稿的构成表里，不要塞进提示词。

### 常见陷阱

| 现象 | 原因 | 对策 |
|---|---|---|
| 内搭跑到外套外 | 内层描述太长、太完整 | 只写露出的领口 / 袖口 / 下摆 |
| 外套结构被简化 | 外层被后续层级稀释 | 外层放最前，且描述最全 |
| 配饰消失（挂腰的手套、腰带） | 配饰权重最低 | 给位置锚点：`tucked into the waistband at the right hip` |
| 叠穿后比例失真、显矮 | 层数多，AI 压缩身高 | 加 `full figure including shoes with floor visible`，并明确鞋跟高度 |
| 整套糊成一团 | 想同时强调每一件 | 只突出主体单品，其余按层级简写 |

### 主体单品要单独出平面图

效果图是整套，平面图只画主体（夹克 / 外套 / 西装）。别试图给整套画 CAD —— 出来是一团线，版师也用不了。

---

## 五、实测校准记录

三组案例的完整实测、根因与修正过程已移到 `references/calibration-log.md`。本文件只留可执行规则 —— 配方越长越难执行。

**已知不可控项（每次交付都要跟用户交代）：**

- 生成结果图**右下角带平台水印**（AI生成 / WORKBUDDY），由生成服务强制添加，提示词里的 `no watermark` 无法去除。排版预留该区域，或交付时说明。
- 平面图底色**可能不是纯白**（实测偶发 245 左右的浅灰）。出图后看四角像素，明显偏灰就重出，提示词加 `pure white #FFFFFF background, no off-white, no paper texture`；仍不行就在交付说明里写清，不要硬塞进白框装作干净。
- 面部细节在全身图中仍偶有轻微失真，侧身三分之四角度下基本可接受。
