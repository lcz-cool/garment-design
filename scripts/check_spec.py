#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""设计稿交付前自检。

用法：
    python scripts/check_spec.py <设计目录>

检查项（FAIL 会让退出码为 1，WARN 只提示）：
    1  三件交付物是否齐全
    2  HTML 里是否残留 {{占位符}}
    3  章节、款号、性别归属、设计假设是否在
    4  色板 HEX 格式与 Pantone 近似号
    5  克重是否落在季节区间
    6  成衣尺寸与「净X + 松量」是否加得上
    7  档差说明、季节适配的套话
    8  图片画幅（竖 2:3 / 横 3:2）与平面图白底

目录里有 series-spec.html 时按系列查：款表 ≥3 行、款号连号、每款的
looks / flats / specs 是否齐、网格图片是否存在、混男女装时两套基准是否齐。

有 variants/<v2-变量>/ 时按变体查：三件是否齐、是否真的只改了一个变量、
文档里有没有提到那个变量、版本号是否递增。

系列变体（series 目录下的 variants/）只允许换共享板：色板或面料板变、款表不变；
少画 flats 算复用主系列。另外所有文档都会查「性别归属 ↔ 基准号型」是否自洽。

只依赖标准库；装了 Pillow 才做第 8 项的像素检查。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:  # 可选依赖
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None

FAIL: list[str] = []
WARN: list[str] = []
OK: list[str] = []

SEASON_RANGE = {
    "SS": (60, 180),
    "PF": (180, 280),
    "AW": (280, 600),
}

CLICHE = ["清爽舒适", "简约大方", "适合春夏穿着", "适合秋冬穿着", "高级感"]


def fail(msg: str) -> None:
    FAIL.append(msg)


def warn(msg: str) -> None:
    WARN.append(msg)


def ok(msg: str) -> None:
    OK.append(msg)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def strip_comments(html: str) -> str:
    return re.sub(r"<!--.*?-->", "", html, flags=re.S)


def check_files(root: Path) -> str | None:
    missing = [n for n in ("lookbook.png", "technical-flat.png", "design-spec.html")
               if not (root / n).is_file()]
    if missing:
        fail(f"缺文件：{', '.join(missing)}")
        return None
    ok("三件交付物齐全")
    return read_text(root / "design-spec.html")


def check_placeholders(html: str) -> None:
    body = strip_comments(html)
    left = sorted(set(re.findall(r"\{\{[^}]{1,40}\}\}", body)))
    if left:
        fail(f"占位符未替换（{len(left)} 处）：{', '.join(left[:8])}"
             + (" …" if len(left) > 8 else ""))
    else:
        ok("无占位符残留")


def check_structure(html: str) -> None:
    body = strip_comments(html)
    sections = len(re.findall(r'<div class="rail">', body))
    if sections < 8:
        warn(f"章节数只有 {sections}，模板是 10 节，确认删减是故意的")
    else:
        ok(f"章节数 {sections}")

    if not re.search(r"[A-Z]{2}\d{2}-[A-Z]{2}-\d{3}", body):
        warn("没找到形如 SS26-DR-001 的款号")
    else:
        ok("款号格式正确")

    if "性别归属" not in body:
        fail("第 10 节缺「性别归属」—— 它是全篇最基础的假设")
    else:
        ok("设计假设含性别归属")

    if "设计假设" not in body:
        fail("缺「设计假设」区块，用户不知道哪些是你替他决定的")

    check_gender_base(html, "")
    check_register(html)


REGISTERS = {
    "静奢": r"静奢|[Qq]uiet\s*[Ll]uxury",
    "老钱": r"老钱|[Oo]ld\s*[Mm]oney",
    "Clean Fit": r"[Cc]lean\s*-?\s*[Ff]it",
}


def check_register(html: str) -> None:
    """男装必须选一个语域，且只能选一个 —— 静奢 / 老钱 / Clean Fit 互斥。

    词库依据：references/menswear-register.md（08 三套语域配方对照）。
    静奢要挺括、老钱要软糯、Clean Fit 要刚刚好的整洁，同一件衣服不可能全要。
    """
    body = strip_comments(html)
    if not (("性别归属：男装" in body) or ("男装 ·" in body)):
        return
    plain = re.sub(r"<[^>]+>", "", body)
    # 工装 / 机能 / 街头 / 先锋不属于这三套语域，01–07 的数值门槛照用，08 的三分法不适用
    outside = re.search(r"语域[：:]\s*(工装|机能|街头|先锋|运动|不属)", plain)
    if outside:
        ok(f"语域：{outside.group(1)}（非三分法语域，跳过互斥检查）")
        return
    found = [name for name, pat in REGISTERS.items() if re.search(pat, plain)]
    if not found:
        warn("男装设计稿没写语域：静奢 / 老钱 / Clean Fit 必须三选一，写进第 01 节")
    elif len(found) == 1:
        ok(f"语域单一：{found[0]}")
    else:
        warn("同时出现 " + " / ".join(found)
             + " —— 三者互斥，混用会互相抵消；确认是否真的叠在同一件上")


