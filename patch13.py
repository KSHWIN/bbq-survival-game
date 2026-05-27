# -*- coding: utf-8 -*-
# Patch 13: 四方向貼圖 + 衝撞取代推 + 移除白線
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. 加入 _buildDir(key) 方法（緊接在 _rmWhite 之後）─────────────────
old = (
    "    this.textures.remove(key);\n"
    "    this.textures.addCanvas(key,cv);\n"
    "  }"
)
new = (
    "    this.textures.remove(key);\n"
    "    this.textures.addCanvas(key,cv);\n"
    "  }\n"
    "\n"
    "  _buildDir(key){\n"
    "    if(!this.textures.exists(key))return;\n"
    "    const src=this.textures.get(key).getSourceImage();\n"
    "    const W=src.width,H=src.height;\n"
    "    // 側面：壓縮寬度至 55%，模擬側視圖\n"
    "    if(!this.textures.exists(key+'_s')){\n"
    "      const cs=document.createElement('canvas');\n"
    "      cs.width=Math.ceil(W*0.55);cs.height=H;\n"
    "      cs.getContext('2d').drawImage(src,0,0,cs.width,H);\n"
    "      this.textures.addCanvas(key+'_s',cs);\n"
    "    }\n"
    "    // 背面：水平翻轉 + 加深（模擬看到背部）\n"
    "    if(!this.textures.exists(key+'_b')){\n"
    "      const cb=document.createElement('canvas');\n"
    "      cb.width=W;cb.height=H;\n"
    "      const ctxb=cb.getContext('2d');\n"
    "      ctxb.translate(W,0);ctxb.scale(-1,1);\n"
    "      ctxb.drawImage(src,0,0);\n"
    "      ctxb.globalCompositeOperation='multiply';\n"
    "      ctxb.fillStyle='rgba(25,15,45,0.62)';\n"
    "      ctxb.fillRect(-W,0,W,H);\n"
    "      this.textures.addCanvas(key+'_b',cb);\n"
    "    }\n"
    "  }"
)
if old in html: html=html.replace(old,new,1); print("_buildDir method: OK")
else: print("FAIL _buildDir method")

# ── 2. onAdded：_rmWhite 後加 _buildDir ──────────────────────────────
old = "CHARS.forEach(ch=>this._rmWhite(ch.img)); this.scene.start('Select');"
new = "CHARS.forEach(ch=>this._rmWhite(ch.img)); CHARS.forEach(ch=>this._buildDir(ch.img)); this.scene.start('Select');"
if old in html: html=html.replace(old,new); print("onAdded buildDir: OK")
else: print("FAIL onAdded buildDir")

# ── 3. create() 加入 dashState 初始化 ────────────────────────────────
old = "this.lastDir={x:1,y:0}; this.firePhase=0; this.pushWas=false; this.wobbleTween=null;"
new = "this.lastDir={x:1,y:0}; this.firePhase=0; this.pushWas=false; this.wobbleTween=null; this.dashState=null;"
if old in html: html=html.replace(old,new); print("dashState init: OK")
else: print("FAIL dashState init")

# ── 4. 重寫 doPush() — 改用衝撞，移除白線 ────────────────────────────
old = (
    "    const c=this.charData, RANGE=52, base=c.key==='pork'?105:75, FORCE=base*(ae.garlic>0?2:1);\n"
    "    const dx=this.lastDir.x, dy=this.lastDir.y;\n"
    "    let hit=false;\n"
    "    // 玉米引爆\n"
    "    if(c.key==='corn'&&this.heat>=70){\n"
    "      this.showPop('💥 爆米花！');\n"
    "      this.enemies.forEach((e,i)=>{\n"
    "        if(!e.alive) return;\n"
    "        const d=Math.hypot(this.p.x-e.x,this.p.y-e.y);\n"
    "        if(d<150){ const nx=d>0?(e.x-this.p.x)/d:1, ny=d>0?(e.y-this.p.y)/d:0; e.x+=nx*120; e.y+=ny*120; this.checkEnemyFall(e,i); }\n"
    "      });\n"
    "      this.heat=Math.max(0,this.heat-28); return;\n"
    "    }\n"
    "    this.enemies.forEach((e,i)=>{\n"
    "      if(!e.alive) return;\n"
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
    "      }\n"
    "    });\n"
    "    if(!hit){ const nx=this.p.x+dx*24, ny=this.p.y+dy*24; if(inGrill(nx,ny)){this.p.x=nx;this.p.y=ny;} }\n"
    "    this.fxLayer.clear();\n"
    "    this.fxLayer.lineStyle(3,0xffffff,0.8);\n"
    "    this.fxLayer.lineBetween(this.p.x,this.p.y,this.p.x+dx*60,this.p.y+dy*60);\n"
    "    this.time.delayedCall(120,()=>this.fxLayer.clear());\n"
    "  }"
)
new = (
    "    const c=this.charData;\n"
    "    const boost=ae.garlic>0?1.35:1;\n"
    "    // 玉米爆炸（保留，改用 tween）\n"
    "    if(c.key==='corn'&&this.heat>=70){\n"
    "      this.showPop('💥 爆米花！');\n"
    "      this.enemies.forEach((e,i)=>{\n"
    "        if(!e.alive)return;\n"
    "        const d=Math.hypot(this.p.x-e.x,this.p.y-e.y);\n"
    "        if(d<150){const nx2=d>0?(e.x-this.p.x)/d:1,ny2=d>0?(e.y-this.p.y)/d:0;\n"
    "          this.tweens.add({targets:e,x:e.x+nx2*110,y:e.y+ny2*110,\n"
    "            duration:200,ease:'Cubic.easeOut',onComplete:()=>this.checkEnemyFall(e,i)});}\n"
    "      });\n"
    "      this.heat=Math.max(0,this.heat-28);return;\n"
    "    }\n"
    "    // 衝撞衝刺：玩家自己衝過去，碰到敵人才算撞\n"
    "    const DIST=(c.key==='pork'?80:64)*boost;\n"
    "    const FORCE=(c.key==='pork'?86:70)*boost;\n"
    "    this.dashState={active:true,dx:this.lastDir.x,dy:this.lastDir.y,\n"
    "      dist:0,maxDist:DIST,force:FORCE};\n"
    "  }"
)
if old in html: html=html.replace(old,new); print("doPush rewrite: OK")
else: print("FAIL doPush rewrite")

