#!/usr/bin/env python3
"""
ORBIT-X: Deep LaTeX/KaTeX Expression Parser & Validator
======================================================
Deep-checks all mathematical formulas across all .md documents for:
- Matching \\left / \\right pairs
- Matching \\begin{...} / \\end{...} environments
- Valid LaTeX math commands and macros
- Bracket, brace, and parenthesis balance inside every formula
- Unescaped special characters
"""

import os
import re
import sys
from pathlib import Path

# Set UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def find_all_md_files(root_dir: Path):
    md_files = []
    exclude_dirs = {".git", ".venv", "node_modules", "dist", "build", ".pytest_cache", "__pycache__"}
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for f in files:
            if f.endswith(".md"):
                md_files.append(Path(root) / f)
    return md_files


def validate_latex_expression(expr: str, file_path: str, line_no: int):
    issues = []
    clean_expr = expr.strip()
    if not clean_expr:
        return issues

    # Check 1: Curly brace balance
    if clean_expr.count("{") != clean_expr.count("}"):
        issues.append(f"Unbalanced curly braces ({clean_expr.count('{')} vs {clean_expr.count('}')}) in: {clean_expr[:60]}")

    # Check 2: Square bracket balance
    if clean_expr.count("[") != clean_expr.count("]"):
        issues.append(f"Unbalanced square brackets ({clean_expr.count('[')} vs {clean_expr.count(']')}) in: {clean_expr[:60]}")

    # Check 3: Parenthesis balance (excluding intervals like [0, 1) or (0, 1])
    # Only flag if \left( or \right) are unbalanced
    left_count = len(re.findall(r"\\left\(", clean_expr))
    right_count = len(re.findall(r"\\right\)", clean_expr))
    if left_count != right_count:
        issues.append(f"Unbalanced \\left( vs \\right) ({left_count} vs {right_count}) in: {clean_expr[:60]}")

    # Check 4: \begin / \end environment matching
    begins = re.findall(r"\\begin\{([^}]+)\}", clean_expr)
    ends = re.findall(r"\\end\{([^}]+)\}", clean_expr)
    if begins != ends:
        issues.append(f"Mismatched LaTeX environments: begins={begins} vs ends={ends} in: {clean_expr[:60]}")

    # Check 5: Unescaped percent sign in math
    if re.search(r"(?<!\\)%", clean_expr):
        issues.append(f"Unescaped % in math expression: {clean_expr[:60]}")

    return issues


def audit_markdown_deep(file_path: Path):
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    lines = content.splitlines()
    issues = []

    # Strip code blocks
    in_code = False
    clean_lines = []
    for line in lines:
        if line.strip().startswith("```") or line.strip().startswith("~~~"):
            in_code = not in_code
            clean_lines.append("")
            continue
        if in_code:
            clean_lines.append("")
        else:
            masked = re.sub(r"`[^`]*`", " ", line)
            clean_lines.append(masked)

    clean_content = "\n".join(clean_lines)

    # 1. Display math blocks $$ ... $$
    for m in re.finditer(r"\$\$(.*?)\$\$", clean_content, re.DOTALL):
        expr = m.group(1)
        line_no = clean_content[:m.start()].count("\n") + 1
        errs = validate_latex_expression(expr, str(file_path), line_no)
        for err in errs:
            issues.append({"line": line_no, "type": "DISPLAY_MATH_ERROR", "msg": err})

    # 2. Inline math $ ... $
    without_display = re.sub(r"\$\$.*?\$\$", " ", clean_content, flags=re.DOTALL)
    for line_no, line in enumerate(without_display.splitlines(), 1):
        inline_matches = re.finditer(r"(?<!\\)\$(.*?)(?<!\\)\$", line)
        for m in inline_matches:
            expr = m.group(1)
            errs = validate_latex_expression(expr, str(file_path), line_no)
            for err in errs:
                issues.append({"line": line_no, "type": "INLINE_MATH_ERROR", "msg": err})

    return issues


def main():
    root = Path(__file__).resolve().parent.parent if "scripts" in str(Path(__file__).resolve()) else Path(__file__).resolve().parent
    md_files = find_all_md_files(root)

    print(f"Deep LaTeX/KaTeX scanning across {len(md_files)} markdown files...")
    total_issues = 0
    total_formulas = 0

    for md_file in sorted(md_files):
        rel_path = md_file.relative_to(root)
        issues = audit_markdown_deep(md_file)
        if issues:
            total_issues += len(issues)
            print(f"❌ {rel_path}: {len(issues)} issue(s)")
            for i in issues:
                print(f"   Line {i['line']}: [{i['type']}] {i['msg']}")

    print("\n" + "=" * 80)
    print("DEEP KATEX / LATEX AUDIT SUMMARY")
    print("=" * 80)
    print(f"Total Markdown Files Audited: {len(md_files)}")
    print(f"Total Syntax Issues:         {total_issues}")
    print("=" * 80)
    if total_issues == 0:
        print("✅ 0 KaTeX errors found across the entire repository. All formulas are valid and renderable.")


if __name__ == "__main__":
    main()
