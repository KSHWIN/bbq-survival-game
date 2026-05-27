# -*- coding: utf-8 -*-
# Patch 8: 10 角色特殊技能 (Space 鍵觸發)
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. Add ability vars to create() init ────────────────────────────────
old = (
    "    this.tilt=null; this.tiltTimer=14;\n"
    "    this.tiltInterval=()=>11+Math.random()*8;\n"
    "    const AC=window.AudioContext||window.webkitAudioContext;"
)
new = (
    "    this.tilt=null; this.tiltTimer=14;\n"
    "    this.tiltInterval=()=>11+Math.random()*8;\n"
    "    this.abilityCD=0; this.abilityCDMax=6; this.abilityActive=null; this.abilityWas=false;\n"
    "    const AC=window.AudioContext||window.webkitAudioContext;"
)
if old in html: html=html.replace(old,new); print("ability init: OK")
else: print("FAIL ability init")

# ── 2. Extend UI background height 78→100 ─────────────────────────────
old = "    this.add.rectangle(0,0,320,78,0x000000,0.65).setOrigin(0,0);"
new = "    this.add.rectangle(0,0,320,100,0x000000,0.65).setOrigin(0,0);"
if old in html: html=html.replace(old,new); print("UI bg height: OK")
else: print("FAIL UI bg height")

# ── 3. Add ability bar UI after pushCdTxt ─────────────────────────────
old = (
    "    this.pushCdTxt=this.add.text(204,50,'Ready!',ts(11,'#66ccff'));\n"
    "    this.timerTxt =this.add.text(W-14,14,'60s',ts(22)).setOrigin(1,0);"
)
new = (
    "    this.pushCdTxt=this.add.text(204,50,'Ready!',ts(11,'#66ccff'));\n"
    "    this.add.text(12,70,'[空白] '+c.ability,ts(10,'#ffdd44'));\n"
    "    this.abilBarBg=this.add.rectangle(86,80,120,10,0x332200).setOrigin(0,0.5);\n"
    "    this.abilBarFg=this.add.rectangle(86,80,120,8,0xffaa00).setOrigin(0,0.5);\n"
    "    this.abilCdTxt=this.add.text(216,70,'Ready!',ts(11,'#ffdd44'));\n"
    "    this.timerTxt =this.add.text(W-14,14,'60s',ts(22)).setOrigin(1,0);"
)
if old in html: html=html.replace(old,new); print("ability bar UI: OK")
else: print("FAIL ability bar UI")

# ── 4. Add Space key to input ─────────────────────────────────────────
old = (
    "      push:Phaser.Input.Keyboard.KeyCodes.S,\n"
    "      restart:Phaser.Input.Keyboard.KeyCodes.R,"
)
new = (
    "      push:Phaser.Input.Keyboard.KeyCodes.S,\n"
    "      skill:Phaser.Input.Keyboard.KeyCodes.SPACE,\n"
    "      restart:Phaser.Input.Keyboard.KeyCodes.R,"
)
if old in html: html=html.replace(old,new); print("skill key: OK")
else: print("FAIL skill key")

