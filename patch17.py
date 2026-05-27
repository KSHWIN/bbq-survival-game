# -*- coding: utf-8 -*-
# Patch 17: 鍵盤修正+WASD備援 / 三舌火焰 / 範圍擴大 / AI追擊 / 道具強化 / 道具壓力
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. CSS overflow:hidden + 全局方向鍵 preventDefault ────────────────────
old = "  <title>烤肉求生</title>\n  <script src="
new = (
    "  <title>烤肉求生</title>\n"
    "  <style>html,body{overflow:hidden;margin:0;padding:0;}</style>\n"
    "  <script>window.addEventListener('keydown',e=>{"
    "if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.key))"
    "e.preventDefault();},{passive:false});</script>\n"
    "  <script src="
)
if old in html: html=html.replace(old,new); print("CSS overflow + arrow preventDefault: OK")
else: print("FAIL CSS/arrow")

# ── 2. addKeys 加入 W/A/D 備援方向鍵 ──────────────────────────────────────
old = (
    "this.input.keyboard.addCapture([37,38,39,40,32,83,82,27]); // ←↑→↓ Space S R Esc\n"
    "    this.keys=this.input.keyboard.addKeys({\n"
    "      up:Phaser.Input.Keyboard.KeyCodes.UP,\n"
    "      down:Phaser.Input.Keyboard.KeyCodes.DOWN,\n"
    "      left:Phaser.Input.Keyboard.KeyCodes.LEFT,\n"
    "      right:Phaser.Input.Keyboard.KeyCodes.RIGHT,"
)
new = (
    "this.input.keyboard.addCapture([37,38,39,40,32,83,82,27,65,68,87]); // 含WAD\n"
    "    this.keys=this.input.keyboard.addKeys({\n"
    "      up:Phaser.Input.Keyboard.KeyCodes.UP,\n"
    "      down:Phaser.Input.Keyboard.KeyCodes.DOWN,\n"
    "      left:Phaser.Input.Keyboard.KeyCodes.LEFT,\n"
    "      right:Phaser.Input.Keyboard.KeyCodes.RIGHT,\n"
    "      up2:Phaser.Input.Keyboard.KeyCodes.W,\n"
    "      left2:Phaser.Input.Keyboard.KeyCodes.A,\n"
    "      right2:Phaser.Input.Keyboard.KeyCodes.D,"
)
if old in html: html=html.replace(old,new); print("addKeys W/A/D: OK")
else: print("FAIL addKeys")

# ── 3. 移動讀取加入 W/A/D ─────────────────────────────────────────────────
old = (
    "    let mx=0, my=0;\n"
    "    if(this.keys.left.isDown)  mx=-1;\n"
    "    if(this.keys.right.isDown) mx=1;\n"
    "    if(this.keys.up.isDown)    my=-1;\n"
    "    if(this.keys.down.isDown)  my=1;\n"
)
new = (
    "    let mx=0, my=0;\n"
    "    if(this.keys.left.isDown||this.keys.left2.isDown)   mx=-1;\n"
    "    if(this.keys.right.isDown||this.keys.right2.isDown) mx=1;\n"
    "    if(this.keys.up.isDown||this.keys.up2.isDown)       my=-1;\n"
    "    if(this.keys.down.isDown)                           my=1;\n"
)
if old in html: html=html.replace(old,new); print("movement W/A/D: OK")
else: print("FAIL movement keys")

# ── 4. lastDir 更新也用 W/A/D ─────────────────────────────────────────────
old = (
    "    const kx=(this.keys.left.isDown?-1:this.keys.right.isDown?1:0);\n"
    "    const ky=(this.keys.up.isDown?-1:this.keys.down.isDown?1:0);\n"
)
new = (
    "    const kx=(this.keys.left.isDown||this.keys.left2.isDown?-1:this.keys.right.isDown||this.keys.right2.isDown?1:0);\n"
    "    const ky=(this.keys.up.isDown||this.keys.up2.isDown?-1:this.keys.down.isDown?1:0);\n"
)
if old in html: html=html.replace(old,new); print("lastDir W/A/D: OK")
else: print("FAIL lastDir keys")

# ── 5. 火焰大小：FIRE_R_BASE 40 → 60 ─────────────────────────────────────
old = "this.FIRE_R_BASE=40; this.FIRE_R_AMP=18;"
new = "this.FIRE_R_BASE=60; this.FIRE_R_AMP=4;  // 範圍擴大，振幅縮小（固定大小）"
if old in html: html=html.replace(old,new); print("FIRE_R_BASE 40->60: OK")
else: print("FAIL FIRE_R_BASE")

