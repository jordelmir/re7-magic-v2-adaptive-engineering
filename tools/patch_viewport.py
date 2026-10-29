#!/usr/bin/env python3
"""Apply the tested cover-scale and touch-transform edits to decoded Smali.

This script does not decode, rebuild, sign, install, or distribute an APK.
Run it only on an APK you are authorized to modify. It fails closed when its
version-specific method anchors do not match.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


RENDERER_REL = Path(
    "smali_classes12/com/winlator/cmod/renderer/ViewTransformation.smali"
)
TOUCH_REL = Path(
    "smali_classes14/com/winlator/cmod/widget/TouchpadView.smali"
)


def method_block(source: str, signature: str) -> tuple[int, int, str]:
    lines = source.splitlines(keepends=True)
    starts = [
        i for i, line in enumerate(lines)
        if line.strip().startswith(".method ")
        and signature in line
    ]
    if len(starts) != 1:
        raise ValueError(
            f"expected one method containing {signature!r}; found {len(starts)}"
        )

    start = starts[0]
    ends = [
        i for i in range(start + 1, len(lines))
        if lines[i].strip() == ".end method"
    ]
    if not ends:
        raise ValueError(f"method {signature!r} has no .end method")

    end = ends[0] + 1
    return start, end, "".join(lines[start:end])


def patch_renderer(path: Path, apply: bool) -> str:
    source = path.read_text()
    start, end, block = method_block(source, "update(IIII)V")
    old = "Ljava/lang/Math;->min(FF)F"
    new = "Ljava/lang/Math;->max(FF)F"

    if block.count(new) == 1 and block.count(old) == 0:
        return "renderer: already uses cover scale"
    if block.count(old) != 1:
        raise ValueError(
            "renderer update method did not contain exactly one Math.min anchor"
        )

    updated = block.replace(old, new, 1)
    if apply:
        path.write_text(source[:start] + updated + source[end:])
    return "renderer: min scale -> max scale"


def patch_touch(path: Path, apply: bool) -> str:
    source = path.read_text()
    start, end, block = method_block(source, "updateXform(IIII)V")
    branch = "    if-nez v2, :cond_0"
    neutralized = "    nop\n    nop"

    if branch not in block and neutralized in block:
        return "touch: fullscreen transform branch already neutralized"
    if block.count(branch) != 1:
        raise ValueError(
            "touch updateXform method did not contain the expected fullscreen branch"
        )

    updated = block.replace(branch, neutralized, 1)
    if apply:
        path.write_text(source[:start] + updated + source[end:])
    return "touch: fullscreen coordinate transform aligned with cover mode"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "decoded_apk",
        type=Path,
        help="directory produced by Apktool decode",
    )
    parser.add_argument(
        "--renderer-file",
        type=Path,
        help=f"override default renderer Smali path ({RENDERER_REL})",
    )
    parser.add_argument(
        "--touch-file",
        type=Path,
        help=f"override default touch Smali path ({TOUCH_REL})",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="write changes; without this flag, only report matched edits",
    )
    args = parser.parse_args()

    renderer = args.renderer_file or args.decoded_apk / RENDERER_REL
    touch = args.touch_file or args.decoded_apk / TOUCH_REL
    missing = [str(path) for path in (renderer, touch) if not path.is_file()]
    if missing:
        parser.error("missing expected Smali file(s): " + ", ".join(missing))

    try:
        actions = [
            patch_renderer(renderer, False),
            patch_touch(touch, False),
        ]
        if args.apply:
            patch_renderer(renderer, True)
            patch_touch(touch, True)
    except (OSError, ValueError) as exc:
        print(f"patch refused: {exc}", file=sys.stderr)
        return 2

    mode = "applied" if args.apply else "matched; dry run only"
    print(f"{mode}:")
    for action in actions:
        print(f"- {action}")
    if not args.apply:
        print("Re-run with --apply to write the two guarded changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
