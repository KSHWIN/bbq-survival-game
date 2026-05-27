# -*- coding: utf-8 -*-
# Patch 40: Center Orb + All 10 Enhanced Ultimates + Game Feel

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
        print(f"FAIL [{label}] - not found in HTML")

# ── 1. Add state vars in create() ──────────────────────────────────────
rep("ultState vars",
    "this.ultSpeedTimer=0; this.ultOrbs=[]; this.ultOrbTimer=2;",
    "this.ultSpeedTimer=0; this.ultOrbs=[]; this.ultOrbTimer=2;\n"
    "    this.centerOrbTimer=45; this.centerOrb=null; this.ultState=null;"
)

# ── 2. Update loop: center orb + ultState ──────────────────────────────
rep("update centerOrb ultState",
    "    this.updateUltOrbs(dt);",
    "    this.updateUltOrbs(dt);\n"
    "    if(!this.centerOrb){this.centerOrbTimer-=dt;if(this.centerOrbTimer<=0){this.spawnCenterOrb();this.centerOrbTimer=45;}}\n"
    "    this.updateCenterOrb(dt);\n"
    "    if(this.ultState)this.updateUltState(dt);"
)

# ── 3. Game feel in doUltimate(): time slow + vignette ─────────────────
rep("game feel ult",
    "    this.ultCinema=true; this.ultCharge=0; this.updateUltUI();",
    "    this.ultCinema=true; this.ultCharge=0; this.updateUltUI();\n"
    "    this.time.timeScale=0.06;\n"
    "    this.time.delayedCall(140,()=>{if(this.time)this.time.timeScale=1;});\n"
    "    const _vig=this.add.rectangle(W/2,H/2,W,H,0x000000,0).setDepth(87);\n"
    "    this.tweens.add({targets:_vig,alpha:{from:0,to:0.55},duration:100,yoyo:true,hold:250,\n"
    "      onComplete:()=>_vig.destroy()});"
)

# ── 4. Reversed controls support (pepper ult) ──────────────────────────
rep("reversed controls",
    "    let mx=0, my=0;\n"
    "    if(this.keys.left.isDown  ||GKEYS['ArrowLeft'])  mx=-1;\n"
    "    if(this.keys.right.isDown ||GKEYS['ArrowRight']) mx=1;\n"
    "    if(this.keys.up.isDown    ||GKEYS['ArrowUp'])    my=-1;\n"
    "    if(this.keys.down.isDown  ||GKEYS['ArrowDown'])  my=1;",
    "    let mx=0, my=0;\n"
    "    const _ctrlRev=(this.ultState&&this.ultState.reversed)?-1:1;\n"
    "    if(this.keys.left.isDown  ||GKEYS['ArrowLeft'])  mx=-_ctrlRev;\n"
    "    if(this.keys.right.isDown ||GKEYS['ArrowRight']) mx=_ctrlRev;\n"
    "    if(this.keys.up.isDown    ||GKEYS['ArrowUp'])    my=-_ctrlRev;\n"
    "    if(this.keys.down.isDown  ||GKEYS['ArrowDown'])  my=_ctrlRev;"
)

# ── 5. Wing flying suppresses movement ─────────────────────────────────
rep("wing flying suppress",
    "    if(this.activeEffects.stun>0){mx=0;my=0;if(isDash&&this.dashState)this.dashState.active=false;}",
    "    if(this.activeEffects.stun>0){mx=0;my=0;if(isDash&&this.dashState)this.dashState.active=false;}\n"
    "    if(this.ultState&&this.ultState.flying){mx=0;my=0;}"
)

# ── 6. Speed multiplier from ultState ─────────────────────────────────
rep("speed ultState mul",
    "    const SPD=isDash?120:this.charData.speed*(this.activeEffects.slowpow>0?0.5:1)*ultSpd;",
    "    const _ultSpdMul=(this.ultState&&this.ultState.spdMul)?this.ultState.spdMul:1;\n"
    "    const SPD=isDash?120:this.charData.speed*(this.activeEffects.slowpow>0?0.5:1)*ultSpd*_ultSpdMul;"
)

# ── 7. Skill key: mushroom blink + wing bomb override ──────────────────
rep("skill key override",
    "    if(this.keys.skill.isDown&&!this.abilityWas&&this.abilityCD<=0) this.useAbility();",
    "    if(this.keys.skill.isDown&&!this.abilityWas){\n"
    "      if(this.ultState&&this.ultState.blinks>0) this.doUltBlink();\n"
    "      else if(this.ultState&&this.ultState.flying&&this.ultState.bombs>0) this.dropWingBomb();\n"
    "      else if(this.abilityCD<=0) this.useAbility();\n"
    "    }"
)

# ── 8. Heat stop for beef + dynamic heatCap ────────────────────────────
rep("heat stop beef",
    "    const mult=this.charData.heatMult*(ae.sauce>0?2:1)*(armorOn?0.5:1)*this.levelData.heatMod;",
    "    const _hsMul=(this.ultState&&this.ultState.heatStop)?0:1;\n"
    "    const mult=_hsMul*this.charData.heatMult*(ae.sauce>0?2:1)*(armorOn?0.5:1)*this.levelData.heatMod;"
)

rep("dynamic heatCap",
    "    const heatCap=shieldOn?130:100;",
    "    const heatCap=(this.ultState&&this.ultState.heatMax)?this.ultState.heatMax:(shieldOn?130:100);"
)

# ── 9. Pork 4x push multiplier in doPush() ────────────────────────────
rep("pork push mul",
    "    const DIST=Math.round(115*spd)*boost*myBst;  // 快→遠\n"
    "    const FORCE=Math.round(140*wgt)*boost*myBst*wingBst; // 重→強",
    "    const _pMul=(this.ultState&&this.ultState.pushMul)?this.ultState.pushMul:1;\n"
    "    const DIST=Math.round(115*spd)*boost*myBst*_pMul;  // 快→遠\n"
    "    const FORCE=Math.round(140*wgt)*boost*myBst*wingBst*_pMul; // 重→強"
)

# ── 10. Beef knockback resistance (enemy push on player) ───────────────
rep("beef knockRes",
    "          if(pTgt.isPlayer){\n"
    "            const cBst=Math.min(1.5,1+this.heat/100*0.8);\n"
    "            this.tweens.add({targets:this.p,\n"
    "              x:this.p.x+pnx*pForce*cBst,y:this.p.y+pny*pForce*cBst,",
    "          if(pTgt.isPlayer){\n"
    "            const _kRes=(this.ultState&&this.ultState.knockRes)?this.ultState.knockRes:1;\n"
    "            const cBst=Math.min(1.5,1+this.heat/100*0.8);\n"
    "            this.tweens.add({targets:this.p,\n"
    "              x:this.p.x+pnx*pForce*cBst*_kRes,y:this.p.y+pny*pForce*cBst*_kRes,"
)

# ── 11. AI: center orb bias ───────────────────────────────────────────
rep("AI center orb bias",
    "      // 油漬：在油上無法發動衝刺、無法轉向（只能滑行）",
    "      // 中央大絕道具：吸引 AI 往中心移動\n"
    "      if(this.centerOrb){\n"
    "        const _cox=this.centerOrb.x-e.x,_coy=this.centerOrb.y-e.y;\n"
    "        const _cod=Math.hypot(_cox,_coy)||1;\n"
    "        e.vx+=(_cox/_cod)*[0.12,0.22,0.36][diff];\n"
    "        e.vy+=(_coy/_cod)*[0.12,0.22,0.36][diff];\n"
    "      }\n"
    "      // 油漬：在油上無法發動衝刺、無法轉向（只能滑行）"
)

