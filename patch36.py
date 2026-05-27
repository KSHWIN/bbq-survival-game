# -*- coding: utf-8 -*-
# Patch 36: FoodItem/PorkBelly/Mushroom 類別 + 油漬系統 + fireMult 弱點
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

# ── 1. FoodItem / PorkBelly / Mushroom 類別定義 ───────────────────
rep("fooditem classes",
    "const CHARS = [",
    "// ── 食材基礎類別 ──────────────────────────────────────────────\n"
    "class FoodItem {\n"
    "  constructor(d){ Object.assign(this,{heatMult:1.0,fireMult:1.0},d); }\n"
    "}\n"
    "class PorkBelly extends FoodItem {\n"
    "  constructor(){ super({key:'pork',name:'五花肉',img:'char_pork',speed:90,weight:1.5,\n"
    "    heatMult:1.0,fireMult:1.2,\n"
    "    ability:'滑油衝刺',abilityDesc:'衝刺留下3秒油漬，踩到者失控滑行；火焰傷害+20%',\n"
    "    stats:{'血量':'★★★','速度':'★☆☆','耐熱':'★★☆'},color:0xffbbaa}); }\n"
    "}\n"
    "class Mushroom extends FoodItem {\n"
    "  constructor(){ super({key:'mushroom',name:'香菇',img:'char_mushroom',speed:155,weight:0.7,\n"
    "    heatMult:1.3,fireMult:1.0,\n"
    "    ability:'縮水跳躍',abilityDesc:'按技能鍵縮小後瞬移至安全位置；熟度累積+30%',\n"
    "    stats:{'血量':'★☆☆','速度':'★★★','耐熱':'★★★'},color:0xaa7744}); }\n"
    "}\n\n"
    "const CHARS = [")

# ── 2. CHARS：pork 改用 new PorkBelly() ──────────────────────────
rep("chars pork class",
    "  { key:'pork',     name:'五花肉', img:'char_pork',     speed:90,  heatMult:1.0, weight:1.5, ability:'滑油衝刺', abilityDesc:'推力×1.5，炸開周圍所有食材',        stats:{'血量':'★★★','速度':'★☆☆','耐熱':'★★☆'}, color:0xffbbaa },",
    "  new PorkBelly(),")

# ── 3. CHARS：mushroom 改用 new Mushroom() ────────────────────────
rep("chars mushroom class",
    "  { key:'mushroom', name:'香菇',   img:'char_mushroom', speed:155, heatMult:1.3, weight:0.7, ability:'縮水跳躍', abilityDesc:'被推瞬間可反向彈跳脫逃',              stats:{'血量':'★☆☆','速度':'★★★','耐熱':'★★★'}, color:0xaa7744 },",
    "  new Mushroom(),")

# ── 4. activeEffects 加 oilSlick ─────────────────────────────────
rep("oilslick effect",
    "    this.activeEffects={foil:0,garlic:0,sauce:0,slowpow:0,stun:0,toxic:0};",
    "    this.activeEffects={foil:0,garlic:0,sauce:0,slowpow:0,stun:0,toxic:0,oilSlick:0};")

# ── 5. create() 加 oilSlicks / oilDir / oilLayer ─────────────────
rep("oil init",
    "    this.mapItems=[]; this.itemTimer=3; this.sizzleTimer=0;",
    "    this.mapItems=[]; this.itemTimer=3; this.sizzleTimer=0;\n"
    "    this.oilSlicks=[]; this.oilDir={x:0,y:0};\n"
    "    this.oilLayer=this.add.graphics().setDepth(3);")