def check_colorway(html: str) -> None:
    body = strip_comments(html)
    chips = re.findall(r'class="chip"[^>]*style="background:\s*(#[^";]+)', body)
    if not chips:
        warn("没解析到色板 chip，跳过色号检查")
        return
    bad = [c for c in chips if not re.fullmatch(r"#[0-9A-Fa-f]{6}", c.strip())]
    if bad:
        fail(f"HEX 不是 6 位：{', '.join(bad)}")
    else:
        ok(f"色板 {len(chips)} 个，HEX 均为 6 位")

    pantone = re.findall(r"[Pp]antone\s*[0-9]{2}-[0-9]{4}|\d{2}-\d{4}\s*TCX|待色卡确认", body)
    if not pantone:
        fail("色板没有 Pantone 近似号：供应商照 HEX 打不出色")
    elif len(pantone) < len(chips):
        warn(f"色板 {len(chips)} 个，Pantone 只找到 {len(pantone)} 个，逐个补齐或写明「待色卡确认」")
    else:
        ok("Pantone 近似号齐全")

    if "打色" not in body:
        warn("缺「Pantone 为视觉近似，打色以实物色卡为准」的说明")


def detect_season(html: str) -> str | None:
    if re.search(r"\bSS\s?\d{2}\b|春夏", html):
        return "SS"
    if re.search(r"\bPF\s?\d{2}\b|早秋", html):
        return "PF"
    if re.search(r"\bAW\s?\d{2}\b|秋冬", html):
        return "AW"
    return None


def check_weight(html: str) -> None:
    season = detect_season(html)
    if not season:
        warn("没识别出季节，跳过克重区间检查")
        return
    lo, hi = SEASON_RANGE[season]
    weights = [float(w) for w in re.findall(r"(\d{2,3}(?:\.\d+)?)\s*(?:g/m²|g/m2|gsm|克)", html)]
    if not weights:
        warn("没找到克重数值，第 04 节应该给 g/m²")
        return
    out = [w for w in weights if not (lo * 0.75 <= w <= hi * 1.25)]
    if out:
        warn(f"{season} 主力区间 {lo}–{hi} g/m²，以下偏离较远（含 ±25% 容差）：{sorted(set(out))}"
             "—— 先看品类再判定，参考 season-fabric.md 的品类浮动表")
    else:
        ok(f"克重 {sorted(set(weights))} 落在 {season} 区间")


def check_measurement(html: str) -> None:
    body = strip_comments(html)
    rows = re.findall(r"<tr>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*</tr>",
                      body, flags=re.S)
    checked = 0
    for part, size_cell, note_cell in rows:
        note = re.sub(r"<[^>]+>", "", note_cell)
        m = re.search(r"净\s*\S{0,4}?\s*(\d+(?:\.\d+)?)\s*\+\s*(\d+(?:\.\d+)?)", note)
        if not m:
            continue
        nums = re.findall(r"(\d+(?:\.\d+)?)", re.sub(r"<[^>]+>", "", size_cell))
        if not nums:
            continue
        net, ease = float(m.group(1)), float(m.group(2))
        size = float(nums[0])
        checked += 1
        if abs(size - (net + ease)) > 1.0:
            fail(f"{re.sub(r'<[^>]+>', '', part)}：成衣 {size} ≠ 净 {net} + 松量 {ease} = {net + ease}")
    if checked and not any("成衣" in f for f in FAIL):
        ok(f"尺寸加和自洽（核对 {checked} 行）")
    elif not checked:
        warn("没有「净X + 松量」写法的行，无法自动核对尺寸加和")

    if "档差" not in body:
        warn("第 06 节没提放码档差，工厂出不了全码")


def check_cliche(html: str) -> None:
    hit = [c for c in CLICHE if c in html]
    if hit:
        warn(f"出现空话/套话：{', '.join(hit)}，改成可验证的事实")


