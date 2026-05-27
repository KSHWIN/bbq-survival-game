# -*- coding: utf-8 -*-
# Patch 15: 衝刺卡死修正 + 火焰視覺重做（穩定大小、寬底窄頂、深外淺內）
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. doPush 加入衝刺中不重複觸發的 guard ────────────────────────────────
old = (
    "    // 速度決定衝刺距離，體重決定推力\n"
    "    const spd=c.speed/155, wgt=c.weight||1;\n"
)
new = (
    "    // 衝刺中不重複觸發\n"
    "    if(this.dashState&&this.dashState.active) return;\n"
    "    // 速度決定衝刺距離，體重決定推力\n"
    "    const spd=c.speed/155, wgt=c.weight||1;\n"
)
if old in html: html=html.replace(old,new); print("doPush guard: OK")
else: print("FAIL doPush guard")

# ── 2. isDash 計算後加入安全逾時清除 ────────────────────────────────────
old = (
    "    const isDash=!!(this.dashState&&this.dashState.active);\n"
    "    const SPD=isDash?320:this.charData.speed*(this.activeEffects.slowpow>0?0.5:1);\n"
)
new = (
    "    // 安全機制：衝刺超過 0.6 秒強制結束\n"
    "    if(this.dashState&&this.dashState.active){\n"
    "      this.dashState.age=(this.dashState.age||0)+dt;\n"
    "      if(this.dashState.age>0.6) this.dashState.active=false;\n"
    "    }\n"
    "    if(this.dashState&&!this.dashState.active) this.dashState=null;\n"
    "    const isDash=!!(this.dashState&&this.dashState.active);\n"
    "    const SPD=isDash?320:this.charData.speed*(this.activeEffects.slowpow>0?0.5:1);\n"
)
if old in html: html=html.replace(old,new); print("dash safety timeout: OK")
else: print("FAIL dash safety")

# ── 3. lastDir 只從鍵盤更新，不被衝刺方向覆蓋 ────────────────────────────
old = "    if(mx||my){this.lastDir.x=mx;this.lastDir.y=my;}"
new = (
    "    // lastDir 只從鍵盤輸入更新，忽略衝刺覆蓋方向\n"
    "    const kx=(this.keys.left.isDown?-1:this.keys.right.isDown?1:0);\n"
    "    const ky=(this.keys.up.isDown?-1:this.keys.down.isDown?1:0);\n"
    "    if(kx||ky){this.lastDir.x=kx;this.lastDir.y=ky;}"
)
if old in html: html=html.replace(old,new); print("lastDir keyboard-only: OK")
else: print("FAIL lastDir")

