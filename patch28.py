# -*- coding: utf-8 -*-
# Patch 28: 空投事件/縮圈/越熟越黑/脆化擊退/油脂粒子
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

# ── 1. activeEffects 加 stun / toxic ─────────────────────────────
rep("activeEffects",
    "this.activeEffects={foil:0,garlic:0,sauce:0,slowpow:0};",
    "this.activeEffects={foil:0,garlic:0,sauce:0,slowpow:0,stun:0,toxic:0};")

# ── 2. 縮圈 + 事件佇列初始化 ──────────────────────────────────────
rep("init vars",
    "    this.FIRE_R_BASE=46; this.FIRE_R_AMP=12;",
    "    this.FIRE_R_BASE=46; this.FIRE_R_AMP=12;\n"
    "    this.shrinkPad=0; this.shrinkStep=10; this.shrinkMax=50;\n"
    "    this.shrinkTimer=22+Math.random()*8; this.shrinkWarning=false; this.shrinkWarnTimer=0;\n"
    "    this.evtTimer=12+Math.random()*5; this.evtQueue=[];")

# ── 3. 加兩個繪圖層 ───────────────────────────────────────────────
rep("layers",
    "    this.abilFxLayer=this.add.graphics().setDepth(22);",
    "    this.abilFxLayer=this.add.graphics().setDepth(22);\n"
    "    this.eventLayer =this.add.graphics().setDepth(16);\n"
    "    this.shrinkLayer=this.add.graphics().setDepth(4);")

# ── 4. 暈眩時封鎖移動 ─────────────────────────────────────────────
rep("stun block",
    "    if(mx&&my){mx*=0.707;my*=0.707;}",
    "    if(mx&&my){mx*=0.707;my*=0.707;}\n"
    "    if(this.activeEffects.stun>0){"
    "mx=0;my=0;if(isDash&&this.dashState)this.dashState.active=false;}")

# ── 5. 焦糖化持續扣血 ─────────────────────────────────────────────
rep("toxic heat",
    "    } else this.heat=Math.min(heatCap,this.heat+0.2*dt);",
    "    } else this.heat=Math.min(heatCap,this.heat+0.2*dt);\n"
    "    if(ae.toxic>0) this.heat=Math.min(heatCap,this.heat+18*dt);")

# ── 6. 脆化擊退 + 油脂粒子 + 比例震動 ────────────────────────────
rep("charred knockback + particles",
    "          const resist=(e.heat||0)<50?0.65:1.0;\n"
    "          if(resist<1)this.showPop('\U0001f4aa 撐住了！');\n"
    "          else this.showPop('\U0001f4a5 撞飛！');\n"
    "          this.tweens.add({targets:e,\n"
    "            x:e.x+mx*this.dashState.force*resist,\n"
    "            y:e.y+my*this.dashState.force*resist,\n"
    "            duration:260,ease:'Cubic.easeOut',\n"
    "            onComplete:()=>this.checkEnemyFall(e,i)});\n"
    "          // 震屏 + 閃光\n"
    "          this.cameras.main.shake(160,0.007);\n"
    "          const fx=this.add.graphics().setDepth(25);\n"
    "          const fobj={v:0};\n"
    "          this.tweens.add({targets:fobj,v:1,duration:220,ease:'Quad.easeOut',\n"
    "            onUpdate:()=>{fx.clear();const p=fobj.v;fx.lineStyle(5*(1-p),0xffffff,1-p);fx.strokeCircle(e.x,e.y,50*p);},\n"
    "            onComplete:()=>fx.destroy()});",

    "          const resist=(e.heat||0)<50?0.65:1.0;\n"
    "          const charBst=Math.min(2.5,1+(e.heat||0)/100*2);\n"
    "          if(charBst>1.8)this.showPop('\U0001f525 脆了！飛出去！');\n"
    "          else if(resist<1)this.showPop('\U0001f4aa 撐住了！');\n"
    "          else this.showPop('\U0001f4a5 撞飛！');\n"
    "          this.tweens.add({targets:e,\n"
    "            x:e.x+mx*this.dashState.force*resist*charBst,\n"
    "            y:e.y+my*this.dashState.force*resist*charBst,\n"
    "            duration:260,ease:'Cubic.easeOut',\n"
    "            onComplete:()=>this.checkEnemyFall(e,i)});\n"
    "          this.cameras.main.shake(160,0.005+charBst*0.007);\n"
    "          const fx=this.add.graphics().setDepth(25);\n"
    "          const fobj={v:0};\n"
    "          this.tweens.add({targets:fobj,v:1,duration:220,ease:'Quad.easeOut',\n"
    "            onUpdate:()=>{fx.clear();const p=fobj.v;fx.lineStyle(5*(1-p),0xffffff,1-p);fx.strokeCircle(e.x,e.y,50*p);},\n"
    "            onComplete:()=>fx.destroy()});\n"
    "          const gCnt=3+Math.round(charBst*3);\n"
    "          for(let gi=0;gi<gCnt;gi++){\n"
    "            const gObj={px:e.x,py:e.y,life:1};\n"
    "            const gAng=Math.atan2(my,mx)+(Math.random()-0.5)*1.8;\n"
    "            const gDst=50+Math.random()*90;\n"
    "            const gCol=Math.random()<0.5?0xffcc00:0xff6600;\n"
    "            const gGfx=this.add.graphics().setDepth(24);\n"
    "            this.tweens.add({targets:gObj,\n"
    "              px:e.x+Math.cos(gAng)*gDst,py:e.y+Math.sin(gAng)*gDst,life:0,\n"
    "              duration:380+Math.random()*160,ease:'Quad.easeOut',\n"
    "              onUpdate:()=>{gGfx.clear();gGfx.fillStyle(gCol,gObj.life*0.85);\n"
    "                gGfx.fillCircle(gObj.px,gObj.py,gObj.life*5+1);},\n"
    "              onComplete:()=>gGfx.destroy()});\n"
    "          }")

