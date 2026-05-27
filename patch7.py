# -*- coding: utf-8 -*-
# Patch 7: 翻面機制 + 敵人熟度條
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. Add tilt vars to create() init ────────────────────────────────────
old = (
    "    this.runPhase=0; this.bgmEvent=null;\n"
    "    const AC=window.AudioContext||window.webkitAudioContext;"
)
new = (
    "    this.runPhase=0; this.bgmEvent=null;\n"
    "    this.tilt=null; this.tiltTimer=14;\n"
    "    this.tiltInterval=()=>11+Math.random()*8;\n"
    "    const AC=window.AudioContext||window.webkitAudioContext;"
)
if old in html:
    html = html.replace(old, new); print("tilt init: OK")
else: print("FAIL tilt init")

# ── 2. Add hbLayer (enemy heat bar graphics layer) ───────────────────────
old = (
    "    this.fxLayer   =this.add.graphics();\n"
    "    // 餐廳背景"
)
new = (
    "    this.fxLayer   =this.add.graphics();\n"
    "    this.hbLayer   =this.add.graphics().setDepth(18);\n"
    "    // 餐廳背景"
)
if old in html:
    html = html.replace(old, new); print("hbLayer: OK")
else: print("FAIL hbLayer")

# ── 3. Add tiltTxt to UI ─────────────────────────────────────────────────
old = (
    "    this.effectTxt=this.add.text(W/2,H-16,'',ts(12,'#ffff88')).setOrigin(0.5).setDepth(35);\n"
    "\n"
    "    // 輸入（方向鍵移動，S 推擠）"
)
new = (
    "    this.effectTxt=this.add.text(W/2,H-16,'',ts(12,'#ffff88')).setOrigin(0.5).setDepth(35);\n"
    "    this.tiltTxt  =this.add.text(W/2,G.y+24,'',{fontSize:'24px',color:'#ffee00',fontFamily:'sans-serif',fontStyle:'bold',stroke:'#000000',strokeThickness:5}).setOrigin(0.5).setDepth(36).setVisible(false);\n"
    "\n"
    "    // 輸入（方向鍵移動，S 推擠）"
)
if old in html:
    html = html.replace(old, new); print("tiltTxt UI: OK")
else: print("FAIL tiltTxt UI")

# ── 4. endGame: reset tilt + camera ──────────────────────────────────────
old = (
    "  endGame(win){\n"
    "    this.alive=false;\n"
    "    if(this.bgmEvent){this.bgmEvent.remove();this.bgmEvent=null;}"
)
new = (
    "  endGame(win){\n"
    "    this.alive=false;\n"
    "    if(this.tilt){this.tilt=null;this.cameras.main.setRotation(0);}\n"
    "    if(this.tiltTxt) this.tiltTxt.setVisible(false);\n"
    "    if(this.bgmEvent){this.bgmEvent.remove();this.bgmEvent=null;}"
)
if old in html:
    html = html.replace(old, new); print("endGame tilt reset: OK")
else: print("FAIL endGame")

# ── 5. Movement: add tilt force to nx/ny ─────────────────────────────────
old = (
    "    if(mx&&my){mx*=0.707;my*=0.707;}\n"
    "    const nx=this.p.x+mx*SPD*dt, ny=this.p.y+my*SPD*dt;"
)
new = (
    "    if(mx&&my){mx*=0.707;my*=0.707;}\n"
    "    const tfx=this.tilt&&this.tilt.state==='active'?this.tilt.x*this.tilt.force:0;\n"
    "    const tfy=this.tilt&&this.tilt.state==='active'?this.tilt.y*this.tilt.force:0;\n"
    "    const nx=this.p.x+(mx*SPD+tfx)*dt, ny=this.p.y+(my*SPD+tfy)*dt;"
)
if old in html:
    html = html.replace(old, new); print("tilt force on player: OK")
else: print("FAIL movement tilt")