# ── 12. endGame: cleanup ultState ────────────────────────────────────
rep("endGame ultState cleanup",
    "    this.abilityActive=null;\n"
    "    if(this.abilFxLayer) this.abilFxLayer.clear();",
    "    this.abilityActive=null;\n"
    "    if(this.ultState){\n"
    "      if(this.ultState.trailGfx) this.ultState.trailGfx.destroy();\n"
    "      if(this.ultState.spinGfx) this.ultState.spinGfx.destroy();\n"
    "      if(this.ultState.aimGfx) this.ultState.aimGfx.destroy();\n"
    "      this.ultState=null;\n"
    "    }\n"
    "    if(this.abilFxLayer) this.abilFxLayer.clear();"
)

# ── 13. Rewrite pork ult ─────────────────────────────────────────────
rep("pork ult new",
"""      case 'pork':{
        // 油漬漫野 + 3 秒無敵衝撞
        for(let i=0;i<24;i++){
          const ox=G.x+35+Math.random()*(G.w-70);
          const oy=G.y+35+Math.random()*(G.h-70);
          this.oilSlicks.push({x:ox,y:oy,r:55,life:7.0,ph:Math.random()*Math.PI*2});
        }
        this.activeEffects.foil=Math.max(this.activeEffects.foil,3.0);
        gBurst(this.p.x,this.p.y,22,0xffcc00);
        this.cameras.main.shake(250,0.014);
        this.showPop('🛢 油脂浪潮！油漬漫野＋3秒無敵衝撞！');
        break;}""",
"""      case 'pork':{
        // 豬油災難：1.8倍體型＋無敵＋移動留油漬＋4倍推力 (5秒)
        this.ultState={type:'pork',timer:5,invincible:true,oilTrail:true,trailTimer:0,pushMul:4,spdMul:1.2};
        if(this.playerSprite){this.tweens.add({targets:this.playerSprite,scaleX:1.8,scaleY:1.8,duration:300});this.playerSprite._ultScale=1.8;}
        this.activeEffects.foil=Math.max(this.activeEffects.foil,5.2);
        gBurst(this.p.x,this.p.y,28,0xffcc00);
        this.cameras.main.shake(320,0.020);
        this.showPop('🐷 豬油災難！無敵＋4倍推力！移動留油漬！');
        break;}"""
)

# ── 14. Rewrite beef ult ─────────────────────────────────────────────
rep("beef ult new",
"""      case 'beef':
        this.dashState={active:true,dx:this.lastDir.x,dy:this.lastDir.y,dist:0,maxDist:330,force:350};
        break;""",
"""      case 'beef':{
        // 鋼鐵熟度：熟度凍結＋90%擊退抵抗＋衝撞震盪波 (6秒)
        this.ultState={type:'beef',timer:6,heatStop:true,knockRes:0.1};
        for(let ci=0;ci<8;ci++){const ang=ci*Math.PI/4;const crk={r:0};const crkg=this.add.graphics().setDepth(24);
          this.tweens.add({targets:crk,r:1,duration:500+ci*40,ease:'Quad.easeOut',
            onUpdate:()=>{crkg.clear();crkg.lineStyle(3*(1-crk.r*0.5),0xccaa55,1-crk.r*0.7);
              crkg.lineBetween(this.p.x,this.p.y,this.p.x+Math.cos(ang)*crk.r*90,this.p.y+Math.sin(ang)*crk.r*90);},
            onComplete:()=>crkg.destroy()});}
        gBurst(this.p.x,this.p.y,20,0xccaa55);
        this.cameras.main.shake(300,0.018);
        this.showPop('🥩 鋼鐵熟度！熟度凍結＋90%擊退抵抗！6秒！');
        break;}"""
)

# ── 15. Rewrite mushroom ult ──────────────────────────────────────────
rep("mushroom ult new",
"""      case 'mushroom':{
        // 第一波：孢子從玩家噴散（視覺）
        for(let si=0;si<24;si++){
          const ang=Math.random()*Math.PI*2;
          const dst=60+Math.random()*130;
          const go={px:this.p.x,py:this.p.y,life:1};
          const gfx=this.add.graphics().setDepth(24);
          this.tweens.add({targets:go,
            px:this.p.x+Math.cos(ang)*dst, py:this.p.y+Math.sin(ang)*dst,
            life:0, duration:500+Math.random()*400, ease:'Quad.easeOut',
            onUpdate:()=>{
              gfx.clear();
              gfx.fillStyle(0xeeffcc,go.life*0.95); gfx.fillCircle(go.px,go.py,3.5+go.life*2.5);
              gfx.fillStyle(0x88ff44,go.life*0.7); gfx.fillCircle(go.px,go.py,2);
            },
            onComplete:()=>gfx.destroy()});
        }
        // 第二波：3層霧氣環向外擴散
        for(let ri=0;ri<3;ri++){
          const fog={r:0,a:0}; const fgfx=this.add.graphics().setDepth(23);
          this.tweens.add({targets:fog,r:1,a:1,delay:ri*200,duration:750,ease:'Quad.easeOut',
            onUpdate:()=>{
              fgfx.clear();
              const fade=fog.a>0.6?1-fog.a:fog.a*1.4;
              fgfx.fillStyle(0xbbff88,fade*0.22);
              fgfx.fillCircle(this.p.x,this.p.y,fog.r*(130+ri*45));
              fgfx.lineStyle(2,0x88ff44,fade*0.6);
              fgfx.strokeCircle(this.p.x,this.p.y,fog.r*(130+ri*45));
            },
            onComplete:()=>fgfx.destroy()});
        }
        // 霧氣擴散完畢後才暈眩（延遲 1.1 秒）
        this.time.delayedCall(1100,()=>{
          if(!this.alive) return;
          this.enemyCC.stun=Math.max(this.enemyCC.stun,3.5);
        });
        // 隱身 2 秒 + 隨機傳送
        if(this.playerSprite) this.tweens.add({targets:this.playerSprite,alpha:0.08,duration:400});
        this.time.delayedCall(2000,()=>{
          if(!this.alive) return;
          for(let attempt=0;attempt<20;attempt++){
            const nx=G.x+80+Math.random()*(G.w-160);
            const ny=G.y+80+Math.random()*(G.h-160);
            if(inGrill(nx,ny)){this.p.x=nx;this.p.y=ny;break;}
          }
          if(this.playerSprite){this.playerSprite.setPosition(this.p.x,this.p.y);this.tweens.add({targets:this.playerSprite,alpha:1,duration:300});}
          const rp={r:0};const rgfx=this.add.graphics().setDepth(25);
          this.tweens.add({targets:rp,r:1,duration:420,ease:'Quad.easeOut',
            onUpdate:()=>{rgfx.clear();rgfx.lineStyle(5*(1-rp.r),0x88ff44,1-rp.r);rgfx.strokeCircle(this.p.x,this.p.y,rp.r*80);},
            onComplete:()=>rgfx.destroy()});
          this.showPop('👤 突然現身！');
        });
        this.showPop('🍄 孢子偽裝！迷霧隱身 2 秒後傳送！');
        break;}""",
"""      case 'mushroom':{
        // 孢子幻影：縮小0.5倍＋3次閃現＋紫色殘影 (8秒)
        this.ultState={type:'mushroom',timer:8,blinks:3,trailTimer:0,trailGfx:this.add.graphics().setDepth(21),spdMul:1.4};
        if(this.playerSprite){this.tweens.add({targets:this.playerSprite,scaleX:0.5,scaleY:0.5,alpha:0.5,duration:300});this.playerSprite._ultScale=0.5;}
        for(let si=0;si<22;si++){const ang=Math.random()*Math.PI*2;const go={px:this.p.x,py:this.p.y,life:1};const gfx=this.add.graphics().setDepth(24);
          this.tweens.add({targets:go,px:this.p.x+Math.cos(ang)*(50+Math.random()*110),py:this.p.y+Math.sin(ang)*(50+Math.random()*110),life:0,duration:500,ease:'Quad.easeOut',
            onUpdate:()=>{gfx.clear();gfx.fillStyle(0xcc88ff,go.life*0.9);gfx.fillCircle(go.px,go.py,3+go.life*2);},
            onComplete:()=>gfx.destroy()});}
        this.showPop('🍄 孢子幻影！3次閃現！按[S]閃現！');
        break;}"""
)

