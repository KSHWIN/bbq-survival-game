# -*- coding: utf-8 -*-
# Patch 12: 推力平滑 + 腳步陰影 + 白邊修正 + 推力博弈機制
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. 調高 _rmWhite 閾值，減少過度去白（保留角色高光）────────────────
old = (
    "    for(let i=0;i<d.length;i+=4){\n"
    "      const mn=Math.min(d[i],d[i+1],d[i+2]);\n"
    "      if(mn>225) d[i+3]=0;\n"
    "      else if(mn>185) d[i+3]=Math.round(d[i+3]*(mn-185)/40);\n"
    "    }"
)
new = (
    "    for(let i=0;i<d.length;i+=4){\n"
    "      const mn=Math.min(d[i],d[i+1],d[i+2]);\n"
    "      const mx=Math.max(d[i],d[i+1],d[i+2]);\n"
    "      const sat=mx-mn; // 低飽和度才是真白底\n"
    "      if(mn>238&&sat<18) d[i+3]=0;\n"
    "      else if(mn>222&&sat<25) d[i+3]=Math.round(d[i+3]*(mn-222)/16);\n"
    "    }"
)
if old in html: html=html.replace(old,new); print("_rmWhite threshold: OK")
else: print("FAIL _rmWhite threshold")

# ── 2. 加入 footLayer 圖層初始化 ─────────────────────────────────────
old = (
    "    this.hbLayer   =this.add.graphics().setDepth(18);\n"
    "    this.abilFxLayer=this.add.graphics().setDepth(22);"
)
new = (
    "    this.hbLayer   =this.add.graphics().setDepth(18);\n"
    "    this.footLayer  =this.add.graphics().setDepth(19);\n"
    "    this.abilFxLayer=this.add.graphics().setDepth(22);"
)
if old in html: html=html.replace(old,new); print("footLayer init: OK")
else: print("FAIL footLayer init")

# ── 3. 推力範圍縮小 70 → 52 ──────────────────────────────────────────
old = "const ae=this.activeEffects;\n    const c=this.charData, RANGE=70, base=c.key==='pork'?115:82"
new = "const ae=this.activeEffects;\n    const c=this.charData, RANGE=52, base=c.key==='pork'?105:75"
if old in html: html=html.replace(old,new); print("RANGE 70->52: OK")
else: print("FAIL RANGE")

# ── 4. 推力改用 tween 滑行 + 熟度博弈（未熟抵抗）───────────────────────
old = (
    "      if(Math.hypot(this.p.x-e.x,this.p.y-e.y)<RANGE)"
    "{ hit=true; e.x+=dx*FORCE; e.y+=dy*FORCE; this.checkEnemyFall(e,i); }"
)
new = (
    "      if(Math.hypot(this.p.x-e.x,this.p.y-e.y)<RANGE){\n"
    "        hit=true;\n"
    "        // 未熟敵人（熟度<50）有抵抗力，推力減半\n"
    "        const resist=(e.heat||0)<50?0.5:1.0;\n"
    "        if(resist<1){ this.showPop('💪 撐住了！'); }\n"
    "        const tx=e.x+dx*FORCE*resist, ty=e.y+dy*FORCE*resist;\n"
    "        this.tweens.add({\n"
    "          targets:e, x:tx, y:ty, duration:220, ease:'Cubic.easeOut',\n"
    "          onComplete:()=>this.checkEnemyFall(e,i)\n"
    "        });\n"
    "      }"
)
if old in html: html=html.replace(old,new); print("push tween+resist: OK")
else: print("FAIL push tween+resist")

# ── 5. 腳步陰影動畫（移動時在腳下畫交替橢圓）────────────────────────────
old = (
    "        this.playerSprite.setAngle(this.lastDir.x*11 - this.lastDir.y*4);\n"
    "          this.playerSprite.setPosition(this.p.x, this.p.y+c*5.5);\n"
    "        } else {\n"
    "          this.playerSprite.setScale(BS);\n"
    "          this.playerSprite.setAngle(this.lastDir.x*3);\n"
    "          this.playerSprite.setFlipX(this.lastDir.x<-0.1);\n"
    "          this.playerSprite.setPosition(this.p.x, this.p.y);\n"
    "        }"
)
new = (
    "        this.playerSprite.setAngle(this.lastDir.x*11 - this.lastDir.y*4);\n"
    "          this.playerSprite.setPosition(this.p.x, this.p.y+c*5.5);\n"
    "        } else {\n"
    "          this.playerSprite.setScale(BS);\n"
    "          this.playerSprite.setAngle(this.lastDir.x*3);\n"
    "          this.playerSprite.setFlipX(this.lastDir.x<-0.1);\n"
    "          this.playerSprite.setPosition(this.p.x, this.p.y);\n"
    "        }\n"
    "        // 腳步陰影\n"
    "        if(this.footLayer){\n"
    "          this.footLayer.clear();\n"
    "          if(isMoving){\n"
    "            const fc=Math.sin(this.runPhase);\n"
    "            const px=this.p.x, py=this.p.y;\n"
    "            const pvx=-this.lastDir.y*0.45, pvy=this.lastDir.x*0.45;\n"
    "            this.footLayer.fillStyle(0x1a0e06,0.55);\n"
    "            this.footLayer.fillEllipse(px+pvx*11+this.lastDir.x*5,py+pvy*11+this.lastDir.y*5+16+fc*5,8,4);\n"
    "            this.footLayer.fillStyle(0x1a0e06,0.4);\n"
    "            this.footLayer.fillEllipse(px-pvx*11+this.lastDir.x*5,py-pvy*11+this.lastDir.y*5+16-fc*5,8,4);\n"
    "          }\n"
    "        }"
)
if old in html: html=html.replace(old,new); print("foot shadow: OK")
else: print("FAIL foot shadow")

# ── 6. endGame 清除 footLayer ────────────────────────────────────────
old = (
    "    this.abilityActive=null;\n"
    "    if(this.abilFxLayer) this.abilFxLayer.clear();"
)
new = (
    "    this.abilityActive=null;\n"
    "    if(this.abilFxLayer) this.abilFxLayer.clear();\n"
    "    if(this.footLayer) this.footLayer.clear();"
)
if old in html: html=html.replace(old,new); print("endGame footLayer clear: OK")
else: print("FAIL endGame footLayer clear")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
print("rmWhite sat check:", "const sat=mx-mn;" in v)
print("footLayer init:", "this.footLayer  =this.add.graphics()" in v)
print("RANGE=52:", "RANGE=52" in v)
print("push tween:", "Cubic.easeOut" in v)
print("resist mechanic:", "撐住了" in v)
print("foot shadow:", "footLayer.fillEllipse" in v)
print("endGame clear:", "this.footLayer.clear()" in v)
