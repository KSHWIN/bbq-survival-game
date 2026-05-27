# -*- coding: utf-8 -*-
# Patch 18: 多邊形實體火焰 + 動態出現/消失循環（cooldown→warning→active→dying）
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. 火焰初始化：改成四狀態，分散初始狀態讓火焰不會全部同時出現 ──────────
old = (
    "    // 火焰：各自獨立振盪 + 會移動到新位置\n"
    "    const rndPos=()=>({ x:G.x+70+Math.random()*(G.w-140), y:G.y+70+Math.random()*(G.h-140) });\n"
    "    this.firePts=Array.from({length:this.levelData.fireCnt},(_,i)=>{\n"
    "      const p=rndPos();\n"
    "      return { x:p.x,y:p.y, tx:p.x,ty:p.y, state:'active', timer:0.8+i*0.5, r:40, spd:2.2+Math.random()*1.8, ph:Math.random()*Math.PI*2 };\n"
    "    });\n"
    "    this.FIRE_R_BASE=60; this.FIRE_R_AMP=4;  // 範圍擴大，振幅縮小（固定大小）"
)
new = (
    "    // 火焰：動態出現/消失循環（cooldown→warning→active→dying→cooldown）\n"
    "    const rndPos=()=>({ x:G.x+80+Math.random()*(G.w-160), y:G.y+80+Math.random()*(G.h-160) });\n"
    "    this.firePts=Array.from({length:this.levelData.fireCnt},(_,i)=>{\n"
    "      const p=rndPos();\n"
    "      // 分散初始狀態：約 60% active，20% cooldown，20% warning\n"
    "      const r=Math.random();\n"
    "      const st=r<0.6?'active':r<0.8?'warning':'cooldown';\n"
    "      const tm=st==='active'?1.0+Math.random()*2.5\n"
    "              :st==='warning'?0.3+Math.random()*0.8\n"
    "              :0.8+Math.random()*2.0;\n"
    "      return { x:p.x,y:p.y, tx:p.x,ty:p.y, state:st, timer:tm,\n"
    "               alpha:st==='active'?1.0:0.0,\n"
    "               r:40, spd:2.2+Math.random()*1.8, ph:Math.random()*Math.PI*2 };\n"
    "    });\n"
    "    this.FIRE_R_BASE=58; this.FIRE_R_AMP=4;"
)
if old in html: html=html.replace(old,new); print("fire init 4-state: OK")
else: print("FAIL fire init")

# ── 2. 火焰狀態機更新：完整四狀態循環 ───────────────────────────────────────
old = (
    "    // 火焰移動\n"
    "    this.firePts.forEach(f=>{\n"
    "      f.timer-=dt;\n"
    "      if(f.state==='active'&&f.timer<=0){\n"
    "        f.state='warning'; f.timer=1.0;\n"
    "        f.tx=G.x+70+Math.random()*(G.w-140);\n"
    "        f.ty=G.y+70+Math.random()*(G.h-140);\n"
    "      } else if(f.state==='warning'&&f.timer<=0){\n"
    "        f.x=f.tx; f.y=f.ty; f.state='active'; f.timer=1.4+Math.random()*1.4;\n"
    "      }\n"
    "    });"
)
new = (
    "    // 火焰狀態機：cooldown → warning → active → dying → cooldown\n"
    "    this.firePts.forEach(f=>{\n"
    "      f.timer-=dt;\n"
    "      if(f.state==='active'){\n"
    "        f.alpha=Math.min(1.0,(f.alpha||0)+dt*4); // 快速淡入\n"
    "        if(f.timer<=0){ f.state='dying'; f.timer=0.50; }\n"
    "      } else if(f.state==='dying'){\n"
    "        f.alpha=Math.max(0,(f.alpha||0)-dt/0.50); // 0.5s 淡出\n"
    "        if(f.timer<=0){ f.state='cooldown'; f.timer=1.2+Math.random()*2.5; f.alpha=0; }\n"
    "      } else if(f.state==='cooldown'){\n"
    "        if(f.timer<=0){\n"
    "          f.tx=G.x+80+Math.random()*(G.w-160);\n"
    "          f.ty=G.y+80+Math.random()*(G.h-160);\n"
    "          f.state='warning'; f.timer=0.7+Math.random()*0.6;\n"
    "        }\n"
    "      } else if(f.state==='warning'){\n"
    "        if(f.timer<=0){\n"
    "          f.x=f.tx; f.y=f.ty; f.state='active';\n"
    "          f.timer=2.0+Math.random()*2.5; // 燃燒 2-4.5s\n"
    "          f.alpha=0.05;\n"
    "        }\n"
    "      }\n"
    "    });"
)
if old in html: html=html.replace(old,new); print("fire state machine: OK")
else: print("FAIL fire state machine")

