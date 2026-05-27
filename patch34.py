# -*- coding: utf-8 -*-
# Patch 34: 碰撞推擠 + 大絕招系統（收集3顆能量球 → Q鍵大絕 + 全螢幕演出）
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

# ── 1. 加 Q 鍵 ────────────────────────────────────────────────────
rep("ult key",
    "      skill:Phaser.Input.Keyboard.KeyCodes.SPACE,",
    "      skill:Phaser.Input.Keyboard.KeyCodes.SPACE,\n"
    "      ult:Phaser.Input.Keyboard.KeyCodes.Q,")

# ── 2. init 加大絕變數 ────────────────────────────────────────────
rep("ult init vars",
    "    this.abilityCD=0; this.abilityCDMax=6; this.abilityActive=null; this.abilityWas=false;",
    "    this.abilityCD=0; this.abilityCDMax=6; this.abilityActive=null; this.abilityWas=false;\n"
    "    this.ultCharge=0; this.ultMax=3; this.ultWas=false; this.ultCinema=false;\n"
    "    this.ultSpeedTimer=0; this.ultOrbs=[]; this.ultOrbTimer=12;\n"
    "    this.enemyCC={stun:0,slow:0};")

# ── 3. UI 大絕充能指示 ─────────────────────────────────────────────
rep("ult ui dots",
    "    this.abilCdTxt=this.add.text(216,70,'Ready!',ts(11,'#ffdd44'));",
    "    this.abilCdTxt=this.add.text(216,70,'Ready!',ts(11,'#ffdd44'));\n"
    "    this.add.text(12,93,'[Q] 大絕',ts(10,'#ff88ff'));\n"
    "    this.ultDots=[];\n"
    "    for(let u=0;u<3;u++){\n"
    "      this.ultDots.push(this.add.circle(88+u*18,100,6,0x333333).setDepth(20));\n"
    "    }")

# ── 4. Q 鍵處理 ───────────────────────────────────────────────────
rep("ult key handler",
    "    this.abilityWas=this.keys.skill.isDown;",
    "    this.abilityWas=this.keys.skill.isDown;\n"
    "    if(this.keys.ult.isDown&&!this.ultWas&&this.ultCharge>=this.ultMax&&!this.ultCinema) this.doUltimate();\n"
    "    this.ultWas=this.keys.ult.isDown;")

# ── 5. 玩家速度加大絕速度倍率 ────────────────────────────────────
rep("ult speed mult",
    "    const SPD=isDash?120:this.charData.speed*(this.activeEffects.slowpow>0?0.5:1);",
    "    this.ultSpeedTimer=Math.max(0,this.ultSpeedTimer-dt);\n"
    "    const ultSpd=this.ultSpeedTimer>0?1.8:1.0;\n"
    "    const SPD=isDash?120:this.charData.speed*(this.activeEffects.slowpow>0?0.5:1)*ultSpd;")

# ── 6. AI forEach 加暈眩/減速守衛 ────────────────────────────────
rep("ai cc guard",
    "      if(!e.alive){if(this.enemySprites[i])this.enemySprites[i].setVisible(false);return;}\n"
    "      // 難度決定積極度與反應品質，速度固定\n"
    "      const diff=this.aiDiff??1;",
    "      if(!e.alive){if(this.enemySprites[i])this.enemySprites[i].setVisible(false);return;}\n"
    "      if(this.enemyCC.stun>0){\n"
    "        e.vx*=0.88;e.vy*=0.88;e.x+=e.vx;e.y+=e.vy;\n"
    "        if(this.enemySprites[i])this.enemySprites[i].setPosition(e.x,e.y).setVisible(true);\n"
    "        return;\n"
    "      }\n"
    "      const sSlow=this.enemyCC.slow>0?0.5:1.0;\n"
    "      // 難度決定積極度與反應品質，速度固定\n"
    "      const diff=this.aiDiff??1;")

# ── 7. AI maxSpd 套用減速 ─────────────────────────────────────────
rep("ai maxspd slow",
    "      const maxSpd=e.charging?4.5:2.8;",
    "      const maxSpd=(e.charging?4.5:2.8)*sSlow;")

