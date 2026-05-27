# -*- coding: utf-8 -*-
# Patch 27: 火焰範圍加大 + 亂數跳動
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. 基礎半徑 30→46，振幅 3→12（讓火更大且有明顯跳動感）────────
old = "    this.FIRE_R_BASE=30; this.FIRE_R_AMP=3;"
new = "    this.FIRE_R_BASE=46; this.FIRE_R_AMP=12;"
if old in html: html=html.replace(old,new); print("FIRE_R BASE/AMP: OK")
else: print("FAIL FIRE_R BASE/AMP")

# ── 2. 每幀把 FIRE_R_AMP 實際套進 f.r（原本只設了但沒用）───────────
old = "      f.r=this.FIRE_R_BASE;"
new = "      f.r=this.FIRE_R_BASE+Math.sin(phase*f.spd*0.6+f.ph)*this.FIRE_R_AMP;"
if old in html: html=html.replace(old,new); print("f.r fluctuation: OK")
else: print("FAIL f.r fluctuation")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
print("FIRE_R_BASE 46:", "FIRE_R_BASE=46" in v)
print("FIRE_R_AMP 12:", "FIRE_R_AMP=12" in v)
print("f.r fluctuation:", "Math.sin(phase*f.spd*0.6+f.ph)*this.FIRE_R_AMP" in v)
