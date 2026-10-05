# -*- coding: utf-8 -*-
"""渲染报告 PDF 为逐页 PNG，用于视觉检查"""
import fitz

PDF = r"D:\smart-chat\report_assets\报告-软件2306班-王一帆-个人报告.pdf"
OUT = r"D:\smart-chat\report_assets\report_pages"

import os
os.makedirs(OUT, exist_ok=True)
doc = fitz.open(PDF)
print("pages:", len(doc))
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=100)
    pix.save(os.path.join(OUT, f"page_{i+1:02d}.png"))
print("rendered")