# ── 5. Add useAbility() method before spawnItem() ────────────────────
old_anchor = "  spawnItem(){"
new_method = (
    "  useAbility(){\n"
    "    const c=this.charData;\n"
    "    const CDs={pork:6,beef:8,mushroom:5,corn:8,wing:7,shrimp:5,tofu:9,bacon:6,pepper:7,saury:5};\n"
    "    this.abilityCDMax=CDs[c.key]||6;\n"
    "    switch(c.key){\n"
    "      case 'pork':{\n"
    "        // 滑油衝刺：衝充啥并炸開周圍\n"
    "        const dx=this.lastDir.x,dy=this.lastDir.y;\n"
    "        this.p.x=Math.max(G.x+20,Math.min(G.x+G.w-20,this.p.x+dx*120));\n"
    "        this.p.y=Math.max(G.y+20,Math.min(G.y+G.h-20,this.p.y+dy*120));\n"
    "        this.enemies.forEach((e,i)=>{\n"
    "          if(!e.alive) return;\n"
    "          const d=Math.hypot(this.p.x-e.x,this.p.y-e.y);\n"
    "          if(d<90){const nx=d>0?(e.x-this.p.x)/d:1,ny=d>0?(e.y-this.p.y)/d:0;e.x+=nx*120;e.y+=ny*120;this.checkEnemyFall(e,i);}\n"
    "        });\n"
    "        this.showPop('滑油衝刺！衝開周圍！');break;}\n"
    "      case 'beef':{\n"
    "        // 厄實裝甲：營度累積減半\n"
    "        this.abilityActive={type:'armor',timer:4};\n"
    "        this.showPop('厄實裝甲！4s 營度累積減半！');break;}\n"
    "      case 'mushroom':{\n"
    "        // 縮水跳躍：尋找安全位置擺移\n"
    "        let bx=this.p.x,by=this.p.y;\n"
    "        for(let att=0;att<30;att++){\n"
    "          const cx=G.x+60+Math.random()*(G.w-120),cy=G.y+60+Math.random()*(G.h-120);\n"
    "          if(!this.onFire(cx,cy)&&inGrill(cx,cy)){bx=cx;by=cy;break;}\n"
    "        }\n"
    "        this.p.x=bx;this.p.y=by;\n"
    "        this.cameras.main.shake(150,0.008);\n"
    "        this.showPop('縮水跳躍！瞬間移位！');break;}\n"
    "      case 'corn':{\n"
    "        // 爆米花：營度≥ 70%才能引爆\n"
    "        if(this.heat<70){this.showPop('營度不足！70%才能引爆！');this.abilityCD=0;return;}\n"
    "        this.showPop('爆米花！炸飛周圍！');\n"
    "        this.enemies.forEach((e,i)=>{\n"
    "          if(!e.alive) return;\n"
    "          const d=Math.hypot(this.p.x-e.x,this.p.y-e.y);\n"
    "          if(d<160){const nx=d>0?(e.x-this.p.x)/d:1,ny=d>0?(e.y-this.p.y)/d:0;e.x+=nx*140;e.y+=ny*140;this.checkEnemyFall(e,i);}\n"
    "        });\n"
    "        this.cameras.main.shake(350,0.012);\n"
    "        this.heat=Math.max(0,this.heat-30);break;}\n"
    "      case 'wing':{\n"
    "        // 短距滑翔：3s 免疫火燈 + 速度加成\n"
    "        this.abilityActive={type:'glide',timer:3};\n"
    "        this.showPop('短距滑翔！3s 免疫火燈！');break;}\n"
    "      case 'shrimp':{\n"
    "        // 彎身彈射：長距離衝刺 200px\n"
    "        const sdx=this.lastDir.x,sdy=this.lastDir.y;\n"
    "        this.p.x=Math.max(G.x+20,Math.min(G.x+G.w-20,this.p.x+sdx*200));\n"
    "        this.p.y=Math.max(G.y+20,Math.min(G.y+G.h-20,this.p.y+sdy*200));\n"
    "        this.cameras.main.shake(120,0.007);\n"
    "        this.showPop('彎身彈射！高速限射！');break;}\n"
    "      case 'tofu':{\n"
    "        // 吸熱護盾：吸收附近敵人營度，自身上限 130%\n"
    "        this.abilityActive={type:'shield',timer:5};\n"
    "        this.showPop('吸熱護盾！營度上限 130%！');break;}\n"
    "      case 'bacon':{\n"
    "        // 捲縮甄打：旋轉璔飛周圍\n"
    "        this.abilityActive={type:'spin',timer:1.5};\n"
    "        this.enemies.forEach((e,i)=>{\n"
    "          if(!e.alive) return;\n"
    "          const d=Math.hypot(this.p.x-e.x,this.p.y-e.y);\n"
    "          if(d<110){const nx=d>0?(e.x-this.p.x)/d:1,ny=d>0?(e.y-this.p.y)/d:0;e.x+=nx*140;e.y+=ny*140;this.checkEnemyFall(e,i);}\n"
    "        });\n"
    "        if(this.playerSprite) this.tweens.add({targets:this.playerSprite,angle:360,duration:600,ease:'Linear',onComplete:()=>{if(this.playerSprite)this.playerSprite.setAngle(0);}});\n"
    "        this.cameras.main.shake(200,0.01);\n"
    "        this.showPop('捲縮甄打！旋轉璔飛周圍！');break;}\n"
    "      case 'pepper':{\n"
    "        // 噴辣氣：減速 + 營度 +10%\n"
    "        this.enemies.forEach((e,i)=>{\n"
    "          if(!e.alive) return;\n"
    "          const d=Math.hypot(this.p.x-e.x,this.p.y-e.y);\n"
    "          if(d<130){e.heat=Math.min(100,e.heat+10);e.vx*=0.25;e.vy*=0.25;}\n"
    "        });\n"
    "        this.showPop('噴辣氣！周圍減速營度+10%！');break;}\n"
    "      case 'saury':{\n"
    "        // 刀型衝刺：橫向強力擊飛\n"
    "        const saurdx=this.lastDir.x,saurdy=this.lastDir.y;\n"
    "        this.p.x=Math.max(G.x+20,Math.min(G.x+G.w-20,this.p.x+saurdx*180));\n"
    "        this.p.y=Math.max(G.y+20,Math.min(G.y+G.h-20,this.p.y+saurdy*180));\n"
    "        const perpx=-saurdy,perpy=saurdx;\n"
    "        this.enemies.forEach((e,i)=>{\n"
    "          if(!e.alive) return;\n"
    "          const d=Math.hypot(this.p.x-e.x,this.p.y-e.y);\n"
    "          if(d<90){e.x+=perpx*150;e.y+=perpy*150;this.checkEnemyFall(e,i);}\n"
    "        });\n"
    "        this.cameras.main.shake(180,0.008);\n"
    "        this.showPop('刀型衝刺！橫向連續擊飛！');break;}\n"
    "    }\n"
    "    this.abilityCD=this.abilityCDMax;\n"
    "    this.playSound('push');\n"
    "  }\n"
    "\n"
)
if old_anchor in html:
    html=html.replace(old_anchor, new_method+old_anchor, 1); print("useAbility: OK")
