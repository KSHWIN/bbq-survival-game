# -*- coding: utf-8 -*-
# Patch 24: 移除接觸加熱 / 飛撲推力加強
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. 移除接觸加熱（AI 靠近就燙你）──────────────────────────────────────
old = "      // 接觸玩家加速熟化（敵人「燙到」你）\n      if(edist<38) this.heat=Math.min(100,this.heat+10*dt);\n"
new = ""
if old in html: html=html.replace(old,new); print("remove contact heat: OK")
else: print("FAIL remove contact heat")

# ── 2. 飛撲推力加強：FORCE 60→140，偵測半徑 28→38，加震屏 + 閃光 ────────
old = (
    "      this.enemies.forEach((e,i)=>{\n"
    "        if(!e.alive||dHit)return;\n"
    "        if(Math.hypot(this.p.x-e.x,this.p.y-e.y)<28){\n"
    "          dHit=true;\n"
    "          const resist=(e.heat||0)<50?0.5:1.0;\n"
    "          if(resist<1)this.showPop('💪 撐住了！');\n"
    "          this.tweens.add({targets:e,\n"
    "            x:e.x+mx*this.dashState.force*resist,\n"
    "            y:e.y+my*this.dashState.force*resist,\n"
    "            duration:180,ease:'Cubic.easeOut',\n"
    "            onComplete:()=>this.checkEnemyFall(e,i)});\n"
    "          const bx=this.p.x-mx*14,by=this.p.y-my*14;\n"
    "          if(inGrill(bx,by)){this.p.x=bx;this.p.y=by;}\n"
    "          this.dashState.active=false;\n"
    "        }\n"
    "      });"
)
new = (
    "      this.enemies.forEach((e,i)=>{\n"
    "        if(!e.alive||dHit)return;\n"
    "        if(Math.hypot(this.p.x-e.x,this.p.y-e.y)<38){\n"
    "          dHit=true;\n"
    "          const resist=(e.heat||0)<50?0.65:1.0;\n"
    "          if(resist<1)this.showPop('💪 撐住了！');\n"
    "          else this.showPop('💥 撞飛！');\n"
    "          this.tweens.add({targets:e,\n"
    "            x:e.x+mx*this.dashState.force*resist,\n"
    "            y:e.y+my*this.dashState.force*resist,\n"
    "            duration:260,ease:'Cubic.easeOut',\n"
    "            onComplete:()=>this.checkEnemyFall(e,i)});\n"
    "          // 震屏 + 閃光\n"
    "          this.cameras.main.shake(160,0.007);\n"
    "          const fx=this.add.graphics().setDepth(25);\n"
    "          const fobj={v:0};\n"
    "          this.tweens.add({targets:fobj,v:1,duration:220,ease:'Quad.easeOut',\n"
    "            onUpdate:()=>{fx.clear();const p=fobj.v;fx.lineStyle(5*(1-p),0xffffff,1-p);fx.strokeCircle(e.x,e.y,50*p);},\n"
    "            onComplete:()=>fx.destroy()});\n"
    "          const bx=this.p.x-mx*18,by=this.p.y-my*18;\n"
    "          if(inGrill(bx,by)){this.p.x=bx;this.p.y=by;}\n"
    "          this.dashState.active=false;\n"
    "        }\n"
    "      });"
)
if old in html: html=html.replace(old,new); print("dash push stronger: OK")
else: print("FAIL dash push")

# ── 3. FORCE 60 → 140 ──────────────────────────────────────────────────────
old = "    const DIST=Math.round(58*spd)*boost;   // 快→遠\n    const FORCE=Math.round(60*wgt)*boost;  // 重→強"
new = "    const DIST=Math.round(70*spd)*boost;   // 快→遠\n    const FORCE=Math.round(140*wgt)*boost; // 重→強"
if old in html: html=html.replace(old,new); print("FORCE 140: OK")
else: print("FAIL FORCE")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
print("no contact heat:", "edist<38) this.heat" not in v)
print("hit radius 38:", "Math.hypot(this.p.x-e.x,this.p.y-e.y)<38" in v)
print("FORCE 140:", "Math.round(140*wgt)" in v)
print("shake on hit:", "cameras.main.shake(160" in v)