# ── 3. 完全重寫 drawFires：_flamePoly 多邊形 + 動態 alpha ─────────────────
old = (
    "  drawFires(phase){\n"
    "    const g=this.fireLayer; g.clear();\n"
    "    this.firePts.forEach(f=>{\n"
    "      // 預警位置（淡黃閃爍）\n"
    "      if(f.state==='warning'){\n"
    "        // 預警：穩定淡色光圈（比活躍時淺，讓玩家有時間反應）\n"
    "        const wc=(this.levelData&&this.levelData.fireC1)||0xff4400;\n"
    "        g.fillStyle(wc,0.14); g.fillEllipse(f.tx,f.ty,this.FIRE_R_BASE*1.9,this.FIRE_R_BASE*2.3);\n"
    "        g.lineStyle(2,wc,0.50); g.strokeEllipse(f.tx,f.ty,this.FIRE_R_BASE*1.9,this.FIRE_R_BASE*2.3);\n"
    "        // 細十字標記讓玩家知道位置\n"
    "        g.lineStyle(1,0xffffff,0.45);\n"
    "        g.lineBetween(f.tx-12,f.ty,f.tx+12,f.ty);\n"
    "        g.lineBetween(f.tx,f.ty-12,f.tx,f.ty+12);\n"
    "      }\n"
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
    "    });\n"
    "  }"
)
new = (
    "  // 產生火焰輪廓多邊形（寬底尖頂，含搖擺）\n"
    "  _flamePoly(cx,cy,R,sway,sc){\n"
    "    const s=sc||1;\n"
    "    return [\n"
    "      {x:cx,                       y:cy+R*0.10*s},\n"
    "      {x:cx+R*0.72*s,              y:cy-R*0.15*s},\n"
    "      {x:cx+R*0.60*s,              y:cy-R*0.68*s},\n"
    "      {x:cx+R*0.28*s+sway*0.55,   y:cy-R*1.15*s},\n"
    "      {x:cx+sway,                  y:cy-R*1.72*s},\n"
    "      {x:cx-R*0.28*s+sway*0.55,   y:cy-R*1.15*s},\n"
    "      {x:cx-R*0.60*s,              y:cy-R*0.68*s},\n"
    "      {x:cx-R*0.72*s,              y:cy-R*0.15*s},\n"
    "    ];\n"
    "  }\n"
    "\n"
    "  drawFires(phase){\n"
    "    const g=this.fireLayer; g.clear();\n"
    "    this.firePts.forEach(f=>{\n"
    "      const fc1=(this.levelData&&this.levelData.fireC1)||0xff4400;\n"
    "      const fc2=(this.levelData&&this.levelData.fireC2)||0xff9900;\n"
    "      // 預警：地面隱約微光（讓玩家知道即將在哪裡出現）\n"
    "      if(f.state==='warning'){\n"
    "        const pulse=0.10+0.06*Math.sin(phase*7);\n"
    "        g.fillStyle(fc1,pulse);\n"
    "        g.fillEllipse(f.tx,f.ty,this.FIRE_R_BASE*2.1,this.FIRE_R_BASE*0.52);\n"
    "        g.lineStyle(1,fc2,pulse*2.8);\n"
    "        g.strokeEllipse(f.tx,f.ty,this.FIRE_R_BASE*2.1,this.FIRE_R_BASE*0.52);\n"
    "      }\n"
    "      // 只有 active / dying 才畫火焰本體\n"
    "      if(f.state!=='active'&&f.state!=='dying') return;\n"
    "      const alpha=f.alpha||0;\n"
    "      if(alpha<0.01) return;\n"
    "      f.r=this.FIRE_R_BASE;\n"
    "      const R=f.r;\n"
    "      const sway =Math.sin(phase*f.spd       +f.ph      )*R*0.14;\n"
    "      const sway2=Math.sin(phase*f.spd*1.55  +f.ph+2.0  )*R*0.08;\n"
    "      // ① 地面炭火底光（扁橢圓）\n"
    "      g.fillStyle(0x0c0000,0.85*alpha);\n"
    "      g.fillEllipse(f.x,f.y+R*0.12,R*2.2,R*0.55);\n"
    "      // ② 外層主火焰（fc1，最大多邊形輪廓）\n"
    "      g.fillStyle(fc1,0.90*alpha);\n"
    "      g.fillPoints(this._flamePoly(f.x,f.y,R,sway,1.0),true);\n"
    "      // ③ 側舌（左偏，相位偏移，增加不規則感）\n"
    "      g.fillStyle(fc1,0.55*alpha);\n"
    "      g.fillPoints(this._flamePoly(f.x-R*0.28,f.y+R*0.06,R,sway2,0.68),true);\n"
    "      // ④ 亮內核（fc2，比外層更亮更小）\n"
    "      g.fillStyle(fc2,0.92*alpha);\n"
    "      g.fillPoints(this._flamePoly(f.x,f.y,R,sway*0.35,0.58),true);\n"
    "      // ⑤ 白熱底核（最亮，靠近底部）\n"
    "      g.fillStyle(0xffffff,0.60*alpha);\n"
    "      g.fillEllipse(f.x,f.y-R*0.08,R*0.58,R*0.36);\n"
    "      g.fillStyle(0xffffcc,0.38*alpha);\n"
    "      g.fillEllipse(f.x,f.y-R*0.28,R*0.32,R*0.26);\n"
    "    });\n"
    "  }"
)
if old in html: html=html.replace(old,new); print("drawFires polygon: OK")
else: print("FAIL drawFires polygon")

