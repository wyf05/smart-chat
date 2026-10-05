# -*- coding: utf-8 -*-
"""docx -> PDF，用于渲染逐页检查"""
import os
import win32com.client

word = win32com.client.Dispatch("Word.Application")
word.Visible = False
doc_path = r"D:\smart-chat\报告-软件2306班-王一帆-个人报告.docx"
pdf_path = r"D:\smart-chat\report_assets\报告-软件2306班-王一帆-个人报告.pdf"
d = word.Documents.Open(doc_path, ReadOnly=True)
d.SaveAs(pdf_path, FileFormat=17)
d.Close(False)
word.Quit()
print("pdf saved:", os.path.getsize(pdf_path))