# ── 7. 越熟越黑 - 玩家 ────────────────────────────────────────────
rep("player charring tint",
    "    sprite.setTint(Phaser.Display.Color.GetColor(255,Math.floor(255*(1-t*0.75)),Math.floor(255*(1-t))));",
    "    sprite.setTint(Phaser.Display.Color.GetColor(\n"
    "      Math.round(255*(1-t*0.82)),\n"
    "      Math.round(255*Math.max(0,1-t*1.3)),\n"
    "      Math.round(255*Math.max(0,1-t*1.6))));")

# ── 8. 越熟越黑 - 敵人 ────────────────────────────────────────────
rep("enemy charring tint",
    "        this.enemySprites[i].setTint(Phaser.Display.Color.GetColor(255,Math.floor(255*(1-t*0.7)),Math.floor(255*(1-t))));",
    "        this.enemySprites[i].setTint(Phaser.Display.Color.GetColor(\n"
    "          Math.round(255*(1-t*0.82)),\n"
    "          Math.round(255*Math.max(0,1-t*1.3)),\n"
    "          Math.round(255*Math.max(0,1-t*1.6))));")

# ── 9. 效果顯示加 stun / toxic ────────────────────────────────────
rep("effect display",
    "    if(ae2.slowpow>0) eff2.push('!慢速 '+ae2.slowpow.toFixed(0)+'s');",
    "    if(ae2.slowpow>0) eff2.push('!慢速 '+ae2.slowpow.toFixed(0)+'s');\n"
    "    if(ae2.stun>0)    eff2.push('XX穿刺 '+ae2.stun.toFixed(1)+'s');\n"
    "    if(ae2.toxic>0)   eff2.push('!!焦糖 '+ae2.toxic.toFixed(1)+'s');")

# ── 10. update 裡加事件 + 縮圈呼叫 ──────────────────────────────
rep("event+shrink update calls",
    "    if(this.itemTimer<=0){this.spawnItem();this.itemTimer=5+Math.random()*4;}",
    "    if(this.itemTimer<=0){this.spawnItem();this.itemTimer=5+Math.random()*4;}\n"
    "    this.evtTimer-=dt;\n"
    "    if(this.evtTimer<=0){this.spawnRandEvent();this.evtTimer=15+Math.random()*8;}\n"
    "    this.updateRandEvents(dt); if(!this.alive) return;\n"
    "    this.updateShrink(dt);    if(!this.alive) return;")

