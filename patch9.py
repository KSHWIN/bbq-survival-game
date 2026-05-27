# -*- coding: utf-8 -*-
# Patch 9: 技能視覺特效 (burst on activate + persistent aura)
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. Add abilFxLayer graphics layer ────────────────────────────────
old = (
    "    this.hbLayer   =this.add.graphics().setDepth(18);\n"
    "    // 餐廳背景"
)
new = (
    "    this.hbLayer   =this.add.graphics().setDepth(18);\n"
    "    this.abilFxLayer=this.add.graphics().setDepth(22);\n"
    "    // 餐廳背景"
)
if old in html: html=html.replace(old,new); print("abilFxLayer: OK")
else: print("FAIL abilFxLayer")

# ── 2. Call fireAbilityFx() at end of useAbility() ───────────────────
old = (
    "    this.abilityCD=this.abilityCDMax;\n"
    "    this.playSound('push');\n"
    "  }\n"
    "\n"
    "  spawnItem(){"
)
new = (
    "    this.fireAbilityFx(c.key);\n"
    "    this.abilityCD=this.abilityCDMax;\n"
    "    this.playSound('push');\n"
    "  }\n"
    "\n"
    # ── fireAbilityFx() helper ─────────────────────────────────────────
    "  fireAbilityFx(key){\n"
    "    const px=this.p.x,py=this.p.y;\n"
    "    // Expanding ring burst helper\n"
    "    const mkBurst=(color,maxR,dur,thick=3)=>{\n"
    "      const bg=this.add.graphics().setDepth(24);\n"
    "      const obj={v:0};\n"
    "      this.tweens.add({targets:obj,v:1,duration:dur,ease:'Quad.easeOut',\n"
    "        onUpdate:()=>{bg.clear();const p=obj.v;bg.lineStyle(thick*(1-p),color,1-p);bg.strokeCircle(px,py,maxR*p);},\n"
    "        onComplete:()=>bg.destroy()});\n"
    "    };\n"
    "    // Instant filled flash helper\n"
    "    const mkFlash=(color,r,dur)=>{\n"
    "      const fg=this.add.graphics().setDepth(24);\n"
    "      fg.fillStyle(color,0.85); fg.fillCircle(px,py,r);\n"
    "      this.tweens.add({targets:fg,alpha:0,duration:dur,onComplete:()=>fg.destroy()});\n"
    "    };\n"
    "    switch(key){\n"
    "      case 'pork':   // 橙色衝刺爆炸\n"
    "        mkFlash(0xffcc44,42,180); mkBurst(0xff9900,95,500,5); mkBurst(0xffee88,62,320); break;\n"
    "      case 'beef':   // 藍色護甲閃光\n"
    "        mkFlash(0x4488ff,38,220); mkBurst(0x4488ff,58,600,4); mkBurst(0x88aaff,42,800,2); break;\n"
    "      case 'mushroom': // 白色傳送閃\n"
    "        mkFlash(0xffffff,55,140); mkBurst(0xbbddff,75,380,4); mkBurst(0xffffff,48,260,2); break;\n"
    "      case 'corn':   // 大型爆炸多環\n"
    "        mkFlash(0xffff44,65,160); mkBurst(0xffdd00,115,650,6); mkBurst(0xff8800,82,480,4); mkBurst(0xffff88,55,320,2); break;\n"
    "      case 'wing':   // 青綠色滑翔圈\n"
    "        mkFlash(0x44ffee,38,160); mkBurst(0x00ffee,65,450,4); mkBurst(0x88ffff,42,580,2); break;\n"
    "      case 'shrimp': // 藍紫速度圈\n"
    "        mkFlash(0x88aaff,42,140); mkBurst(0x4466ff,85,380,5); mkBurst(0xaabbff,55,260,2); break;\n"
    "      case 'tofu':   // 金色護盾波\n"
    "        mkFlash(0xffee88,48,200); mkBurst(0xffdd00,72,550,4); mkBurst(0xffffff,52,380,2); break;\n"
    "      case 'bacon':  // 紅橙旋轉大爆炸\n"
    "        mkFlash(0xff6600,55,160); mkBurst(0xff4400,105,650,6); mkBurst(0xffaa00,78,480,4); mkBurst(0xff8800,52,320,2); break;\n"
    "      case 'pepper': // 綠色辣氣爆散\n"
    "        mkFlash(0x44ff44,42,160); mkBurst(0x44ff44,85,480,5); mkBurst(0x88ff88,58,320,2); break;\n"
    "      case 'saury':  // 白色刀光\n"
    "        mkFlash(0xffffff,58,140); mkBurst(0xffffff,105,380,5); mkBurst(0x88ccff,72,270,2); break;\n"
    "    }\n"
    "  }\n"
    "\n"
    "  spawnItem(){"
)
if old in html: html=html.replace(old,new); print("fireAbilityFx: OK")
else: print("FAIL fireAbilityFx")

