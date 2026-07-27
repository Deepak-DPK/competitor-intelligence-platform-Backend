"""
scripts/fix_uuid_defaults.py
----------------------------
Patches all SQLAlchemy model files to replace:
    server_default=func.gen_random_uuid()
with:
    default=uuid.uuid4

This makes models compatible with both PostgreSQL (production) and
SQLite in-memory (test) databases.

Run once: python scripts/fix_uuid_defaults.py
"""

import re
from pathlib import Path

MODELS_DIR = Path(__file__).parent.parent / "app" / "models"

# Regex: matches server_default=func.gen_random_uuid() with any whitespace
PATTERN = re.compile(r"server_default=func\.gen_random_uuid\(\),")
REPLACEMENT = "default=uuid.uuid4,"

# Also ensure 'import uuid' is present at the top of each file
UUID_IMPORT = "import uuid"


def patch_file(path: Path) -> bool:
    content = path.read_text(encoding="utf-8")

    if "gen_random_uuid" not in content:
        return False  # Nothing to patch

    # Replace the server_default
    new_content = PATTERN.sub(REPLACEMENT, content)

    # Ensure 'import uuid' is present
    if UUID_IMPORT not in new_content:
        # Insert after the first line (module docstring ends before imports)
        lines = new_content.splitlines(keepends=True)
        # Find first non-docstring import line
        insert_pos = 0
        in_docstring = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('"""') or stripped.startswith("'''"):
                if in_docstring:
                    in_docstring = False
                else:
                    in_docstring = True
                continue
            if not in_docstring and (stripped.startswith("import ") or stripped.startswith("from ")):
                insert_pos = i
                break
        lines.insert(insert_pos, UUID_IMPORT + "\n")
        new_content = "".join(lines)

    if new_content != content:
        path.write_text(new_content, encoding="utf-8")
        print(f"  PATCHED: {path.name}")
        return True

    return False


def main():
    print(f"Scanning models in: {MODELS_DIR}")
    patched = 0
    for py_file in sorted(MODELS_DIR.glob("*.py")):
        if patch_file(py_file):
            patched += 1
    print(f"\nDone. Patched {patched} file(s).")


if __name__ == "__main__":
    main()
