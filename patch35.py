# -*- coding: utf-8 -*-
# Patch 35: 越熟推擠力道越大（施力者熱度乘數）
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

results = []
def rep(label, old, new):
    global html
    if old in html:
        html = html.replace(old, new, 1)
        results.append(label + ": OK")
    else:
        results.append("FAIL " + label)

# ── 1. 玩家 doPush：玉米爆炸版加施力者乘數 ──────────────────────
rep("corn push heat boost",
    "        if(d<150){const nx2=d>0?(e.x-this.p.x)/d:1,ny2=d>0?(e.y-this.p.y)/d:0;\n"
    "          this.tweens.add({targets:e,x:e.x+nx2*110,y:e.y+ny2*110,",
    "        if(d<150){const nx2=d>0?(e.x-this.p.x)/d:1,ny2=d>0?(e.y-this.p.y)/d:0;\n"
    "          const myB=Math.min(2.0,1+this.heat/100*1.5);\n"
    "          this.tweens.add({targets:e,x:e.x+nx2*110*myB,y:e.y+ny2*110*myB,")

# ── 2. 玩家 doPush：一般衝刺加施力者乘數 ─────────────────────────
rep("dash push heat boost",
    "    const spd=c.speed/155, wgt=c.weight||1;\n"
    "    const DIST=Math.round(115*spd)*boost;  // 快→遠\n"
    "    const FORCE=Math.round(140*wgt)*boost; // 重→強",
    "    const spd=c.speed/155, wgt=c.weight||1;\n"
    "    const myBst=Math.min(2.0,1+this.heat/100*1.5); // 越熟衝得越遠越猛\n"
    "    const DIST=Math.round(115*spd)*boost*myBst;  // 快→遠\n"
    "    const FORCE=Math.round(140*wgt)*boost*myBst; // 重→強")

# ── 3. AI 推人：依 AI 熱度放大推力 ──────────────────────────────
rep("ai push heat boost",
    "          const pForce=95;",
    "          const pForce=95*Math.min(2.0,1+e.heat/100*1.5); // AI 越熟推越猛")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

for r in results:
    print(r)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
checks = [
    ("myB=Math.min(2.0",       "corn myBst"),
    ("nx2*110*myB",            "corn dist scaled"),
    ("myBst=Math.min(2.0",     "dash myBst"),
    ("DIST.*myBst",            "dash dist scaled"),
    ("FORCE.*myBst",           "dash force scaled"),
    ("e.heat/100*1.5",         "ai heat boost"),
]
import re
for pattern, label in checks:
    print(f"{label}: {'OK' if re.search(pattern, v) else 'MISSING'}")
