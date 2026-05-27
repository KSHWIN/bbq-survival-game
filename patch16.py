# -*- coding: utf-8 -*-
# Patch 16: 鍵盤截取修正 + 邊界行為改善（鍵盤碰牆夾緊，傾斜力才能致死）
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. Phaser 設定加入 input capture（防止瀏覽器攔截方向鍵捲頁）────────────
old = "new Phaser.Game({\n  type: Phaser.AUTO,"
new = (
    "new Phaser.Game({\n"
    "  type: Phaser.AUTO,\n"
    "  input: { keyboard: { capture: [38,40,37,39,32,83,82,27] } }, // 阻止瀏覽器攔截↑↓←→SpaceSREsc"
)
if old in html: html=html.replace(old,new); print("Phaser input capture: OK")
else: print("FAIL input capture")

# ── 2. 在 GameScene.create() 的 addKeys 後，也加入場景級 capture ─────────
old = (
    "this.keys=this.input.keyboard.addKeys({\n"
    "      up:Phaser.Input.Keyboard.KeyCodes.UP,\n"
    "      down:Phaser.Input.Keyboard.KeyCodes.DOWN,\n"
    "      left:Phaser.Input.Keyboard.KeyCodes.LEFT,\n"
    "      right:Phaser.Input.Keyboard.KeyCodes.RIGHT,"
)
new = (
    "this.input.keyboard.addCapture([37,38,39,40,32,83,82,27]); // ←↑→↓ Space S R Esc\n"
    "    this.keys=this.input.keyboard.addKeys({\n"
    "      up:Phaser.Input.Keyboard.KeyCodes.UP,\n"
    "      down:Phaser.Input.Keyboard.KeyCodes.DOWN,\n"
    "      left:Phaser.Input.Keyboard.KeyCodes.LEFT,\n"
    "      right:Phaser.Input.Keyboard.KeyCodes.RIGHT,"
)
if old in html: html=html.replace(old,new); print("scene addCapture: OK")
else: print("FAIL scene addCapture")

# ── 3. 邊界行為改善：鍵盤碰牆夾緊，純傾斜才致死 ─────────────────────────
old = (
    "    if(!inGrill(nx,ny)){\n"
    "      if(isDash){this.dashState.active=false;}\n"
    "      else{this.subTxt.setText('掉落烤盤！');this.endGame(false);return;}\n"
    "    } else {this.p.x=nx;this.p.y=ny;}\n"
)
new = (
    "    if(!inGrill(nx,ny)){\n"
    "      if(isDash){this.dashState.active=false;}\n"
    "      else{\n"
    "        // 鍵盤移動頂牆時夾緊（不死），純傾斜力才能把角色推落\n"
    "        const txo=this.p.x+tfx*dt, tyo=this.p.y+tfy*dt;\n"
    "        if(!inGrill(txo,tyo)){\n"
    "          this.subTxt.setText('掉落烤盤！');this.endGame(false);return;\n"
    "        }\n"
    "        // 鍵盤在安全範圍頂牆：夾緊座標\n"
    "        this.p.x=Phaser.Math.Clamp(nx,G.x+4,G.x+G.w-4);\n"
    "        this.p.y=Phaser.Math.Clamp(ny,G.y+4,G.y+G.h-4);\n"
    "      }\n"
    "    } else {this.p.x=nx;this.p.y=ny;}\n"
)
if old in html: html=html.replace(old,new); print("boundary clamp: OK")
else: print("FAIL boundary clamp")

# ── 4. 傾斜力稍降 88→70，確保速度最慢的角色也能抗衡 ─────────────────────
old = "this.tilt={x:d.x,y:d.y,force:88,rot:d.rot,state:'warn',timer:2.5,lbl:d.lbl};"
new = "this.tilt={x:d.x,y:d.y,force:70,rot:d.rot,state:'warn',timer:2.5,lbl:d.lbl};"
if old in html: html=html.replace(old,new); print("tilt force 88→70: OK")
else: print("FAIL tilt force")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
print("Phaser input capture:", "input: { keyboard: { capture:" in v)
print("scene addCapture:", "addCapture([37,38" in v)
print("boundary clamp logic:", "純傾斜力才能把角色推落" in v)
print("Phaser.Math.Clamp:", "Phaser.Math.Clamp(nx" in v)
print("tilt force 70:", "force:70" in v)