# ── 8. 碰撞系統 + 計時器（插在 AI forEach 後）────────────────────
rep("collision and timers",
    "    });\n\n    // 道具效果倒計時\n"
    "    const ae2=this.activeEffects;\n"
    "    Object.keys(ae2).forEach(k=>{if(ae2[k]>0)ae2[k]=Math.max(0,ae2[k]-dt);});",

    "    });\n\n"
    "    // ── 碰撞：角色互不穿越 ──────────────────────────\n"
    "    const CR=19;\n"
    "    this.enemies.forEach(e=>{\n"
    "      if(!e.alive)return;\n"
    "      const dx=this.p.x-e.x,dy=this.p.y-e.y,d=Math.hypot(dx,dy)||1;\n"
    "      if(d<CR*2){const ov=(CR*2-d)/2,nx=dx/d,ny=dy/d;\n"
    "        const px2=this.p.x+nx*ov,py2=this.p.y+ny*ov;\n"
    "        if(inGrill(px2,py2)){this.p.x=px2;this.p.y=py2;}\n"
    "        e.x-=nx*ov;e.y-=ny*ov;}\n"
    "    });\n"
    "    for(let ai=0;ai<this.enemies.length-1;ai++){\n"
    "      const ea=this.enemies[ai];if(!ea.alive)continue;\n"
    "      for(let bi=ai+1;bi<this.enemies.length;bi++){\n"
    "        const eb=this.enemies[bi];if(!eb.alive)continue;\n"
    "        const dx2=ea.x-eb.x,dy2=ea.y-eb.y,d2=Math.hypot(dx2,dy2)||1;\n"
    "        if(d2<CR*2){const ov2=(CR*2-d2)/2,nx2=dx2/d2,ny2=dy2/d2;\n"
    "          ea.x+=nx2*ov2;ea.y+=ny2*ov2;eb.x-=nx2*ov2;eb.y-=ny2*ov2;}\n"
    "      }\n"
    "    }\n"
    "    // 道具效果倒計時\n"
    "    const ae2=this.activeEffects;\n"
    "    Object.keys(ae2).forEach(k=>{if(ae2[k]>0)ae2[k]=Math.max(0,ae2[k]-dt);});\n"
    "    if(this.enemyCC.stun>0)this.enemyCC.stun=Math.max(0,this.enemyCC.stun-dt);\n"
    "    if(this.enemyCC.slow>0)this.enemyCC.slow=Math.max(0,this.enemyCC.slow-dt);\n"
    "    this.ultOrbTimer-=dt;\n"
    "    if(this.ultOrbTimer<=0&&this.ultCharge<this.ultMax){this.spawnUltOrb();this.ultOrbTimer=12+Math.random()*6;}\n"
    "    this.updateUltOrbs(dt);")

# ── 9. draw 更新大絕 UI ───────────────────────────────────────────
rep("ult ui update",
    "    this.abilCdTxt.setText(aReady?'Ready!':this.abilityCD.toFixed(1)+'s');",
    "    this.abilCdTxt.setText(aReady?'Ready!':this.abilityCD.toFixed(1)+'s');\n"
    "    this.updateUltUI();")