# ── 6. 三舌焰重做（分離舌焰，真火感）─────────────────────────────────────
old = (
    "      // 活躍火焰\n"
    "      const alpha=f.state==='active'?1.0:0.45;\n"
    "      // 大小幾乎固定，只有極微小呼吸感（±5%）\n"
    "      const breathe=1+Math.sin(phase*f.spd+f.ph)*0.05;\n"
    "      f.r=this.FIRE_R_BASE*breathe;\n"
    "      const R=f.r;\n"
    "      const fw=R*0.72;           // 焰寬（比高窄）\n"
    "      const fh=R*1.75;           // 焰高（寬底窄頂的橢圓）\n"
    "      const cx=f.x, cy=f.y-R*0.18; // 整體往上移，模擬火焰升起\n"
    "      const fc1=(this.levelData&&this.levelData.fireC1)||0xff4400;\n"
    "      const fc2=(this.levelData&&this.levelData.fireC2)||0xff9900;\n"
    "      // ① 地面暗影（橢圓扁平，在火焰正下方）\n"
    "      g.fillStyle(0x000000,0.40*alpha); g.fillEllipse(cx,f.y+R*0.45,fw*2.1,R*0.45);\n"
    "      // ② 最外層暗暈（深色，模擬真火外緣燻黑感）\n"
    "      g.fillStyle(0x110000,0.55*alpha); g.fillEllipse(cx,cy,fw*1.7,fh*1.15);\n"
    "      // ③ 主體火焰（fc1，中深色）\n"
    "      g.fillStyle(fc1,0.90*alpha); g.fillEllipse(cx,cy,fw*1.1,fh);\n"
    "      // ④ 側搖舌（微量橫向偏移，增加不規則感）\n"
    "      const toff=Math.sin(phase*f.spd*1.8+f.ph+0.9)*fw*0.18;\n"
    "      g.fillStyle(fc2,0.65*alpha); g.fillEllipse(cx+toff,cy-R*0.18,fw*0.62,fh*0.72);\n"
    "      // ⑤ 亮核（fc2，較亮）\n"
    "      g.fillStyle(fc2,0.88*alpha); g.fillEllipse(cx,cy+R*0.10,fw*0.48,fh*0.45);\n"
    "      // ⑥ 中心白熱點（最亮）\n"
    "      g.fillStyle(0xffffff,0.55*alpha); g.fillEllipse(cx,cy+R*0.15,fw*0.22,fh*0.22);\n"
)
new = (
    "      // 活躍火焰 —— 三舌焰設計\n"
    "      const alpha=f.state==='active'?1.0:0.45;\n"
    "      f.r=this.FIRE_R_BASE;\n"
    "      const R=f.r;\n"
    "      const fc1=(this.levelData&&this.levelData.fireC1)||0xff4400;\n"
    "      const fc2=(this.levelData&&this.levelData.fireC2)||0xff9900;\n"
    "      // 底盤：炭火橙紅底光\n"
    "      g.fillStyle(0x1a0200,0.85*alpha); g.fillEllipse(f.x,f.y+R*0.12,R*2.2,R*0.70);\n"
    "      g.fillStyle(fc1,0.55*alpha);      g.fillEllipse(f.x,f.y,R*1.5,R*0.50);\n"
    "      // 三根火舌（左舌/中舌最高/右舌）\n"
    "      [\n"
    "        {ox:-R*0.40,hM:0.88,wM:0.48,ph2:0.0},\n"
    "        {ox: R*0.05,hM:1.30,wM:0.60,ph2:1.4},\n"
    "        {ox: R*0.42,hM:0.96,wM:0.45,ph2:2.6},\n"
    "      ].forEach(({ox,hM,wM,ph2})=>{\n"
    "        const sway=Math.sin(phase*f.spd+f.ph+ph2)*R*0.09;\n"
    "        const tx=f.x+ox+sway, H=R*hM*1.65, W=R*wM;\n"
    "        const tcy=f.y-H*0.38;\n"
    "        g.fillStyle(fc1,0.92*alpha); g.fillEllipse(tx,tcy,W,H);\n"
    "        g.fillStyle(fc2,0.82*alpha); g.fillEllipse(tx,tcy+H*0.06,W*0.58,H*0.68);\n"
    "        g.fillStyle(0xffffaa,0.52*alpha); g.fillEllipse(tx,tcy-H*0.25,W*0.26,H*0.24);\n"
    "      });\n"
)
if old in html: html=html.replace(old,new); print("three-tongue fire: OK")
else: print("FAIL fire tongues")