# ── 6. pork useAbility：衝刺後留油漬 ─────────────────────────────
rep("pork oil slick ability",
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
    "        this.showPop('滑油衝刺！衝開周圍！');break;}",

    "      case 'pork':{\n"
    "        const dx=this.lastDir.x,dy=this.lastDir.y;\n"
    "        const ox=this.p.x,oy=this.p.y;\n"
    "        this.p.x=Math.max(G.x+20,Math.min(G.x+G.w-20,this.p.x+dx*120));\n"
    "        this.p.y=Math.max(G.y+20,Math.min(G.y+G.h-20,this.p.y+dy*120));\n"
    "        // 衝刺路徑留下 3 個油漬\n"
    "        for(let s=1;s<=3;s++){\n"
    "          this.oilSlicks.push({x:ox+dx*40*s,y:oy+dy*40*s,r:30,life:3.0,ph:Math.random()*Math.PI*2});\n"
    "        }\n"
    "        this.enemies.forEach((e,i)=>{\n"
    "          if(!e.alive) return;\n"
    "          const d=Math.hypot(this.p.x-e.x,this.p.y-e.y);\n"
    "          if(d<90){const nx=d>0?(e.x-this.p.x)/d:1,ny=d>0?(e.y-this.p.y)/d:0;e.x+=nx*120;e.y+=ny*120;this.checkEnemyFall(e,i);}\n"
    "        });\n"
    "        this.showPop('🛢 滑油衝刺！地面留下油漬！');break;}")

# ── 7. mushroom useAbility：縮小動畫再瞬移 ────────────────────────
rep("mushroom shrink jump",
    "      case 'mushroom':{\n"
    "        // 縮水跳躍：尋找安全位置擺移\n"
    "        let bx=this.p.x,by=this.p.y;\n"
    "        for(let att=0;att<30;att++){\n"
    "          const cx=G.x+60+Math.random()*(G.w-120),cy=G.y+60+Math.random()*(G.h-120);\n"
    "          if(!this.onFire(cx,cy)&&inGrill(cx,cy)){bx=cx;by=cy;break;}\n"
    "        }\n"
    "        this.p.x=bx;this.p.y=by;\n"
    "        this.cameras.main.shake(150,0.008);\n"
    "        this.showPop('縮水跳躍！瞬間移位！');break;}",

    "      case 'mushroom':{\n"
    "        // 縮水跳躍：找安全位置 → 縮小動畫 → 瞬移 → 放大\n"
    "        let bx=this.p.x,by=this.p.y;\n"
    "        for(let att=0;att<40;att++){\n"
    "          const cx=G.x+55+Math.random()*(G.w-110),cy=G.y+55+Math.random()*(G.h-110);\n"
    "          if(!this.onFire(cx,cy)&&inGrill(cx,cy)&&Math.hypot(cx-this.p.x,cy-this.p.y)>60){bx=cx;by=cy;break;}\n"
    "        }\n"
    "        if(this.playerSprite){\n"
    "          const SS=this.playerSprite.baseScale||0.19;\n"
    "          this.tweens.add({targets:this.playerSprite,scaleX:SS*0.08,scaleY:SS*0.08,duration:160,\n"
    "            onComplete:()=>{\n"
    "              this.p.x=bx;this.p.y=by;\n"
    "              this.playerSprite.setPosition(bx,by);\n"
    "              this.tweens.add({targets:this.playerSprite,scaleX:SS,scaleY:SS,duration:220,ease:'Back.easeOut'});\n"
    "            }});\n"
    "        } else { this.p.x=bx;this.p.y=by; }\n"
    "        this.cameras.main.shake(150,0.008);\n"
    "        this.showPop('🍄 縮水跳躍！縮小後瞬移！');break;}")

# ── 8. 火焰傷害乘上 fireMult ──────────────────────────────────────
rep("fire mult",
    "      if(!fireImmune) this.heat=Math.min(heatCap,this.heat+15*mult*dt);",
    "      if(!fireImmune) this.heat=Math.min(heatCap,this.heat+15*mult*(this.charData.fireMult||1.0)*dt);")

