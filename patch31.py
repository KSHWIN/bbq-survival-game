# -*- coding: utf-8 -*-
# Patch 31: 地板隨機破洞 + 縮圈邊緣純黑化
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

# ── 1. 加 holeLayer ───────────────────────────────────────────────
rep("holeLayer",
    "    this.shrinkLayer=this.add.graphics().setDepth(4);",
    "    this.shrinkLayer=this.add.graphics().setDepth(4);\n"
    "    this.holeLayer  =this.add.graphics().setDepth(5);")

# ── 2. 加破洞初始化 ──────────────────────────────────────────────
rep("hole init",
    "    this.evtTimer=12+Math.random()*5; this.evtQueue=[];",
    "    this.evtTimer=12+Math.random()*5; this.evtQueue=[];\n"
    "    this.holes=[]; this.holeTimer=10+Math.random()*5;")

# ── 3. update 裡加破洞更新 ───────────────────────────────────────
rep("hole update call",
    "    this.updateShrink(dt);    if(!this.alive) return;",
    "    this.updateShrink(dt);    if(!this.alive) return;\n"
    "    this.updateHoles(dt);     if(!this.alive) return;")

# ── 4. 繪製呼叫加入 drawHoles ────────────────────────────────────
rep("hole draw call",
    "    this.drawShrinkRing();\n"
    "    this.drawEventFx();",
    "    this.drawShrinkRing();\n"
    "    this.drawHoles();\n"
    "    this.drawEventFx();")

# ── 5. 縮圈死區改純黑 ───────────────────────────────────────────
rep("shrink black fill",
    "      g.fillStyle(0x0d0000,0.90);",
    "      g.fillStyle(0x000000,1.0);")

# ── 6. 縮圈邊界改為白線 + 紅焰 ─────────────────────────────────
rep("shrink border lines",
    "      const glow=0.5+0.3*Math.sin(ph*3.5);\n"
    "      g.lineStyle(4,0xff2200,glow); g.strokeRect(G.x+pad,G.y+pad,G.w-pad*2,G.h-pad*2);\n"
    "      g.lineStyle(1,0xff6600,glow*0.5); g.strokeRect(G.x+pad+3,G.y+pad+3,G.w-pad*2-6,G.h-pad*2-6);",
    "      const glow=0.5+0.3*Math.sin(ph*3.5);\n"
    "      g.lineStyle(3,0xffffff,0.95); g.strokeRect(G.x+pad,G.y+pad,G.w-pad*2,G.h-pad*2);\n"
    "      g.lineStyle(5,0xff2200,glow*0.65); g.strokeRect(G.x+pad-1,G.y+pad-1,G.w-pad*2+2,G.h-pad*2+2);")

# ── 7. 新增 updateHoles + drawHoles 方法 ─────────────────────────
HOLE_METHODS = """
  updateHoles(dt){
    // 生成計時
    this.holeTimer-=dt;
    if(this.holeTimer<=0){
      this.holeTimer=7+Math.random()*6;
      const pad=this.shrinkPad+32;
      const sx=G.w-pad*2-56, sy=G.h-pad*2-56;
      if(sx>0&&sy>0){
        this.holes.push({
          x:G.x+pad+28+Math.random()*sx,
          y:G.y+pad+28+Math.random()*sy,
          r:18+Math.random()*10,
          state:'warn', timer:2.2, alpha:0
        });
      }
    }
    // 更新每個洞
    let fell=false;
    this.holes=this.holes.filter(h=>{
      h.timer-=dt;
      if(h.state==='warn'){
        if(h.timer<=0){h.state='active';h.timer=4+Math.random()*3;h.alpha=0;}
        return true;
      }
      if(h.state==='active'){
        h.alpha=Math.min(1,h.alpha+dt*2.5);
        // 玩家掉落
        if(!fell&&h.alpha>0.5&&Math.hypot(this.p.x-h.x,this.p.y-h.y)<h.r*0.78){
          fell=true;
          this.subTxt.setText('掉進洞裡了！'); this.endGame(false);
        }
        // AI 掉落
        this.enemies.forEach((e,i)=>{
          if(!e.alive||h.alpha<0.5) return;
          if(Math.hypot(e.x-h.x,e.y-h.y)<h.r*0.78) this.checkEnemyFall(e,i);
        });
        if(h.timer<=0){h.state='closing';h.timer=0.9;}
        return true;
      }
      if(h.state==='closing'){
        h.alpha=Math.max(0,(h.timer/0.9));
        return h.timer>0;
      }
      return false;
    });
  }

  drawHoles(){
    const g=this.holeLayer; g.clear();
    const ph=this.firePhase;
    this.holes.forEach(h=>{
      if(h.state==='warn'){
        const pulse=0.35+0.3*Math.sin(ph*11);
        g.fillStyle(0xff6600,pulse*0.25);
        g.fillCircle(h.x,h.y,h.r*(1.1+pulse*0.15));
        g.lineStyle(3,0xff8800,0.55+pulse);
        g.strokeCircle(h.x,h.y,h.r);
        const cx=h.r*0.55;
        g.lineStyle(2,0xff4400,0.8);
        g.lineBetween(h.x-cx,h.y-cx,h.x+cx,h.y+cx);
        g.lineBetween(h.x+cx,h.y-cx,h.x-cx,h.y+cx);
      } else if(h.state==='active'||h.state==='closing'){
        const a=h.alpha;
        g.fillStyle(0x000000,a);
        g.fillCircle(h.x,h.y,h.r);
        const glow=0.6+0.4*Math.sin(ph*5);
        g.lineStyle(3,0xff3300,a*glow);
        g.strokeCircle(h.x,h.y,h.r);
        g.lineStyle(1,0xff8800,a*0.4);
        g.strokeCircle(h.x,h.y,h.r*1.25);
      }
    });
  }
"""

rep("hole methods",
    "  }\n}\n\nnew Phaser.Game({",
    "  }\n" + HOLE_METHODS + "}\n\nnew Phaser.Game({")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

for r in results:
    print(r)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
checks = [
    ("holeLayer",           "holeLayer init"),
    ("this.holes=[]",       "holes array"),
    ("holeTimer",           "holeTimer"),
    ("updateHoles",         "updateHoles call"),
    ("drawHoles",           "drawHoles call"),
    ("0x000000,1.0",        "pure black fill"),
    ("0xffffff,0.95",       "white border"),
    ("state==='warn'",      "warn state"),
    ("state==='closing'",   "closing state"),
    ("掉進洞裡了",          "hole death msg"),
]
for key, label in checks:
    print(f"{label}: {'OK' if key in v else 'MISSING'}")
