# -*- coding: utf-8 -*-
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. Fire count 5 → 8 (×1.5) ───────────────────────────────────────────
old = "this.firePts=[0,1,2,3,4].map((_,i)=>{"
new = "this.firePts=[0,1,2,3,4,5,6,7].map((_,i)=>{"
html = html.replace(old, new)
print("fire count:", "0,1,2,3,4,5,6,7" in html)

# ── 2. Add init vars in create() ─────────────────────────────────────────
old = (
    "    this.heat=0; this.alive=true; this.pushCD=0; this.timeLeft=60;\n"
    "    this.lastDir={x:1,y:0}; this.firePhase=0; this.pushWas=false; this.wobbleTween=null;\n"
    "    this.forkTimer=4; this.fork=null;"
)
new = (
    "    this.heat=0; this.alive=true; this.pushCD=0; this.timeLeft=60;\n"
    "    this.lastDir={x:1,y:0}; this.firePhase=0; this.pushWas=false; this.wobbleTween=null;\n"
    "    this.forkTimer=4; this.fork=null;\n"
    "    this.activeEffects={foil:0,garlic:0,sauce:0,slowpow:0};\n"
    "    this.mapItems=[]; this.itemTimer=3; this.sizzleTimer=0;\n"
    "    const AC=window.AudioContext||window.webkitAudioContext;\n"
    "    this.ac=AC?new AC():null;"
)
if old in html:
    html = html.replace(old, new)
    print("init vars: OK")
else:
    print("FAIL init vars")

# ── 3. Add effectTxt to UI ───────────────────────────────────────────────
old = (
    "    this.subTxt   =this.add.text(W/2,H/2+28,'',ts(20,'#ffaaaa')).setOrigin(0.5).setDepth(40);\n"
    "\n"
    "    // 輸入（方向鍵移動，S 推擠）"
)
new = (
    "    this.subTxt   =this.add.text(W/2,H/2+28,'',ts(20,'#ffaaaa')).setOrigin(0.5).setDepth(40);\n"
    "    this.effectTxt=this.add.text(W/2,H-16,'',ts(12,'#ffff88')).setOrigin(0.5).setDepth(35);\n"
    "\n"
    "    // 輸入（方向鍵移動，S 推擠）"
)
if old in html:
    html = html.replace(old, new)
    print("effectTxt: OK")
else:
    print("FAIL effectTxt")

