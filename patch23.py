# -*- coding: utf-8 -*-
# Patch 23: 三修 — 降低被動熱度 / 往上顯示背影 / 烤盤改為鐵條
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. 被動熱度 1.2/s → 0.2/s（不站火上也不至於莫名其妙被烤熟）─────────
old = "    } else this.heat=Math.min(heatCap,this.heat+1.2*dt);"
new = "    } else this.heat=Math.min(heatCap,this.heat+0.2*dt);"
if old in html: html=html.replace(old,new); print("passive heat 0.2: OK")
else: print("FAIL passive heat")

# ── 2. _b 貼圖加深（背面更明顯）─────────────────────────────────────────
old = "      ctxb.fillStyle='rgba(25,15,45,0.62)';"
new = "      ctxb.fillStyle='rgba(12,6,28,0.82)';"
if old in html: html=html.replace(old,new); print("_b darker: OK")
else: print("FAIL _b darker")

# ── 3. 往上走時壓縮 Y 軸（背影俯視感）──────────────────────────────────
old = (
    "        } else if(isMoving){\n"
    "          const c=Math.sin(this.runPhase);\n"
    "          const dirScaleY=1+this.lastDir.y*0.05; // 上小下大（景深感）\n"
    "          const sqX=1-Math.abs(c)*0.08; // 水平擠壓\n"
    "          const sqY=1+Math.abs(c)*0.07; // 垂直拉伸\n"
    "          this.playerSprite.setScale(BS*sqX*dirScaleY, BS*sqY*dirScaleY);\n"
    "          this.playerSprite.setFlipX(this.lastDir.x<-0.1);\n"
    "          this.playerSprite.setAngle(this.lastDir.x*11 - this.lastDir.y*4);\n"
    "          this.playerSprite.setPosition(this.p.x, this.p.y+c*5.5);\n"
    "        } else {\n"
    "          this.playerSprite.setScale(BS);\n"
    "          this.playerSprite.setAngle(this.lastDir.x*3);\n"
    "          this.playerSprite.setFlipX(this.lastDir.x<-0.1);\n"
    "          this.playerSprite.setPosition(this.p.x, this.p.y);\n"
    "        }"
)
new = (
    "        } else if(isMoving){\n"
    "          const c=Math.sin(this.runPhase);\n"
    "          const isBack=this.playerSprite.texture.key.endsWith('_b');\n"
    "          const dirScaleY=isBack?0.60:(1+this.lastDir.y*0.08); // 往上：壓縮Y俯視背影\n"
    "          const sqX=1-Math.abs(c)*0.08; // 水平擠壓\n"
    "          const sqY=1+Math.abs(c)*0.07; // 垂直拉伸\n"
    "          this.playerSprite.setScale(BS*sqX, BS*sqY*dirScaleY);\n"
    "          this.playerSprite.setFlipX(this.lastDir.x<-0.1);\n"
    "          this.playerSprite.setAngle(this.lastDir.x*11 - this.lastDir.y*4);\n"
    "          this.playerSprite.setPosition(this.p.x, this.p.y+c*5.5);\n"
    "        } else {\n"
    "          const isBack=this.playerSprite.texture.key.endsWith('_b');\n"
    "          this.playerSprite.setScale(BS, isBack?BS*0.62:BS);\n"
    "          this.playerSprite.setAngle(this.lastDir.x*3);\n"
    "          this.playerSprite.setFlipX(this.lastDir.x<-0.1);\n"
    "          this.playerSprite.setPosition(this.p.x, this.p.y);\n"
    "        }"
)
if old in html: html=html.replace(old,new); print("back view scaleY: OK")
else: print("FAIL back view scaleY")

