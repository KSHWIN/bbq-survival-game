# -*- coding: utf-8 -*-
# Patch 6: Running animation + BGM
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. Add runPhase + BGM start to create() init ─────────────────────────
old = (
    "    this.activeEffects={foil:0,garlic:0,sauce:0,slowpow:0};\n"
    "    this.mapItems=[]; this.itemTimer=3; this.sizzleTimer=0;\n"
    "    const AC=window.AudioContext||window.webkitAudioContext;\n"
    "    this.ac=AC?new AC():null;"
)
new = (
    "    this.activeEffects={foil:0,garlic:0,sauce:0,slowpow:0};\n"
    "    this.mapItems=[]; this.itemTimer=3; this.sizzleTimer=0;\n"
    "    this.runPhase=0; this.bgmEvent=null;\n"
    "    const AC=window.AudioContext||window.webkitAudioContext;\n"
    "    this.ac=AC?new AC():null;\n"
    "    this.time.delayedCall(200,()=>this.startBGM());"
)
if old in html:
    html = html.replace(old, new)
    print("init runPhase+BGM: OK")
else:
    print("FAIL init")

# ── 2. Stop BGM in endGame ───────────────────────────────────────────────
old = (
    "  endGame(win){\n"
    "    this.alive=false;\n"
    "    this.playSound(win?'win':'death');\n"
    "    if(this.wobbleTween)"
)
new = (
    "  endGame(win){\n"
    "    this.alive=false;\n"
    "    if(this.bgmEvent){this.bgmEvent.remove();this.bgmEvent=null;}\n"
    "    this.playSound(win?'win':'death');\n"
    "    if(this.wobbleTween)"
)
if old in html:
    html = html.replace(old, new)
    print("endGame stop BGM: OK")
else:
    print("FAIL endGame")

# ── 3. Add startBGM() method after playSound() ───────────────────────────
old_after = "  spawnItem(){"
new_bgm = (
    "  startBGM(){\n"
    "    if(!this.ac||this.bgmEvent) return;\n"
    "    // Fun upbeat cooking melody in C major (16 eighth-notes)\n"
    "    const mel=[262,330,392,330,349,440,392,349,\n"
    "               294,392,440,392,523,494,440,262];\n"
    "    let step=0;\n"
    "    this.bgmEvent=this.time.addEvent({\n"
    "      delay:214, loop:true, // ~140bpm 8th note\n"
    "      callback:()=>{\n"
    "        if(!this.ac) return;\n"
    "        const t=this.ac.currentTime, f=mel[step%mel.length];\n"
    "        // Lead melody (square wave, soft)\n"
    "        const o=this.ac.createOscillator(),g=this.ac.createGain();\n"
    "        o.type='square'; o.frequency.value=f;\n"
    "        o.connect(g); g.connect(this.ac.destination);\n"
    "        g.gain.setValueAtTime(0.045,t); g.gain.exponentialRampToValueAtTime(0.001,t+0.19);\n"
    "        o.start(t); o.stop(t+0.19);\n"
    "        // Bass on beats 1 & 3 (every 4 steps)\n"
    "        if(step%4===0){\n"
    "          const b=this.ac.createOscillator(),bg=this.ac.createGain();\n"
    "          b.type='triangle'; b.frequency.value=f/2;\n"
    "          b.connect(bg); bg.connect(this.ac.destination);\n"
    "          bg.gain.setValueAtTime(0.07,t); bg.gain.exponentialRampToValueAtTime(0.001,t+0.25);\n"
    "          b.start(t); b.stop(t+0.25);\n"
    "        }\n"
    "        // Hi-hat on every other step\n"
    "        if(step%2===0){ try{\n"
    "          const sz=Math.floor(this.ac.sampleRate*0.015);\n"
    "          const buf=this.ac.createBuffer(1,sz,this.ac.sampleRate);\n"
    "          const d=buf.getChannelData(0);\n"
    "          for(let i=0;i<sz;i++) d[i]=(Math.random()*2-1)*0.055;\n"
    "          const s=this.ac.createBufferSource(),hf=this.ac.createBiquadFilter();\n"
    "          hf.type='highpass'; hf.frequency.value=5000;\n"
    "          s.buffer=buf; s.connect(hf); hf.connect(this.ac.destination); s.start(t);\n"
    "        }catch(e){} }\n"
    "        step++;\n"
    "      }\n"
    "    });\n"
    "  }\n"
    "\n"
)
if old_after in html:
    html = html.replace(old_after, new_bgm + old_after, 1)
    print("startBGM: OK")
else:
    print("FAIL startBGM")

# ── 4. Replace player sprite update with full running animation ───────────
old_sprite_update = (
    "    // 玩家 sprite\n"
    "    if(this.playerSprite){ this.playerSprite.setPosition(this.p.x,this.p.y); if(!this.wobbleTween) this.playerSprite.setScale(0.16); }\n"
    "    this.updateHeatFx(this.playerSprite,this.heat,this.sweatTxt);"
)
new_sprite_update = (
    "    // 玩家 sprite + 跑步動畫\n"
    "    const isMoving=!!(mx||my);\n"
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
    "          this.playerSprite.setAngle(this.lastDir.x*7);\n"
    "          this.playerSprite.setPosition(this.p.x, this.p.y+c*3.5);\n"
    "        } else {\n"
    "          this.playerSprite.setScale(BS);\n"
    "          this.playerSprite.setAngle(0);\n"
    "          this.playerSprite.setFlipX(this.lastDir.x<-0.1);\n"
    "          this.playerSprite.setPosition(this.p.x, this.p.y);\n"
    "        }\n"
    "      } else {\n"
    "        this.playerSprite.setX(this.p.x);\n"
    "      }\n"
    "    }\n"
    "    this.updateHeatFx(this.playerSprite,this.heat,this.sweatTxt);"
)
if old_sprite_update in html:
    html = html.replace(old_sprite_update, new_sprite_update)
    print("running anim: OK")
else:
    print("FAIL running anim")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
print("runPhase:", "this.runPhase=0" in v)
print("startBGM:", "startBGM()" in v)
print("BGM melody:", "mel=[262" in v)
print("running anim:", "sqX=1-Math.abs" in v)
print("flipX:", "setFlipX(this.lastDir.x<-0.1)" in v)
print("lean:", "setAngle(this.lastDir.x*7)" in v)
print("depth scale:", "lastDir.y*0.05" in v)