# ── 16. Rewrite corn ult ──────────────────────────────────────────────
rep("corn ult new",
"""      case 'corn':{
        if(this.heat<80){
          this.ultCharge=this.ultMax; this.ultCinema=false;
          this.showPop('⚠️ 需要熟度 80% 以上才能釋放！');
          return;
        }
        // 3 顆大砲彈，各鎖定一個敵人，強力擊退
        for(let ki=0;ki<3;ki++){
          this.time.delayedCall(ki*350,()=>{
            if(!this.alive||!aliveE.length) return;
            const tgt=aliveE[ki%aliveE.length];
            const dd=Math.hypot(tgt.x-this.p.x,tgt.y-this.p.y)||1;
            const dx=(tgt.x-this.p.x)/dd, dy=(tgt.y-this.p.y)/dd;
            const go={px:this.p.x,py:this.p.y}; const gfx=this.add.graphics().setDepth(24);
            let hit=false;
            this.tweens.add({targets:go,px:tgt.x+dx*40,py:tgt.y+dy*40,duration:280,ease:'Linear',
              onUpdate:()=>{
                if(hit){gfx.clear();return;}
                gfx.clear();
                gfx.fillStyle(0xfffae0,1.0);gfx.fillCircle(go.px,go.py,11);
                gfx.fillStyle(0xffeebb,0.85);gfx.fillCircle(go.px-2,go.py-2,6);
                if(Math.hypot(go.px-tgt.x,go.py-tgt.y)<32){
                  hit=true;
                  const idx=this.enemies.indexOf(tgt);
                  this.tweens.add({targets:tgt,x:tgt.x+dx*300,y:tgt.y+dy*300,duration:340,ease:'Quad.easeOut',onComplete:()=>this.checkEnemyFall(tgt,idx)});
                  tgt.stunTimer=(tgt.stunTimer||0)+1.2;
                  this.cameras.main.shake(220,0.016);
                  const ef={r:0};const eg=this.add.graphics().setDepth(25);
                  this.tweens.add({targets:ef,r:1,duration:300,ease:'Quad.easeOut',
                    onUpdate:()=>{eg.clear();eg.lineStyle(7*(1-ef.r),0xfffae0,1-ef.r);eg.strokeCircle(go.px,go.py,ef.r*65);},
                    onComplete:()=>eg.destroy()});
                }
              },onComplete:()=>gfx.destroy()});
          });
        }
        this.showPop('🍿 連鎖爆裂！三顆大砲彈強力射出！');
        break;}""",
"""      case 'corn':{
        // 加特林爆裂：速度減半＋每0.2秒自動射擊 (5秒)
        this.ultState={type:'corn',timer:5,autoShoot:true,shootTimer:0,spdMul:0.5};
        gBurst(this.p.x,this.p.y,16,0xfffae0);
        this.cameras.main.shake(200,0.012);
        this.showPop('🍿 加特林爆裂！全自動連射5秒！');
        break;}"""
)

# ── 17. Rewrite wing ult ──────────────────────────────────────────────
rep("wing ult new",
"""      case 'wing':{
        this.activeEffects.foil=Math.max(this.activeEffects.foil,5);
        this.ultSpeedTimer=5;
        // 旋風環 + 螺旋粒子爆散
        for(let wi=0;wi<18;wi++){
          const ang=wi*Math.PI/9;
          const go={px:this.p.x,py:this.p.y,r:0};
          const gfx=this.add.graphics().setDepth(24);
          this.tweens.add({targets:go,px:this.p.x+Math.cos(ang)*110,py:this.p.y+Math.sin(ang)*110,
            r:1,duration:420,ease:'Quad.easeOut',
            onUpdate:()=>{gfx.clear();gfx.fillStyle(0x44ffee,1-go.r*0.8);gfx.fillCircle(go.px,go.py,5*(1-go.r*0.5));},
            onComplete:()=>gfx.destroy()});
        }
        const ring1={r:0}; const rgfx=this.add.graphics().setDepth(24);
        this.tweens.add({targets:ring1,r:1,duration:600,ease:'Quad.easeOut',
          onUpdate:()=>{rgfx.clear();rgfx.lineStyle(5*(1-ring1.r),0x00ffee,1-ring1.r);rgfx.strokeCircle(this.p.x,this.p.y,ring1.r*160);},
          onComplete:()=>rgfx.destroy()});
        this.showPop('🪽 旋風疾飛！速度爆發！');
        break;}""",
"""      case 'wing':{
        // 火海轟炸：飛起＋準心＋3次投彈 (3.5秒)
        const _wAimGfx=this.add.graphics().setDepth(86);
        this.ultState={type:'wing',timer:3.5,flying:true,bombs:3,bombTimer:1.0,aimX:this.p.x,aimY:this.p.y,aimGfx:_wAimGfx};
        if(this.playerSprite)this.tweens.add({targets:this.playerSprite,alpha:0.08,scaleX:0.3,scaleY:0.3,duration:350});
        for(let wi=0;wi<10;wi++){const ang=wi*Math.PI*2/10;const go={r:0};const wfx=this.add.graphics().setDepth(22);
          this.tweens.add({targets:go,r:1,delay:wi*25,duration:380,ease:'Quad.easeOut',
            onUpdate:()=>{wfx.clear();wfx.lineStyle(3*(1-go.r),0xaaffff,1-go.r);wfx.strokeCircle(W/2+Math.cos(ang)*W*0.52,H/2+Math.sin(ang)*H*0.52,go.r*55);},
            onComplete:()=>wfx.destroy()});}
        this.showPop('🪽 火海轟炸！方向鍵移動準心，[S]投彈！');
        break;}"""
)

