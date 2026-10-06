# -*- coding: utf-8 -*-
"""对比 .vue/.css 中使用的 --sk-* 变量与 skeuo.css 中定义的变量"""
import os, re

src = r"D:\smart-chat\frontend\src"
css = open(os.path.join(src, "styles", "skeuo.css"), encoding="utf-8").read()
defined = set(re.findall(r"(--sk-[a-z0-9-]+)\s*:", css))

used = set()
for root, _, files in os.walk(src):
    for f in files:
        if f.endswith((".vue", ".css")):
            t = open(os.path.join(root, f), encoding="utf-8").read()
            used |= set(re.findall(r"var\((--sk-[a-z0-9-]+)\)", t))

missing = sorted(used - defined)
print("defined:", len(defined), "used:", len(used))
print("MISSING:", missing if missing else "none")
