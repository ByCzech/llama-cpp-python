#!/usr/bin/python3
import re
import sys
from pathlib import Path


def fail(message: str) -> None:
    print(f"cuda12.9-glibc2.41: {message}", file=sys.stderr)
    raise SystemExit(1)


if len(sys.argv) != 2:
    fail("usage: cuda12.9-glibc2.41.py PATH/TO/math_functions.h")

header = Path(sys.argv[1])
try:
    text = header.read_text()
except OSError as exc:
    fail(f"cannot read {header}: {exc}")

functions = (
    ("sinpi",  "double"),
    ("sinpif", "float"),
    ("cospi",  "double"),
    ("cospif", "float"),
)

for name, ctype in functions:
    # CUDA 12.9 declares these device builtins without the exception
    # specification used by glibc 2.41.  Accept arbitrary whitespace so the
    # workaround is independent of line-number and documentation changes in
    # NVIDIA's header, but require the exact CUDA declaration shape.
    declaration = (
        rf"(?m)^(?P<decl>\s*extern\s+__DEVICE_FUNCTIONS_DECL__\s+"
        rf"__device_builtin__\s+{ctype}\s+{name}\s*\(\s*{ctype}\s+x\s*\))"
    )
    fixed_re = re.compile(declaration + r"\s+noexcept\s*\(\s*true\s*\)\s*;\s*$")
    old_re = re.compile(declaration + r"\s*;\s*$")

    fixed = list(fixed_re.finditer(text))
    if len(fixed) == 1:
        print(f"cuda12.9-glibc2.41: {name} already has noexcept(true)")
        continue
    if len(fixed) > 1:
        fail(f"found {len(fixed)} already-fixed declarations for {name}, expected one")

    old = list(old_re.finditer(text))
    if len(old) != 1:
        fail(f"found {len(old)} unpatched declarations for {name}, expected one")

    text, count = old_re.subn(r"\g<decl> noexcept (true);", text, count=1)
    if count != 1:
        fail(f"failed to patch declaration for {name}")
    print(f"cuda12.9-glibc2.41: patched {name}")

# Final strict verification.  This catches both a silently changed NVIDIA
# declaration and an incomplete transformation before nvcc is ever invoked.
for name, ctype in functions:
    verify_re = re.compile(
        rf"(?m)^\s*extern\s+__DEVICE_FUNCTIONS_DECL__\s+__device_builtin__\s+"
        rf"{ctype}\s+{name}\s*\(\s*{ctype}\s+x\s*\)\s+"
        rf"noexcept\s*\(\s*true\s*\)\s*;\s*$"
    )
    matches = list(verify_re.finditer(text))
    if len(matches) != 1:
        fail(f"verification failed for {name}: found {len(matches)} matching declarations")

try:
    header.write_text(text)
except OSError as exc:
    fail(f"cannot write {header}: {exc}")