else: print("FAIL useAbility")

# ── 6. Add Space key handling in update() after pushWas ──────────────
old = (
    "    this.pushCD=Math.max(0,this.pushCD-dt);\n"
    "    if(this.keys.push.isDown&&!this.pushWas&&this.pushCD<=0) this.doPush();\n"
    "    this.pushWas=this.keys.push.isDown;"
)
new = (
    "    this.pushCD=Math.max(0,this.pushCD-dt);\n"
    "    if(this.keys.push.isDown&&!this.pushWas&&this.pushCD<=0) this.doPush();\n"
    "    this.pushWas=this.keys.push.isDown;\n"
    "    this.abilityCD=Math.max(0,this.abilityCD-dt);\n"
    "    if(this.keys.skill.isDown&&!this.abilityWas&&this.abilityCD<=0) this.useAbility();\n"
    "    this.abilityWas=this.keys.skill.isDown;"
)
if old in html: html=html.replace(old,new); print("skill input: OK")
else: print("FAIL skill input")

# ── 7. Modify heat section for armor / glide / shield ────────────────
old = (
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
new = (
    "    // 熟度（只增不減）\n"
    "    const ae=this.activeEffects;\n"
    "    const aa=this.abilityActive;\n"
    "    const armorOn=aa&&aa.type==='armor', glideOn=aa&&aa.type==='glide', shieldOn=aa&&aa.type==='shield';\n"
    "    const mult=this.charData.heatMult*(ae.sauce>0?2:1)*(armorOn?0.5:1);\n"
    "    const fireImmune=ae.foil>0||glideOn;\n"
    "    const heatCap=shieldOn?130:100;\n"
    "    if(this.onFire(this.p.x,this.p.y)){\n"
    "      if(!fireImmune) this.heat=Math.min(heatCap,this.heat+15*mult*dt);\n"
    "      this.sizzleTimer-=dt;\n"
    "      if(this.sizzleTimer<=0&&!fireImmune){this.playSound('sizzle');this.sizzleTimer=0.6;}\n"
    "    } else this.heat=Math.min(heatCap,this.heat+1.2*dt);\n"
    "    if(shieldOn){\n"
    "      this.enemies.forEach(e=>{\n"
    "        if(!e.alive) return;\n"
    "        const d=Math.hypot(this.p.x-e.x,this.p.y-e.y);\n"
    "        if(d<120){const absorb=5*dt;e.heat=Math.max(0,e.heat-absorb);this.heat=Math.min(130,this.heat+absorb*0.5);}\n"
    "      });\n"
    "    }\n"
    "    if(this.heat>=heatCap){this.subTxt.setText('被烤熟了！');this.endGame(false);return;}"
)
if old in html: html=html.replace(old,new); print("heat section: OK")
else: print("FAIL heat section")

# ── 8. Add abilityActive timer after activeEffects timer ─────────────
old = (
    "    // 道具效果倒計時\n"
    "    const ae2=this.activeEffects;\n"
    "    Object.keys(ae2).forEach(k=>{if(ae2[k]>0)ae2[k]=Math.max(0,ae2[k]-dt);});"
)
new = (
    "    // 道具效果倒計時\n"
    "    const ae2=this.activeEffects;\n"
    "    Object.keys(ae2).forEach(k=>{if(ae2[k]>0)ae2[k]=Math.max(0,ae2[k]-dt);});\n"
    "    // 技能倒計時\n"
    "    if(this.abilityActive){\n"
    "      this.abilityActive.timer-=dt;\n"
    "      if(this.abilityActive.timer<=0){\n"
    "        if(this.abilityActive.type==='shield') this.heat=Math.min(99,this.heat);\n"
    "        this.abilityActive=null;\n"
    "      }\n"
    "    }"
)
if old in html: html=html.replace(old,new); print("ability timer: OK")
else: print("FAIL ability timer")

# ── 9. Add active ability display in effect indicator ─────────────────
old = (
    "    if(ae2.slowpow>0) eff2.push('!慢速 '+ae2.slowpow.toFixed(0)+'s');\n"
    "    this.effectTxt.setText(eff2.join('  '));"
)
new = (
    "    if(ae2.slowpow>0) eff2.push('!慢速 '+ae2.slowpow.toFixed(0)+'s');\n"
    "    const aa2=this.abilityActive;\n"
    "    if(aa2&&aa2.type==='armor')  eff2.push('裝甲 '+aa2.timer.toFixed(1)+'s');\n"
    "    if(aa2&&aa2.type==='glide')  eff2.push('滑翔免疫 '+aa2.timer.toFixed(1)+'s');\n"
    "    if(aa2&&aa2.type==='shield') eff2.push('護盾吸熱 '+aa2.timer.toFixed(1)+'s');\n"
    "    if(aa2&&aa2.type==='spin')   eff2.push('旋轉中…');\n"
    "    this.effectTxt.setText(eff2.join('  '));"
)
if old in html: html=html.replace(old,new); print("effect indicator: OK")
else: print("FAIL effect indicator")

# ── 10. Update UI section (heat cap + ability bar) ────────────────────
old = (
    "    // UI\n"
    "    this.heatBarFg.width=this.heat*2.2;\n"
    "    this.heatTxt.setText(Math.floor(this.heat)+'%');\n"
    "    this.timerTxt.setText(this.timeLeft+'s');\n"
    "    const ready=this.pushCD<=0;\n"
    "    this.pushBarFg.width=ready?120:(1-this.pushCD/2)*120;\n"
    "    this.pushCdTxt.setText(ready?'Ready!':this.pushCD.toFixed(1)+'s');"
)
new = (
    "    // UI\n"
    "    this.heatBarFg.width=Math.min(220,this.heat*2.2);\n"
    "    this.heatTxt.setText(Math.floor(this.heat)+'%');\n"
    "    this.timerTxt.setText(this.timeLeft+'s');\n"
    "    const ready=this.pushCD<=0;\n"
    "    this.pushBarFg.width=ready?120:(1-this.pushCD/2)*120;\n"
    "    this.pushCdTxt.setText(ready?'Ready!':this.pushCD.toFixed(1)+'s');\n"
    "    const aReady=this.abilityCD<=0;\n"
    "    this.abilBarFg.width=aReady?120:(1-this.abilityCD/this.abilityCDMax)*120;\n"
    "    this.abilBarFg.setFillStyle(aReady?0xffaa00:0x664400);\n"
    "    this.abilCdTxt.setText(aReady?'Ready!':this.abilityCD.toFixed(1)+'s');"
)
if old in html: html=html.replace(old,new); print("UI update: OK")
else: print("FAIL UI update")

# ── 11. Clear abilityActive in endGame ────────────────────────────────
old = (
    "    if(this.tilt){this.tilt=null;this.cameras.main.setRotation(0);}\n"
    "    if(this.tiltTxt) this.tiltTxt.setVisible(false);\n"
    "    if(this.bgmEvent){this.bgmEvent.remove();this.bgmEvent=null;}"
)
new = (
    "    if(this.tilt){this.tilt=null;this.cameras.main.setRotation(0);}\n"
    "    if(this.tiltTxt) this.tiltTxt.setVisible(false);\n"
    "    this.abilityActive=null;\n"
    "    if(this.bgmEvent){this.bgmEvent.remove();this.bgmEvent=null;}"
)
if old in html: html=html.replace(old,new); print("endGame cleanup: OK")
else: print("FAIL endGame cleanup")

# ── 12. Update info div ───────────────────────────────────────────────
old_info = ('↑↓←→ 移動 &nbsp;|&nbsp; S 推擠'
            ' &nbsp;|&nbsp; R 重開 &nbsp;|&nbsp; ESC 返回選角')
new_info = ('↑↓←→ 移動 &nbsp;|&nbsp; S 推擠'
            ' &nbsp;|&nbsp; 空白 技能'
            ' &nbsp;|&nbsp; R 重開 &nbsp;|&nbsp; ESC 返回選角')
if old_info in html: html=html.replace(old_info,new_info); print("info div: OK")
else: print("FAIL info div")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
print("abilityCD init:", "this.abilityCD=0" in v)
print("SPACE key:", "SPACE" in v)
print("useAbility method:", "useAbility(){" in v)
print("skill input:", "this.keys.skill.isDown" in v)
print("armor:", "type:'armor'" in v)
print("glide:", "type:'glide'" in v)
print("shield:", "type:'shield'" in v)
print("spin:", "type:'spin'" in v)
print("heatCap:", "heatCap" in v)
print("abilBarFg:", "abilBarFg" in v)
print("ability timer:", "abilityActive.timer-=dt" in v)
print("effect aa2:", "aa2=this.abilityActive" in v)
print("aReady:", "aReady" in v)
