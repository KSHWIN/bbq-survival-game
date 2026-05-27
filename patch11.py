# -*- coding: utf-8 -*-
# Patch 11: 關卡烤盤差異視覺 + 角色白色背景去除 + 移動方向感增強

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. BootScene onAdded：全部載入後去除白色背景 ──────────────────────────
old = (
    "if(done>=keys.length) this.scene.start('Select');"
)
new = (
    "if(done>=keys.length){ "
    "CHARS.forEach(ch=>this._rmWhite(ch.img)); "
    "this.scene.start('Select'); }"
)
if old in html: html=html.replace(old,new,1); print("onAdded rmWhite: OK")
else: print("FAIL onAdded rmWhite")

# ── 2. BootScene 加入 _rmWhite 方法 ──────────────────────────────────────
old = (
    "    keys.forEach(k=>{ if(this.textures.exists(k)){onAdded();return;} "
    "this.textures.once('addtexture-'+k,onAdded); "
    "this.textures.once('onerror-'+k,onAdded); "
    "this.textures.addBase64(k,IMG[k]); });\n"
    "  }\n"
    "}"
)
new = (
    "    keys.forEach(k=>{ if(this.textures.exists(k)){onAdded();return;} "
    "this.textures.once('addtexture-'+k,onAdded); "
    "this.textures.once('onerror-'+k,onAdded); "
    "this.textures.addBase64(k,IMG[k]); });\n"
    "  }\n"
    "  _rmWhite(key){\n"
    "    if(!this.textures.exists(key)) return;\n"
    "    const src=this.textures.get(key).getSourceImage();\n"
    "    const cv=document.createElement('canvas');\n"
    "    cv.width=src.width; cv.height=src.height;\n"
    "    const ctx=cv.getContext('2d'); ctx.drawImage(src,0,0);\n"
    "    const id=ctx.getImageData(0,0,cv.width,cv.height),d=id.data;\n"
    "    for(let i=0;i<d.length;i+=4){\n"
    "      const mn=Math.min(d[i],d[i+1],d[i+2]);\n"
    "      if(mn>225) d[i+3]=0;\n"
    "      else if(mn>185) d[i+3]=Math.round(d[i+3]*(mn-185)/40);\n"
    "    }\n"
    "    ctx.putImageData(id,0,0);\n"
    "    this.textures.remove(key);\n"
    "    this.textures.addCanvas(key,cv);\n"
    "  }\n"
    "}"
)
if old in html: html=html.replace(old,new,1); print("_rmWhite method: OK")
else: print("FAIL _rmWhite method")

