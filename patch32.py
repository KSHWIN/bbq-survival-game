# -*- coding: utf-8 -*-
# Patch 32: 角色放大 + 檸檬雨提示更長 + AI 難度選擇 + AI 推人技能
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

results = []
def rep(label, old, new):
    global html
    if old in html:
        html = html.replace(old, new, 1)
        results.append(label + ": OK")
    else:
        results.append("FAIL " + label)

# ── 1. 角色放大 ───────────────────────────────────────────────────
rep("sprite scale",
    "    const SS=0.16, ES=0.14;  // sprite scale (300px native → ~48px / ~42px)",
    "    const SS=0.19, ES=0.17;  // sprite scale (300px native → ~57px / ~51px)")

# ── 2. 檸檬雨更長警告 + 更慢落下 ─────────────────────────────────
rep("lemon warn timer",
    "          state:'warn',timer:0.9+i*0.7,",
    "          state:'warn',timer:2.0+i*0.6,")

rep("lemon fall speed",
    "          fallY:G.y-40,fallSpd:60,splashR:0,done:false});",
    "          fallY:G.y-40,fallSpd:35,splashR:0,done:false});")

# ── 3. 檸檬出現頻率提高（types 加兩個 lemon）────────────────────
rep("lemon frequency",
    "    const types=['brush','lemon','skewer'];",
    "    const types=['brush','lemon','lemon','lemon','skewer'];")

# ── 4. 事件整體頻率加快 ───────────────────────────────────────────
rep("event timer",
    "    if(this.evtTimer<=0){this.spawnRandEvent();this.evtTimer=15+Math.random()*8;}",
    "    if(this.evtTimer<=0){this.spawnRandEvent();this.evtTimer=11+Math.random()*5;}")

# ── 5. SelectScene：加 AI 難度按鈕 ───────────────────────────────
rep("ai diff UI",
    "    // ── Start Button ─────────────────────────────────────",
    "    // ── AI Difficulty Selector ───────────────────────────\n"
    "    this.aiDiff=1;\n"
    "    const ADY=488;\n"
    "    this.add.text(W/2-104,ADY,'AI 難度：',{fontSize:'12px',color:'#888888',fontFamily:'sans-serif'}).setOrigin(0,0.5);\n"
    "    this.adBtns=[];\n"
    "    ['弱','中','強'].forEach((lbl,bi)=>{\n"
    "      const bx=W/2-4+bi*56, by=ADY;\n"
    "      const col=[0x1a4a1a,0xff6600,0x8b0000][bi];\n"
    "      const bBg=this.add.rectangle(bx,by,48,26,bi===1?0xff6600:col,1).setStrokeStyle(1,0x886644);\n"
    "      const bTxt=this.add.text(bx,by,lbl,{fontSize:'13px',color:'#ffffff',fontFamily:'sans-serif',fontStyle:'bold'}).setOrigin(0.5);\n"
    "      bBg.setInteractive();\n"
    "      bBg.on('pointerdown',()=>{\n"
    "        this.aiDiff=bi;\n"
    "        this.adBtns.forEach((b,j)=>b.bg.setFillStyle(j===bi?[0x1a4a1a,0xff6600,0x8b0000][j]:0x2a2a2a));\n"
    "      });\n"
    "      bBg.on('pointerover',()=>bBg.setScale(1.1));\n"
    "      bBg.on('pointerout', ()=>bBg.setScale(1));\n"
    "      this.adBtns.push({bg:bBg,txt:bTxt});\n"
    "    });\n"
    "\n"
    "    // ── Start Button ─────────────────────────────────────")

# ── 6. startGame 傳遞 aiDiff ──────────────────────────────────────
rep("startGame pass aiDiff",
    "    this.scene.start('Game',{char:CHARS[this.sel], level:LEVELS[this.lvSel], enemyCnt:this.enemyCnt||2});",
    "    this.scene.start('Game',{char:CHARS[this.sel], level:LEVELS[this.lvSel], enemyCnt:this.enemyCnt||2, aiDiff:this.aiDiff||1});")