# ── 10. 新增大絕相關方法 ──────────────────────────────────────────
ULT_METHODS = """
  doUltimate(){
    if(this.ultCinema||this.ultCharge<this.ultMax)return;
    this.ultCinema=true; this.ultCharge=0; this.updateUltUI();
    const NAMES={pork:'油爆四濺',beef:'鐵板衝鋒',mushroom:'孢子迷霧',
      corn:'爆米花連炸',wing:'旋風疾飛',shrimp:'衝擊浪潮',
      tofu:'冷卻護盾',bacon:'煙燻覆蓋',pepper:'辣椒震波',saury:'魚骨連射'};
    const ultName=NAMES[this.charData.key]||'大絕招';
    const ovBg=this.add.rectangle(W/2,H/2,W,H,0x000000,0).setDepth(88);
    const ovFlash=this.add.rectangle(W/2,H/2,W,H,0xffffff,1).setDepth(89).setAlpha(0);
    const ovT1=this.add.text(W/2,H/2-36,this.charData.name+' 的大絕招！',
      {fontSize:'30px',color:'#ffdd44',fontFamily:'sans-serif',fontStyle:'bold',
       stroke:'#000000',strokeThickness:7}).setOrigin(0.5).setDepth(90).setAlpha(0);
    const ovT2=this.add.text(W/2,H/2+18,'✦ '+ultName+' ✦',
      {fontSize:'24px',color:'#ffffff',fontFamily:'sans-serif',fontStyle:'bold',
       stroke:'#000000',strokeThickness:5}).setOrigin(0.5).setDepth(90).setAlpha(0);
    // 白閃 → 黑幕 → 文字 → 放技能 → 淡出
    this.tweens.add({targets:ovFlash,alpha:{from:0.9,to:0},duration:200,onComplete:()=>{
      this.tweens.add({targets:ovBg,alpha:{from:0,to:0.82},duration:260,onComplete:()=>{
        this.tweens.add({targets:[ovT1,ovT2],alpha:1,duration:160,onComplete:()=>{
          this.time.delayedCall(480,()=>{
            this.fireUltimate();
            this.cameras.main.shake(360,0.018);
            this.tweens.add({targets:[ovBg,ovT1,ovT2,ovFlash],alpha:0,duration:500,
              onComplete:()=>{
                ovBg.destroy();ovT1.destroy();ovT2.destroy();ovFlash.destroy();
                this.ultCinema=false;
              }});
          });
        }});
      }});
    }});
  }

  fireUltimate(){
    const ck=this.charData.key;
    const aliveE=this.enemies.filter(e=>e.alive);
    const gBurst=(ox,oy,cnt,col)=>{
      for(let g=0;g<cnt;g++){
        const go={px:ox,py:oy,life:1};
        const ang=Math.random()*Math.PI*2,dst=55+Math.random()*90;
        const gfx=this.add.graphics().setDepth(24);
        this.tweens.add({targets:go,px:ox+Math.cos(ang)*dst,py:oy+Math.sin(ang)*dst,life:0,
          duration:350+Math.random()*150,ease:'Quad.easeOut',
          onUpdate:()=>{gfx.clear();gfx.fillStyle(col,go.life*0.9);gfx.fillCircle(go.px,go.py,go.life*6+2);},
          onComplete:()=>gfx.destroy()});
      }
    };
    switch(ck){
      case 'pork': case 'shrimp':{
        const force=ck==='pork'?230:160;
        aliveE.forEach((e,i)=>{
          const dx=e.x-this.p.x,dy=e.y-this.p.y,d=Math.hypot(dx,dy)||1;
          this.tweens.add({targets:e,x:e.x+dx/d*force,y:e.y+dy/d*force,
            duration:350,ease:'Cubic.easeOut',onComplete:()=>this.checkEnemyFall(e,i)});
        });
        gBurst(this.p.x,this.p.y,16,ck==='pork'?0xffcc00:0x88ccff);
        break;}
      case 'beef':
        this.dashState={active:true,dx:this.lastDir.x,dy:this.lastDir.y,dist:0,maxDist:330,force:350};
        break;
      case 'mushroom': case 'pepper':
        this.enemyCC.stun=Math.max(this.enemyCC.stun,ck==='mushroom'?4.0:2.5);
        gBurst(W/2,H/2,18,ck==='mushroom'?0x88ff88:0xff6622);
        this.showPop(ck==='mushroom'?'🍄 孢子迷霧！敵人暈眩！':'🌶 辣椒震波！全員暈眩！');
        break;
      case 'corn':
        for(let b=0;b<5;b++){
          const bx=G.x+70+Math.random()*(G.w-140),by=G.y+70+Math.random()*(G.h-140);
          this.time.delayedCall(b*200,()=>{
            if(!this.alive)return;
            this.cameras.main.shake(100,0.007);
            gBurst(bx,by,8,0xffdd00);
            this.enemies.forEach((e,i)=>{
              if(!e.alive)return;
              const d2=Math.hypot(e.x-bx,e.y-by);
              if(d2<130){const nx=(e.x-bx)/(d2||1),ny=(e.y-by)/(d2||1);
                this.tweens.add({targets:e,x:e.x+nx*130,y:e.y+ny*130,
                  duration:260,ease:'Cubic.easeOut',onComplete:()=>this.checkEnemyFall(e,i)});}
            });
          });
        }
        break;
      case 'wing':
        this.activeEffects.foil=Math.max(this.activeEffects.foil,5);
        this.ultSpeedTimer=5;
        this.showPop('🪽 旋風疾飛！速度爆發！');
        gBurst(this.p.x,this.p.y,12,0x44ffee);
        break;
      case 'tofu':
        this.heat=Math.max(0,this.heat-70);
        this.abilityActive={type:'shield',timer:4.0};
        this.showPop('💧 冷卻護盾！熱度大降！');
        gBurst(this.p.x,this.p.y,10,0xaaddff);
        break;
      case 'bacon':
        this.enemyCC.slow=Math.max(this.enemyCC.slow,5);
        gBurst(W/2,H/2,14,0x996644);
        this.showPop('🥓 煙燻覆蓋！全場減速！');
        break;
      case 'saury':
        for(let t=0;t<3;t++){
          this.time.delayedCall(t*260,()=>{
            if(!this.alive||!aliveE.length)return;
            const ne=aliveE.reduce((a,b)=>
              Math.hypot(a.x-this.p.x,a.y-this.p.y)<=Math.hypot(b.x-this.p.x,b.y-this.p.y)?a:b);
            if(!ne)return;
            const dd=Math.hypot(ne.x-this.p.x,ne.y-this.p.y)||1;
            this.dashState={active:true,dx:(ne.x-this.p.x)/dd,dy:(ne.y-this.p.y)/dd,
              dist:0,maxDist:200,force:180};
          });
        }
        break;
    }
  }

  spawnUltOrb(){
    const margin=70;
    const x=G.x+margin+Math.random()*(G.w-margin*2);
    const y=G.y+margin+Math.random()*(G.h-margin*2);
    const gfx=this.add.graphics().setDepth(17);
    this.ultOrbs.push({x,y,gfx,life:18,ph:Math.random()*Math.PI*2});
  }

  updateUltOrbs(dt){
    this.ultOrbs=this.ultOrbs.filter(orb=>{
      orb.life-=dt; orb.ph+=dt*3;
      const glow=0.5+0.5*Math.sin(orb.ph);
      orb.gfx.clear();
      orb.gfx.fillStyle(0xdd88ff,0.2+glow*0.3); orb.gfx.fillCircle(orb.x,orb.y,18+glow*4);
      orb.gfx.fillStyle(0xffffff,0.95);          orb.gfx.fillCircle(orb.x,orb.y,6);
      orb.gfx.lineStyle(2,0xff88ff,0.55+glow*0.45);
      orb.gfx.strokeCircle(orb.x,orb.y,13+glow*3);
      if(orb.life<=0){orb.gfx.destroy();return false;}
      if(Math.hypot(this.p.x-orb.x,this.p.y-orb.y)<22&&this.ultCharge<this.ultMax){
        this.ultCharge++;
        this.updateUltUI();
        const msg=this.ultCharge>=this.ultMax?'✦ 大絕蓄滿！按 [Q] 釋放！':'✦ 大絕充能 '+this.ultCharge+'/'+this.ultMax;
        this.showPop(msg);
        const fx=this.add.graphics().setDepth(28); const fo={v:0};
        this.tweens.add({targets:fo,v:1,duration:300,
          onUpdate:()=>{fx.clear();fx.lineStyle(4*(1-fo.v),0xff88ff,1-fo.v);fx.strokeCircle(orb.x,orb.y,42*fo.v);},
          onComplete:()=>fx.destroy()});
        orb.gfx.destroy(); return false;
      }
      return true;
    });
  }

  updateUltUI(){
    if(!this.ultDots)return;
    const full=this.ultCharge>=this.ultMax;
    this.ultDots.forEach((d,u)=>{
      d.setFillStyle(u<this.ultCharge?(full?0xffaaff:0xff88ff):0x333333);
    });
  }
"""