# ── 3. 關卡專屬 drawGrill ────────────────────────────────────────────────
old = (
    "  drawGrill(){\n"
    "    const g=this.grillLayer; g.clear();\n"
    "    // 烤桌面（餐廳桌面遮罩）\n"
    "    g.fillStyle(0x1a0e05,0.55); g.fillRect(0,0,W,H);\n"
    "    // 烤盤底（深色鑄鐵）\n"
    "    g.fillStyle(0x0f0908); g.fillRect(G.x-8,G.y-8,G.w+16,G.h+16);\n"
    "    g.fillStyle(0x1c1410); g.fillRect(G.x,G.y,G.w,G.h);\n"
    "    // 用 grill_bg 圖作底（如果存在）\n"
    "    if(this.textures.exists('grill_bg')){\n"
    "      this.grillBgImg=this.add.image(G.x+G.w/2,G.y+G.h/2,'grill_bg').setDisplaySize(G.w,G.h).setDepth(-1);\n"
    "    }\n"
    "    // 烤網格條（模擬鑄鐵烤網）\n"
    "    const BAR=22, THICK=4;\n"
    "    g.lineStyle(THICK,0x0a0805,0.92);\n"
    "    for(let x=G.x;x<=G.x+G.w;x+=BAR) g.lineBetween(x,G.y,x,G.y+G.h);\n"
    "    for(let y=G.y;y<=G.y+G.h;y+=BAR) g.lineBetween(G.x,y,G.x+G.w,y);\n"
    "    // 烤網高光（金屬反光感）\n"
    "    g.lineStyle(1,0x3a2a18,0.35);\n"
    "    for(let x=G.x+2;x<=G.x+G.w;x+=BAR) g.lineBetween(x,G.y,x,G.y+G.h);\n"
    "    for(let y=G.y+2;y<=G.y+G.h;y+=BAR) g.lineBetween(G.x,y,G.x+G.w,y);\n"
    "    // 邊框（危險邊緣）\n"
    "    g.lineStyle(6,0x3a1a00,0.9); g.strokeRect(G.x-4,G.y-4,G.w+8,G.h+8);\n"
    "    g.lineStyle(3,0xff5500,0.65); g.strokeRect(G.x,G.y,G.w,G.h);\n"
    "  }"
)
new = (
    "  drawGrill(){\n"
    "    const lk=this.levelData?this.levelData.key:'lv1';\n"
    "    const g=this.grillLayer; g.clear();\n"
    "\n"
    "    if(lk==='lv1'){\n"
    "      // 家庭烤肉架：暖色系標準鑄鐵烤網\n"
    "      g.fillStyle(0x1a0e05,0.55); g.fillRect(0,0,W,H);\n"
    "      g.fillStyle(0x0f0908); g.fillRect(G.x-8,G.y-8,G.w+16,G.h+16);\n"
    "      g.fillStyle(0x1c1410); g.fillRect(G.x,G.y,G.w,G.h);\n"
    "      const B1=22;\n"
    "      g.lineStyle(4,0x0a0805,0.92);\n"
    "      for(let x=G.x;x<=G.x+G.w;x+=B1) g.lineBetween(x,G.y,x,G.y+G.h);\n"
    "      for(let y=G.y;y<=G.y+G.h;y+=B1) g.lineBetween(G.x,y,G.x+G.w,y);\n"
    "      g.lineStyle(1,0x3a2a18,0.35);\n"
    "      for(let x=G.x+2;x<=G.x+G.w;x+=B1) g.lineBetween(x,G.y,x,G.y+G.h);\n"
    "      for(let y=G.y+2;y<=G.y+G.h;y+=B1) g.lineBetween(G.x,y,G.x+G.w,y);\n"
    "      g.lineStyle(6,0x3a1a00,0.9); g.strokeRect(G.x-4,G.y-4,G.w+8,G.h+8);\n"
    "      g.lineStyle(3,0xff5500,0.65); g.strokeRect(G.x,G.y,G.w,G.h);\n"
    "    }\n"
    "\n"
    "    else if(lk==='lv2'){\n"
    "      // 餐廳鐵板燒：光滑金屬平板，細橫紋，銀藍邊框\n"
    "      g.fillStyle(0x0d0d12,0.65); g.fillRect(0,0,W,H);\n"
    "      g.fillStyle(0x16161e); g.fillRect(G.x-8,G.y-8,G.w+16,G.h+16);\n"
    "      g.fillStyle(0x22222e); g.fillRect(G.x,G.y,G.w,G.h);\n"
    "      const B2=8;\n"
    "      g.lineStyle(1,0x1a1a28,0.7);\n"
    "      for(let y=G.y;y<=G.y+G.h;y+=B2) g.lineBetween(G.x,y,G.x+G.w,y);\n"
    "      g.fillStyle(0xff3300,0.07); g.fillCircle(G.x+G.w/2,G.y+G.h/2,110);\n"
    "      g.fillStyle(0xff5500,0.04); g.fillCircle(G.x+G.w/2,G.y+G.h/2,175);\n"
    "      g.lineStyle(2,0x7799bb,0.16);\n"
    "      for(let y=G.y+4;y<=G.y+G.h;y+=B2) g.lineBetween(G.x,y,G.x+G.w,y);\n"
    "      g.lineStyle(8,0x223344,0.9); g.strokeRect(G.x-4,G.y-4,G.w+8,G.h+8);\n"
    "      g.lineStyle(3,0x99ccee,0.85); g.strokeRect(G.x,G.y,G.w,G.h);\n"
    "      g.lineStyle(1,0xffffff,0.22); g.strokeRect(G.x+2,G.y+2,G.w-4,G.h-4);\n"
    "    }\n"
    "\n"
    "    else if(lk==='lv3'){\n"
    "      // 露營野火烤架：鏽棕色寬格，炭痕，綠棕邊框\n"
    "      g.fillStyle(0x0a1205,0.62); g.fillRect(0,0,W,H);\n"
    "      g.fillStyle(0x1a0a00); g.fillRect(G.x-8,G.y-8,G.w+16,G.h+16);\n"
    "      g.fillStyle(0x2a1508); g.fillRect(G.x,G.y,G.w,G.h);\n"
    "      const B3=32;\n"
    "      g.lineStyle(5,0x100800,0.95);\n"
    "      for(let x=G.x;x<=G.x+G.w;x+=B3) g.lineBetween(x,G.y,x,G.y+G.h);\n"
    "      for(let y=G.y;y<=G.y+G.h;y+=B3) g.lineBetween(G.x,y,G.x+G.w,y);\n"
    "      g.lineStyle(2,0x5a2a08,0.4);\n"
    "      for(let x=G.x+2;x<=G.x+G.w;x+=B3) g.lineBetween(x,G.y,x,G.y+G.h);\n"
    "      for(let y=G.y+2;y<=G.y+G.h;y+=B3) g.lineBetween(G.x,y,G.x+G.w,y);\n"
    "      g.fillStyle(0x080400,0.55);\n"
    "      [[G.x+85,G.y+72,24],[G.x+275,G.y+118,18],[G.x+165,G.y+205,22],[G.x+345,G.y+195,20]].forEach(([cx,cy,r])=>g.fillCircle(cx,cy,r));\n"
    "      g.lineStyle(7,0x1a2805,0.9); g.strokeRect(G.x-4,G.y-4,G.w+8,G.h+8);\n"
    "      g.lineStyle(3,0x88aa33,0.75); g.strokeRect(G.x,G.y,G.w,G.h);\n"
    "      g.lineStyle(1,0xaacc55,0.28); g.strokeRect(G.x+3,G.y+3,G.w-6,G.h-6);\n"
    "    }\n"
    "\n"
    "    else{\n"
    "      // 地獄料理直播：極暗底，熔岩裂縫，紅橙多層邊框\n"
    "      g.fillStyle(0x0e0000,0.78); g.fillRect(0,0,W,H);\n"
    "      g.fillStyle(0x080000); g.fillRect(G.x-8,G.y-8,G.w+16,G.h+16);\n"
    "      g.fillStyle(0x140300); g.fillRect(G.x,G.y,G.w,G.h);\n"
    "      const B4=22;\n"
    "      g.lineStyle(3,0x050000,0.98);\n"
    "      for(let x=G.x;x<=G.x+G.w;x+=B4) g.lineBetween(x,G.y,x,G.y+G.h);\n"
    "      for(let y=G.y;y<=G.y+G.h;y+=B4) g.lineBetween(G.x,y,G.x+G.w,y);\n"
    "      [\n"
    "        [G.x+55,G.y+38,G.x+105,G.y+88],[G.x+195,G.y+18,G.x+155,G.y+75],\n"
    "        [G.x+295,G.y+55,G.x+338,G.y+135],[G.x+78,G.y+198,G.x+125,G.y+258],\n"
    "        [G.x+248,G.y+175,G.x+285,G.y+238],[G.x+355,G.y+198,G.x+388,G.y+268],\n"
    "        [G.x+130,G.y+95,G.x+165,G.y+145],[G.x+320,G.y+280,G.x+370,G.y+320],\n"
    "      ].forEach(([x1,y1,x2,y2])=>{\n"
    "        g.lineStyle(3,0xff4400,0.55); g.lineBetween(x1,y1,x2,y2);\n"
    "        g.lineStyle(1,0xffaa00,0.85); g.lineBetween(x1,y1,x2,y2);\n"
    "      });\n"
    "      g.fillStyle(0xff2200,0.04); g.fillCircle(G.x+G.w/2,G.y+G.h/2,130);\n"
    "      g.lineStyle(10,0x3a0000,0.9); g.strokeRect(G.x-6,G.y-6,G.w+12,G.h+12);\n"
    "      g.lineStyle(4,0xff2200,0.85); g.strokeRect(G.x-2,G.y-2,G.w+4,G.h+4);\n"
    "      g.lineStyle(2,0xff8800,0.65); g.strokeRect(G.x,G.y,G.w,G.h);\n"
    "      g.lineStyle(1,0xffcc44,0.4); g.strokeRect(G.x+2,G.y+2,G.w-4,G.h-4);\n"
    "    }\n"
    "  }"
)
if old in html: html=html.replace(old,new); print("drawGrill levels: OK")
else: print("FAIL drawGrill levels")

