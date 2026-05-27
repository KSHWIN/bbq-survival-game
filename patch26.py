# -*- coding: utf-8 -*-
# Patch 26: 飛撲弧線化 — 速度放慢 + 跳躍弧 + 離地陰影
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. 速度 165 → 120，更慢更可見 ─────────────────────────────────
old = "    const SPD=isDash?165:this.charData.speed*(this.activeEffects.slowpow>0?0.5:1);"
new = "    const SPD=isDash?120:this.charData.speed*(this.activeEffects.slowpow>0?0.5:1);"
if old in html: html=html.replace(old,new); print("dash SPD 120: OK")
else: print("FAIL dash SPD")

# ── 2. dist 追蹤同步 165 → 120 ────────────────────────────────────
old = "      this.dashState.dist+=165*dt;"
new = "      this.dashState.dist+=120*dt;"
if old in html: html=html.replace(old,new); print("dist tracking 120: OK")
else: print("FAIL dist tracking")

# ── 3. maxDist 95 → 115（慢速但距離夠）───────────────────────────
old = "    const DIST=Math.round(95*spd)*boost;   // 快→遠"
new = "    const DIST=Math.round(115*spd)*boost;  // 快→遠"
if old in html: html=html.replace(old,new); print("maxDist 115: OK")
else: print("FAIL maxDist")

# ── 4. 超時保護 0.6 → 1.0s（慢速飛撲需要更長時間）────────────────
old = "      if(this.dashState.age>0.6) this.dashState.active=false;"
new = "      if(this.dashState.age>1.0) this.dashState.active=false;"
if old in html: html=html.replace(old,new); print("timeout 1.0s: OK")
else: print("FAIL timeout")

# ── 5. 飛撲弧線動畫：角色sprite加跳躍弧 + 腳步層補地面陰影 ────────
old = (
    "        if(isDash&&this.dashState){\n"
    "          // 衝刺：沿衝方向拉伸，垂直壓扁，大角度傾斜（「扑」的視覺）\n"
    "          const ds=this.dashState;\n"
    "          const isH=Math.abs(ds.dx)>Math.abs(ds.dy);\n"
    "          this.playerSprite.setScale(isH?BS*1.55:BS*0.70, isH?BS*0.70:BS*1.45);\n"
    "          this.playerSprite.setFlipX(ds.dx<-0.1);\n"
    "          this.playerSprite.setAngle(ds.dx*30-ds.dy*20);\n"
    "          this.playerSprite.setPosition(this.p.x, this.p.y);\n"
    "        }"
)
new = (
    "        if(isDash&&this.dashState){\n"
    "          // 飛撲弧線：沿方向拉伸 + sin弧高度偏移（讓角色像跳出去）\n"
    "          const ds=this.dashState;\n"
    "          const prog=Math.min(ds.dist/ds.maxDist,1);\n"
    "          const arc=-Math.sin(prog*Math.PI)*18; // 弧頂高 18px\n"
    "          const isH=Math.abs(ds.dx)>Math.abs(ds.dy);\n"
    "          this.playerSprite.setScale(isH?BS*1.55:BS*0.70, isH?BS*0.70:BS*1.45);\n"
    "          this.playerSprite.setFlipX(ds.dx<-0.1);\n"
    "          this.playerSprite.setAngle(ds.dx*30-ds.dy*20);\n"
    "          this.playerSprite.setPosition(this.p.x, this.p.y+arc);\n"
    "          // 地面陰影：角色飛在空中時地上留影子\n"
    "          if(this.footLayer){\n"
    "            const arcH=Math.sin(prog*Math.PI);\n"
    "            this.footLayer.clear();\n"
    "            this.footLayer.fillStyle(0x000000,0.45-arcH*0.25);\n"
    "            this.footLayer.fillEllipse(this.p.x,this.p.y,(22-arcH*8),(10-arcH*4));\n"
    "          }\n"
    "        }"
)
if old in html: html=html.replace(old,new); print("jump arc + shadow: OK")
else: print("FAIL jump arc")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
print("SPD 120:", "isDash?120:" in v)
print("dist 120:", "dashState.dist+=120*dt" in v)
print("maxDist 115:", "Math.round(115*spd)" in v)
print("timeout 1.0:", "dashState.age>1.0" in v)
print("jump arc:", "Math.sin(prog*Math.PI)*18" in v)
print("ground shadow:", "fillEllipse(this.p.x,this.p.y" in v)