# ── 4. onFire：dying 狀態仍有傷害（alpha>0.3），cooldown/warning 無傷 ──────
old = "    return this.firePts.some(f=>f.state==='active'&&Math.hypot(x-f.x,y-f.y)<(f.r||this.FIRE_R_BASE)+8);"
new = "    return this.firePts.some(f=>(f.state==='active'||f.state==='dying')&&(f.alpha||0)>0.25&&Math.hypot(x-f.x,y-f.y)<(f.r||this.FIRE_R_BASE)*0.88);"
if old in html: html=html.replace(old,new); print("onFire states: OK")
else: print("FAIL onFire states")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
print("fire init 4-state:", "state:st, timer:tm" in v)
print("dying state:", "f.state==='dying'" in v)
print("cooldown timer:", "f.timer=1.2+Math.random()*2.5" in v)
print("warning→active:", "f.timer=2.0+Math.random()*2.5" in v)
print("_flamePoly method:", "_flamePoly(cx,cy,R,sway,sc)" in v)
print("fillPoints outer:", "fillPoints(this._flamePoly(f.x,f.y,R,sway,1.0),true)" in v)
print("fillPoints inner:", "fillPoints(this._flamePoly(f.x,f.y,R,sway*0.35,0.58),true)" in v)
print("onFire dying:", "(f.alpha||0)>0.25" in v)