# ── 4. 增強移動方向感 ──────────────────────────────────────────────────────
old = (
    "          this.playerSprite.setScale(BS*sqX*dirScaleY, BS*sqY*dirScaleY);\n"
    "          this.playerSprite.setFlipX(this.lastDir.x<-0.1);\n"
    "          this.playerSprite.setAngle(this.lastDir.x*7);\n"
    "          this.playerSprite.setPosition(this.p.x, this.p.y+c*3.5);"
)
new = (
    "          this.playerSprite.setScale(BS*sqX*dirScaleY, BS*sqY*dirScaleY);\n"
    "          this.playerSprite.setFlipX(this.lastDir.x<-0.1);\n"
    "          this.playerSprite.setAngle(this.lastDir.x*11 - this.lastDir.y*4);\n"
    "          this.playerSprite.setPosition(this.p.x, this.p.y+c*5.5);"
)
if old in html: html=html.replace(old,new); print("player direction: OK")
else: print("FAIL player direction")

# ── 5. 靜止時也保持面朝方向 ───────────────────────────────────────────────
old = (
    "          this.playerSprite.setScale(BS);\n"
    "          this.playerSprite.setAngle(0);\n"
    "          this.playerSprite.setFlipX(this.lastDir.x<-0.1);\n"
    "          this.playerSprite.setPosition(this.p.x, this.p.y);"
)
new = (
    "          this.playerSprite.setScale(BS);\n"
    "          this.playerSprite.setAngle(this.lastDir.x*3);\n"
    "          this.playerSprite.setFlipX(this.lastDir.x<-0.1);\n"
    "          this.playerSprite.setPosition(this.p.x, this.p.y);"
)
if old in html: html=html.replace(old,new); print("player idle facing: OK")
else: print("FAIL player idle facing")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
print("_rmWhite method:", "_rmWhite(key){" in v)
print("onAdded calls rmWhite:", "CHARS.forEach(ch=>this._rmWhite(ch.img))" in v)
print("lv1 grill:", "家庭烤肉架：暖色系" in v)
print("lv2 grill:", "餐廳鐵板燒" in v)
print("lv3 grill:", "露營野火烤架" in v)
print("lv4 grill:", "地獄料理直播" in v)
print("player angle 11:", "lastDir.x*11" in v)
print("player bobbing 5.5:", "y+c*5.5" in v)