# ── 18. Rewrite shrimp ult ────────────────────────────────────────────
rep("shrimp ult new",
"""      case 'shrimp':{
        aliveE.forEach((e,i)=>{
          const dx=e.x-this.p.x,dy=e.y-this.p.y,d=Math.hypot(dx,dy)||1;
          this.tweens.add({targets:e,x:e.x+dx/d*160,y:e.y+dy/d*160,
            duration:350,ease:'Cubic.easeOut',onComplete:()=>this.checkEnemyFall(e,i)});
        });
        // 衝擊波：3層擴散環
        for(let ri=0;ri<3;ri++){
          const wave={r:0}; const wgfx=this.add.graphics().setDepth(24);
          this.tweens.add({targets:wave,r:1,delay:ri*90,duration:520,ease:'Quad.easeOut',
            onUpdate:()=>{wgfx.clear();wgfx.lineStyle(5*(1-wave.r),0x4466ff,1-wave.r);wgfx.strokeCircle(this.p.x,this.p.y,wave.r*190);},
            onComplete:()=>wgfx.destroy()});
        }
        gBurst(this.p.x,this.p.y,16,0x88ccff);
        this.showPop('🦐 衝擊浪潮！全員飛出！');
        break;}""",
"""      case 'shrimp':{
        // 超導彈射：球形模式＋彈跳每次+20%速度 (5秒)
        this.ultState={type:'shrimp',timer:5,ballMode:true,bounceSpd:1.0,trailTimer:0};
        if(this.playerSprite){this.tweens.add({targets:this.playerSprite,scaleX:0.8,scaleY:0.8,duration:200});this.playerSprite._ultScale=0.8;}
        aliveE.forEach((e,i)=>{
          const dx=e.x-this.p.x,dy=e.y-this.p.y,d=Math.hypot(dx,dy)||1;
          this.tweens.add({targets:e,x:e.x+dx/d*140,y:e.y+dy/d*140,duration:350,ease:'Cubic.easeOut',onComplete:()=>this.checkEnemyFall(e,i)});
        });
        for(let ri=0;ri<3;ri++){const wave={r:0};const wgfx=this.add.graphics().setDepth(24);
          this.tweens.add({targets:wave,r:1,delay:ri*90,duration:500,ease:'Quad.easeOut',
            onUpdate:()=>{wgfx.clear();wgfx.lineStyle(5*(1-wave.r),0x4466ff,1-wave.r);wgfx.strokeCircle(this.p.x,this.p.y,wave.r*180);},
            onComplete:()=>wgfx.destroy()});}
        gBurst(this.p.x,this.p.y,18,0x44aaff);
        this.showPop('🦐 超導彈射！球形＋彈跳加速！');
        break;}"""
)

# ── 19. Rewrite tofu ult ──────────────────────────────────────────────
rep("tofu ult new",
"""      case 'tofu':{
        this.heat=Math.max(0,this.heat-70);
        this.abilityActive={type:'shield',timer:4.0};
        // 吸收附近敵人熱度
        aliveE.forEach(e=>{
          const d=Math.hypot(this.p.x-e.x,this.p.y-e.y);
          if(d<200){const absorb=Math.min(e.heat,45);e.heat=Math.max(0,e.heat-absorb);}
        });
        // 震波推開
        aliveE.forEach((e,i2)=>{
          const d=Math.hypot(this.p.x-e.x,this.p.y-e.y);
          if(d<200){
            const ex=(e.x-this.p.x)/(d||1),ey=(e.y-this.p.y)/(d||1);
            const force=(1-d/200)*320;
            this.tweens.add({targets:e,x:e.x+ex*force,y:e.y+ey*force,duration:350,ease:'Quad.easeOut',onComplete:()=>this.checkEnemyFall(e,i2)});
          }
        });
        // 震波視覺：3層擴散環
        for(let ri=0;ri<3;ri++){
          const sh={r:0}; const sgfx=this.add.graphics().setDepth(24);
          this.tweens.add({targets:sh,r:1,delay:ri*100,duration:520,ease:'Quad.easeOut',
            onUpdate:()=>{sgfx.clear();sgfx.lineStyle(6*(1-sh.r),0x88ccff,1-sh.r);sgfx.strokeCircle(this.p.x,this.p.y,sh.r*200+12);},
            onComplete:()=>sgfx.destroy()});
        }
        this.cameras.main.shake(280,0.016);
        this.showPop('💧 完美冷卻！吸盡附近熱度＋震波推開！');
        break;}""",
"""      case 'tofu':{
        // 吸熱冰封：熟度上限200%＋強力吸熱＋凍結 (5秒)
        this.ultState={type:'tofu',timer:5,heatMax:200,absorbTimer:0};
        aliveE.forEach(e=>{
          const d=Math.hypot(this.p.x-e.x,this.p.y-e.y);
          if(d<220){
            const absorb=Math.min(e.heat,55); e.heat=Math.max(0,e.heat-absorb);
            this.heat=Math.min(200,this.heat+absorb*0.8);
            e.stunTimer=(e.stunTimer||0)+2.5;
            for(let ic=0;ic<8;ic++){const ang=ic*Math.PI/4;const icg={r:0};const icfx=this.add.graphics().setDepth(24);
              this.tweens.add({targets:icg,r:1,duration:400,ease:'Quad.easeOut',
                onUpdate:()=>{icfx.clear();icfx.lineStyle(2*(1-icg.r*0.5),0x88eeff,1-icg.r*0.8);
                  icfx.lineBetween(e.x,e.y,e.x+Math.cos(ang)*icg.r*45,e.y+Math.sin(ang)*icg.r*45);},
                onComplete:()=>icfx.destroy()});}
          }
        });
        for(let ic=0;ic<6;ic++){const rang=Math.random()*Math.PI*2,rdst=30+Math.random()*80;
          const icx=this.p.x+Math.cos(rang)*rdst,icy=this.p.y+Math.sin(rang)*rdst;
          const icg={r:0,a:1};const icfx=this.add.graphics().setDepth(15);
          this.tweens.add({targets:icg,r:1,duration:600,ease:'Quad.easeOut',
            onUpdate:()=>{icfx.clear();icfx.fillStyle(0x88eeff,icg.a*0.35);icfx.fillCircle(icx,icy,icg.r*40);
              icfx.lineStyle(2,0xccffff,icg.a*0.6);icfx.strokeCircle(icx,icy,icg.r*40);},
            onComplete:()=>{this.tweens.add({targets:icg,a:0,duration:4000,onComplete:()=>icfx.destroy()});}});}
        this.cameras.main.shake(300,0.018);
        this.showPop('💧 吸熱冰封！熟度上限200%！吸熱並凍結！');
        break;}"""
)

# ── 20. Rewrite bacon ult ─────────────────────────────────────────────
rep("bacon ult new",
"""      case 'bacon':{
        this.enemyCC.slow=Math.max(this.enemyCC.slow,9);
        // 煙霧瀰漫：全場隨機冒出煙雲
        for(let si=0;si<12;si++){
          const sx=G.x+50+Math.random()*(G.w-100);
          const sy=G.y+50+Math.random()*(G.h-100);
          this.time.delayedCall(si*70,()=>{
            if(!this.alive) return;
            const smoke={v:0}; const sfx=this.add.graphics().setDepth(24);
            this.tweens.add({targets:smoke,v:1,duration:900,ease:'Quad.easeInOut',
              onUpdate:()=>{sfx.clear();const a=smoke.v>0.5?1-smoke.v*1.6:smoke.v*1.6;
                sfx.fillStyle(0xaa7744,a*0.4);sfx.fillCircle(sx,sy,smoke.v*52);
                sfx.fillStyle(0x886633,a*0.25);sfx.fillCircle(sx+14,sy-10,smoke.v*36);},
              onComplete:()=>sfx.destroy()});
          });
        }
        this.showPop('🥓 煙燻覆蓋！全場減速！');
        break;}""",
"""      case 'bacon':{
        // 死亡電鋸：高速旋轉＋摩擦傷害＋每秒+熟度 (5秒)
        this.ultState={type:'bacon',timer:5,spinning:true,spinAngle:0,heatTimer:0,spinGfx:this.add.graphics().setDepth(25)};
        if(this.playerSprite)this.playerSprite.setTint(0xff6600);
        this.cameras.main.shake(220,0.014);
        this.showPop('🥓 死亡電鋸！高速旋轉＋摩擦傷害5秒！');
        break;}"""
)