# ── 11. 繪製呼叫 ─────────────────────────────────────────────────
rep("draw calls",
    "    this.firePhase+=dt*3;\n    this.drawFires(this.firePhase);",
    "    this.firePhase+=dt*3;\n"
    "    this.drawFires(this.firePhase);\n"
    "    this.drawShrinkRing();\n"
    "    this.drawEventFx();")

# ── 12. 新增五個方法 ──────────────────────────────────────────────
METHODS = """
  spawnRandEvent(){
    const types=['brush','lemon','skewer'];
    const type=types[Math.floor(Math.random()*types.length)];
    if(type==='brush'){
      const fromTop=Math.random()<0.5;
      const sauceType=Math.random()<0.5?'sticky':'toxic';
      this.evtQueue.push({type:'brush',sauceType,
        y:fromTop?G.y-30:G.y+G.h+30,
        dir:fromTop?1:-1, speed:(G.h+60)/3.0,
        h:22, hitPlayer:false, done:false});
      this.showPop(sauceType==='sticky'?'⚠️ 神之刷！（黨醒醬）':'⚠️ 神之刷！（劇毒醬）');
      this.cameras.main.shake(150,0.004);
    }
    if(type==='lemon'){
      const cnt=2+Math.floor(Math.random()*2);
      for(let i=0;i<cnt;i++){
        const lx=G.x+55+Math.random()*(G.w-110);
        const ly=G.y+55+Math.random()*(G.h-110);
        this.evtQueue.push({type:'lemon',x:lx,y:ly,
          state:'warn',timer:0.9+i*0.7,
          fallY:G.y-40,fallSpd:60,splashR:0,done:false});
      }
      this.showPop('\U0001f34b 檬檬雨！快跑！');
    }
    if(type==='skewer'){
      const cnt=1+Math.floor(Math.random()*2);
      for(let i=0;i<cnt;i++){
        const kx=G.x+45+Math.random()*(G.w-90);
        const ky=G.y+45+Math.random()*(G.h-90);
        this.evtQueue.push({type:'skewer',x:kx,targetY:ky,
          state:'warn',timer:1.6,curY:G.y-80,done:false});
      }
      this.showPop('⚠️ 竹簽串！快閃！');
      this.cameras.main.shake(100,0.003);
    }
  }

  updateRandEvents(dt){
    const ae=this.activeEffects;
    this.evtQueue=this.evtQueue.filter(ev=>{
      if(ev.done) return false;
      // ── brush ──────────────────────────────────────────────────
      if(ev.type==='brush'){
        ev.y+=ev.dir*ev.speed*dt;
        if(ev.y>G.y-5&&ev.y<G.y+G.h+5&&!ev.hitPlayer){
          const bT=ev.y-ev.h/2, bB=ev.y+ev.h/2;
          if(this.p.y>=bT&&this.p.y<=bB){
            ev.hitPlayer=true;
            if(ev.sauceType==='sticky') ae.slowpow=Math.max(ae.slowpow,4.0);
            else                        ae.toxic  =Math.max(ae.toxic,3.5);
            this.cameras.main.shake(100,0.005);
          }
        }
        if(ev.dir>0&&ev.y>G.y+G.h+40) ev.done=true;
        if(ev.dir<0&&ev.y<G.y-40)     ev.done=true;
        return !ev.done;
      }
      // ── lemon ──────────────────────────────────────────────────
      if(ev.type==='lemon'){
        ev.timer-=dt;
        if(ev.state==='warn'){
          if(ev.timer<=0) ev.state='fall';
        } else if(ev.state==='fall'){
          ev.fallSpd+=340*dt;
          ev.fallY+=ev.fallSpd*dt;
          if(ev.fallY>=ev.y){
            ev.state='splash'; ev.splashR=8; ev.timer=0.55;
            const dist=Math.hypot(this.p.x-ev.x,this.p.y-ev.y);
            if(dist<72){
              const ddx=(this.p.x-ev.x)/(dist||1);
              const ddy=(this.p.y-ev.y)/(dist||1);
              const force=(1-dist/72)*200;
              const nx2=this.p.x+ddx*force, ny2=this.p.y+ddy*force;
              this.cameras.main.shake(280,0.015);
              if(!inGrill(nx2,ny2)){
                this.subTxt.setText('被檬檬汁喵飛！');this.endGame(false);
              } else {
                this.p.x=nx2; this.p.y=ny2;
                this.showPop('\U0001f4a6 被咮飛！');
              }
            }
          }
        } else if(ev.state==='splash'){
          ev.splashR+=(90-ev.splashR)*dt*6;
          ev.timer-=dt;
          if(ev.timer<=0) ev.done=true;
        }
        return !ev.done;
      }
      // ── skewer ─────────────────────────────────────────────────
      if(ev.type==='skewer'){
        ev.timer-=dt;
        if(ev.state==='warn'&&ev.timer<=0){
          ev.state='strike'; ev.timer=0.18;
        } else if(ev.state==='strike'){
          const prog=Math.max(0,1-ev.timer/0.18);
          ev.curY=(G.y-80)+(ev.targetY-G.y+80)*prog;
          if(ev.timer<=0){
            ev.state='stuck'; ev.timer=1.8; ev.curY=ev.targetY;
            if(Math.hypot(this.p.x-ev.x,this.p.y-ev.targetY)<30){
              ae.stun=Math.max(ae.stun,2.0);
              this.cameras.main.shake(340,0.016);
              this.showPop('⚡ 被竹簽穿了！不能動！');
            }
          }
        } else if(ev.state==='stuck'){
          if(ev.timer<=0){ev.state='retract';ev.timer=0.28;}
        } else if(ev.state==='retract'){
          const prog=Math.max(0,1-ev.timer/0.28);
          ev.curY=ev.targetY+(G.y-90-ev.targetY)*prog;
          if(ev.timer<=0) ev.done=true;
        }
        return !ev.done;
      }
      return false;
    });
  }

  drawEventFx(){
    const g=this.eventLayer; g.clear();
    const ph=this.firePhase;
    this.evtQueue.forEach(ev=>{
      // ── brush ────────────────────────────────────────────────
      if(ev.type==='brush'){
        const sC=ev.sauceType==='sticky'?0xcc5500:0x228800;
        const sC2=ev.sauceType==='sticky'?0xff8800:0x66ee22;
        // 掃過的醬料痕跡
        if(ev.dir>0&&ev.y>G.y){
          g.fillStyle(sC,0.12);
          g.fillRect(G.x,G.y,G.w,Math.min(ev.y-G.y,G.h));
        } else if(ev.dir<0&&ev.y<G.y+G.h){
          const top=Math.max(ev.y,G.y);
          g.fillStyle(sC,0.12);
          g.fillRect(G.x,top,G.w,G.y+G.h-top);
        }
        // 刷子本體（木柄 + 刷頭）
        if(ev.y>G.y-50&&ev.y<G.y+G.h+50){
          g.fillStyle(0x8B4513,0.95);
          g.fillRect(G.x,ev.y-ev.h/2-20,G.w,20);
          g.fillStyle(sC,0.95);
          g.fillRect(G.x,ev.y-ev.h/2,G.w,ev.h);
          for(let i=0;i<10;i++){
            const dx=G.x+(i/9)*G.w;
            g.fillStyle(sC2,0.75);
            g.fillEllipse(dx,ev.y+ev.h/2+Math.sin(ph*3.5+i)*3,5,7+Math.abs(Math.sin(ph*4+i))*4);
          }
        }
      }
      // ── lemon ────────────────────────────────────────────────
      if(ev.type==='lemon'){
        if(ev.state==='warn'){
          const pulse=0.18+0.14*Math.sin(ph*9);
          g.fillStyle(0xffff00,pulse); g.fillEllipse(ev.x,ev.y,80,80);
          g.lineStyle(3,0xddcc00,0.5+pulse); g.strokeEllipse(ev.x,ev.y,80,80);
          g.lineStyle(3,0xff8800,0.75);
          g.lineBetween(ev.x-14,ev.y-14,ev.x+14,ev.y+14);
          g.lineBetween(ev.x+14,ev.y-14,ev.x-14,ev.y+14);
        } else if(ev.state==='fall'){
          const fy=ev.fallY;
          const prog=Math.max(0,Math.min(1,(fy-(G.y-40))/(ev.y-(G.y-40)+1)));
          const r=12+prog*22;
          g.fillStyle(0xffff33,0.92); g.fillCircle(ev.x,fy,r);
          g.fillStyle(0xffffaa,0.5); g.fillCircle(ev.x-r*0.25,fy-r*0.2,r*0.3);
          g.fillStyle(0xaaaa00,0.08+prog*0.28);
          g.fillEllipse(ev.x,ev.y,(1.3-prog)*70,(1.3-prog)*25);
        } else if(ev.state==='splash'){
          const r=ev.splashR, a=Math.max(0,1-r/90);
          g.fillStyle(0xffff55,0.28*a); g.fillCircle(ev.x,ev.y,r);
          g.lineStyle(3,0xffcc00,0.8*a); g.strokeCircle(ev.x,ev.y,r);
          for(let i=0;i<8;i++){
            const ang=i*Math.PI/4;
            g.fillStyle(0xffff00,0.7*a);
            g.fillCircle(ev.x+Math.cos(ang)*r*0.65,ev.y+Math.sin(ang)*r*0.65,5);
          }
          g.fillStyle(0xcccc00,0.6*a); g.fillEllipse(ev.x,ev.y,28,16);
        }
      }
      // ── skewer ───────────────────────────────────────────────
      if(ev.type==='skewer'){
        if(ev.state==='warn'){
          const pulse=0.3+0.28*Math.sin(ph*11);
          g.fillStyle(0xff8800,pulse); g.fillEllipse(ev.x,ev.targetY,58,20);
          g.lineStyle(3,0xffaa00,0.55+pulse); g.strokeEllipse(ev.x,ev.targetY,58,20);
          g.lineStyle(4,0xff4400,0.75); g.strokeCircle(ev.x,ev.targetY,28);
        } else if(ev.state==='strike'||ev.state==='stuck'){
          const top=ev.curY, bot=ev.targetY+28;
          g.fillStyle(0xcc8844,1.0); g.fillRect(ev.x-5,top,10,bot-top);
          g.fillStyle(0xffe8cc,0.9);
          g.fillTriangle(ev.x-5,bot,ev.x+5,bot,ev.x,bot+14);
          g.fillStyle(0xffffff,0.25); g.fillRect(ev.x-2,top,3,bot-top);
          if(ev.state==='stuck'){
            const pr=10+Math.sin(ph*7)*4;
            g.lineStyle(2,0xffcc44,0.45); g.strokeCircle(ev.x,ev.targetY,pr);
            g.lineStyle(1,0xffcc44,0.22); g.strokeCircle(ev.x,ev.targetY,pr*1.9);
          }
        }
      }
    });
  }

  updateShrink(dt){
    if(this.shrinkPad>=this.shrinkMax) return;
    this.shrinkTimer-=dt;
    if(this.shrinkTimer<=0&&!this.shrinkWarning){
      this.shrinkWarning=true; this.shrinkWarnTimer=3.2;
      this.showPop('\U0001f525 燒盤邊緬要崩了！');
      this.cameras.main.shake(200,0.005);
    }
    if(this.shrinkWarning){
      this.shrinkWarnTimer-=dt;
      if(this.shrinkWarnTimer<=0){
        this.shrinkPad=Math.min(this.shrinkMax,this.shrinkPad+this.shrinkStep);
        this.shrinkWarning=false;
        this.shrinkTimer=18+Math.random()*8;
        this.cameras.main.shake(480,0.014);
        this.showPop('\U0001f480 邊緬崩塌！中心死鬥！');
        const pad=this.shrinkPad;
        if(this.p.x<G.x+pad+2||this.p.x>G.x+G.w-pad-2||
           this.p.y<G.y+pad+2||this.p.y>G.y+G.h-pad-2){
          this.subTxt.setText('掉進火坑了！'); this.endGame(false); return;
        }
        this.enemies.forEach((e,i)=>{
          if(!e.alive)return;
          if(e.x<G.x+pad||e.x>G.x+G.w-pad||e.y<G.y+pad||e.y>G.y+G.h-pad)
            this.checkEnemyFall(e,i);
        });
      }
    }
    // 在縮圈邊緣快速加熱
    const pad=this.shrinkPad;
    if(pad>0){
      const edge=10;
      const inDanger=this.p.x<G.x+pad+edge||this.p.x>G.x+G.w-pad-edge||
                     this.p.y<G.y+pad+edge||this.p.y>G.y+G.h-pad-edge;
      if(inDanger){
        const heatCap=this.abilityActive&&this.abilityActive.type==='shield'?130:100;
        this.heat=Math.min(heatCap,this.heat+24*dt);
        this.sizzleTimer-=dt;
        if(this.sizzleTimer<=0){this.playSound('sizzle');this.sizzleTimer=0.4;}
      }
      this.p.x=Phaser.Math.Clamp(this.p.x,G.x+pad+2,G.x+G.w-pad-2);
      this.p.y=Phaser.Math.Clamp(this.p.y,G.y+pad+2,G.y+G.h-pad-2);
    }
  }

  drawShrinkRing(){
    const g=this.shrinkLayer; g.clear();
    const ph=this.firePhase;
    const pad=this.shrinkPad;
    const step=this.shrinkStep;
    if(pad>0){
      g.fillStyle(0x0d0000,0.90);
      g.fillRect(G.x,G.y,G.w,pad);
      g.fillRect(G.x,G.y+G.h-pad,G.w,pad);
      g.fillRect(G.x,G.y+pad,pad,G.h-pad*2);
      g.fillRect(G.x+G.w-pad,G.y+pad,pad,G.h-pad*2);
      const glow=0.5+0.3*Math.sin(ph*3.5);
      g.lineStyle(4,0xff2200,glow); g.strokeRect(G.x+pad,G.y+pad,G.w-pad*2,G.h-pad*2);
      g.lineStyle(1,0xff6600,glow*0.5); g.strokeRect(G.x+pad+3,G.y+pad+3,G.w-pad*2-6,G.h-pad*2-6);
    }
    if(this.shrinkWarning){
      const np=pad+step;
      const blink=0.22+0.38*Math.sin(ph*(9+((3.2-this.shrinkWarnTimer)/3.2)*8));
      g.fillStyle(0xff4400,blink*0.2);
      g.fillRect(G.x+pad,G.y+pad,G.w-pad*2,step);
      g.fillRect(G.x+pad,G.y+G.h-pad-step,G.w-pad*2,step);
      g.fillRect(G.x+pad,G.y+pad+step,step,G.h-pad*2-step*2);
      g.fillRect(G.x+G.w-pad-step,G.y+pad+step,step,G.h-pad*2-step*2);
      g.lineStyle(3,0xff8800,0.5+0.5*Math.sin(ph*14));
      g.strokeRect(G.x+np,G.y+np,G.w-np*2,G.h-np*2);
    }
  }
"""

rep("new methods",
    "  }\n}\n\nnew Phaser.Game({",
    "  }\n" + METHODS + "}\n\nnew Phaser.Game({")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

for r in results:
    print(r)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
checks = [
    ("stun:0,toxic:0",   "activeEffects stun/toxic"),
    ("shrinkPad=0",       "shrink init"),
    ("evtQueue=[]",       "event queue"),
    ("eventLayer",        "eventLayer"),
    ("shrinkLayer",       "shrinkLayer"),
    ("stun>0){mx=0",      "stun block"),
    ("ae.toxic>0",        "toxic heat"),
    ("charBst",           "charred knockback"),
    ("gObj.life",         "grease particles"),
    ("1-t*0.82",          "charring tint"),
    ("spawnRandEvent",    "spawnRandEvent method"),
    ("updateRandEvents",  "updateRandEvents method"),
    ("drawEventFx",       "drawEventFx method"),
    ("updateShrink",      "updateShrink method"),
    ("drawShrinkRing",    "drawShrinkRing method"),
]
for key, label in checks:
    print(f"{label}: {'OK' if key in v else 'MISSING'}")