def check_image_file(path: Path, want: str, label: str) -> None:
    """want: portrait（2:3）/ landscape（3:2）"""
    if Image is None:
        return
    try:
        with Image.open(path) as im:
            w, h = im.size
            rgb = im.convert("RGB")
    except Exception as exc:  # pragma: no cover
        warn(f"{label} 打不开：{exc}")
        return
    ratio = w / h
    target = 1.5 if want == "landscape" else 2 / 3
    if want == "portrait" and ratio >= 1:
        warn(f"{label} 是 {w}×{h}，效果图应为竖构图 2:3")
    if want == "landscape" and ratio <= 1:
        warn(f"{label} 是 {w}×{h}，平面图应为横构图 3:2")
    if abs(ratio - target) > 0.06:
        warn(f"{label} 比例 {ratio:.2f}，应为 {target:.2f}（3:2 / 2:3），排版会留白不均")
    if want == "landscape":
        corners = [rgb.getpixel(p) for p in ((2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3))]
        darkest = min(min(px) for px in corners)
        if darkest < 248:
            warn(f"{label} 底色偏灰（最暗角 {darkest}），放进白框会是一块灰面板：重出或说明")
        else:
            ok(f"{label} 白底合格（最暗角 {darkest}）")
    else:
        ok(f"{label} {w}×{h}")


def check_images(root: Path) -> None:
    if Image is None:
        warn("没装 Pillow，跳过画幅与白底检查")
        return
    check_image_file(root / "lookbook.png", "portrait", "lookbook.png")
    check_image_file(root / "technical-flat.png", "landscape", "平面图")


CODE_RE = re.compile(r"[A-Z]{2}\d{2}-[A-Z]{2}-\d{3}")


def check_series(root: Path) -> None:
    """系列目录：series-spec.html + looks/ + flats/ + specs/"""
    html = read_text(root / "series-spec.html")
    body = strip_comments(html)
    ok("系列页存在")
    check_placeholders(html)

    sections = len(re.findall(r'<div class="rail">', body))
    if sections < 8:
        warn(f"章节数只有 {sections}，系列页模板是 9 节（01–09）")
    else:
        ok(f"章节数 {sections}")

    need = [("共享色彩方案", "共享色彩方案"), ("共享面料板", "共享面料板"),
            ("系列逻辑", "系列逻辑"), ("款表", '<table class="styles">')]
    for label, needle in need:
        if needle not in body:
            fail(f"系列页缺「{label}」")
    if "性别归属" not in body:
        fail("第 09 节缺「性别归属」")
    if "放码" not in body:
        warn("第 07 节没提放码")

    # ---- 混男女装：必须给两套基准 ----
    meta_vals = re.findall(r'class="k">[^<]+</div><div class="v">(.*?)</div>', body, re.S)
    gender_cell = re.sub(r"<[^>]+>", " ", meta_vals[0]) if meta_vals else ""
    if "女装" in gender_cell and "男装" in gender_cell:
        has_f, has_m = "160/84A" in body, "170/88A" in body
        if not (has_f and has_m):
            fail("系列混男女装，但缺两套基准号型（女装 160/84A / 男装 170/88A）")
        else:
            ok("混男女装，双基准号型齐")
        if not re.search(r"两套|双基准|两条线|分别", body):
            warn("混男女装，但没写清哪几款走女装基准、哪几款走男装基准")

    # ---- 款表 ----
    codes: list[str] = []
    m = re.search(r'<table class="styles">(.*?)</table>', body, re.S)
    if not m:
        fail('找不到款表 <table class="styles">，买手没法一眼看完系列')
    else:
        raw = re.findall(r"<tr>\s*<td>(.*?)</td>", m.group(1), re.S)
        codes = [re.sub(r"<[^>]+>", "", c).strip() for c in raw]
        codes = [c for c in codes if c]
        if len(codes) < 3:
            fail(f"款表只有 {len(codes)} 行，系列至少 3 款（2 款请逐款走单件）")
        bad = [c for c in codes if not CODE_RE.fullmatch(c)]
        if bad:
            fail(f"款号格式不对：{', '.join(bad)}（应为 AW26-CT-001）")
        if len(set(codes)) != len(codes):
            fail("款表里有重复款号")
        nums = sorted(int(c[-3:]) for c in codes if CODE_RE.fullmatch(c))
        if nums and nums != list(range(nums[0], nums[0] + len(nums))):
            warn(f"款号序号不连续：{codes}，系列内应连号")
        if codes:
            ok(f"款表 {len(codes)} 款：{', '.join(codes)}")

    # ---- 逐款文件 ----
    for c in codes:
        for sub, ext, hard in (("looks", ".png", True), ("flats", ".png", True),
                               ("specs", ".html", False)):
            p = root / sub / (c + ext)
            if p.is_file():
                continue
            (fail if hard else warn)(f"缺 {sub}/{c}{ext}" + ("（每款都要有）" if hard else "（单款页）"))

    # ---- 网格图引用 ----
    for src in re.findall(r'<img[^>]+src="([^"]+)"', body):
        if src.startswith(("http://", "https://", "data:")):
            continue
        if not (root / src).is_file():
            fail(f"系列页引用的图不存在：{src}")

    # ---- 共用检查 ----
    check_colorway(html)
    check_weight(html)
    check_cliche(html)

    # ---- 图片画幅 ----
    if Image is None:
        warn("没装 Pillow，跳过画幅与白底检查")
    else:
        for c in codes:
            check_image_file(root / "looks" / (c + ".png"), "portrait", f"looks/{c}.png")
            check_image_file(root / "flats" / (c + ".png"), "landscape", f"flats/{c}.png")

    # ---- 单款页：性别与基准必须自洽 ----
    check_gender_base(html, "系列页")
    for c in codes:
        sp = root / "specs" / (c + ".html")
        if sp.is_file():
            check_gender_base(read_text(sp), f"{c} 单款页")

    # ---- 系列变体 ----
    check_series_variants(root, codes)


