# -*- coding: utf-8 -*-
"""订单数据修正：DD2024 -> DD2026，并补充王一帆的订单"""
import sqlite3

DB = r"D:\smart-chat\backend\data\smartchat.db"
conn = sqlite3.connect(DB)
cur = conn.cursor()

# 1. 老订单号改年份
cur.execute("UPDATE orders SET order_id = REPLACE(order_id, 'DD2024', 'DD2026') WHERE order_id LIKE 'DD2024%'")
print("renamed:", cur.rowcount)

# 2. 补充王一帆的订单（存在则跳过）
new_orders = [
    ("DD20260005", "已发货", "329.00", "王一帆", "顺丰速运，预计明天 15:00 前送达"),
    ("DD20260006", "待付款", "159.00", "王一帆", "30 分钟内未支付将自动取消"),
    ("DD20260007", "已签收", "459.00", "王一帆", "2026-09-30 11:20 签收"),
]
for oid, status, amount, receiver, logistics in new_orders:
    cur.execute("SELECT COUNT(*) FROM orders WHERE order_id = ?", (oid,))
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO orders (order_id, status, amount, receiver, logistics) VALUES (?,?,?,?,?)",
            (oid, status, amount, receiver, logistics))
        print("inserted:", oid)
    else:
        print("exists:", oid)

conn.commit()
cur.execute("SELECT order_id, status, amount, receiver FROM orders ORDER BY order_id")
for row in cur.fetchall():
    print(row)
conn.close()