# ── 7. GameScene.init 接收 aiDiff ─────────────────────────────────
rep("init aiDiff",
    "  init(data){ this.charData=data.char||this.charData||CHARS[0]; this.levelData=data.level||this.levelData||LEVELS[0]; this.enemyCnt=data.enemyCnt||2; }",
    "  init(data){ this.charData=data.char||this.charData||CHARS[0]; this.levelData=data.level||this.levelData||LEVELS[0]; this.enemyCnt=data.enemyCnt||2; this.aiDiff=data.aiDiff??1; }")

# ── 8. 敵人初始化加入 pushTimer + abilTimer ───────────────────────
rep("enemy push abil timers",
    "      chargeTimer:1.5+Math.random()*2, charging:false, chDx:1, chDy:0, chargeTime:0,",
    "      chargeTimer:1.5+Math.random()*2, charging:false, chDx:1, chDy:0, chargeTime:0,\n"
    "      pushTimer:3+Math.random()*3, abilTimer:5+Math.random()*4, abilActive:false,")

# ── 9. AI 邏輯：加難度參數 + 推人 + 技能 ────────────────────────
rep("AI difficulty params",
    "      const edx=this.p.x-e.x, edy=this.p.y-e.y;\n"
    "      const edist=Math.hypot(edx,edy)||1;\n"
    "      e.chargeTimer-=dt;\n"
    "      const aggrMult=this.heat>60?1.5:1.0;",

    "      const DIFF_P=[{spd:1.8,accel:0.12,cdm:2.2},{spd:2.8,accel:0.20,cdm:1.0},{spd:3.8,accel:0.30,cdm:0.55}];\n"
    "      const dp=DIFF_P[this.aiDiff??1];\n"
    "      const edx=this.p.x-e.x, edy=this.p.y-e.y;\n"
    "      const edist=Math.hypot(edx,edy)||1;\n"
    "      e.chargeTimer-=dt; e.pushTimer-=dt; e.abilTimer-=dt;\n"
    "      const aggrMult=(this.heat>60?1.5:1.0)*(this.aiDiff===2?1.3:1.0);")

