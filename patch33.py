# -*- coding: utf-8 -*-
# Patch 33: AI 互相攻擊 + 難度改為積極度/判斷品質（速度固定）
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

# ── 整個 AI 邏輯區塊替換 ─────────────────────────────────────────
OLD_AI = (
    "      const DIFF_P=[{spd:1.8,accel:0.12,cdm:2.2},{spd:2.8,accel:0.20,cdm:1.0},{spd:3.8,accel:0.30,cdm:0.55}];\n"
    "      const dp=DIFF_P[this.aiDiff??1];\n"
    "      const edx=this.p.x-e.x, edy=this.p.y-e.y;\n"
    "      const edist=Math.hypot(edx,edy)||1;\n"
    "      e.chargeTimer-=dt; e.pushTimer-=dt; e.abilTimer-=dt;\n"
    "      const aggrMult=(this.heat>60?1.5:1.0)*(this.aiDiff===2?1.3:1.0);\n"
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
    "      }"
)

NEW_AI = (
    "      // 難度決定積極度與反應品質，速度固定\n"
    "      const diff=this.aiDiff??1;\n"
    "      // 選追擊目標：全部生存者（玩家 + 其他 AI）\n"
    "      const allLive=[\n"
    "        {x:this.p.x,y:this.p.y,isPlayer:true,heat:this.heat,ref:null,idx:-1},\n"
    "        ...this.enemies\n"
    "          .map((en,j)=>({x:en.x,y:en.y,isPlayer:false,heat:en.heat,ref:en,idx:j}))\n"
    "          .filter((_,j)=>j!==i&&this.enemies[j].alive)\n"
    "      ];\n"
    "      let tgt;\n"
    "      if(diff===0){\n"
    "        tgt=allLive[0]; // 弱：只追玩家，不看其他 AI\n"
    "      } else if(diff===1){\n"
    "        tgt=allLive.reduce((a,b)=>Math.hypot(a.x-e.x,a.y-e.y)<=Math.hypot(b.x-e.x,b.y-e.y)?a:b);\n"
    "      } else {\n"
    "        // 強：優先選 heat 最高（最脆）且距離 200 內的目標\n"
    "        const near200=allLive.filter(t=>Math.hypot(t.x-e.x,t.y-e.y)<200);\n"
    "        const pool=near200.length?near200:allLive;\n"
    "        tgt=pool.reduce((a,b)=>a.heat>=b.heat?a:b);\n"
    "      }\n"
    "      const edx=tgt.x-e.x, edy=tgt.y-e.y;\n"
    "      const edist=Math.hypot(edx,edy)||1;\n"
    "      e.chargeTimer-=dt; e.pushTimer-=dt;\n"
    "      // 躲火（弱遲鈍，強靈敏）\n"
    "      const fireW=[0.02,0.055,0.10][diff];\n"
    "      let avX=0,avY=0;\n"
    "      this.firePts.forEach(f=>{\n"
    "        if(f.state!=='active'&&f.state!=='dying') return;\n"
    "        const fd=Math.hypot(e.x-f.x,e.y-f.y)||1;\n"
    "        if(fd<80){avX+=(e.x-f.x)/fd*(80-fd)*fireW;avY+=(e.y-f.y)/fd*(80-fd)*fireW;}\n"
    "      });\n"
    "      e.vx+=avX; e.vy+=avY;\n"
    "      // 躲縮圈（強更早反應）\n"
    "      if(this.shrinkPad>0){\n"
    "        const mg=this.shrinkPad+[16,22,32][diff];\n"
    "        const cxA=G.x+G.w/2, cyA=G.y+G.h/2;\n"
    "        if(e.x<G.x+mg||e.x>G.x+G.w-mg||e.y<G.y+mg||e.y>G.y+G.h-mg){\n"
    "          const dl=Math.hypot(cxA-e.x,cyA-e.y)||1;\n"
    "          e.vx+=(cxA-e.x)/dl*[0.30,0.55,0.85][diff];\n"
    "          e.vy+=(cyA-e.y)/dl*[0.30,0.55,0.85][diff];\n"
    "        }\n"
    "      }\n"
    "      // 衝刺：難度決定頻率，速度固定 4.5\n"
    "      const chargeCd=diff===0?6+Math.random()*4:diff===1?3.5+Math.random()*3:2+Math.random()*2;\n"
    "      if(e.chargeTimer<=0&&edist<(diff===1?165:200)){\n"
    "        e.chargeTimer=chargeCd;\n"
    "        e.charging=true; e.chargeTime=0.32;\n"
    "        e.chDx=edx/edist; e.chDy=edy/edist;\n"
    "      }\n"
    "      if(e.charging){\n"
    "        e.chargeTime-=dt;\n"
    "        e.vx=e.chDx*4.5; e.vy=e.chDy*4.5;\n"
    "        if(e.chargeTime<=0){e.charging=false; e.vx*=0.25; e.vy*=0.25;}\n"
    "      } else if(edist>52){\n"
    "        e.vx+=(edx/edist)*0.20;\n"
    "        e.vy+=(edy/edist)*0.20;\n"
    "      }\n"
    "      const espd=Math.hypot(e.vx,e.vy)||1;\n"
    "      const maxSpd=e.charging?4.5:2.8;\n"
    "      if(espd>maxSpd){e.vx=(e.vx/espd)*maxSpd;e.vy=(e.vy/espd)*maxSpd;}\n"
    "      // 推人：找最近對象（玩家或其他 AI 都算）\n"
    "      const pushCd=[5.0,3.0,2.0][diff];\n"
    "      if(e.pushTimer<=0&&!e.charging){\n"
    "        const pTgt=allLive.reduce((a,b)=>Math.hypot(a.x-e.x,a.y-e.y)<=Math.hypot(b.x-e.x,b.y-e.y)?a:b);\n"
    "        const pd=Math.hypot(pTgt.x-e.x,pTgt.y-e.y);\n"
    "        if(pd<44){\n"
    "          e.pushTimer=pushCd+Math.random()*2;\n"
    "          const pnx=(pTgt.x-e.x)/pd, pny=(pTgt.y-e.y)/pd;\n"
    "          const pForce=95;\n"
    "          if(pTgt.isPlayer){\n"
    "            const cBst=Math.min(2.5,1+this.heat/100*2);\n"
    "            this.tweens.add({targets:this.p,\n"
    "              x:this.p.x+pnx*pForce*cBst,y:this.p.y+pny*pForce*cBst,\n"
    "              duration:240,ease:'Cubic.easeOut',\n"
    "              onComplete:()=>{if(!inGrill(this.p.x,this.p.y)){this.subTxt.setText('被推落！');this.endGame(false);}}});\n"
    "            this.cameras.main.shake(120,0.004+cBst*0.005);\n"
    "            if(cBst>1.8) this.showPop('🔥 脆了！被 '+e.label+' 推飛！');\n"
    "            else         this.showPop('💥 被 '+e.label+' 推開！');\n"
    "          } else {\n"
    "            const eRef=pTgt.ref, eIdx=pTgt.idx;\n"
    "            const cBst=Math.min(2.5,1+(eRef.heat||0)/100*2);\n"
    "            this.tweens.add({targets:eRef,\n"
    "              x:eRef.x+pnx*pForce*cBst,y:eRef.y+pny*pForce*cBst,\n"
    "              duration:240,ease:'Cubic.easeOut',\n"
    "              onComplete:()=>this.checkEnemyFall(eRef,eIdx)});\n"
    "          }\n"
    "          const gOriX=pTgt.isPlayer?this.p.x:pTgt.ref.x;\n"
    "          const gOriY=pTgt.isPlayer?this.p.y:pTgt.ref.y;\n"
    "          for(let gi=0;gi<4;gi++){\n"
    "            const gOb={px:gOriX,py:gOriY,life:1};\n"
    "            const gAng=Math.atan2(pny,pnx)+(Math.random()-0.5)*1.6;\n"
    "            const gGfx=this.add.graphics().setDepth(24);\n"
    "            this.tweens.add({targets:gOb,\n"
    "              px:gOriX+Math.cos(gAng)*(40+Math.random()*55),\n"
    "              py:gOriY+Math.sin(gAng)*(40+Math.random()*55),life:0,\n"
    "              duration:300+Math.random()*130,ease:'Quad.easeOut',\n"
    "              onUpdate:()=>{gGfx.clear();gGfx.fillStyle(0xffcc00,gOb.life*0.85);\n"
    "                gGfx.fillCircle(gOb.px,gOb.py,gOb.life*5+1);},\n"
    "              onComplete:()=>gGfx.destroy()});\n"
    "          }\n"
    "        } else { e.pushTimer=0.5; }\n"
    "      }"
)

rep("AI full overhaul", OLD_AI, NEW_AI)

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

for r in results:
    print(r)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
checks = [
    ("allLive=",             "allLive array"),
    ("isPlayer:true",        "player entry"),
    ("isPlayer:false",       "enemy entry"),
    ("diff===0",             "diff weak"),
    ("diff===1",             "diff mid"),
    ("near200",              "strong targets vuln"),
    ("fireW=",               "fire weight by diff"),
    ("e.vx=e.chDx*4.5",     "charge speed fixed 4.5"),
    ("maxSpd=e.charging?4.5:2.8", "max speed fixed"),
    ("pTgt.isPlayer",        "push check isPlayer"),
    ("eRef=pTgt.ref",        "push enemy ref"),
    ("checkEnemyFall(eRef",  "push enemy fall check"),
    ("DIFF_P=",              "old DIFF_P gone"),
]
for key, label in checks:
    if key == "DIFF_P=":
        print(f"{label}: {'OK (removed)' if key not in v else 'STILL PRESENT (bug)'}")
    else:
        print(f"{label}: {'OK' if key in v else 'MISSING'}")
