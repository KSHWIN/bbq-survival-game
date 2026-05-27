# -*- coding: utf-8 -*-
# Patch 22: 側面貼圖加寬 + 衝刺視覺動畫（拉伸 + 殘影軌跡）
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. 側面貼圖寬度：38% → 52%（更能分辨左右）──────────────────────────────
old = (
    "      cs.width=Math.ceil(W*0.38);cs.height=H;\n"
    "      cs.getContext('2d').drawImage(src,0,0,cs.width,H);\n"
    "      this.textures.addCanvas(key+'_s',cs);"
)
new = (
    "      cs.width=Math.ceil(W*0.52);cs.height=H;\n"
    "      cs.getContext('2d').drawImage(src,0,0,cs.width,H);\n"
    "      this.textures.addCanvas(key+'_s',cs);"
)
if old in html: html=html.replace(old,new); print("side texture 52%: OK")
else: print("FAIL side texture")

# ── 2. create() 加入 dashTrail 初始化 ────────────────────────────────────────
old = "    this.lastDir={x:1,y:0}; this.firePhase=0; this.pushWas=false; this.wobbleTween=null; this.dashState=null;"
new = "    this.lastDir={x:1,y:0}; this.firePhase=0; this.pushWas=false; this.wobbleTween=null; this.dashState=null; this.dashTrail=[];"
if old in html: html=html.replace(old,new); print("dashTrail init: OK")
else: print("FAIL dashTrail init")

# ── 3. create() 加入殘影 Graphics 圖層（depth 9，玩家 depth 10 之下）──────────
old = (
    "    this.grillLayer=this.add.graphics();\n"
    "    this.fireLayer =this.add.graphics();"
)
new = (
    "    this.trailLayer=this.add.graphics().setDepth(9);\n"
    "    this.grillLayer=this.add.graphics();\n"
    "    this.fireLayer =this.add.graphics();"
)
if old in html: html=html.replace(old,new); print("trailLayer: OK")
else: print("FAIL trailLayer")