# ── 5. 移動區：加入 isDash 旗標，修改 SPD ────────────────────────────
old = "    // 移動（方向鍵）\n    const SPD=this.charData.speed*(this.activeEffects.slowpow>0?0.5:1);"
new = (
    "    // 移動（方向鍵）\n"
    "    const isDash=!!(this.dashState&&this.dashState.active);\n"
    "    const SPD=isDash?320:this.charData.speed*(this.activeEffects.slowpow>0?0.5:1);"
)
if old in html: html=html.replace(old,new); print("isDash + SPD: OK")
else: print("FAIL isDash + SPD")

# ── 6. 衝撞碰撞處理（在 if(mx&&my) 之後插入）──────────────────────────
old = "    if(mx&&my){mx*=0.707;my*=0.707;}"
new = (
    "    if(mx&&my){mx*=0.707;my*=0.707;}\n"
    "    // 衝撞：覆蓋鍵盤方向，移動並碰撞敵人\n"
    "    if(isDash){\n"
    "      mx=this.dashState.dx; my=this.dashState.dy;\n"
    "      this.dashState.dist+=320*dt;\n"
    "      let dHit=false;\n"
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
    "      });\n"
    "      if(this.dashState.dist>=this.dashState.maxDist)this.dashState.active=false;\n"
    "    }"
)
if old in html: html=html.replace(old,new); print("dash collision: OK")
else: print("FAIL dash collision")

# ── 7. 邊界檢查：衝撞時撞牆就停（不結束遊戲）────────────────────────────
old = (
    "    if(!inGrill(nx,ny)){this.subTxt.setText('掉落烤盤！');this.endGame(false);return;}\n"
    "    this.p.x=nx; this.p.y=ny;"
)
new = (
    "    if(!inGrill(nx,ny)){\n"
    "      if(isDash){this.dashState.active=false;}\n"
    "      else{this.subTxt.setText('掉落烤盤！');this.endGame(false);return;}\n"
    "    } else {this.p.x=nx;this.p.y=ny;}"
)
if old in html: html=html.replace(old,new); print("boundary dash: OK")
else: print("FAIL boundary dash")

# ── 8. 方向貼圖切換（isMoving 同時也算 dash 中為移動）──────────────────
old = "    const isMoving=!!(mx||my);"
new = (
    "    const isMoving=!!(mx||my)||isDash;\n"
    "    // 依方向切換貼圖\n"
    "    if(this.playerSprite&&this.charData){\n"
    "      const ld=this.lastDir;\n"
    "      let tKey=this.charData.key;\n"
    "      if(ld.y<-0.5&&Math.abs(ld.x)<0.7) tKey+='_b';            // 往上：背面\n"
    "      else if(Math.abs(ld.x)>Math.abs(ld.y)&&Math.abs(ld.x)>0.3) tKey+='_s'; // 左右：側面\n"
    "      if(this.textures.exists(tKey)&&this.playerSprite.texture.key!==tKey)\n"
    "        this.playerSprite.setTexture(tKey);\n"
    "    }"
)
if old in html: html=html.replace(old,new); print("dir texture switch: OK")
else: print("FAIL dir texture switch")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
print("_buildDir method:", "_buildDir(key){" in v)
print("buildDir call in onAdded:", "_buildDir(ch.img)" in v)
print("dashState init:", "this.dashState=null;" in v)
print("doPush dash:", "dashState={active:true" in v)
print("white line removed:", "lineStyle(3,0xffffff" not in v)
print("isDash flag:", "const isDash=" in v)
print("dash collision:", "dHit=false;" in v)
print("boundary dash:", "isDash){this.dashState.active=false;" in v)
print("dir texture:", "tKey+='_b'" in v)
print("side texture:", "tKey+='_s'" in v)
