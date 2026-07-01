"""Patch script: rewrite the source_field_sets_equivalent function in semantic_match.py
to properly handle single vs multi form.
"""
import re
from pathlib import Path

TARGET = Path(r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\KQP\semantic_match.py")

OLD = '''def source_field_sets_equivalent(sf_a: str, sf_b: str) -> bool:'''
NEW_END = '''# end'''

NEW_FUNC = '''def source_field_sets_equivalent(sf_a: str, sf_b: str) -> bool:
    """Two source_fields are equivalent if they reference the same design_plan
    leaf values, regardless of '+ ' concat syntax.

    Equivalent forms:
      A. '$.a.b.X.value + $.a.b.Y.value' (full-path multi-piece)
      B. '$.a.b.X.value + .Y.value'        (relative-path multi-piece)
      C. '$.a.b.X.Y.value'                  (single-path, container-folded)

    All three are equivalent. To match A vs C or B vs C, we detect when
    the single side is a CONCATENATED form of the multi-side.
    """
    def pieces_sorted(sf: str) -> list[str]:
        if not sf:
            return []
        sf = re.sub(r"\\s*\\(.*\\)\\s*$", "", sf)
        raw_pieces = [p.strip() for p in sf.split("+") if p.strip()]
        norm_pieces = []
        for p in raw_pieces:
            p = _DOT_OR_BRACKET_PATTERN.sub(
                lambda m: f"[{m.group(0)[1:]}]" if m.group(0).startswith(".") else m.group(0),
                p,
            )
            if p.startswith("$"):
                norm_pieces.append(p)
                continue
            if not norm_pieces:
                norm_pieces.append(p)
                continue
            prev = norm_pieces[-1]
            container = _strip_trailing_value(prev)
            if p.startswith("."):
                norm_pieces[-1] = container + p
            else:
                norm_pieces[-1] = container + "." + p
        return sorted(norm_pieces)

    list_a = pieces_sorted(sf_a)
    list_b = pieces_sorted(sf_b)
    if list_a == list_b:
        return True
    # Try single vs multi
    if len(list_a) == 1 and len(list_b) > 1:
        return _try_fold(list_b, list_a[0])
    if len(list_b) == 1 and len(list_a) > 1:
        return _try_fold(list_a, list_b[0])
    return False


def _try_fold(multi: list[str], single: str) -> bool:
    """Fold a list of normalized multi-pieces into a single path. Identify the
    piece that ends with '.value' (the container); strip the trailing
    '.value' to get the base; extract the last segment of each other piece
    (the relative path); concatenate. If the result equals single, return True.
    """
    if not multi:
        return False
    # Find the piece ending with '.value' (the container)
    base = None
    for p in multi:
        if p.endswith(".value") and (base is None or len(p) > len(base)):
            base = p
    if base is None:
        return False
    container = _strip_trailing_value(base)
    # Extract the last segment of each other piece
    extras = []
    for p in multi:
        if p == base:
            continue
        last_dot = p.rfind(".")
        if last_dot >= 0:
            extras.append(p[last_dot:])
    candidate = container + "".join(extras)
    return candidate == single
'''

text = TARGET.read_text(encoding="utf-8")
# find the source_field_sets_equivalent function
start = text.find("def source_field_sets_equivalent(")
if start < 0:
    print("ERROR: function not found")
    raise SystemExit(1)
# find the next top-level 'def ' to know where the function ends
# find the line after the function
lines = text.split("\n")
start_line = None
for i, ln in enumerate(lines):
    if ln.startswith("def source_field_sets_equivalent("):
        start_line = i
        break
# find the next top-level 'def ' or class
end_line = None
indent = "    "  # 4 spaces for class/function level
for i in range(start_line + 1, len(lines)):
    if lines[i].startswith("def ") or lines[i].startswith("class ") or lines[i].startswith("if __name__"):
        end_line = i
        break
if end_line is None:
    end_line = len(lines)

print(f"Replacing lines {start_line}..{end_line-1}")
new_lines = lines[:start_line] + NEW_FUNC.split("\n") + lines[end_line:]
TARGET.write_text("\n".join(new_lines), encoding="utf-8")
print("Done")
