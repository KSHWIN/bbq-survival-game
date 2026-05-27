# -*- coding: utf-8 -*-
# Patch 19: 移除WASD還原方向鍵 + 縮小火焰 + 選角技能小動畫預覽
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. 移除 WASD，恢復純方向鍵 ───────────────────────────────────────────
old = (
    "    this.input.keyboard.addCapture([37,38,39,40,32,83,82,27,65,68,87]); // 含WAD\n"
    "    this.keys=this.input.keyboard.addKeys({\n"
    "      up:Phaser.Input.Keyboard.KeyCodes.UP,\n"
    "      down:Phaser.Input.Keyboard.KeyCodes.DOWN,\n"
    "      left:Phaser.Input.Keyboard.KeyCodes.LEFT,\n"
    "      right:Phaser.Input.Keyboard.KeyCodes.RIGHT,\n"
    "      up2:Phaser.Input.Keyboard.KeyCodes.W,\n"
    "      left2:Phaser.Input.Keyboard.KeyCodes.A,\n"
    "      right2:Phaser.Input.Keyboard.KeyCodes.D,\n"
    "      push:Phaser.Input.Keyboard.KeyCodes.S,\n"
    "      skill:Phaser.Input.Keyboard.KeyCodes.SPACE,\n"
    "      restart:Phaser.Input.Keyboard.KeyCodes.R,\n"
    "      back:Phaser.Input.Keyboard.KeyCodes.ESC,\n"
    "    });"
)
new = (
    "    this.input.keyboard.addCapture([37,38,39,40,32,83,82,27]);\n"
    "    this.keys=this.input.keyboard.addKeys({\n"
    "      up:Phaser.Input.Keyboard.KeyCodes.UP,\n"
    "      down:Phaser.Input.Keyboard.KeyCodes.DOWN,\n"
    "      left:Phaser.Input.Keyboard.KeyCodes.LEFT,\n"
    "      right:Phaser.Input.Keyboard.KeyCodes.RIGHT,\n"
    "      push:Phaser.Input.Keyboard.KeyCodes.S,\n"
    "      skill:Phaser.Input.Keyboard.KeyCodes.SPACE,\n"
    "      restart:Phaser.Input.Keyboard.KeyCodes.R,\n"
    "      back:Phaser.Input.Keyboard.KeyCodes.ESC,\n"
    "    });"
)
if old in html: html=html.replace(old,new); print("remove WASD keys: OK")
else: print("FAIL remove WASD")

# ── 2. 移動判斷移除 left2/right2/up2 ─────────────────────────────────────
old = (
    "    if(this.keys.left.isDown||this.keys.left2.isDown)   mx=-1;\n"
    "    if(this.keys.right.isDown||this.keys.right2.isDown) mx=1;\n"
    "    if(this.keys.up.isDown||this.keys.up2.isDown)       my=-1;\n"
    "    if(this.keys.down.isDown)                           my=1;"
)
new = (
    "    if(this.keys.left.isDown)  mx=-1;\n"
    "    if(this.keys.right.isDown) mx=1;\n"
    "    if(this.keys.up.isDown)    my=-1;\n"
    "    if(this.keys.down.isDown)  my=1;"
)
if old in html: html=html.replace(old,new); print("movement arrow-only: OK")
else: print("FAIL movement")

# ── 3. lastDir 移除 left2/right2/up2 ─────────────────────────────────────
old = (
    "    const kx=(this.keys.left.isDown||this.keys.left2.isDown?-1:this.keys.right.isDown||this.keys.right2.isDown?1:0);\n"
    "    const ky=(this.keys.up.isDown||this.keys.up2.isDown?-1:this.keys.down.isDown?1:0);"
)
new = (
    "    const kx=(this.keys.left.isDown?-1:this.keys.right.isDown?1:0);\n"
    "    const ky=(this.keys.up.isDown?-1:this.keys.down.isDown?1:0);"
)
if old in html: html=html.replace(old,new); print("lastDir arrow-only: OK")
else: print("FAIL lastDir")

# ── 4. 縮小火焰：FIRE_R_BASE 58 → 30 ─────────────────────────────────────
old = "    this.FIRE_R_BASE=58; this.FIRE_R_AMP=4;"
new = "    this.FIRE_R_BASE=30; this.FIRE_R_AMP=3;"
if old in html: html=html.replace(old,new); print("fire size 30: OK")
else: print("FAIL fire size")