# ── 4. Add playSound + spawnItem + applyItem before doPush ───────────────
new_methods = (
    "\n"
    "  playSound(type){\n"
    "    const ac=this.ac; if(!ac) return;\n"
    "    const now=ac.currentTime;\n"
    "    const mk=(freq,dur,vol,wave)=>{\n"
    "      wave=wave||'sine'; vol=vol||0.18;\n"
    "      const o=ac.createOscillator(),g=ac.createGain();\n"
    "      o.type=wave; o.frequency.value=freq;\n"
    "      o.connect(g); g.connect(ac.destination);\n"
    "      g.gain.setValueAtTime(vol,now); g.gain.exponentialRampToValueAtTime(0.001,now+dur);\n"
    "      o.start(now); o.stop(now+dur);\n"
    "    };\n"
    "    if(type==='push'){\n"
    "      const o=ac.createOscillator(),g=ac.createGain();\n"
    "      o.type='sawtooth'; o.connect(g); g.connect(ac.destination);\n"
    "      o.frequency.setValueAtTime(280,now); o.frequency.exponentialRampToValueAtTime(70,now+0.15);\n"
    "      g.gain.setValueAtTime(0.22,now); g.gain.exponentialRampToValueAtTime(0.001,now+0.15);\n"
    "      o.start(now); o.stop(now+0.15);\n"
    "    } else if(type==='sizzle'){\n"
    "      try{\n"
    "        const sz=Math.floor(ac.sampleRate*0.08),buf=ac.createBuffer(1,sz,ac.sampleRate),d=buf.getChannelData(0);\n"
    "        for(let i=0;i<sz;i++) d[i]=(Math.random()*2-1)*0.1;\n"
    "        const s=ac.createBufferSource(),f=ac.createBiquadFilter();\n"
    "        f.type='bandpass'; f.frequency.value=3000; f.Q.value=0.7;\n"
    "        s.buffer=buf; s.connect(f); f.connect(ac.destination); s.start();\n"
    "      }catch(e){}\n"
    "    } else if(type==='good'){\n"
    "      [440,554,659].forEach((fr,i)=>setTimeout(()=>mk(fr,0.2,0.16),i*80));\n"
    "    } else if(type==='bad'){\n"
    "      [220,165].forEach((fr,i)=>setTimeout(()=>mk(fr,0.25,0.2,'sawtooth'),i*100));\n"
    "    } else if(type==='death'){\n"
    "      [440,392,330,220].forEach((fr,i)=>setTimeout(()=>mk(fr,0.3,0.2),i*130));\n"
    "    } else if(type==='win'){\n"
    "      [523,659,784,1047].forEach((fr,i)=>setTimeout(()=>mk(fr,0.35,0.17),i*110));\n"
    "    } else if(type==='fork'){\n"
    "      mk(880,0.1,0.15,'square'); setTimeout(()=>mk(660,0.1,0.15,'square'),150);\n"
    "    }\n"
    "  }\n"
    "\n"
    "  spawnItem(){\n"
    "    const TYPES=[\n"
    "      {type:'ice',    label:'❌冰塊',   good:true,  dur:0},\n"
    "      {type:'foil',   label:'◎鋁箔紙', good:true,  dur:4},\n"
    "      {type:'garlic', label:'★大蒜',   good:true,  dur:5},\n"
    "      {type:'sauce',  label:'!醬油',   good:false, dur:5},\n"
    "      {type:'pepper', label:'!胡椒粉', good:false, dur:3},\n"
    "    ];\n"
    "    if(this.mapItems.length>=3) return;\n"
    "    const tp=TYPES[Math.floor(Math.random()*TYPES.length)];\n"
    "    const margin=60;\n"
    "    const x=G.x+margin+Math.random()*(G.w-margin*2);\n"
    "    const y=G.y+margin+Math.random()*(G.h-margin*2);\n"
    "    const col=tp.good?'#88ffcc':'#ff8888';\n"
    "    const bg=tp.good?'#0a3322':'#440000';\n"
    "    const txt=this.add.text(x,y,tp.label,{\n"
    "      fontSize:'14px',fontFamily:'sans-serif',color:col,\n"
    "      backgroundColor:bg,padding:{x:5,y:3}\n"
    "    }).setOrigin(0.5).setDepth(16);\n"
    "    this.mapItems.push({x,y,type:tp.type,good:tp.good,dur:tp.dur,txt,life:12});\n"
    "  }\n"
    "\n"
    "  applyItem(item){\n"
    "    const ae=this.activeEffects;\n"
    "    if(item.type==='ice')   {this.heat=Math.max(0,this.heat-25); this.showPop('❌ 冰塊！冷靜一下'); this.playSound('good');}\n"
    "    if(item.type==='foil')  {ae.foil=item.dur;    this.showPop('◎ 鋁箔紙！暫時险4秒'); this.playSound('good');}\n"
    "    if(item.type==='garlic'){ae.garlic=item.dur;  this.showPop('★ 大蒜！推力加倍！'); this.playSound('good');}\n"
    "    if(item.type==='sauce') {ae.sauce=item.dur;   this.showPop('! 醬油！營腦加速！'); this.playSound('bad');}\n"
    "    if(item.type==='pepper'){ae.slowpow=item.dur; this.showPop('! 胡椒粉！脟麻了！'); this.playSound('bad');}\n"
    "  }\n"
    "\n"
)
old_dopush = "  doPush(){"
if old_dopush in html:
    html = html.replace(old_dopush, new_methods + "  doPush(){", 1)
    print("new methods: OK")
else:
    print("FAIL new methods")

# ── 5. doPush - garlic multiplier + push sound ───────────────────────────
old = (
    "  doPush(){\n"
    "    this.pushCD=2;\n"
    "    const c=this.charData, RANGE=70, FORCE=c.key==='pork'?115:82;"
)
new = (
    "  doPush(){\n"
    "    this.pushCD=2;\n"
    "    this.playSound('push');\n"
    "    const ae=this.activeEffects;\n"
    "    const c=this.charData, RANGE=70, base=c.key==='pork'?115:82, FORCE=base*(ae.garlic>0?2:1);"
)
if old in html:
    html = html.replace(old, new)
    print("doPush garlic+sound: OK")
else:
    print("FAIL doPush")

# ── 6. endGame - sounds ───────────────────────────────────────────────────
old = (
    "  endGame(win){\n"
    "    this.alive=false;\n"
    "    if(this.wobbleTween)"
)
new = (
    "  endGame(win){\n"
    "    this.alive=false;\n"
    "    this.playSound(win?'win':'death');\n"
    "    if(this.wobbleTween)"
)
if old in html:
    html = html.replace(old, new)
    print("endGame sound: OK")
else:
    print("FAIL endGame sound")

# ── 7. spawnFork - fork warning sound ────────────────────────────────────
old = (
    "  spawnFork(){\n"
    "    const CELL=40, ZONE=3, half=CELL*ZONE/2;"
)
new = (
    "  spawnFork(){\n"
    "    this.playSound('fork');\n"
    "    const CELL=40, ZONE=3, half=CELL*ZONE/2;"
)
if old in html:
    html = html.replace(old, new)
    print("spawnFork sound: OK")