# ── 21. Rewrite pepper ult ────────────────────────────────────────────
rep("pepper ult new",
"""      case 'pepper':{
        this.enemyCC.stun=Math.max(this.enemyCC.stun,2.5);
        // 從玩家位置向外噴辣氣：30顆辣椒粒子往四面放射
        for(let pi=0;pi<30;pi++){
          const ang=pi*Math.PI*2/30;
          const dst=40+Math.random()*130;
          const go={px:this.p.x,py:this.p.y,life:1};
          const gfx=this.add.graphics().setDepth(24);
          this.tweens.add({targets:go,
            px:this.p.x+Math.cos(ang)*dst, py:this.p.y+Math.sin(ang)*dst,
            life:0, duration:350+Math.random()*250, ease:'Quad.easeOut',
            onUpdate:()=>{
              gfx.clear();
              gfx.fillStyle(0x88ff44,go.life*0.9); gfx.fillCircle(go.px,go.py,3+go.life*2.5);
              gfx.fillStyle(0xffff00,go.life*0.5); gfx.fillCircle(go.px,go.py,1.5);
            },
            onComplete:()=>gfx.destroy()});
        }
        // 衝擊環
        for(let ri=0;ri<2;ri++){
          const pw={r:0}; const pgfx=this.add.graphics().setDepth(23);
          this.tweens.add({targets:pw,r:1,delay:ri*120,duration:500,ease:'Quad.easeOut',
            onUpdate:()=>{pgfx.clear();pgfx.lineStyle(5*(1-pw.r),0x44cc44,1-pw.r);pgfx.strokeCircle(this.p.x,this.p.y,pw.r*160);},
            onComplete:()=>pgfx.destroy()});
        }
        this.showPop('🌶 辣椒震波！辣氣四射！全員暈眩！');
        break;}""",
"""      case 'pepper':{
        // 毒霧迷蹤：速度+50%＋噴綠毒氣＋敵人控制反轉 (6秒)
        this.ultState={type:'pepper',timer:6,reversed:true,spdMul:1.5,gasTimer:0,gasClouds:[]};
        for(let pi=0;pi<30;pi++){const ang=pi*Math.PI*2/30;const go={px:this.p.x,py:this.p.y,life:1};const gfx=this.add.graphics().setDepth(24);
          this.tweens.add({targets:go,px:this.p.x+Math.cos(ang)*(40+Math.random()*130),py:this.p.y+Math.sin(ang)*(40+Math.random()*130),life:0,duration:400+Math.random()*200,ease:'Quad.easeOut',
            onUpdate:()=>{gfx.clear();gfx.fillStyle(0x44ff44,go.life*0.85);gfx.fillCircle(go.px,go.py,3+go.life*3);},
            onComplete:()=>gfx.destroy()});}
        this.cameras.main.shake(150,0.010);
        this.showPop('🌶 毒霧迷蹤！速度+50%＋毒氣反轉操控！');
        break;}"""
)

# ── 22. Rewrite saury ult ─────────────────────────────────────────────
rep("saury ult new",
"""      case 'saury':{
        // 穿心刺：超長衝刺，撈起沿路敵人，衝到底甩出去
        const sDir={x:this.lastDir.x||1,y:this.lastDir.y};
        const sDist=380;
        const sEndX=Phaser.Math.Clamp(this.p.x+sDir.x*sDist,G.x+30,G.x+G.w-30);
        const sEndY=Phaser.Math.Clamp(this.p.y+sDir.y*sDist,G.y+30,G.y+G.h-30);
        // 找路徑上的敵人
        const grabbed=[];
        aliveE.forEach((e,i2)=>{
          const dot=(e.x-this.p.x)*sDir.x+(e.y-this.p.y)*sDir.y;
          const cx=(e.x-this.p.x)-dot*sDir.x, cy=(e.y-this.p.y)-dot*sDir.y;
          if(dot>0&&dot<sDist&&Math.hypot(cx,cy)<38) grabbed.push({e,i:i2});
        });
        // 衝刺動畫
        const pos={px:this.p.x,py:this.p.y};
        this.tweens.add({targets:pos,px:sEndX,py:sEndY,duration:380,ease:'Quad.easeIn',
          onUpdate:()=>{
            this.p.x=pos.px; this.p.y=pos.py;
            grabbed.forEach(g2=>{g2.e.x=pos.px;g2.e.y=pos.py;});
            // 魚骨殘影
            if(Math.random()<0.5){
              const trFx={life:1};const trG=this.add.graphics().setDepth(24);
              const tx=pos.px,ty=pos.py;
              this.tweens.add({targets:trFx,life:0,duration:180,ease:'Quad.easeOut',
                onUpdate:()=>{trG.clear();trG.fillStyle(0x8899cc,trFx.life*0.6);trG.fillCircle(tx,ty,trFx.life*14+4);},
                onComplete:()=>trG.destroy()});
            }
          },
          onComplete:()=>{
            this.cameras.main.shake(350,0.02);
            // 甩出抓到的敵人
            grabbed.forEach((g2,k)=>{
              const ang=k*Math.PI*2/Math.max(1,grabbed.length)+(Math.random()-0.5)*0.8;
              this.tweens.add({targets:g2.e,x:g2.e.x+Math.cos(ang)*240,y:g2.e.y+Math.sin(ang)*240,duration:320,ease:'Quad.easeOut',onComplete:()=>this.checkEnemyFall(g2.e,g2.i)});
              this.cameras.main.shake(180,0.012);
            });
            const efx={r:0};const eg=this.add.graphics().setDepth(25);
            this.tweens.add({targets:efx,r:1,duration:380,ease:'Quad.easeOut',
              onUpdate:()=>{eg.clear();eg.lineStyle(6*(1-efx.r),0x8899cc,1-efx.r);eg.strokeCircle(pos.px,pos.py,efx.r*90);},
              onComplete:()=>eg.destroy()});
            this.showPop('🐟 穿心刺！撈起敵人甩飛！');
          }
        });
        break;}""",
"""      case 'saury':{
        // 極意一閃：蓄力1秒→全場穿透衝刺
        this.activeEffects.stun=Math.max(this.activeEffects.stun,1.0);
        const _sCharGfx=this.add.graphics().setDepth(86);
        const _sBw=this.add.rectangle(W/2,H/2,W,H,0x000000,0.65).setDepth(87);
        this.tweens.add({targets:_sBw,alpha:0,duration:1200,onComplete:()=>_sBw.destroy()});
        const _sCha={r:0};
        this.tweens.add({targets:_sCha,r:1,duration:1000,ease:'Quad.easeIn',
          onUpdate:()=>{_sCharGfx.clear();_sCharGfx.lineStyle(4,0xffffff,_sCha.r*0.9);_sCharGfx.strokeCircle(this.p.x,this.p.y,_sCha.r*85);
            _sCharGfx.fillStyle(0xffffff,_sCha.r*0.22);_sCharGfx.fillCircle(this.p.x,this.p.y,_sCha.r*38);},
          onComplete:()=>_sCharGfx.destroy()});
        if(this.playerSprite)this.tweens.add({targets:this.playerSprite,alpha:0.15,duration:800,yoyo:true,hold:200});
        this.showPop('⚡ 蓄力中...');
        const _sSx=this.p.x,_sSy=this.p.y;
        const _sSDir={x:this.lastDir.x||1,y:this.lastDir.y};
        this.time.delayedCall(1000,()=>{
          if(!this.alive)return;
          const sDist=400;
          const sEndX=Phaser.Math.Clamp(_sSx+_sSDir.x*sDist,G.x+30,G.x+G.w-30);
          const sEndY=Phaser.Math.Clamp(_sSy+_sSDir.y*sDist,G.y+30,G.y+G.h-30);
          const grabbed=[];
          this.enemies.forEach((e,i2)=>{
            if(!e.alive)return;
            const dot=(e.x-_sSx)*_sSDir.x+(e.y-_sSy)*_sSDir.y;
            const cx=(e.x-_sSx)-dot*_sSDir.x,cy=(e.y-_sSy)-dot*_sSDir.y;
            if(dot>0&&dot<sDist&&Math.hypot(cx,cy)<42)grabbed.push({e,i:i2});
          });
          const pos={px:_sSx,py:_sSy};
          this.tweens.add({targets:pos,px:sEndX,py:sEndY,duration:300,ease:'Quad.easeIn',
            onUpdate:()=>{
              this.p.x=pos.px;this.p.y=pos.py;
              grabbed.forEach(g2=>{g2.e.x=pos.px;g2.e.y=pos.py;});
              if(Math.random()<0.55){const trFx={life:1};const trG=this.add.graphics().setDepth(24);const tx=pos.px,ty=pos.py;
                this.tweens.add({targets:trFx,life:0,duration:160,
                  onUpdate:()=>{trG.clear();trG.fillStyle(0xeeeeff,trFx.life*0.8);trG.fillCircle(tx,ty,trFx.life*16+5);},
                  onComplete:()=>trG.destroy()});}
            },
            onComplete:()=>{
              this.cameras.main.shake(400,0.025);
              grabbed.forEach((g2,k)=>{
                const ang=k*Math.PI*2/Math.max(1,grabbed.length)+(Math.random()-0.5)*0.8;
                this.tweens.add({targets:g2.e,x:g2.e.x+Math.cos(ang)*280,y:g2.e.y+Math.sin(ang)*280,duration:320,ease:'Quad.easeOut',onComplete:()=>this.checkEnemyFall(g2.e,g2.i)});
              });
              const efx={r:0};const eg=this.add.graphics().setDepth(25);
              this.tweens.add({targets:efx,r:1,duration:380,
                onUpdate:()=>{eg.clear();eg.lineStyle(7*(1-efx.r),0xeeeeff,1-efx.r);eg.strokeCircle(pos.px,pos.py,efx.r*100);},
                onComplete:()=>eg.destroy()});
              this.showPop('🐟 極意一閃！全場穿透！');
            }
          });
        });
        break;}"""
)