VAR_NAME_RE = re.compile(r"v\d+[-_].+")


def doc_signature(html: str) -> dict[str, tuple]:
    """抽出可比对的三个变量：色板、克重、02 节结构文本。"""
    body = strip_comments(html)
    colors = tuple(sorted(set(re.findall(r"background:\s*(#[0-9A-Fa-f]{6})", body))))
    weights = tuple(sorted(set(re.findall(r"(\d{2,3})\s*(?:g/m²|g/m2|gsm)", body))))
    m = re.search(r'class="num">02</div>.*?</table>', body, re.S)
    struct = re.sub(r"<[^>]+>", " ", m.group(0)) if m else ""
    struct = re.sub(r"\s+", "", struct)
    return {"色板": colors, "克重": weights, "结构": struct}


def check_gender_base(text: str, ctx: str) -> None:
    """性别归属与基准号型不能打架：男装配 160/84A、女装配 170/88A 都是复制粘贴事故。"""
    body = strip_comments(text) if "<" in text else text
    m = re.search(r"性别归属[：:]\s*([^<\n]{0,24})", body)
    if not m:
        return
    g = m.group(1)
    has_f, has_m = "160/84A" in body, "170/88A" in body
    if "男装" in g and "女装" not in g:
        if has_f and not has_m:
            fail(f"{ctx}性别归属是男装，基准号型却写 160/84A（女装基准）")
        elif not has_m:
            warn(f"{ctx}性别归属是男装，但没写 170/88A 基准")
    elif "女装" in g and "男装" not in g:
        if has_m and not has_f:
            fail(f"{ctx}性别归属是女装，基准号型却写 170/88A（男装基准）")
        elif not has_f:
            warn(f"{ctx}性别归属是女装，但没写 160/84A 基准")


def series_signature(html: str) -> dict[str, tuple]:
    body = strip_comments(html)
    colors = tuple(sorted(set(re.findall(r"background:\s*(#[0-9A-Fa-f]{6})", body))))
    weights = tuple(sorted(set(re.findall(r"(\d{2,3})\s*(?:g/m²|g/m2|gsm)", body))))
    m = re.search(r'<table class="styles">(.*?)</table>', body, re.S)
    rows: tuple = ()
    if m:
        all_rows = re.findall(r"<tr>.*?</tr>", m.group(1), re.S)
        rows = tuple(re.sub(r"\s+", "", re.sub(r"<[^>]+>", " ", r)) for r in all_rows[1:])
    return {"色板": colors, "克重": weights, "款表": rows}


