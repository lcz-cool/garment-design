# garment-design

WorkBuddy 技能：把一句口头的服装设计需求，变成一套可交付的设计方案 —— 上身效果图、款式平面图、设计稿页面。

男女装通用，支持**单件**、**整套 look**、**系列**三种形态。

## 它做什么

输入一句描述（品类 + 款式特征 + 适用季节），输出三件互相咬合的东西：

| 文件 | 内容 | 可信度定位 |
|---|---|---|
| `lookbook.png` | 模特上身效果图 | 气质参考，细节可能漂移 |
| `technical-flat.png` | 款式平面图（沟通用款式图） | 结构沟通，**不是可直接放码打版的 CAD** |
| `design-spec.html` | 设计稿页面 | 唯一权威：尺寸、克重、色号以文档为准 |

三者不是等权证据，技能内定义了「权威顺序」处理冲突。

## 结构

```
SKILL.md                          主流程，7 步 + 前置检查
references/
├── garment-vocabulary.md         通用术语（廓形/领型/袖型/工艺/面料）
├── menswear.md                   男装结构与版型体系
├── menswear-register.md          男装高级感语域（静奢/老钱/Clean Fit，互斥三选一）
├── season-fabric.md              季节 × 克重 × 面料 × 结构
├── series-mode.md                系列模式
├── techpack.md                   交付深度：展示版 / 生产版（Tech Pack 字段要求）
├── design-doc-structure.md       设计稿章节写什么、写到什么深度
├── image-prompt-recipes.md       效果图与平面图的提示词配方
└── calibration-log.md            实测记录：失败案例、根因、修正
assets/
├── design-spec-template.html     单款设计稿版式
├── series-spec-template.html     系列页版式
└── flat-skeleton.svg             打版用 A3 分层工作稿
scripts/
├── check_spec.py                 设计稿自检（结构/色号/克重/尺寸/图片）
└── package.ps1                   打包与安装
```

## 安装

```bash
git clone <this-repo> ~/.workbuddy/skills/garment-design
```

Windows 默认位置：`C:\Users\<你>\.workbuddy\skills\garment-design`

## 依赖

- **图像生成能力**（文生图；有图生图更好，用于换脸与一致性约束）
- **Python 3.10+**（可选，仅自检脚本需要）
- **Pillow**（可选，装了才会检查画幅与平面图白底四角像素）

缺图像能力时会自动降级：只交付文字方案 + 结构描述 + 设计稿，并给一份可直接复用的英文提示词。

## 自检

```bash
python scripts/check_spec.py <设计目录>
```

查占位符残留、章节完整性、款号格式、性别归属、语域是否混用、色号与 Pantone、克重与季节是否自洽、尺寸加和、放码档差、图片画幅与白底。退出码非 0 表示有必须修的问题。

生产版加 `--production`，另查 BOM 九类、缝制四要素（缝型 / SPI / 缝份 / 熨烫）、± 允差与测量方法、Colorway 套数、封面系列与设计师，以及**图形缺口声明**。

```bash
python scripts/check_spec.py <设计目录> --production
```

## 设计取舍

- **平面图只做沟通用**，不做自动描摹。曲线描得再像，对版师也没用，还会让人误以为可以打版了。要打版走 `flat-skeleton.svg` 手工路径。
- **提示词里否定比肯定有力**。`not a gown` 比 `lightweight` 更能约束结果；这条是从失败案例里得出的。
- **穿法动词几乎不生效**。写 `untucked` 会被塞进裤腰，得写成可见部件 `hem below the belt line`。
- **语域不许混用**。静奢要挺括、老钱要软糯、Clean Fit 要刚刚好，同一件不可能全要。

更多实证见 `references/calibration-log.md`。

## 维护

这个技能有三份副本，改的时候容易漏：

| 位置 | 作用 |
|---|---|
| 仓库根（本目录） | 源文件，改动都在这里做 |
| `~/.workbuddy/skills/garment-design/` | 实际生效的安装副本 |
| `dist/garment-design.zip` | 分发包 |

**正确顺序：改源 → `git commit` → `git push` → `scripts/package.ps1 -Install`**

`-Install` 只同步安装副本，不管 git；`git push` 也不管安装副本。只做一边，就会出现「代码推上去了，但本地技能还是旧的」。

```powershell
# Windows 上执行策略可能拦截，加进程级 Bypass
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\scripts\package.ps1 -Install -KeepBackups 1
```

备份落在 `~/.workbuddy/skill-backups/garment-design/`，**刻意放在 skills 目录之外** —— 放进去会被技能扫描器当成另一个同名技能，装几次列表里就多几个。`-KeepBackups N` 控制保留份数，默认 3。

## 许可证

MIT · 见 [LICENSE](LICENSE)

## 版本

v1.6.0 · 2026-11-01