# ── 6. Add tilt system before AI section ─────────────────────────────────
old = "    // AI\n    this.enemies.forEach((e,i)=>{"
new = (
    "    // 翻面系統\n"
    "    this.tiltTimer-=dt;\n"
    "    if(this.tiltTimer<=0&&!this.tilt){\n"
    "      const DIRS=[\n"
    "        {x:0,y:1,lbl:'\\u2193 \\u5f80\\u4e0b\\u6ed1\\uff01',rot:0.035},\n"
    "        {x:0,y:-1,lbl:'\\u2191 \\u5f80\\u4e0a\\u6ed1\\uff01',rot:-0.035},\n"
    "        {x:1,y:0,lbl:'\\u2192 \\u5f80\\u53f3\\u6ed1\\uff01',rot:0.03},\n"
    "        {x:-1,y:0,lbl:'\\u2190 \\u5f80\\u5de6\\u6ed1\\uff01',rot:-0.03},\n"
    "      ];\n"
    "      const d=DIRS[Math.floor(Math.random()*DIRS.length)];\n"
    "      this.tilt={x:d.x,y:d.y,force:150,rot:d.rot,state:'warn',timer:2.2,lbl:d.lbl};\n"
    "      this.showPop('\\u26a0\\ufe0f \\u5ee1\\u5e2b\\u7ffb\\u9762\\uff01'+d.lbl);\n"
    "      this.cameras.main.shake(300,0.006);\n"
    "      this.tiltTimer=this.tiltInterval();\n"
    "    }\n"
    "    if(this.tilt){\n"
    "      this.tilt.timer-=dt;\n"
    "      if(this.tilt.state==='warn'){\n"
    "        const prog=1-this.tilt.timer/2.2;\n"
    "        this.cameras.main.setRotation(this.tilt.rot*prog);\n"
    "        this.tiltTxt.setText('\\u26a0 '+this.tilt.lbl+' ('+this.tilt.timer.toFixed(1)+'s)').setVisible(true);\n"
    "        if(this.tilt.timer<=0){\n"
    "          this.tilt.state='active'; this.tilt.timer=3.5;\n"
    "          this.cameras.main.shake(220,0.009);\n"
    "        }\n"
    "      } else {\n"
    "        this.cameras.main.setRotation(this.tilt.rot);\n"
    "        this.tiltTxt.setText(this.tilt.lbl+' '+this.tilt.timer.toFixed(1)+'s').setVisible(true);\n"
    "        if(this.tilt.timer<=0){\n"
    "          this.tilt=null;\n"
    "          this.cameras.main.setRotation(0);\n"
    "          this.tiltTxt.setVisible(false);\n"
    "        }\n"
    "      }\n"
    "    } else { this.tiltTxt.setVisible(false); }\n"
    "\n"
    "    // AI\n"
    "    this.enemies.forEach((e,i)=>{"
)
if "    // AI\n    this.enemies.forEach((e,i)=>{" in html:
    html = html.replace("    // AI\n    this.enemies.forEach((e,i)=>{", new); print("tilt system: OK")
else: print("FAIL tilt system")

# ── 7. Add tilt force to enemies + fall check ────────────────────────────
old = (
    "      e.x+=e.vx; e.y+=e.vy;\n"
    "      if(e.x<G.x+e.r||e.x>G.x+G.w-e.r) e.vx*=-1;\n"
    "      if(e.y<G.y+e.r||e.y>G.y+G.h-e.r) e.vy*=-1;"
)
new = (
    "      e.x+=e.vx; e.y+=e.vy;\n"
    "      if(e.x<G.x+e.r||e.x>G.x+G.w-e.r) e.vx*=-1;\n"
    "      if(e.y<G.y+e.r||e.y>G.y+G.h-e.r) e.vy*=-1;\n"
    "      if(this.tilt&&this.tilt.state==='active'){\n"
    "        e.x+=this.tilt.x*this.tilt.force*dt;\n"
    "        e.y+=this.tilt.y*this.tilt.force*dt;\n"
    "        if(!inGrill(e.x,e.y)&&e.alive) this.checkEnemyFall(e,i);\n"
    "      }"
)
if old in html:
    html = html.replace(old, new); print("enemy tilt: OK")
else: print("FAIL enemy tilt")

# ── 8. Draw enemy heat bars after drawFires ───────────────────────────────
old = (
    "    // 繪製\n"
    "    this.firePhase+=dt*3;\n"
    "    this.drawFires(this.firePhase);\n"
    "\n"
    "    // UI"
)
new = (
    "    // 繪製\n"
    "    this.firePhase+=dt*3;\n"
    "    this.drawFires(this.firePhase);\n"
    "    // 敵人熟度條\n"
    "    this.hbLayer.clear();\n"
    "    this.enemies.forEach((e,i)=>{\n"
    "      if(!e.alive||!this.enemySprites[i]) return;\n"
    "      const BW=38,BH=5,bx=e.x-BW/2,by=e.y-34;\n"
    "      this.hbLayer.fillStyle(0x111111,0.85); this.hbLayer.fillRect(bx-1,by-1,BW+2,BH+2);\n"
    "      const ht=e.heat/100;\n"
    "      const hr=Math.min(255,Math.floor(510*ht)),hg=Math.min(255,Math.floor(510*(1-ht)));\n"
    "      this.hbLayer.fillStyle(Phaser.Display.Color.GetColor(hr,hg,0),1);\n"
    "      this.hbLayer.fillRect(bx,by,BW*ht,BH);\n"
    "      this.hbLayer.lineStyle(1,0xffffff,0.4); this.hbLayer.strokeRect(bx,by,BW,BH);\n"
    "    });\n"
    "\n"
    "    // UI"
)
if old in html:
    html = html.replace(old, new); print("enemy heat bars: OK")
else: print("FAIL heat bars")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
print("tiltTimer:", "this.tiltTimer=14" in v)
print("hbLayer:", "this.hbLayer" in v)
print("tiltTxt:", "this.tiltTxt" in v)
print("tilt force:", "this.tilt.force" in v)
print("camera rotate:", "setRotation(this.tilt.rot" in v)
print("enemy tilt:", "this.tilt.x*this.tilt.force" in v)
print("heat bars:", "BW=38,BH=5" in v)
print("endGame reset:", "this.cameras.main.setRotation(0)" in v)
