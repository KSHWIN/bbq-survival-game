# -*- coding: utf-8 -*-
# Patch 29: AI 攻擊性 + 對手數量選擇
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

# ── 1. SelectScene.create()：加對手數量選擇器（在開始按鈕前）───────────
rep("enemy count UI",
    "    // ── Start Button ─────────────────────────────────────",
    "    // ── Enemy Count Selector ─────────────────────────────\n"
    "    this.enemyCnt=2;\n"
    "    const ECY=462;\n"
    "    this.add.text(W/2-104,ECY,'對手數量：',{fontSize:'12px',color:'#888888',fontFamily:'sans-serif'}).setOrigin(0,0.5);\n"
    "    this.ecBtns=[];\n"
    "    [1,2,3].forEach((n,bi)=>{\n"
    "      const bx=W/2+20+bi*52, by=ECY;\n"
    "      const bBg=this.add.rectangle(bx,by,44,26,n===2?0xff6600:0x2a2a2a,1).setStrokeStyle(1,0x886644);\n"
    "      const bTxt=this.add.text(bx,by,n+'個',{fontSize:'12px',color:'#ffffff',fontFamily:'sans-serif',fontStyle:'bold'}).setOrigin(0.5);\n"
    "      bBg.setInteractive();\n"
    "      bBg.on('pointerdown',()=>{\n"
    "        this.enemyCnt=n;\n"
    "        this.ecBtns.forEach((b,j)=>b.bg.setFillStyle(j===bi?0xff6600:0x2a2a2a));\n"
    "      });\n"
    "      bBg.on('pointerover',()=>bBg.setScale(1.1));\n"
    "      bBg.on('pointerout', ()=>bBg.setScale(1));\n"
    "      this.ecBtns.push({bg:bBg,txt:bTxt,val:n});\n"
    "    });\n"
    "\n"
    "    // ── Start Button ─────────────────────────────────────")

# ── 2. startGame 傳遞 enemyCnt ────────────────────────────────────
rep("startGame pass enemyCnt",
    "    this.scene.start('Game',{char:CHARS[this.sel], level:LEVELS[this.lvSel]});",
    "    this.scene.start('Game',{char:CHARS[this.sel], level:LEVELS[this.lvSel], enemyCnt:this.enemyCnt||2});")

# ── 3. GameScene.init 接收 enemyCnt ─────────────────────────────────
rep("init enemyCnt",
    "  init(data){ this.charData=data.char||this.charData||CHARS[0]; this.levelData=data.level||this.levelData||LEVELS[0]; }",
    "  init(data){ this.charData=data.char||this.charData||CHARS[0]; this.levelData=data.level||this.levelData||LEVELS[0]; this.enemyCnt=data.enemyCnt||2; }")

# ── 4. 敵人生成：三個預設位置 + 依 enemyCnt ────────────────────────
rep("enemy spawn positions",
    "    // 敵人（選非玩家的前2個）\n"
    "    const aiChars=CHARS.filter(ch=>ch.key!==c.key).slice(0,2);\n"
    "    this.enemies=aiChars.map((ch,i)=>({\n"
    "      x:i===0?240:510, y:i===0?220:340, r:18,\n"
    "      vx:i===0?2.1:-1.8, vy:i===0?1.5:2.0,\n"
    "      heat:0, alive:true, label:ch.name, img:ch.img,\n"
    "    }));",

    "    // 敵人（依對手數量）\n"
    "    const EPOS=[{x:240,y:220,vx:2.1,vy:1.5},{x:510,y:340,vx:-1.8,vy:2.0},{x:390,y:430,vx:1.5,vy:-2.2}];\n"
    "    const aiChars=CHARS.filter(ch=>ch.key!==c.key).slice(0,this.enemyCnt);\n"
    "    this.enemies=aiChars.map((ch,i)=>({\n"
    "      x:EPOS[i].x, y:EPOS[i].y, r:18,\n"
    "      vx:EPOS[i].vx, vy:EPOS[i].vy,\n"
    "      heat:0, alive:true, label:ch.name, img:ch.img,\n"
    "      chargeTimer:1.5+Math.random()*2, charging:false, chDx:1, chDy:0, chargeTime:0,\n"
    "    }));")