# ── 4. 完全重做 drawFires：穩定大小 + 火焰形狀 + 深外淺內 ─────────────────
old = (
    "      // 活躍火焰\n"
    "      const alpha=f.state==='active'?1.0:0.45;\n"
    "      // 第二振盪讓火焰形狀更不規則\n"
    "      const s=this.FIRE_R_BASE+this.FIRE_R_AMP*Math.sin(phase*f.spd+f.ph)\n"
    "              +this.FIRE_R_AMP*0.35*Math.sin(phase*f.spd*1.7+f.ph+1.2);\n"
    "      f.r=Math.max(12,s);\n"
    "      const fc1=(this.levelData&&this.levelData.fireC1)||0xff4400;\n"
    "      const fc2=(this.levelData&&this.levelData.fireC2)||0xff9900;\n"
    "      // 暗底陰影（增加立體感與緊張感）\n"
    "      g.fillStyle(0x000000,0.30*alpha); g.fillCircle(f.x,f.y+4,f.r*1.1);\n"
    "      // 主火焰（明亮）\n"
    "      g.fillStyle(fc1,0.88*alpha); g.fillCircle(f.x,f.y,f.r);\n"
    "      // 內層亮核\n"
    "      g.fillStyle(fc2,0.72*alpha); g.fillCircle(f.x,f.y,f.r*0.52);\n"
    "      // 白熱核心\n"
    "      g.fillStyle(0xffffff,0.42*alpha); g.fillCircle(f.x,f.y,f.r*0.20);\n"
)
new = (
    "      // 活躍火焰\n"
    "      const alpha=f.state==='active'?1.0:0.45;\n"
    "      // 大小幾乎固定，只有極微小呼吸感（±5%）\n"
    "      const breathe=1+Math.sin(phase*f.spd+f.ph)*0.05;\n"
    "      f.r=this.FIRE_R_BASE*breathe;\n"
    "      const R=f.r;\n"
    "      const fw=R*0.72;           // 焰寬（比高窄）\n"
    "      const fh=R*1.75;           // 焰高（寬底窄頂的橢圓）\n"
    "      const cx=f.x, cy=f.y-R*0.18; // 整體往上移，模擬火焰升起\n"
    "      const fc1=(this.levelData&&this.levelData.fireC1)||0xff4400;\n"
    "      const fc2=(this.levelData&&this.levelData.fireC2)||0xff9900;\n"
    "      // ① 地面暗影（橢圓扁平，在火焰正下方）\n"
    "      g.fillStyle(0x000000,0.40*alpha); g.fillEllipse(cx,f.y+R*0.45,fw*2.1,R*0.45);\n"
    "      // ② 最外層暗暈（深色，模擬真火外緣燻黑感）\n"
    "      g.fillStyle(0x110000,0.55*alpha); g.fillEllipse(cx,cy,fw*1.7,fh*1.15);\n"
    "      // ③ 主體火焰（fc1，中深色）\n"
    "      g.fillStyle(fc1,0.90*alpha); g.fillEllipse(cx,cy,fw*1.1,fh);\n"
    "      // ④ 側搖舌（微量橫向偏移，增加不規則感）\n"
    "      const toff=Math.sin(phase*f.spd*1.8+f.ph+0.9)*fw*0.18;\n"
    "      g.fillStyle(fc2,0.65*alpha); g.fillEllipse(cx+toff,cy-R*0.18,fw*0.62,fh*0.72);\n"
    "      // ⑤ 亮核（fc2，較亮）\n"
    "      g.fillStyle(fc2,0.88*alpha); g.fillEllipse(cx,cy+R*0.10,fw*0.48,fh*0.45);\n"
    "      // ⑥ 中心白熱點（最亮）\n"
    "      g.fillStyle(0xffffff,0.55*alpha); g.fillEllipse(cx,cy+R*0.15,fw*0.22,fh*0.22);\n"
)
if old in html: html=html.replace(old,new); print("drawFires reshape: OK")
else: print("FAIL drawFires")

# ── 5. 警告火焰改為穩定淡色光圈（不閃爍）────────────────────────────────
old = (
    "      if(f.state==='warning'){\n"
    "        const a=0.22+0.16*Math.sin(phase*8);\n"
    "        const wc=(this.levelData&&this.levelData.fireC1)||0xff4400;\n"
    "        g.fillStyle(wc,a*0.5); g.fillCircle(f.tx,f.ty,this.FIRE_R_BASE);\n"
    "        g.lineStyle(3,wc,a*2.5); g.strokeCircle(f.tx,f.ty,this.FIRE_R_BASE);\n"
    "        // 警告十字\n"
    "        g.lineStyle(2,0xffffff,a*1.8);\n"
    "        g.lineBetween(f.tx-10,f.ty,f.tx+10,f.ty);\n"
    "        g.lineBetween(f.tx,f.ty-10,f.tx,f.ty+10);\n"
    "      }\n"
)
new = (
    "      if(f.state==='warning'){\n"
    "        // 預警：穩定淡色光圈（比活躍時淺，讓玩家有時間反應）\n"
    "        const wc=(this.levelData&&this.levelData.fireC1)||0xff4400;\n"
    "        g.fillStyle(wc,0.14); g.fillEllipse(f.tx,f.ty,this.FIRE_R_BASE*1.9,this.FIRE_R_BASE*2.3);\n"
    "        g.lineStyle(2,wc,0.50); g.strokeEllipse(f.tx,f.ty,this.FIRE_R_BASE*1.9,this.FIRE_R_BASE*2.3);\n"
    "        // 細十字標記讓玩家知道位置\n"
    "        g.lineStyle(1,0xffffff,0.45);\n"
    "        g.lineBetween(f.tx-12,f.ty,f.tx+12,f.ty);\n"
    "        g.lineBetween(f.tx,f.ty-12,f.tx,f.ty+12);\n"
    "      }\n"
)
if old in html: html=html.replace(old,new); print("warning fire steady: OK")
else: print("FAIL warning fire")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
print("doPush guard:", "dashState.active) return;" in v)
print("dash timeout 0.6s:", "dashState.age>0.6" in v)
print("dashState null cleanup:", "dashState=null;" in v)
print("lastDir keyboard-only:", "lastDir.x=kx;this.lastDir.y=ky;" in v)
print("fire ellipse shape:", "fh=R*1.75;" in v)
print("fire breathe ±5%:", "breathe=1+Math.sin" in v)
print("fire dark outer:", "最外層暗暈" in v)
print("warning steady:", "穩定淡色光圈" in v)
