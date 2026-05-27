# -*- coding: utf-8 -*-
# Patch 14: 透明修正 + 體重物理 + 地圖火焰差異化
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. _rmWhite：大幅提高閾值，避免去掉豆腐等淡色角色的身體 ──────────────
old = (
    "      if(mn>238&&sat<18) d[i+3]=0;\n"
    "      else if(mn>222&&sat<25) d[i+3]=Math.round(d[i+3]*(mn-222)/16);\n"
)
new = (
    "      if(mn>250&&sat<6) d[i+3]=0;\n"
    "      else if(mn>245&&sat<10) d[i+3]=Math.round(d[i+3]*(mn-245)/5);\n"
)
if old in html: html=html.replace(old,new); print("_rmWhite threshold: OK")
else: print("FAIL _rmWhite threshold")

# ── 2. _buildDir fillRect bug：-W → 0（translate+scale 後座標系修正）──────
old = "      ctxb.fillRect(-W,0,W,H);"
new = "      ctxb.fillRect(0,0,W,H);"
if old in html: html=html.replace(old,new); print("_buildDir fillRect: OK")
else: print("FAIL _buildDir fillRect")

# ── 3. doPush 物理：體重→推力，速度→衝刺距離 ──────────────────────────────
old = (
    "    const DIST=(c.key==='pork'?80:64)*boost;\n"
    "    const FORCE=(c.key==='pork'?86:70)*boost;\n"
)
new = (
    "    // 速度決定衝刺距離，體重決定推力\n"
    "    const spd=c.speed/155, wgt=c.weight||1;\n"
    "    const DIST=Math.round(58*spd)*boost;   // 快→遠\n"
    "    const FORCE=Math.round(60*wgt)*boost;  // 重→強\n"
)
if old in html: html=html.replace(old,new); print("doPush weight/speed physics: OK")
else: print("FAIL doPush physics")

# ── 4. LEVELS 加入地圖專屬火焰色 ──────────────────────────────────────────
old = (
    "  {key:'lv1',name:'家庭烤肉架',  sub:'初心者友好',       diff:1, timer:60, heatMod:1.0, forkMod:1.0, tiltMod:1.0, fireCnt:8 },\n"
    "  {key:'lv2',name:'餐廳鐵板燒',  sub:'高溫快節奏',       diff:3, timer:75, heatMod:1.3, forkMod:1.5, tiltMod:1.0, fireCnt:10},\n"
    "  {key:'lv3',name:'露營野火烤架', sub:'風向不定傾斜頻繁',  diff:4, timer:90, heatMod:1.1, forkMod:1.0, tiltMod:2.5, fireCnt:8 },\n"
    "  {key:'lv4',name:'地獄料理直播', sub:'雙叉子超高溫',     diff:5, timer:45, heatMod:1.5, forkMod:2.5, tiltMod:1.5, fireCnt:12},\n"
)
new = (
    "  {key:'lv1',name:'家庭烤肉架',  sub:'初心者友好',       diff:1, timer:60, heatMod:1.0, forkMod:1.0, tiltMod:1.0, fireCnt:8,  fireC1:0xff4400,fireC2:0xff9900 },\n"
    "  {key:'lv2',name:'餐廳鐵板燒',  sub:'高溫快節奏',       diff:3, timer:75, heatMod:1.3, forkMod:1.5, tiltMod:1.0, fireCnt:10, fireC1:0x3388ff,fireC2:0xaaccff },\n"
    "  {key:'lv3',name:'露營野火烤架', sub:'風向不定傾斜頻繁',  diff:4, timer:90, heatMod:1.1, forkMod:1.0, tiltMod:2.5, fireCnt:8,  fireC1:0xcc8800,fireC2:0xffee44 },\n"
    "  {key:'lv4',name:'地獄料理直播', sub:'雙叉子超高溫',     diff:5, timer:45, heatMod:1.5, forkMod:2.5, tiltMod:1.5, fireCnt:12, fireC1:0xcc0055,fireC2:0xff44cc },\n"
)
if old in html: html=html.replace(old,new); print("LEVELS fireC1/fireC2: OK")
else: print("FAIL LEVELS colors")

# ── 5. drawFires：使用地圖色，提高火焰強度與戲劇感 ────────────────────────
old = (
    "      // 活躍火焰\n"
    "      const alpha=f.state==='active'?1.0:0.45;\n"
    "      const s=this.FIRE_R_BASE+this.FIRE_R_AMP*Math.sin(phase*f.spd+f.ph);\n"
    "      f.r=Math.max(10,s);\n"
    "      g.fillStyle(0xff5500,0.50*alpha); g.fillCircle(f.x,f.y,f.r);\n"
    "      g.fillStyle(0xffaa00,0.34*alpha); g.fillCircle(f.x,f.y,f.r*0.55);\n"
    "      g.fillStyle(0xffffff,0.11*alpha); g.fillCircle(f.x,f.y,f.r*0.22);\n"
)
new = (
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
if old in html: html=html.replace(old,new); print("drawFires dramatic: OK")
else: print("FAIL drawFires")

# ── 6. 警告火焰也根據地圖色稍作調整 ──────────────────────────────────────
old = (
    "      if(f.state==='warning'){\n"
    "        const a=0.15+0.10*Math.sin(phase*6);\n"
    "        g.fillStyle(0xffee44,a); g.fillCircle(f.tx,f.ty,this.FIRE_R_BASE);\n"
    "        g.lineStyle(2,0xffcc00,a*3); g.strokeCircle(f.tx,f.ty,this.FIRE_R_BASE);\n"
    "      }\n"
)
new = (
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
if old in html: html=html.replace(old,new); print("warning fire: OK")
else: print("FAIL warning fire")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
print("rmWhite threshold 250:", "mn>250&&sat<6" in v)
print("fillRect fixed:", "ctxb.fillRect(0,0,W,H)" in v)
print("weight/speed physics:", "spd=c.speed/155" in v)
print("fireC1 in lv1:", "fireC1:0xff4400" in v)
print("fireC1 blue lv2:", "fireC1:0x3388ff" in v)
print("fireC1 hell lv4:", "fireC1:0xcc0055" in v)
print("dramatic fire:", "暗底陰影" in v)
print("warning cross:", "警告十字" in v)