# ── 5. 選角畫面：替換底部 detail bar 為帶動畫的技能預覽面板 ──────────────
old = (
    "    // ── Detail bar ───────────────────────────────────────\n"
    "    this.add.rectangle(W/2,H-18,W-20,24,0x0a0600,0.9).setStrokeStyle(1,0x664422).setDepth(-1);\n"
    "    this.detailTxt=this.add.text(W/2,H-18,'',{fontSize:'11px',color:'#ffcc88',fontFamily:'sans-serif',align:'center'}).setOrigin(0.5);"
)
new = (
    "    // ── Detail bar（技能預覽面板）─────────────────────────\n"
    "    this.add.rectangle(W/2,H-44,W-20,82,0x060400,0.94).setStrokeStyle(1,0x885522).setDepth(10);\n"
    "    // 左側：動畫區 90×70\n"
    "    this.prevG=this.add.graphics().setDepth(12);\n"
    "    this.previewKey=''; this.previewPhase=0;\n"
    "    // 右側：文字\n"
    "    this.abilNameTxt=this.add.text(110,H-72,'',{fontSize:'13px',color:'#ffaa44',fontFamily:'sans-serif',fontStyle:'bold'}).setDepth(12);\n"
    "    this.abilDescTxt=this.add.text(110,H-55,'',{fontSize:'10px',color:'#aaccff',fontFamily:'sans-serif',wordWrap:{width:560}}).setDepth(12);\n"
    "    this.detailTxt  =this.add.text(110,H-24,'',{fontSize:'10px',color:'#887755',fontFamily:'sans-serif'}).setDepth(12);"
)
if old in html: html=html.replace(old,new); print("detail panel: OK")
else: print("FAIL detail panel")

# ── 6. _updateDetail 更新三行文字 ─────────────────────────────────────────
old = (
    "  _updateDetail(){\n"
    "    if(!this.detailTxt) return;\n"
    "    const c=CHARS[this.sel], lv=LEVELS[this.lvSel];\n"
    "    this.detailTxt.setText(c.name+'  ❆  '+c.ability+'：'+c.abilityDesc+'    |    關卡：'+lv.name+'（'+lv.sub+'）    |    Enter / 點擊開戰');\n"
    "  }"
)
new = (
    "  _updateDetail(){\n"
    "    if(!this.detailTxt) return;\n"
    "    const c=CHARS[this.sel], lv=LEVELS[this.lvSel];\n"
    "    this.abilNameTxt.setText('❆ '+c.name+'「'+c.ability+'」');\n"
    "    this.abilDescTxt.setText(c.abilityDesc);\n"
    "    this.detailTxt.setText('關卡：'+lv.name+'　'+lv.sub+'　│　Enter / 點擊開戰');\n"
    "    this.previewKey=c.key;\n"
    "  }"
)
if old in html: html=html.replace(old,new); print("_updateDetail 3-line: OK")
else: print("FAIL _updateDetail")