# ── 9. 玩家在油漬上失控滑行 ──────────────────────────────────────
rep("player oil slip",
    "    if(this.activeEffects.stun>0){mx=0;my=0;if(isDash&&this.dashState)this.dashState.active=false;}",
    "    if(this.activeEffects.stun>0){mx=0;my=0;if(isDash&&this.dashState)this.dashState.active=false;}\n"
    "    if(!isDash){\n"
    "      if(this.activeEffects.oilSlick>0){\n"
    "        mx=mx*0.15+(this.oilDir.x||0)*0.85;\n"
    "        my=my*0.15+(this.oilDir.y||0)*0.85;\n"
    "      } else if(mx||my){this.oilDir.x=mx;this.oilDir.y=my;}\n"
    "    }")

# ── 10. AI 在油漬上加速滑行 ──────────────────────────────────────
rep("ai oil slip",
    "      e.x+=e.vx; e.y+=e.vy;\n"
    "      if(e.x<G.x+e.r||e.x>G.x+G.w-e.r) e.vx*=-1;",
    "      if(this.oilSlicks&&this.oilSlicks.some(os=>Math.hypot(e.x-os.x,e.y-os.y)<os.r)){e.vx*=1.06;e.vy*=1.06;}\n"
    "      e.x+=e.vx; e.y+=e.vy;\n"
    "      if(e.x<G.x+e.r||e.x>G.x+G.w-e.r) e.vx*=-1;")

# ── 11. update() 呼叫 updateOilSlicks ────────────────────────────
rep("oil update call",
    "    this.updateUltOrbs(dt);",
    "    this.updateUltOrbs(dt);\n"
    "    this.updateOilSlicks(dt);")

# ── 12. 新增 updateOilSlicks 方法 ────────────────────────────────
OIL_METHOD = """
  updateOilSlicks(dt){
    const g=this.oilLayer; g.clear();
    this.oilSlicks=this.oilSlicks.filter(os=>{
      os.life-=dt; os.ph=(os.ph||0)+dt*1.5;
      if(os.life<=0) return false;
      const fadeA=Math.min(1,os.life/0.4);
      const shimmer=0.5+0.5*Math.sin(os.ph*2.5);
      g.fillStyle(0xffee55,fadeA*(0.42+shimmer*0.16));
      g.fillCircle(os.x,os.y,os.r);
      g.lineStyle(2,0xffcc00,fadeA*(0.35+shimmer*0.25));
      g.strokeCircle(os.x,os.y,os.r+2);
      // 玩家踩到 → 設定效果
      if(Math.hypot(this.p.x-os.x,this.p.y-os.y)<os.r)
        this.activeEffects.oilSlick=0.35;
      return true;
    });
  }
"""

rep("oil method",
    "  }\n}\n\nnew Phaser.Game({",
    "  }\n" + OIL_METHOD + "}\n\nnew Phaser.Game({")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

for r in results:
    print(r)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
checks = [
    ("class FoodItem",           "FoodItem class"),
    ("class PorkBelly extends",  "PorkBelly class"),
    ("class Mushroom extends",   "Mushroom class"),
    ("fireMult:1.2",             "pork fireMult"),
    ("heatMult:1.3",             "mushroom heatMult"),
    ("new PorkBelly()",          "chars use PorkBelly"),
    ("new Mushroom()",           "chars use Mushroom"),
    ("oilSlick:0",               "oilSlick in effects"),
    ("this.oilSlicks=[]",        "oilSlicks array"),
    ("this.oilLayer",            "oilLayer graphics"),
    ("oil漬",                    "oil popup msg"),
    ("縮小後瞬移",               "mushroom shrink msg"),
    ("fireMult||1.0",            "fireMult in heat"),
    ("activeEffects.oilSlick>0", "player oil check"),
    ("os=>Math.hypot",           "ai oil check"),
    ("updateOilSlicks",          "updateOilSlicks method"),
]
for key, label in checks:
    print(f"{label}: {'OK' if key in v else 'MISSING'}")
