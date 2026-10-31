"""校验 SKILL.md 的 YAML frontmatter 能否被解析。

上架市场时平台会用 YAML 解析 frontmatter，解析失败直接拒绝上传，报错形如：
    SKILL.md 格式错误 — frontmatter 无法解析（yaml: line 2: mapping values are not allowed in this context）

最常见的原因是裸标量里出现了 ": "（冒号加空格）—— 例如
    description: ... three linked deliverables: an on-model lookbook ...
YAML 会把 "deliverables:" 当成嵌套映射的开头，于是整行出错。

用法：
    python scripts/lint_skill.py [SKILL.md 路径]

退出码 0 通过，1 不通过。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED = ("name", "description")

# 上架市场时平台还会强制要求这几个展示字段，缺一个就整包拒收：
#   缺少 Skill 中文展示名（display_name）…
MARKET_REQUIRED = (
    "display_name",
    "display_name_en",
    "description_zh",
    "description_en",
)


def main(argv: list[str]) -> int:
    market = "--market" in argv
    args = [a for a in argv[1:] if not a.startswith("--")]
    path = Path(args[0]) if args else Path("SKILL.md")
    if not path.exists():
        print(f"FAIL: 找不到文件 {path}")
        return 1

    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    if not m:
        print("FAIL: SKILL.md 开头没有 --- 包裹的 frontmatter")
        return 1
    fm = m.group(1)

    try:
        import yaml  # 有就用完整解析，最可靠
    except ImportError:
        return fallback(fm)

    try:
        data = yaml.safe_load(fm)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: YAML 解析失败 — {exc}")
        return 1

    if not isinstance(data, dict):
        print("FAIL: frontmatter 解析结果不是映射")
        return 1

    missing = [k for k in REQUIRED if not str(data.get(k, "")).strip()]
    if missing:
        print(f"FAIL: 缺必填字段 {', '.join(missing)}")
        return 1

    if market:
        miss_mkt = [k for k in MARKET_REQUIRED if not str(data.get(k, "")).strip()]
        if miss_mkt:
            print(f"FAIL: 缺市场展示字段 {', '.join(miss_mkt)}（平台会直接拒收）")
            return 1

    print("OK: YAML 解析通过 — 字段 " + ", ".join(data.keys()))
    desc = str(data["description"])
    print(f"    description 长度 {len(desc)} 字符")
    if market:
        print(f"    市场字段齐全：{', '.join(MARKET_REQUIRED)}")
    return 0


def fallback(fm: str) -> int:
    """没有 PyYAML 时的保守检查：裸标量里禁止出现 ': '。"""
    bad: list[tuple[int, str]] = []
    for i, line in enumerate(fm.splitlines(), start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[:1] in (" ", "\t"):
            continue  # 块标量或嵌套结构的续行
        if ":" not in line:
            continue
        _, _, val = line.partition(":")
        v = val.strip()
        if v in ("", ">", ">-", "|", "|-"):
            continue  # 块标量起始
        if v[:1] in ('"', "'"):
            continue  # 引号包裹的标量安全
        if re.search(r":\s", v):
            bad.append((i, line.strip()[:70]))

    if bad:
        print("FAIL: 以下行在裸标量里含 ': '，YAML 会解析失败（建议改用 >- 块标量）：")
        for i, content in bad:
            print(f"    第 {i} 行: {content}")
        return 1

    print("OK（保守检查）: 未发现裸标量含 ': '；装 PyYAML 可做完整解析")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