rep("AI charge speed use diff",
    "      if(e.chargeTimer<=0&&edist<165){\n"
    "        e.chargeTimer=(3.5+Math.random()*3)/aggrMult;\n"
    "        e.charging=true; e.chargeTime=0.32;\n"
    "        e.chDx=edx/edist; e.chDy=edy/edist;\n"
    "      }\n"
    "      if(e.charging){\n"
    "        e.chargeTime-=dt;\n"
    "        e.vx=e.chDx*4.5; e.vy=e.chDy*4.5;\n"
    "        if(e.chargeTime<=0){e.charging=false; e.vx*=0.25; e.vy*=0.25;}\n"
    "      } else if(edist>52){\n"
    "        e.vx+=(edx/edist)*0.20*aggrMult;\n"
    "        e.vy+=(edy/edist)*0.20*aggrMult;\n"
    "      }\n"
    "      const espd=Math.hypot(e.vx,e.vy)||1;\n"
    "      const maxSpd=e.charging?4.5:2.8;\n"
    "      if(espd>maxSpd){e.vx=(e.vx/espd)*maxSpd;e.vy=(e.vy/espd)*maxSpd;}",

    "      if(e.chargeTimer<=0&&edist<165){\n"
    "        e.chargeTimer=(3.5+Math.random()*3)/aggrMult*dp.cdm;\n"
    "        e.charging=true; e.chargeTime=0.32;\n"
    "        e.chDx=edx/edist; e.chDy=edy/edist;\n"
    "      }\n"
    "      if(e.charging){\n"
    "        e.chargeTime-=dt;\n"
    "        e.vx=e.chDx*dp.spd; e.vy=e.chDy*dp.spd;\n"
    "        if(e.chargeTime<=0){e.charging=false; e.vx*=0.25; e.vy*=0.25;}\n"
    "      } else if(edist>52){\n"
    "        e.vx+=(edx/edist)*dp.accel*aggrMult;\n"
    "        e.vy+=(edy/edist)*dp.accel*aggrMult;\n"
    "      }\n"
    "      const espd=Math.hypot(e.vx,e.vy)||1;\n"
    "      const maxSpd=e.charging?dp.spd:dp.spd*0.62;\n"
    "      if(espd>maxSpd){e.vx=(e.vx/espd)*maxSpd;e.vy=(e.vy/espd)*maxSpd;}\n"
    "      // AI 推人（近距離衝擊，強難度頻率更高）\n"
    "      const pushRng=[4.5,3.0,2.0][this.aiDiff??1];\n"
    "      if(e.pushTimer<=0&&edist<44&&!e.charging){\n"
    "        e.pushTimer=pushRng+Math.random()*2;\n"
    "        const pnx=edx/edist,pny=edy/edist;\n"
    "        const pForce=(60+dp.spd*22);\n"
    "        const charBst2=Math.min(2.5,1+this.heat/100*2);\n"
    "        this.tweens.add({targets:this.p,\n"
    "          x:this.p.x+pnx*pForce*charBst2,y:this.p.y+pny*pForce*charBst2,\n"
    "          duration:240,ease:'Cubic.easeOut',\n"
    "          onComplete:()=>{\n"
    "            if(!inGrill(this.p.x,this.p.y)){this.subTxt.setText('被推落！');this.endGame(false);}\n"
    "          }});\n"
    "        this.cameras.main.shake(120,0.004+charBst2*0.005);\n"
    "        if(charBst2>1.8) this.showPop('🔥 脆了！被 '+e.label+' 推飛！');\n"
    "        else             this.showPop('💥 被 '+e.label+' 推開！');\n"
    "        const gCnt=3+Math.round(charBst2*2);\n"
    "        for(let gi=0;gi<gCnt;gi++){\n"
    "          const gObj={px:this.p.x,py:this.p.y,life:1};\n"
    "          const gAng=Math.atan2(pny,pnx)+(Math.random()-0.5)*1.6;\n"
    "          const gDst=35+Math.random()*65;\n"
    "          const gCol=Math.random()<0.5?0xffcc00:0xff6600;\n"
    "          const gGfx=this.add.graphics().setDepth(24);\n"
    "          this.tweens.add({targets:gObj,\n"
    "            px:this.p.x+Math.cos(gAng)*gDst,py:this.p.y+Math.sin(gAng)*gDst,life:0,\n"
    "            duration:320+Math.random()*140,ease:'Quad.easeOut',\n"
    "            onUpdate:()=>{gGfx.clear();gGfx.fillStyle(gCol,gObj.life*0.85);\n"
    "              gGfx.fillCircle(gObj.px,gObj.py,gObj.life*5+1);},\n"
    "            onComplete:()=>gGfx.destroy()});\n"
    "        }\n"
    "      }\n"
    "      // AI 技能（強：頻繁衝刺爆發，中：偶爾，弱：不用）\n"
    "      const abilRng=[999,8.0,4.5][this.aiDiff??1];\n"
    "      if(e.abilTimer<=0){\n"
    "        e.abilTimer=abilRng+Math.random()*3;\n"
    "        e.charging=true; e.chargeTime=0.55;\n"
    "        e.chDx=edx/edist; e.chDy=edy/edist;\n"
    "        e.vx=e.chDx*dp.spd*1.6; e.vy=e.chDy*dp.spd*1.6;\n"
    "      }")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

for r in results:
    print(r)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
checks = [
    ("SS=0.19",               "sprite scale player"),
    ("ES=0.17",               "sprite scale enemy"),
    ("timer:2.0+i*0.6",       "lemon warn longer"),
    ("fallSpd:35",            "lemon fall slower"),
    ("lemon','lemon','lemon", "lemon 3x weight"),
    ("evtTimer=11+",          "event freq 11s"),
    ("this.aiDiff=1",         "aiDiff default"),
    ("AI 難度",               "ai diff label"),
    ("aiDiff:this.aiDiff",    "pass aiDiff"),
    ("this.aiDiff=data.aiDiff","init aiDiff"),
    ("pushTimer:3+",          "push timer init"),
    ("abilTimer:5+",          "abil timer init"),
    ("DIFF_P=",               "diff params array"),
    ("dp.spd",                "use dp speed"),
    ("e.pushTimer<=0",        "ai push trigger"),
    ("e.abilTimer<=0",        "ai abil trigger"),
    ("被推落",                "fall msg"),
]
for key, label in checks:
    print(f"{label}: {'OK' if key in v else 'MISSING'}")