def check_series_variants(root: Path, codes: list[str]) -> None:
    """系列变体：只允许换共享板（色板 / 面料板），款与结构不动。"""
    vdir = root / "variants"
    if not vdir.is_dir():
        return
    base = series_signature(read_text(root / "series-spec.html"))
    base_ver = re.search(r"v(\d+\.\d+)", strip_comments(read_text(root / "series-spec.html")))
    subs = sorted([d for d in vdir.iterdir() if d.is_dir()])
    if not subs:
        warn("variants/ 是空目录")
        return

    for d in subs:
        name = d.name
        if not VAR_NAME_RE.fullmatch(name):
            warn(f"系列变体目录名「{name}」不含变量，建议 v2-换燕麦色")
        if not (d / "series-spec.html").is_file():
            fail(f"系列变体 {name} 缺 series-spec.html")
            continue
        vtext = read_text(d / "series-spec.html")
        check_placeholders(vtext)

        missing = [c for c in codes if not (d / "looks" / (c + ".png")).is_file()]
        if missing:
            fail(f"系列变体 {name} 缺效果图：{', '.join('looks/' + c + '.png' for c in missing)}")

        sig = series_signature(vtext)
        diff = [k for k in base if sig[k] != base[k]]
        if not diff:
            fail(f"系列变体 {name} 与主系列完全一样，不构成变体")
        elif "款表" in diff:
            fail(f"系列变体 {name} 改了款表（款或结构），这不再是同一个系列的变体 —— 请新开系列")
        elif len(diff) >= 2:
            warn(f"系列变体 {name} 同时改了 {'、'.join(diff)}，横向对比不成立")
        else:
            ok(f"系列变体 {name} 只改了 {'、'.join(diff)}")

        if (d / "flats").is_dir():
            for c in codes:
                p = d / "flats" / (c + ".png")
                if p.is_file():
                    check_image_file(p, "landscape", f"{name}/flats/{c}.png")
        else:
            ok(f"系列变体 {name} 未带 flats，复用主系列平面图（结构未变，合理）")

        token = re.split(r"[-_]", name, 1)[-1]
        if token and token not in strip_comments(vtext):
            warn(f"系列变体 {name} 的文档里没提到「{token}」")

        vm = re.search(r"v(\d+\.\d+)", strip_comments(vtext))
        if base_ver and vm and base_ver.group(1) == vm.group(1):
            warn(f"系列变体 {name} 版本号与主系列相同（v{vm.group(1)}），建议递增")


def check_variants(root: Path) -> None:
    """variants/<v2-变量>/ 下每个变体都要齐全，且只改一个变量。"""
    vdir = root / "variants"
    if not vdir.is_dir():
        return
    main_html = root / "design-spec.html"
    if not main_html.is_file():
        warn("有 variants/ 但没有主交付 design-spec.html，无法比对差异")
        return
    main_text = strip_comments(read_text(main_html))
    base = doc_signature(read_text(main_html))
    base_ver = re.search(r"v(\d+\.\d+)", main_text)

    subs = sorted([d for d in vdir.iterdir() if d.is_dir()])
    if not subs:
        warn("variants/ 是空目录")
        return

    for d in subs:
        name = d.name
        if not VAR_NAME_RE.fullmatch(name):
            warn(f"变体目录名「{name}」不含变量，建议 v2-燕麦色")
        missing = [f for f in ("lookbook.png", "technical-flat.png", "design-spec.html")
                   if not (d / f).is_file()]
        if missing:
            fail(f"变体 {name} 缺文件：{', '.join(missing)}")
            continue

        vtext = read_text(d / "design-spec.html")
        check_placeholders(vtext)
        sig = doc_signature(vtext)
        diff = [k for k in base if sig[k] != base[k]]

        if not diff:
            fail(f"变体 {name} 与主交付完全一样（色板/克重/结构都没动），不构成变体")
        elif len(diff) >= 2:
            warn(f"变体 {name} 同时改了 {'、'.join(diff)}，横向对比不成立（一次只改一个变量）")
        else:
            ok(f"变体 {name} 只改了 {'、'.join(diff)}")

        token = re.split(r"[-_]", name, 1)[-1]
        if token and token not in strip_comments(vtext):
            warn(f"变体 {name} 的文档里没提到「{token}」，读者看不出改了什么")

        vm = re.search(r"v(\d+\.\d+)", strip_comments(vtext))
        if base_ver and vm and base_ver.group(1) == vm.group(1):
            warn(f"变体 {name} 版本号与主交付相同（v{vm.group(1)}），建议递增")