# ── 4. lv1 烤盤：格線 → 橫向鑄鐵條 + 炭火縫隙底光 ────────────────────
old = (
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
    "    }"
)
new = (
    "    if(lk==='lv1'){\n"
    "      // 家庭烤肉架：橫向鑄鐵條 + 炭火縫隙底光\n"
    "      g.fillStyle(0x0e0904,0.88); g.fillRect(0,0,W,H);\n"
    "      g.fillStyle(0x080402); g.fillRect(G.x-10,G.y-10,G.w+20,G.h+20);\n"
    "      g.fillStyle(0x170700); g.fillRect(G.x,G.y,G.w,G.h);\n"
    "      const bH1=7,bg1=15,bt1=22,rows1=Math.ceil(G.h/bt1)+2;\n"
    "      // 炭火縫隙底光\n"
    "      for(let i=0;i<rows1;i++){\n"
    "        const gy=G.y+i*bt1+bH1; if(gy>=G.y+G.h) break;\n"
    "        const gh=Math.min(bg1,G.y+G.h-gy);\n"
    "        g.fillStyle(0x3a0800,0.95); g.fillRect(G.x,gy,G.w,gh);\n"
    "        g.fillStyle(0x7a1800,0.60); g.fillRect(G.x+2,gy+1,G.w-4,Math.max(1,gh-2));\n"
    "        g.fillStyle(0xcc3300,0.25); g.fillRect(G.x+5,gy+2,G.w-10,Math.max(1,gh-4));\n"
    "      }\n"
    "      // 鑄鐵橫條\n"
    "      for(let i=0;i<rows1;i++){\n"
    "        const gy=G.y+i*bt1; if(gy>=G.y+G.h) break;\n"
    "        g.fillStyle(0x1c1510); g.fillRect(G.x,gy,G.w,bH1);\n"
    "        g.fillStyle(0x3c2c1c,0.55); g.fillRect(G.x,gy,G.w,2);\n"
    "        g.fillStyle(0x060402,0.85); g.fillRect(G.x,gy+bH1-1,G.w,1);\n"
    "      }\n"
    "      g.lineStyle(8,0x2a1100,0.95); g.strokeRect(G.x-5,G.y-5,G.w+10,G.h+10);\n"
    "      g.lineStyle(3,0xff5500,0.72); g.strokeRect(G.x,G.y,G.w,G.h);\n"
    "      g.lineStyle(1,0xff8844,0.32); g.strokeRect(G.x+2,G.y+2,G.w-4,G.h-4);\n"
    "    }"
)
if old in html: html=html.replace(old,new); print("lv1 grill bars: OK")
else: print("FAIL lv1 grill")

# ── 5. lv3 烤盤：格線 → 粗鐵條 + 橙黃木炭底光（露營感）──────────────
old = (
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
    "    }"
)
new = (
    "    else if(lk==='lv3'){\n"
    "      // 露營野火烤架：粗鐵條 + 橙黃木炭底光\n"
    "      g.fillStyle(0x080c03,0.82); g.fillRect(0,0,W,H);\n"
    "      g.fillStyle(0x110700); g.fillRect(G.x-10,G.y-10,G.w+20,G.h+20);\n"
    "      g.fillStyle(0x1e0d04); g.fillRect(G.x,G.y,G.w,G.h);\n"
    "      const bH3=10,bg3=20,bt3=30,rows3=Math.ceil(G.h/bt3)+2;\n"
    "      // 木炭橙火底光\n"
    "      for(let i=0;i<rows3;i++){\n"
    "        const gy=G.y+i*bt3+bH3; if(gy>=G.y+G.h) break;\n"
    "        const gh=Math.min(bg3,G.y+G.h-gy);\n"
    "        g.fillStyle(0x4a1200,0.92); g.fillRect(G.x,gy,G.w,gh);\n"
    "        g.fillStyle(0x8a2800,0.55); g.fillRect(G.x+2,gy+1,G.w-4,Math.max(1,gh-2));\n"
    "        g.fillStyle(0xdd5500,0.20); g.fillRect(G.x+6,gy+2,G.w-12,Math.max(1,gh-4));\n"
    "      }\n"
    "      // 粗鐵條（含鏽色紋理）\n"
    "      for(let i=0;i<rows3;i++){\n"
    "        const gy=G.y+i*bt3; if(gy>=G.y+G.h) break;\n"
    "        g.fillStyle(0x281808); g.fillRect(G.x,gy,G.w,bH3);\n"
    "        g.fillStyle(0x4a2e18,0.50); g.fillRect(G.x,gy,G.w,3);\n"
    "        g.fillStyle(0x5a2600,0.28); g.fillRect(G.x+10,gy+3,G.w-20,bH3-5);\n"
    "        g.fillStyle(0x080402,0.75); g.fillRect(G.x,gy+bH3-1,G.w,1);\n"
    "      }\n"
    "      // 炭痕\n"
    "      g.fillStyle(0x0a0400,0.72);\n"
    "      [[G.x+85,G.y+72,18],[G.x+275,G.y+118,13],[G.x+165,G.y+205,16],[G.x+345,G.y+195,14]].forEach(([cx,cy,r])=>g.fillCircle(cx,cy,r));\n"
    "      g.lineStyle(8,0x1a2205,0.92); g.strokeRect(G.x-5,G.y-5,G.w+10,G.h+10);\n"
    "      g.lineStyle(3,0x88aa33,0.82); g.strokeRect(G.x,G.y,G.w,G.h);\n"
    "      g.lineStyle(1,0xaacc55,0.32); g.strokeRect(G.x+3,G.y+3,G.w-6,G.h-6);\n"
    "    }"
)
if old in html: html=html.replace(old,new); print("lv3 grill bars: OK")
else: print("FAIL lv3 grill")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
print("passive heat 0.2:", "this.heat+0.2*dt" in v)
print("_b darker 0.82:", "0.82" in v)
print("back scaleY 0.60:", "isBack?0.60:" in v)
print("lv1 iron bars:", "bH1=7,bg1=15" in v)
print("lv3 iron bars:", "bH3=10,bg3=20" in v)