# ── 3. Per-frame persistent ability aura in update() draw section ─────
old = (
    "    // 繪製\n"
    "    this.firePhase+=dt*3;\n"
    "    this.drawFires(this.firePhase);\n"
    "    // 敵人熟度條"
)
new = (
    "    // 繪製\n"
    "    this.firePhase+=dt*3;\n"
    "    this.drawFires(this.firePhase);\n"
    "    // 技能持續光環\n"
    "    this.abilFxLayer.clear();\n"
    "    const aaFx=this.abilityActive;\n"
    "    if(aaFx){\n"
    "      const gfx=this.abilFxLayer,px2=this.p.x,py2=this.p.y,ph=this.firePhase;\n"
    "      if(aaFx.type==='armor'){\n"
    "        // 藍色六角護甲脈衝\n"
    "        const pulse=0.5+0.5*Math.sin(ph*5);\n"
    "        gfx.lineStyle(4,0x4488ff,pulse); gfx.strokeCircle(px2,py2,32);\n"
    "        gfx.lineStyle(1,0x88aaff,pulse*0.5); gfx.strokeCircle(px2,py2,40);\n"
    "        for(let i=0;i<6;i++){const a=i*Math.PI/3;gfx.fillStyle(0x4488ff,0.12);gfx.fillTriangle(px2,py2,px2+Math.cos(a)*32,py2+Math.sin(a)*32,px2+Math.cos(a+Math.PI/3)*32,py2+Math.sin(a+Math.PI/3)*32);}\n"
    "      }\n"
    "      if(aaFx.type==='glide'){\n"
    "        // 青色翅膀光圈\n"
    "        const flap=0.35+0.35*Math.sin(ph*7);\n"
    "        gfx.lineStyle(2,0x44ffee,0.9); gfx.strokeCircle(px2,py2,28);\n"
    "        gfx.fillStyle(0x44ffee,0.15); gfx.fillCircle(px2,py2,28);\n"
    "        const ld=this.lastDir,wx=-ld.y,wy=ld.x;\n"
    "        for(let s=-1;s<=1;s+=2){gfx.fillStyle(0x00ffee,0.3+flap);gfx.fillTriangle(px2+wx*s*26,py2+wy*s*26,px2-ld.x*20,py2-ld.y*20,px2+wx*s*10-ld.x*10,py2+wy*s*10-ld.y*10);}\n"
    "      }\n"
    "      if(aaFx.type==='shield'){\n"
    "        // 金色旋轉吸收環\n"
    "        const rot=ph*2.5;\n"
    "        gfx.lineStyle(2,0xffdd00,0.45); gfx.strokeCircle(px2,py2,38);\n"
    "        for(let i=0;i<8;i++){const a=rot+i*Math.PI/4,r=34+5*Math.sin(ph*9+i);gfx.fillStyle(i%2===0?0xffdd00:0xffaa00,0.9);gfx.fillCircle(px2+Math.cos(a)*r,py2+Math.sin(a)*r,5);}\n"
    "      }\n"
    "      if(aaFx.type==='spin'){\n"
    "        // 紅橙旋轉火花\n"
    "        const rot=ph*12;\n"
    "        for(let i=0;i<12;i++){const a=rot+i*Math.PI/6,r=12+14*(i%2);const col=i%2===0?0xff4400:0xffaa00;gfx.fillStyle(col,0.9);gfx.fillCircle(px2+Math.cos(a)*r,py2+Math.sin(a)*r,4+i%2);}\n"
    "      }\n"
    "    }\n"
    "    // 敵人熟度條"
)
if old in html: html=html.replace(old,new); print("aura FX: OK")
else: print("FAIL aura FX")

# ── 4. Clear abilFxLayer in endGame ──────────────────────────────────
old = (
    "    this.abilityActive=null;\n"
    "    if(this.bgmEvent){this.bgmEvent.remove();this.bgmEvent=null;}"
)
new = (
    "    this.abilityActive=null;\n"
    "    if(this.abilFxLayer) this.abilFxLayer.clear();\n"
    "    if(this.bgmEvent){this.bgmEvent.remove();this.bgmEvent=null;}"
)
if old in html: html=html.replace(old,new); print("endGame abilFx clear: OK")
else: print("FAIL endGame abilFx clear")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
print("abilFxLayer init:", "this.abilFxLayer=this.add.graphics()" in v)
print("fireAbilityFx method:", "fireAbilityFx(key){" in v)
print("fireAbilityFx call:", "this.fireAbilityFx(c.key)" in v)
print("mkBurst:", "mkBurst" in v)
print("mkFlash:", "mkFlash" in v)
print("aura fx clear:", "this.abilFxLayer.clear()" in v)
print("armor aura:", "type==='armor'" in v)
print("glide wings:", "type==='glide'" in v)
print("shield ring:", "type==='shield'" in v)
print("spin sparks:", "type==='spin'" in v)
print("endGame clear:", "this.abilFxLayer.clear()" in v)