def check_production(html: str) -> None:
    """生产版字段齐不齐（--production）。

    判据是「字段齐不齐」，不是「数值能否直接下单」—— 后者只有版师能定。
    规则依据：references/techpack.md
    """
    body = strip_comments(html)
    plain = re.sub(r"<[^>]+>", "", body)

    # 1 BOM 表：类别不少于九行
    bom_kinds = ["主面料", "里布", "衬布", "拉链", "纽扣", "缝纫线", "织带", "标", "印花"]
    if "BOM" not in plain:
        fail("生产版缺 BOM 物料表（04 节）—— 拉链纽扣线标不能挤在一行「辅料」里")
    else:
        miss = [k for k in bom_kinds if k not in plain]
        if miss:
            fail(f"BOM 表缺类别：{', '.join(miss)}（最少九类，见 techpack.md）")
        else:
            ok("BOM 表类别齐全")

    # 2 缝制规格：缝型 / SPI / 缝份 / 熨烫
    sew_keys = {"缝型": r"缝型|包缝|平缝|来去缝|双针", "SPI": r"SPI|针/英寸|针距",
                "缝份": r"缝份", "熨烫": r"熨烫|整烫"}
    miss_sew = [k for k, pat in sew_keys.items() if not re.search(pat, plain, re.I)]
    if miss_sew:
        fail(f"生产版缺缝制规格：{', '.join(miss_sew)}（05 节，见 techpack.md）")
    else:
        ok("缝制规格含缝型 / SPI / 缝份 / 熨烫")

    # 3 允差与测量方法（允差必须是具体 ± 数值，「非成衣允差标准」这类免责话不算）
    if not re.search(r"[±]\s*\d+(?:\.\d+)?\s*(?:cm|mm|毫米)", plain, re.I):
        fail("生产版缺具体允差（06 节）—— 要写 ±1.0 cm 这种数值，不是一句「非成衣允差标准」")
    elif not re.search(r"从头|自.{0,6}至|量(至|到)|沿.{0,8}(中线|缝)|肩高点|后颈点|袖山|腰头", plain):
        fail("生产版缺测量方法（06 节）—— 同一条尺寸两种量法能差 2 cm")
    else:
        ok("尺寸表含允差与测量方法")

    # 4 Colorway 至少两套
    cw = len(re.findall(r"[Cc]olorway", plain))
    if cw < 2:
        fail(f"生产版只给了 {cw} 套 Colorway，至少两套（主套 + 1 套替代）")
    else:
        ok(f"Colorway {cw} 套")

    # 5 封面信息
    cover = {"系列": r"系列", "设计师": r"设计师"}
    miss_cover = [k for k, pat in cover.items() if not re.search(pat, plain)]
    if miss_cover:
        fail(f"生产版封面缺：{', '.join(miss_cover)}（00 节）")
    else:
        ok("封面含系列与设计师")

    # 6 图形缺口声明 —— 少这一句，整份包会被当成可直接生产的 Tech Pack
    if not re.search(r"待人工|人工补充|手工描|矢量另出|需另出", plain):
        fail("生产版没声明图形缺口 —— 局部详图与印花矢量不由 AI 生成，必须写明待人工补充")
    else:
        ok("已声明图形缺口（详图 / 矢量待人工补）")


def main(argv: list[str]) -> int:
    try:  # Windows 控制台默认 GBK，克重里的 ² 会炸
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    production = "--production" in argv
    args = [a for a in argv[1:] if not a.startswith("--")]
    root = Path(args[0] if args else ".").resolve()
    if not root.is_dir():
        print(f"不是目录：{root}")
        return 2

    is_series = (root / "series-spec.html").is_file()
    print(f"检查：{root}")
    depth = " · 生产版" if production else ""
    print(f"模式：{'系列' if is_series else '单件 / 整套'}{depth}\n")

    if is_series:
        check_series(root)
    else:
        html = check_files(root)
        if html is not None:
            check_placeholders(html)
            check_structure(html)
            check_colorway(html)
            check_weight(html)
            check_measurement(html)
            check_cliche(html)
            check_images(root)
            check_variants(root)
            if production:
                check_production(html)

    for line in OK:
        print(f"  PASS  {line}")
    for line in WARN:
        print(f"  WARN  {line}")
    for line in FAIL:
        print(f"  FAIL  {line}")

    print()
    if FAIL:
        print(f"不合格：{len(FAIL)} 项必须修，{len(WARN)} 项建议看")
        return 1
    print(f"通过：{len(OK)} 项，{len(WARN)} 项建议")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
