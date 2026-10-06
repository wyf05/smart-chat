# -*- coding: utf-8 -*-
"""提取 showcase 关键组件的完整 class/样式"""
import re

s = open(r"C:\Users\16101\Downloads\skeuo-showcase-extract\index.html",
         encoding="utf-8", errors="ignore").read()

def around(idx, pre=1200, post=80):
    return s[max(0, idx - pre):idx + post].replace("\n", " ")

i = s.find("Get Started")
print("==PRIMARY BUTTON==")
print(around(i, 1400, 30))

i = s.find(">Design Philosophy</div>")
print("\n==BADGE==")
print(around(i, 700, 40))

i = s.find("Back to Docs")
print("\n==HEADER==")
print(around(i, 1500, 100))

i = s.find("Get Started")
j = s.find("<button", i - 1400 if i > 1400 else 0)
print("\n==PRIMARY BUTTON EXACT==")
print(s[j:j + 900].replace("\n", " "))

# 输入框 / 表单区
i = s.find("<input")
if i == -1:
    i = s.find("<textarea")
print("\n==INPUT==")
print(s[i:i + 900].replace("\n", " ") if i != -1 else "not found")

# 卡片网格
i = s.find("bg-gradient-to-b from-[#fafae8]")
print("\n==PAPER CARD==")
print(s[max(0, i - 200):i + 700].replace("\n", " ") if i != -1 else "not found")

# 红色细线 / 页脚
for kw in ["b91c1c", "dc2626", "991b1b", "7f1d1d"]:
    idx = s.find(kw)
    if idx != -1:
        print("\n==RED:", kw, "==")
        print(s[max(0, idx - 400):idx + 300].replace("\n", " "))
        break