rep("ult methods",
    "  }\n}\n\nnew Phaser.Game({",
    "  }\n" + ULT_METHODS + "}\n\nnew Phaser.Game({")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

for r in results:
    print(r)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
checks = [
    ("KeyCodes.Q",            "Q key"),
    ("this.ultCharge=0",      "ultCharge init"),
    ("this.enemyCC=",         "enemyCC init"),
    ("ultDots=[]",            "ult dots UI"),
    ("keys.ult.isDown",       "Q key handler"),
    ("ultSpeedTimer",         "speed timer"),
    ("enemyCC.stun>0",        "ai stun guard"),
    ("sSlow=this.enemyCC",    "ai slow var"),
    ("CR=19",                 "collision radius"),
    ("ea.x+=nx2*ov2",         "enemy-enemy push"),
    ("ultOrbTimer",           "orb timer"),
    ("doUltimate",            "doUlt method"),
    ("fireUltimate",          "fireUlt method"),
    ("spawnUltOrb",           "spawnOrb method"),
    ("updateUltOrbs",         "updateOrbs method"),
    ("updateUltUI",           "updateUltUI method"),
    ("case 'saury'",          "saury ult"),
    ("case 'corn'",           "corn ult"),
    ("✦ 大絕蓄滿",            "orb pickup msg"),
]
for key, label in checks:
    print(f"{label}: {'OK' if key in v else 'MISSING'}")