# ── 5. AI 邏輯改良（替換舊的追蹤 + 速度上限）───────────────────────
rep("AI overhaul",
    "      // AI 緩慢追蹤玩家\n"
    "      const edx=this.p.x-e.x, edy=this.p.y-e.y;\n"
    "      const edist=Math.hypot(edx,edy)||1;\n"
    "      if(edist>55){\n"
    "        e.vx+=(edx/edist)*0.18;\n"
    "        e.vy+=(edy/edist)*0.18;\n"
    "      }\n"
    "      // 速度上限\n"
    "      const espd=Math.hypot(e.vx,e.vy)||1;\n"
    "      if(espd>3.8){e.vx=(e.vx/espd)*3.8;e.vy=(e.vy/espd)*3.8;}",

    "      const edx=this.p.x-e.x, edy=this.p.y-e.y;\n"
    "      const edist=Math.hypot(edx,edy)||1;\n"
    "      e.chargeTimer-=dt;\n"
    "      const aggrMult=this.heat>60?1.5:1.0;\n"
    "      // 躲火\n"
    "      let avX=0,avY=0;\n"
    "      this.firePts.forEach(f=>{\n"
    "        if(f.state!=='active'&&f.state!=='dying') return;\n"
    "        const fd=Math.hypot(e.x-f.x,e.y-f.y)||1;\n"
    "        if(fd<80){avX+=(e.x-f.x)/fd*(80-fd)*0.055;avY+=(e.y-f.y)/fd*(80-fd)*0.055;}\n"
    "      });\n"
    "      e.vx+=avX; e.vy+=avY;\n"
    "      // 躲縮圈邊緣\n"
    "      if(this.shrinkPad>0){\n"
    "        const mg=this.shrinkPad+22;\n"
    "        const cxA=G.x+G.w/2, cyA=G.y+G.h/2;\n"
    "        if(e.x<G.x+mg||e.x>G.x+G.w-mg||e.y<G.y+mg||e.y>G.y+G.h-mg){\n"
    "          const dl=Math.hypot(cxA-e.x,cyA-e.y)||1;\n"
    "          e.vx+=(cxA-e.x)/dl*0.55; e.vy+=(cyA-e.y)/dl*0.55;\n"
    "        }\n"
    "      }\n"
    "      // 衝刺攻擊：計時到且距離夠就衝\n"
    "      if(e.chargeTimer<=0&&edist<165){\n"
    "        e.chargeTimer=(3.5+Math.random()*3)/aggrMult;\n"
    "        e.charging=true; e.chargeTime=0.32;\n"
    "        e.chDx=edx/edist; e.chDy=edy/edist;\n"
    "      }\n"
    "      if(e.charging){\n"
    "        e.chargeTime-=dt;\n"
    "        e.vx=e.chDx*9.5; e.vy=e.chDy*9.5;\n"
    "        if(e.chargeTime<=0){e.charging=false; e.vx*=0.25; e.vy*=0.25;}\n"
    "      } else if(edist>52){\n"
    "        e.vx+=(edx/edist)*0.30*aggrMult;\n"
    "        e.vy+=(edy/edist)*0.30*aggrMult;\n"
    "      }\n"
    "      const espd=Math.hypot(e.vx,e.vy)||1;\n"
    "      const maxSpd=e.charging?9.5:5.5;\n"
    "      if(espd>maxSpd){e.vx=(e.vx/espd)*maxSpd;e.vy=(e.vy/espd)*maxSpd;}")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

for r in results:
    print(r)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
checks = [
    ("this.enemyCnt=2",       "enemyCnt default"),
    ("enemyCnt:this.enemyCnt","startGame pass"),
    ("this.enemyCnt=data.enemyCnt", "init accept"),
    ("slice(0,this.enemyCnt)", "enemy slice"),
    ("chargeTimer:1.5",        "charge init"),
    ("aggrMult=this.heat>60",  "aggr mult"),
    ("躲火",                   "fire avoidance"),
    ("shrinkPad+22",           "shrink avoidance"),
    ("chargeTime=0.32",        "charge time"),
    ("9.5",                    "charge speed"),
]
for key, label in checks:
    print(f"{label}: {'OK' if key in v else 'MISSING'}")