# ── 7. 加入 update() 推進動畫 + _drawAbilAnim() ───────────────────────────
old = "  startGame(){\n    this.scene.start('Game',{char:CHARS[this.sel], level:LEVELS[this.lvSel]});\n  }"
new = (
    "  update(t,dt){\n"
    "    this.previewPhase=(this.previewPhase||0)+dt*0.0018;\n"
    "    this._drawAbilAnim();\n"
    "  }\n"
    "\n"
    "  _drawAbilAnim(){\n"
    "    const g=this.prevG; if(!g) return;\n"
    "    g.clear();\n"
    "    const key=this.previewKey;\n"
    "    if(!key) return;\n"
    "    const COL={pork:0xff8800,beef:0x4488ff,mushroom:0xaa66dd,corn:0xddcc00,wing:0x00ccbb,\n"
    "               shrimp:0x4466ff,tofu:0xddaa00,bacon:0xcc4400,pepper:0x44bb44,saury:0x8899cc};\n"
    "    const col=COL[key]||0x888888;\n"
    "    const t=this.previewPhase;\n"
    "    const cx=55, cy=H-44;  // 動畫中心\n"
    "    // 背景框\n"
    "    g.fillStyle(0x000000,0.45); g.fillRect(8,H-84,90,76);\n"
    "    g.lineStyle(1,col,0.5); g.strokeRect(8,H-84,90,76);\n"
    "    g.fillStyle(col,0.9);\n"
    "    switch(key){\n"
    "      case 'pork':{\n"
    "        // 玩家衝刺→推開敵人\n"
    "        const px=cx-30+Math.min(t%1,0.55)*90;\n"
    "        const hit=t%1>0.55;\n"
    "        g.fillStyle(0xff8800,0.9); g.fillCircle(Math.min(px,cx+12),cy,9); // 自己\n"
    "        const ex=hit?cx+12+(t%1-0.55)*80:cx+18;\n"
    "        g.fillStyle(0xffccaa,0.9); g.fillCircle(Math.min(ex,cx+44),cy,8); // 敵人\n"
    "        // 衝刺軌跡\n"
    "        if(t%1<0.55){ g.lineStyle(2,0xff8800,0.4);\n"
    "          for(let i=1;i<=3;i++) g.fillStyle(0xff8800,0.15*i)&&g.fillCircle(px-i*10,cy,5); }\n"
    "        break;\n"
    "      }\n"
    "      case 'beef':{\n"
    "        // 護盾閃爍\n"
    "        const shieldA=0.4+0.5*Math.abs(Math.sin(t*Math.PI));\n"
    "        g.fillStyle(0x4488ff,0.9); g.fillCircle(cx,cy,9);\n"
    "        g.lineStyle(3,0x88bbff,shieldA); g.strokeCircle(cx,cy,18);\n"
    "        g.lineStyle(2,0xaaddff,shieldA*0.6); g.strokeCircle(cx,cy,24);\n"
    "        // 熱度指示 down\n"
    "        const barW=Math.max(0,28-t%2*14);\n"
    "        g.fillStyle(0xff4400,0.7); g.fillRect(cx-14,cy+16,28,5);\n"
    "        g.fillStyle(0x4488ff,0.9); g.fillRect(cx-14,cy+16,barW,5);\n"
    "        break;\n"
    "      }\n"
    "      case 'mushroom':{\n"
    "        // 縮小彈跳\n"
    "        const bt=t%1;\n"
    "        const bx=cx-28+bt*56, by=cy+Math.sin(bt*Math.PI)*-28;\n"
    "        const sc=0.6+0.4*(1-Math.abs(Math.sin(bt*Math.PI)));\n"
    "        g.fillStyle(0xaa66dd,0.9); g.fillEllipse(bx,by,16*sc,16);\n"
    "        g.fillStyle(0x663399,0.5); g.fillEllipse(bx,cy+14,14*sc,5);\n"
    "        break;\n"
    "      }\n"
    "      case 'corn':{\n"
    "        // 爆炸\n"
    "        const et=t%1.5;\n"
    "        if(et<0.5){\n"
    "          const pls=1+0.15*Math.sin(et*Math.PI*8);\n"
    "          g.fillStyle(0xddcc00,0.9); g.fillCircle(cx,cy,10*pls);\n"
    "          g.fillStyle(0xffee88,0.6); g.fillCircle(cx,cy,6*pls);\n"
    "        } else {\n"
    "          const ep=(et-0.5)/1.0;\n"
    "          for(let i=0;i<8;i++){\n"
    "            const a=i*Math.PI/4, r=ep*32;\n"
    "            g.fillStyle(0xffcc00,1-ep); g.fillCircle(cx+Math.cos(a)*r,cy+Math.sin(a)*r,5*(1-ep*0.6));\n"
    "          }\n"
    "        }\n"
    "        break;\n"
    "      }\n"
    "      case 'wing':{\n"
    "        // 弧線飛越障礙\n"
    "        const ft=t%1;\n"
    "        const fx=cx-32+ft*64, fy=cy-Math.sin(ft*Math.PI)*22;\n"
    "        // 障礙\n"
    "        g.fillStyle(0xff4400,0.7); g.fillRect(cx-4,cy-12,8,26);\n"
    "        g.fillStyle(0x00ccbb,0.9); g.fillCircle(fx,fy,9);\n"
    "        // 軌跡\n"
    "        g.lineStyle(1.5,0x00ccbb,0.4);\n"
    "        for(let i=1;i<=5;i++){\n"
    "          const pt2=(ft-i*0.06); if(pt2<0) break;\n"
    "          g.fillStyle(0x00ccbb,0.15); g.fillCircle(cx-32+pt2*64,cy-Math.sin(pt2*Math.PI)*22,4);\n"
    "        }\n"
    "        break;\n"
    "      }\n"
    "      case 'shrimp':{\n"
    "        // 弧線彈射\n"
    "        const st2=t%1;\n"
    "        const sx2=cx-28+st2*56, sy2=cy+Math.sin(st2*Math.PI)*-24-Math.sin(st2*Math.PI*2)*6;\n"
    "        g.fillStyle(0x4466ff,0.9); g.fillCircle(sx2,sy2,8);\n"
    "        for(let i=1;i<=4;i++){\n"
    "          const pt2=st2-i*0.07; if(pt2<0) break;\n"
    "          const tx2=cx-28+pt2*56, ty2=cy+Math.sin(pt2*Math.PI)*-24-Math.sin(pt2*Math.PI*2)*6;\n"
    "          g.fillStyle(0x4466ff,0.12*i); g.fillCircle(tx2,ty2,4);\n"
    "        }\n"
    "        break;\n"
    "      }\n"
    "      case 'tofu':{\n"
    "        // 吸收周圍熟度\n"
    "        g.fillStyle(0xeeeedd,0.9); g.fillRect(cx-9,cy-9,18,18);\n"
    "        for(let i=0;i<5;i++){\n"
    "          const a=i*Math.PI*2/5+t*2;\n"
    "          const r=22-t%1*14;\n"
    "          g.fillStyle(0xddaa00,0.8); g.fillCircle(cx+Math.cos(a)*r,cy+Math.sin(a)*r,4);\n"
    "        }\n"
    "        // 光圈\n"
    "        g.lineStyle(2,0xddaa00,0.3+0.2*Math.sin(t*4));\n"
    "        g.strokeCircle(cx,cy,16+Math.sin(t*3)*3);\n"
    "        break;\n"
    "      }\n"
    "      case 'bacon':{\n"
    "        // 旋轉甩飛\n"
    "        for(let i=0;i<6;i++){\n"
    "          const a=i*Math.PI/3+t*4;\n"
    "          g.fillStyle(0xcc4400,0.9); g.fillCircle(cx+Math.cos(a)*14,cy+Math.sin(a)*14,6);\n"
    "        }\n"
    "        // 被甩出的點\n"
    "        const flyR=14+t%0.8*20;\n"
    "        g.fillStyle(0xff8844,0.5); g.fillCircle(cx+Math.cos(t*4)*flyR,cy+Math.sin(t*4)*flyR,4);\n"
    "        g.fillStyle(0xcc4400,0.9); g.fillCircle(cx,cy,9);\n"
    "        break;\n"
    "      }\n"
    "      case 'pepper':{\n"
    "        // 噴辣氣\n"
    "        g.fillStyle(0x44cc44,0.9); g.fillCircle(cx-20,cy,9);\n"
    "        for(let i=0;i<7;i++){\n"
    "          const a=(i-3)*0.32;\n"
    "          const r=(t%0.8+0.1)*36;\n"
    "          g.fillStyle(0x88ff44,0.7-r/60);\n"
    "          g.fillCircle(cx-10+Math.cos(a)*r,cy+Math.sin(a)*r,3.5*(1-r/55));\n"
    "        }\n"
    "        break;\n"
    "      }\n"
    "      case 'saury':{\n"
    "        // 刀型衝刺\n"
    "        const dt2=t%1;\n"
    "        const sx3=cx-32+dt2*64;\n"
    "        // 長身衝刺體\n"
    "        g.fillStyle(0x8899cc,0.9);\n"
    "        g.fillRect(sx3-18,cy-4,36,8);\n"
    "        g.fillTriangle(sx3+18,cy,sx3+8,cy-7,sx3+8,cy+7);\n"
    "        // 軌跡\n"
    "        for(let i=1;i<=4;i++){ g.fillStyle(0x8899cc,0.12*i); g.fillRect(sx3-18-i*10,cy-3,8,6); }\n"
    "        // 沿路被撞開的敵人\n"
    "        if(dt2>0.4){\n"
    "          const ep=(dt2-0.4)*30;\n"
    "          g.fillStyle(0xffccaa,0.8); g.fillCircle(cx+ep-6,cy-ep,7);\n"
    "        }\n"
    "        break;\n"
    "      }\n"
    "    }\n"
    "  }\n"
    "\n"
    "  startGame(){\n"
    "    this.scene.start('Game',{char:CHARS[this.sel], level:LEVELS[this.lvSel]});\n"
    "  }"
)
if old in html: html=html.replace(old,new); print("ability anim update: OK")
else: print("FAIL ability anim")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
print("no WASD addCapture:", "65,68,87" not in v)
print("no left2 in movement:", "keys.left2" not in v)
print("fire R=30:", "FIRE_R_BASE=30" in v)
print("prevG panel:", "this.prevG=" in v)
print("previewPhase:", "this.previewPhase=" in v)
print("_drawAbilAnim:", "_drawAbilAnim()" in v)
print("update method:", "update(t,dt){" in v)
print("pork anim:", "case 'pork':" in v)
print("saury anim:", "case 'saury':" in v)