# ── 23. Add new methods before spawnUltOrb ───────────────────────────
rep("add new methods",
    "  spawnUltOrb(){",
    """  spawnCenterOrb(){
    const cx=G.x+G.w/2, cy=G.y+G.h/2;
    const gfx=this.add.graphics().setDepth(20);
    this.centerOrb={x:cx,y:cy,gfx,ph:0,ring:0};
    const _at1=this.add.text(W/2,H/2-50,'✦ 大絕道具降臨！',{fontSize:'36px',color:'#ffdd00',fontFamily:'sans-serif',fontStyle:'bold',stroke:'#000000',strokeThickness:8}).setOrigin(0.5).setDepth(95).setAlpha(0);
    const _at2=this.add.text(W/2,H/2+8,'⇒ 往烤盤中央衝！⇐',{fontSize:'22px',color:'#ffffff',fontFamily:'sans-serif',stroke:'#000000',strokeThickness:5}).setOrigin(0.5).setDepth(95).setAlpha(0);
    this.tweens.add({targets:[_at1,_at2],alpha:1,duration:300,hold:1800,yoyo:true,onComplete:()=>{_at1.destroy();_at2.destroy();}});
    const _sf=this.add.rectangle(W/2,H/2,W,H,0xffdd00,0).setDepth(94);
    this.tweens.add({targets:_sf,alpha:{from:0.45,to:0},duration:380,onComplete:()=>_sf.destroy()});
    this.cameras.main.shake(180,0.010);
  }

  updateCenterOrb(dt){
    const orb=this.centerOrb;
    if(!orb) return;
    orb.ph+=dt*3; orb.ring+=dt;
    const gfx=orb.gfx; gfx.clear();
    const glow=0.5+0.5*Math.sin(orb.ph);
    gfx.fillStyle(0xffdd00,0.10+glow*0.14); gfx.fillCircle(orb.x,orb.y,52+glow*14);
    gfx.fillStyle(0xffcc00,0.7+glow*0.3); gfx.fillCircle(orb.x,orb.y,22);
    gfx.fillStyle(0xffffff,0.95); gfx.fillCircle(orb.x,orb.y,10);
    for(let si=0;si<6;si++){
      const sa=orb.ring*2+si*Math.PI/3;
      gfx.fillStyle(0xffee88,0.6+glow*0.4); gfx.fillCircle(orb.x+Math.cos(sa)*(32+glow*8),orb.y+Math.sin(sa)*(32+glow*8),4+glow*2);
    }
    gfx.lineStyle(3,0xffdd00,0.8+glow*0.2); gfx.strokeCircle(orb.x,orb.y,36+glow*8);
    if(Math.hypot(this.p.x-orb.x,this.p.y-orb.y)<32){
      this.ultCharge=this.ultMax; this.updateUltUI();
      const pf={r:0};const pfx=this.add.graphics().setDepth(30);
      this.tweens.add({targets:pf,r:1,duration:400,ease:'Quad.easeOut',
        onUpdate:()=>{pfx.clear();pfx.lineStyle(6*(1-pf.r),0xffdd00,1-pf.r);pfx.strokeCircle(orb.x,orb.y,pf.r*85);},
        onComplete:()=>pfx.destroy()});
      gfx.destroy(); this.centerOrb=null; this.centerOrbTimer=45;
      this.showPop('✦ 大絕蓄滿！按[D]釋放！');
    }
  }

  updateUltState(dt){
    const us=this.ultState;
    if(!us){return;}
    us.timer-=dt;
    if(us.type==='pork'){
      us.trailTimer-=dt;
      if(us.trailTimer<=0&&(this.lastDir.x||this.lastDir.y)){
        this.oilSlicks.push({x:this.p.x,y:this.p.y,r:32,life:6,ph:Math.random()*Math.PI*2});
        us.trailTimer=0.15;
      }
      if(Math.random()<0.4){
        const ang=Math.random()*Math.PI*2,r=25+Math.random()*22;
        const pg={px:this.p.x+Math.cos(ang)*r,py:this.p.y+Math.sin(ang)*r,life:1};const pf=this.add.graphics().setDepth(26);
        this.tweens.add({targets:pg,life:0,duration:240,
          onUpdate:()=>{pf.clear();pf.fillStyle(0xffcc00,pg.life*0.7);pf.fillCircle(pg.px,pg.py,3+pg.life*4);},
          onComplete:()=>pf.destroy()});
      }
    } else if(us.type==='mushroom'){
      us.trailTimer-=dt;
      if(us.trailTimer<=0){
        const tp={x:this.p.x,y:this.p.y,a:0.55};const tfx=this.add.graphics().setDepth(21);
        this.tweens.add({targets:tp,a:0,duration:320,
          onUpdate:()=>{tfx.clear();tfx.fillStyle(0xaa44ff,tp.a);tfx.fillCircle(tp.x,tp.y,10);},
          onComplete:()=>tfx.destroy()});
        us.trailTimer=0.07;
      }
    } else if(us.type==='corn'){
      us.shootTimer-=dt;
      if(us.shootTimer<=0){
        const liveE=this.enemies.filter(e=>e.alive);
        if(liveE.length){
          const tgt=liveE.reduce((a,b)=>Math.hypot(a.x-this.p.x,a.y-this.p.y)<=Math.hypot(b.x-this.p.x,b.y-this.p.y)?a:b);
          const dd=Math.hypot(tgt.x-this.p.x,tgt.y-this.p.y)||1;
          const _cdx=(tgt.x-this.p.x)/dd,_cdy=(tgt.y-this.p.y)/dd;
          const go={px:this.p.x,py:this.p.y};const gfx=this.add.graphics().setDepth(24);let chit=false;
          this.tweens.add({targets:go,px:tgt.x,py:tgt.y,duration:180,ease:'Linear',
            onUpdate:()=>{if(chit){gfx.clear();return;}gfx.clear();gfx.fillStyle(0xfffae0,1);gfx.fillCircle(go.px,go.py,7);
              if(Math.hypot(go.px-tgt.x,go.py-tgt.y)<26){
                chit=true;const idx=this.enemies.indexOf(tgt);
                this.tweens.add({targets:tgt,x:tgt.x+_cdx*150,y:tgt.y+_cdy*150,duration:260,ease:'Quad.easeOut',onComplete:()=>this.checkEnemyFall(tgt,idx)});
                tgt.stunTimer=(tgt.stunTimer||0)+0.25;
                const ef={r:0};const eg=this.add.graphics().setDepth(25);
                this.tweens.add({targets:ef,r:1,duration:180,onUpdate:()=>{eg.clear();eg.lineStyle(5*(1-ef.r),0xfffae0,1-ef.r);eg.strokeCircle(go.px,go.py,ef.r*38);},onComplete:()=>eg.destroy()});}},
            onComplete:()=>gfx.destroy()});
          if(this.playerSprite){
            const _shk={x:this.p.x+(Math.random()-0.5)*6,y:this.p.y+(Math.random()-0.5)*6};
            this.tweens.add({targets:this.playerSprite,x:_shk.x,y:_shk.y,duration:45,yoyo:true});}
        }
        us.shootTimer=0.2;
      }
    } else if(us.type==='wing'){
      const _aimSpd=200;
      if(GKEYS['ArrowLeft']||this.keys.left.isDown) us.aimX-=_aimSpd*dt;
      if(GKEYS['ArrowRight']||this.keys.right.isDown) us.aimX+=_aimSpd*dt;
      if(GKEYS['ArrowUp']||this.keys.up.isDown) us.aimY-=_aimSpd*dt;
      if(GKEYS['ArrowDown']||this.keys.down.isDown) us.aimY+=_aimSpd*dt;
      us.aimX=Phaser.Math.Clamp(us.aimX,G.x+20,G.x+G.w-20);
      us.aimY=Phaser.Math.Clamp(us.aimY,G.y+20,G.y+G.h-20);
      const _ag=us.aimGfx;_ag.clear();
      const _pulse=0.7+0.3*Math.sin(us.timer*8);
      _ag.lineStyle(3,0xff2200,_pulse*0.9);_ag.strokeCircle(us.aimX,us.aimY,34);
      _ag.lineStyle(2,0xff5500,_pulse*0.7);
      _ag.lineBetween(us.aimX-50,us.aimY,us.aimX-28,us.aimY);_ag.lineBetween(us.aimX+28,us.aimY,us.aimX+50,us.aimY);
      _ag.lineBetween(us.aimX,us.aimY-50,us.aimX,us.aimY-28);_ag.lineBetween(us.aimX,us.aimY+28,us.aimX,us.aimY+50);
      us.bombTimer-=dt;
      if(us.bombTimer<=0&&us.bombs>0) this.dropWingBomb();
    } else if(us.type==='shrimp'){
      us.trailTimer-=dt;
      if(us.trailTimer<=0){
        const tp={x:this.p.x,y:this.p.y,a:0.55};const tfx=this.add.graphics().setDepth(21);
        this.tweens.add({targets:tp,a:0,duration:220,
          onUpdate:()=>{tfx.clear();tfx.fillStyle(0x44aaff,tp.a);tfx.fillCircle(tp.x,tp.y,9);},
          onComplete:()=>tfx.destroy()});
        us.trailTimer=0.055;
      }
    } else if(us.type==='tofu'){
      us.absorbTimer-=dt;
      if(us.absorbTimer<=0){
        this.enemies.filter(e=>e.alive).forEach(e=>{
          const d=Math.hypot(this.p.x-e.x,this.p.y-e.y);
          if(d<150){const absorb=10*dt;e.heat=Math.max(0,e.heat-absorb);this.heat=Math.min(200,this.heat+absorb*0.5);
            if(e.heat<3)e.stunTimer=Math.max(e.stunTimer||0,0.4);}
        });
        if(Math.random()<0.25){
          const ang=Math.random()*Math.PI*2,r=50+Math.random()*65;
          const ip={x:this.p.x+Math.cos(ang)*r,y:this.p.y+Math.sin(ang)*r,a:0.7};const ifx=this.add.graphics().setDepth(22);
          this.tweens.add({targets:ip,a:0,duration:550,onUpdate:()=>{ifx.clear();ifx.fillStyle(0x88eeff,ip.a*0.45);ifx.fillCircle(ip.x,ip.y,7);ifx.lineStyle(1,0xccffff,ip.a);ifx.strokeCircle(ip.x,ip.y,7);},onComplete:()=>ifx.destroy()});}
        us.absorbTimer=0;
      }
    } else if(us.type==='bacon'){
      us.spinAngle+=dt*25;
      const _sg=us.spinGfx;_sg.clear();
      for(let bi=0;bi<8;bi++){const a=us.spinAngle+bi*Math.PI/4;const r=20+8*Math.sin(us.spinAngle*2+bi);
        _sg.fillStyle(0xff6600,0.7);_sg.fillCircle(this.p.x+Math.cos(a)*r,this.p.y+Math.sin(a)*r,4);}
      us.heatTimer-=dt;
      if(us.heatTimer<=0){
        this.enemies.filter(e=>e.alive).forEach(e=>{
          const d=Math.hypot(this.p.x-e.x,this.p.y-e.y);
          if(d<52){e.heat=Math.min(100,e.heat+12*dt);e.vx+=(e.x-this.p.x)/(d||1)*0.7;e.vy+=(e.y-this.p.y)/(d||1)*0.7;}
        });
        if(Math.random()<0.45){
          const sa=Math.random()*Math.PI*2,sr=12+Math.random()*22;
          const sp={px:this.p.x+Math.cos(sa)*sr,py:this.p.y+Math.sin(sa)*sr,life:1};const sfx=this.add.graphics().setDepth(27);
          this.tweens.add({targets:sp,life:0,duration:140+Math.random()*90,
            onUpdate:()=>{sfx.clear();sfx.fillStyle(0xffaa00,sp.life*0.9);sfx.fillCircle(sp.px,sp.py,sp.life*4);},
            onComplete:()=>sfx.destroy()});}
        us.heatTimer=0;
      }
    } else if(us.type==='pepper'){
      us.gasTimer-=dt;
      if(us.gasTimer<=0){
        const _gx=this.p.x+(Math.random()-0.5)*65,_gy=this.p.y+(Math.random()-0.5)*65;
        const _gv={r:0,a:1};const _gfx=this.add.graphics().setDepth(23);
        this.tweens.add({targets:_gv,r:1,a:0,duration:1400,ease:'Quad.easeOut',
          onUpdate:()=>{_gfx.clear();_gfx.fillStyle(0x44ff44,_gv.a*0.22);_gfx.fillCircle(_gx,_gy,_gv.r*48);},
          onComplete:()=>_gfx.destroy()});
        us.gasClouds.push({x:_gx,y:_gy,r:48,life:1.4});
        us.gasTimer=0.18;
      }
      us.gasClouds=us.gasClouds.filter(c=>{c.life-=dt;return c.life>0;});
      this.enemies.filter(e=>e.alive).forEach(e=>{
        if(us.gasClouds.some(c=>Math.hypot(c.x-e.x,c.y-e.y)<c.r)){
          e.vx+=(Math.random()-0.5)*1.6;e.vy+=(Math.random()-0.5)*1.6;
        }
      });
    }
    if(us.timer<=0) this._clearUltState();
  }

  _clearUltState(){
    const us=this.ultState;
    if(!us) return;
    if(us.trailGfx) us.trailGfx.destroy();
    if(us.spinGfx) us.spinGfx.destroy();
    if(us.aimGfx) us.aimGfx.destroy();
    if(this.playerSprite){
      const sc=this.charData.scale||1;
      this.tweens.add({targets:this.playerSprite,scaleX:sc,scaleY:sc,alpha:1,duration:300});
      this.playerSprite.clearTint();
    }
    this.ultState=null;
    this.showPop('大絕狀態結束');
  }

  doUltBlink(){
    if(!this.ultState||!this.ultState.blinks) return;
    const bDist=170;
    const nx=Phaser.Math.Clamp(this.p.x+this.lastDir.x*bDist,G.x+20,G.x+G.w-20);
    const ny=Phaser.Math.Clamp(this.p.y+this.lastDir.y*bDist,G.y+20,G.y+G.h-20);
    const nx2=inGrill(nx,ny)?nx:this.p.x;
    const ny2=inGrill(nx,ny)?ny:this.p.y;
    const sx=this.p.x,sy=this.p.y;
    const sv={r:0,a:1};const sfx=this.add.graphics().setDepth(23);
    this.tweens.add({targets:sv,r:1,a:0,duration:900,ease:'Quad.easeOut',
      onUpdate:()=>{sfx.clear();sfx.fillStyle(0xaa44ff,sv.a*0.32);sfx.fillCircle(sx,sy,sv.r*58);},
      onComplete:()=>sfx.destroy()});
    this.p.x=nx2; this.p.y=ny2;
    if(this.playerSprite) this.playerSprite.setPosition(nx2,ny2);
    const af={r:0};const afx=this.add.graphics().setDepth(26);
    this.tweens.add({targets:af,r:1,duration:220,ease:'Quad.easeOut',
      onUpdate:()=>{afx.clear();afx.lineStyle(4*(1-af.r),0xcc88ff,1-af.r);afx.strokeCircle(nx2,ny2,af.r*52);},
      onComplete:()=>afx.destroy()});
    this.enemyCC.stun=Math.max(this.enemyCC.stun,0.6);
    this.ultState.blinks--;
    if(this.ultState.blinks<=0){this.showPop('⚡ 閃現次數用完！');this._clearUltState();}
    else this.showPop('⚡ 閃現！剩餘'+this.ultState.blinks+'次');
  }

  dropWingBomb(){
    if(!this.ultState||!this.ultState.flying||!this.ultState.bombs) return;
    const bx=this.ultState.aimX,by=this.ultState.aimY;
    this.ultState.bombs--;
    this.ultState.bombTimer=1.05;
    const _b={r:0};const _bf=this.add.graphics().setDepth(86);
    this.tweens.add({targets:_b,r:1,duration:330,ease:'Quad.easeOut',
      onUpdate:()=>{_bf.clear();_bf.fillStyle(0xffffff,1-_b.r*0.55);_bf.fillCircle(bx,by,_b.r*85);_bf.lineStyle(8*(1-_b.r),0xff4400,1-_b.r);_bf.strokeCircle(bx,by,_b.r*105);},
      onComplete:()=>_bf.destroy()});
    for(let fi=0;fi<22;fi++){
      const ang=Math.random()*Math.PI*2,dst=30+Math.random()*85;
      const go={px:bx,py:by,life:1};const gfx=this.add.graphics().setDepth(25);
      this.tweens.add({targets:go,px:bx+Math.cos(ang)*dst,py:by+Math.sin(ang)*dst,life:0,duration:360+Math.random()*160,ease:'Quad.easeOut',
        onUpdate:()=>{gfx.clear();gfx.fillStyle(Math.random()<0.5?0xff4400:0xffcc00,go.life*0.9);gfx.fillCircle(go.px,go.py,4+go.life*6);},
        onComplete:()=>gfx.destroy()});}
    this.cameras.main.shake(320,0.022);
    this.enemies.forEach((e,i)=>{
      if(!e.alive)return;
      const d=Math.hypot(e.x-bx,e.y-by)||1;
      if(d<130){const force=(1-d/130)*400;const fdx=(e.x-bx)/d,fdy=(e.y-by)/d;
        this.tweens.add({targets:e,x:e.x+fdx*force,y:e.y+fdy*force,duration:340,ease:'Quad.easeOut',onComplete:()=>this.checkEnemyFall(e,i)});}
    });
    if(this.ultState&&this.ultState.bombs<=0){
      this.showPop('🔥 轟炸完畢！下降中...');
      this.time.delayedCall(600,()=>{
        if(!this.alive)return;
        if(this.ultState&&this.ultState.flying){
          this.p.x=Phaser.Math.Clamp(this.ultState.aimX,G.x+25,G.x+G.w-25);
          this.p.y=Phaser.Math.Clamp(this.ultState.aimY,G.y+25,G.y+G.h-25);
          if(this.playerSprite)this.playerSprite.setPosition(this.p.x,this.p.y);
          this._clearUltState();
        }
      });
    }
  }

  spawnUltOrb(){"""
)

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

for r in results:
    print(r)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
checks = [
    ("centerOrb", "centerOrbTimer" in v),
    ("ultState", "updateUltState" in v),
    ("game feel", "time.timeScale" in v),
    ("reversed controls", "_ctrlRev" in v),
    ("pork new", "豬油災難" in v),
    ("beef new", "鋼鐵熟度" in v),
    ("mushroom new", "孢子幻影" in v),
    ("corn new", "加特林爆裂" in v),
    ("wing new", "火海轟炸" in v),
    ("shrimp new", "超導彈射" in v),
    ("tofu new", "吸熱冰封" in v),
    ("bacon new", "死亡電鋸" in v),
    ("pepper new", "毒霧迷蹤" in v),
    ("saury new", "極意一閃" in v),
    ("spawnCenterOrb", "spawnCenterOrb" in v),
    ("doUltBlink", "doUltBlink" in v),
    ("dropWingBomb", "dropWingBomb" in v),
]
for name, ok in checks:
    print(f"  {name}: {'OK' if ok else 'MISSING'}")