# ── 4. 衝刺視覺動畫：替換整個 sprite animation 區塊 ─────────────────────────
old = (
    "    if(isMoving) this.runPhase+=dt*13;\n"
    "    if(this.playerSprite){\n"
    "      if(!this.wobbleTween){\n"
    "        const BS=0.16;\n"
    "        if(isMoving){\n"
    "          const c=Math.sin(this.runPhase);\n"
    "          const dirScaleY=1+this.lastDir.y*0.05; // 上小下大（景深感）\n"
    "          const sqX=1-Math.abs(c)*0.08; // 水平擠壓\n"
    "          const sqY=1+Math.abs(c)*0.07; // 垂直拉伸\n"
    "          this.playerSprite.setScale(BS*sqX*dirScaleY, BS*sqY*dirScaleY);\n"
    "          this.playerSprite.setFlipX(this.lastDir.x<-0.1);\n"
    "          this.playerSprite.setAngle(this.lastDir.x*11 - this.lastDir.y*4);\n"
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
    "        }\n"
    "      } else {\n"
    "        this.playerSprite.setPosition(this.p.x, this.p.y);\n"
    "      }\n"
    "    }"
)
new = (
    "    if(isMoving) this.runPhase+=dt*13;\n"
    "    // 衝刺殘影軌跡\n"
    "    if(isDash){ this.dashTrail.push({x:this.p.x,y:this.p.y}); if(this.dashTrail.length>6)this.dashTrail.shift(); }\n"
    "    else { if(this.dashTrail.length>0)this.dashTrail=[]; }\n"
    "    if(this.trailLayer){\n"
    "      this.trailLayer.clear();\n"
    "      if(this.dashTrail.length>0){\n"
    "        const col=this.charData?this.charData.color:0xffffff;\n"
    "        this.dashTrail.forEach((pt,i)=>{\n"
    "          const a=(i+1)/this.dashTrail.length*0.50;\n"
    "          this.trailLayer.fillStyle(col,a);\n"
    "          this.trailLayer.fillEllipse(pt.x,pt.y+10,22,13);\n"
    "        });\n"
    "      }\n"
    "    }\n"
    "    if(this.playerSprite){\n"
    "      if(!this.wobbleTween){\n"
    "        const BS=0.16;\n"
    "        if(isDash&&this.dashState){\n"
    "          // 衝刺：沿衝方向拉伸，垂直壓扁，大角度傾斜（「扑」的視覺）\n"
    "          const ds=this.dashState;\n"
    "          const isH=Math.abs(ds.dx)>Math.abs(ds.dy);\n"
    "          this.playerSprite.setScale(isH?BS*1.55:BS*0.70, isH?BS*0.70:BS*1.45);\n"
    "          this.playerSprite.setFlipX(ds.dx<-0.1);\n"
    "          this.playerSprite.setAngle(ds.dx*30-ds.dy*20);\n"
    "          this.playerSprite.setPosition(this.p.x, this.p.y);\n"
    "        } else if(isMoving){\n"
    "          const c=Math.sin(this.runPhase);\n"
    "          const dirScaleY=1+this.lastDir.y*0.05; // 上小下大（景深感）\n"
    "          const sqX=1-Math.abs(c)*0.08; // 水平擠壓\n"
    "          const sqY=1+Math.abs(c)*0.07; // 垂直拉伸\n"
    "          this.playerSprite.setScale(BS*sqX*dirScaleY, BS*sqY*dirScaleY);\n"
    "          this.playerSprite.setFlipX(this.lastDir.x<-0.1);\n"
    "          this.playerSprite.setAngle(this.lastDir.x*11 - this.lastDir.y*4);\n"
    "          this.playerSprite.setPosition(this.p.x, this.p.y+c*5.5);\n"
    "        } else {\n"
    "          this.playerSprite.setScale(BS);\n"
    "          this.playerSprite.setAngle(this.lastDir.x*3);\n"
    "          this.playerSprite.setFlipX(this.lastDir.x<-0.1);\n"
    "          this.playerSprite.setPosition(this.p.x, this.p.y);\n"
    "        }\n"
    "        // 腳步陰影（衝刺中不顯示，避免視覺干擾）\n"
    "        if(this.footLayer){\n"
    "          this.footLayer.clear();\n"
    "          if(isMoving&&!isDash){\n"
    "            const fc=Math.sin(this.runPhase);\n"
    "            const px=this.p.x, py=this.p.y;\n"
    "            const pvx=-this.lastDir.y*0.45, pvy=this.lastDir.x*0.45;\n"
    "            this.footLayer.fillStyle(0x1a0e06,0.55);\n"
    "            this.footLayer.fillEllipse(px+pvx*11+this.lastDir.x*5,py+pvy*11+this.lastDir.y*5+16+fc*5,8,4);\n"
    "            this.footLayer.fillStyle(0x1a0e06,0.4);\n"
    "            this.footLayer.fillEllipse(px-pvx*11+this.lastDir.x*5,py-pvy*11+this.lastDir.y*5+16-fc*5,8,4);\n"
    "          }\n"
    "        }\n"
    "      } else {\n"
    "        this.playerSprite.setPosition(this.p.x, this.p.y);\n"
    "      }\n"
    "    }"
)
if old in html: html=html.replace(old,new); print("dash animation: OK")
else: print("FAIL dash animation")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
print("side 52%:", "W*0.52" in v)
print("dashTrail init:", "this.dashTrail=[]" in v)
print("trailLayer:", "this.trailLayer=this.add.graphics" in v)
print("dash lunge anim:", "isDash&&this.dashState" in v and "BS*1.55" in v)
print("trail render:", "dashTrail.forEach" in v)
print("no 38%:", "W*0.38" not in v)