else:
    print("FAIL spawnFork sound")

# ── 8. Heat - foil/sauce effects + sizzle sound ──────────────────────────
old = (
    "    // 熟度（只增不減）\n"
    "    const mult=this.charData.heatMult;\n"
    "    if(this.onFire(this.p.x,this.p.y)) this.heat=Math.min(100,this.heat+15*mult*dt);\n"
    "    else                                this.heat=Math.min(100,this.heat+1.2*dt);\n"
    "    if(this.heat>=100){this.subTxt.setText('被烤熟了！');this.endGame(false);return;}"
)
new = (
    "    // 熟度（只增不減）\n"
    "    const ae=this.activeEffects;\n"
    "    const mult=this.charData.heatMult*(ae.sauce>0?2:1);\n"
    "    if(this.onFire(this.p.x,this.p.y)){\n"
    "      if(!ae.foil) this.heat=Math.min(100,this.heat+15*mult*dt);\n"
    "      this.sizzleTimer-=dt;\n"
    "      if(this.sizzleTimer<=0&&!ae.foil){this.playSound('sizzle');this.sizzleTimer=0.6;}\n"
    "    } else this.heat=Math.min(100,this.heat+1.2*dt);\n"
    "    if(this.heat>=100){this.subTxt.setText('被烤熟了！');this.endGame(false);return;}"
)
if old in html:
    html = html.replace(old, new)
    print("heat foil/sauce/sizzle: OK")
else:
    print("FAIL heat")

# ── 9. Speed - pepper slowdown ────────────────────────────────────────────
old = "    const SPD=this.charData.speed;"
new = "    const SPD=this.charData.speed*(this.activeEffects.slowpow>0?0.5:1);"
if old in html:
    html = html.replace(old, new)
    print("speed pepper: OK")
else:
    print("FAIL speed")

# ── 10. Item spawn/pickup + effect countdown before drawing ───────────────
old = (
    "    // 繪製\n"
    "    this.firePhase+=dt*3;\n"
    "    this.drawFires(this.firePhase);"
)
new = (
    "    // 道具效果倒計時\n"
    "    const ae2=this.activeEffects;\n"
    "    Object.keys(ae2).forEach(k=>{if(ae2[k]>0)ae2[k]=Math.max(0,ae2[k]-dt);});\n"
    "    // 道具生成\n"
    "    this.itemTimer-=dt;\n"
    "    if(this.itemTimer<=0){this.spawnItem();this.itemTimer=5+Math.random()*4;}\n"
    "    // 道具拾取\n"
    "    this.mapItems=this.mapItems.filter(item=>{\n"
    "      item.life-=dt;\n"
    "      if(Math.hypot(this.p.x-item.x,this.p.y-item.y)<24){this.applyItem(item);item.txt.destroy();return false;}\n"
    "      if(item.life<=0){item.txt.destroy();return false;}\n"
    "      item.txt.setAlpha(item.life<3&&Math.floor(item.life*5)%2===0?0.3:1);\n"
    "      return true;\n"
    "    });\n"
    "    // 效果指示器\n"
    "    const eff2=[];\n"
    "    if(ae2.foil>0)    eff2.push('◎险4 '+ae2.foil.toFixed(0)+'s');\n"
    "    if(ae2.garlic>0)  eff2.push('★推力x2 '+ae2.garlic.toFixed(0)+'s');\n"
    "    if(ae2.sauce>0)   eff2.push('!營腦x2 '+ae2.sauce.toFixed(0)+'s');\n"
    "    if(ae2.slowpow>0) eff2.push('!慢速 '+ae2.slowpow.toFixed(0)+'s');\n"
    "    this.effectTxt.setText(eff2.join('  '));\n"
    "    // 繪製\n"
    "    this.firePhase+=dt*3;\n"
    "    this.drawFires(this.firePhase);"
)
if old in html:
    html = html.replace(old, new)
    print("item logic: OK")
else:
    print("FAIL item logic")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

# ── Verify ───────────────────────────────────────────────────────────────
print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
print("8 fires:", "0,1,2,3,4,5,6,7" in v)
print("playSound:", "playSound(type)" in v)
print("spawnItem:", "spawnItem()" in v)
print("applyItem:", "applyItem(item)" in v)
print("foil effect:", "ae.foil" in v)
print("sauce effect:", "ae.sauce>0?2:1" in v)
print("pepper speed:", "slowpow>0?0.5:1" in v)
print("garlic push:", "ae.garlic>0?2:1" in v)
print("sizzle sound:", "sizzle" in v)
print("win/death sound:", "win?'win':'death'" in v)
print("item logic:", "this.itemTimer" in v)
print("effectTxt:", "this.effectTxt" in v)