# ── 7. AI 追擊 + 接觸傷害 ────────────────────────────────────────────────
old = (
    "      e.x+=e.vx; e.y+=e.vy;\n"
    "      if(e.x<G.x+e.r||e.x>G.x+G.w-e.r) e.vx*=-1;\n"
    "      if(e.y<G.y+e.r||e.y>G.y+G.h-e.r) e.vy*=-1;\n"
)
new = (
    "      // AI 緩慢追蹤玩家\n"
    "      const edx=this.p.x-e.x, edy=this.p.y-e.y;\n"
    "      const edist=Math.hypot(edx,edy)||1;\n"
    "      if(edist>55){\n"
    "        e.vx+=(edx/edist)*0.18;\n"
    "        e.vy+=(edy/edist)*0.18;\n"
    "      }\n"
    "      // 速度上限\n"
    "      const espd=Math.hypot(e.vx,e.vy)||1;\n"
    "      if(espd>3.8){e.vx=(e.vx/espd)*3.8;e.vy=(e.vy/espd)*3.8;}\n"
    "      e.x+=e.vx; e.y+=e.vy;\n"
    "      if(e.x<G.x+e.r||e.x>G.x+G.w-e.r) e.vx*=-1;\n"
    "      if(e.y<G.y+e.r||e.y>G.y+G.h-e.r) e.vy*=-1;\n"
    "      // 接觸玩家加速熟化（敵人「燙到」你）\n"
    "      if(edist<38) this.heat=Math.min(100,this.heat+10*dt);\n"
)
if old in html: html=html.replace(old,new); print("AI pursuit+contact: OK")
else: print("FAIL AI")

# ── 8. 道具效果加強 ───────────────────────────────────────────────────────
old = (
    "    if(item.type==='ice')   {this.heat=Math.max(0,this.heat-25); this.showPop('❌ 冰塊！冷靜一下'); this.playSound('good');}\n"
    "    if(item.type==='foil')  {ae.foil=item.dur;    this.showPop('◎ 鋁箔紙！暫時险4秒'); this.playSound('good');}\n"
    "    if(item.type==='garlic'){ae.garlic=item.dur;  this.showPop('★ 大蒜！推力加倍！'); this.playSound('good');}\n"
)
new = (
    "    if(item.type==='ice')   {this.heat=Math.max(0,this.heat-42); this.showPop('❌ 冰塊！冷卻 -42%！'); this.playSound('good');}\n"
    "    if(item.type==='foil')  {ae.foil=item.dur+3;  this.showPop('◎ 鋁箔紙！隔熱 7 秒！'); this.playSound('good');}\n"
    "    if(item.type==='garlic'){ae.garlic=item.dur+2; this.showPop('★ 大蒜！推力 ×1.7！'); this.playSound('good');}\n"
)
if old in html: html=html.replace(old,new); print("items stronger: OK")
else: print("FAIL items")

# 大蒜 boost 也要改 (1.35→1.70)
old = "    const boost=ae.garlic>0?1.35:1;"
new = "    const boost=ae.garlic>0?1.70:1;"
if old in html: html=html.replace(old,new); print("garlic boost 1.35->1.70: OK")
else: print("FAIL garlic boost")

# ── 9. 道具有 25% 機率在火焰附近生成（強迫冒險）────────────────────────────
old = (
    "    const margin=60;\n"
    "    const x=G.x+margin+Math.random()*(G.w-margin*2);\n"
    "    const y=G.y+margin+Math.random()*(G.h-margin*2);\n"
)
new = (
    "    const margin=60;\n"
    "    let x,y;\n"
    "    // 25% 機率在火焰附近生成，強迫玩家冒險\n"
    "    const nearFire=Math.random()<0.25&&this.firePts&&this.firePts.length>0;\n"
    "    if(nearFire){\n"
    "      const fp=this.firePts[Math.floor(Math.random()*this.firePts.length)];\n"
    "      x=Phaser.Math.Clamp(fp.x+(Math.random()*90-45),G.x+margin,G.x+G.w-margin);\n"
    "      y=Phaser.Math.Clamp(fp.y+(Math.random()*90-45),G.y+margin,G.y+G.h-margin);\n"
    "    } else {\n"
    "      x=G.x+margin+Math.random()*(G.w-margin*2);\n"
    "      y=G.y+margin+Math.random()*(G.h-margin*2);\n"
    "    }\n"
)
if old in html: html=html.replace(old,new); print("items near fire 25%: OK")
else: print("FAIL item spawn")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
print("overflow:hidden:", "overflow:hidden" in v)
print("arrow preventDefault:", "ArrowUp','ArrowDown" in v)
print("W key:", "up2:Phaser.Input.Keyboard.KeyCodes.W" in v)
print("movement W/A/D:", "keys.up2.isDown" in v)
print("FIRE_R_BASE=60:", "this.FIRE_R_BASE=60;" in v)
print("three tongues:", "三舌焰" in v)
print("AI pursuit:", "AI 緩慢追蹤" in v)
print("contact damage:", "接觸玩家加速熟化" in v)
print("items stronger:", "冰塊！冷卻 -42" in v)
print("garlic 1.70:", "1.70" in v)
print("item near fire:", "強迫玩家冒險" in v)
