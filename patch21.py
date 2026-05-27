# -*- coding: utf-8 -*-
# Patch 21: 移除 Shift（致命），加回 WASD，修正 isDash 取消邏輯
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. addCapture 移除 Shift（16），加回 WASD（65,68,87） ─────────────────
old = "    this.input.keyboard.addCapture([37,38,39,40,32,83,82,27,16]); // 含 Shift"
new = "    this.input.keyboard.addCapture([37,38,39,40,32,83,82,27,65,68,87]); // +WASD"
if old in html: html=html.replace(old,new); print("capture: Shift removed, WASD back: OK")
else: print("FAIL capture")

# ── 2. addKeys：移除 push2/Shift，加回 WASD 移動鍵 ──────────────────────
old = (
    "    this.keys=this.input.keyboard.addKeys({\n"
    "      up:Phaser.Input.Keyboard.KeyCodes.UP,\n"
    "      down:Phaser.Input.Keyboard.KeyCodes.DOWN,\n"
    "      left:Phaser.Input.Keyboard.KeyCodes.LEFT,\n"
    "      right:Phaser.Input.Keyboard.KeyCodes.RIGHT,\n"
    "      push:Phaser.Input.Keyboard.KeyCodes.S,\n"
    "      push2:Phaser.Input.Keyboard.KeyCodes.SHIFT, // Shift = 右手推擠（緊鄰方向鍵）\n"
    "      skill:Phaser.Input.Keyboard.KeyCodes.SPACE,\n"
    "      restart:Phaser.Input.Keyboard.KeyCodes.R,\n"
    "      back:Phaser.Input.Keyboard.KeyCodes.ESC,\n"
    "    });"
)
new = (
    "    this.keys=this.input.keyboard.addKeys({\n"
    "      up:Phaser.Input.Keyboard.KeyCodes.UP,\n"
    "      down:Phaser.Input.Keyboard.KeyCodes.DOWN,\n"
    "      left:Phaser.Input.Keyboard.KeyCodes.LEFT,\n"
    "      right:Phaser.Input.Keyboard.KeyCodes.RIGHT,\n"
    "      up2:Phaser.Input.Keyboard.KeyCodes.W,\n"
    "      down2:Phaser.Input.Keyboard.KeyCodes.X,\n"
    "      left2:Phaser.Input.Keyboard.KeyCodes.A,\n"
    "      right2:Phaser.Input.Keyboard.KeyCodes.D,\n"
    "      push:Phaser.Input.Keyboard.KeyCodes.S,\n"
    "      skill:Phaser.Input.Keyboard.KeyCodes.SPACE,\n"
    "      restart:Phaser.Input.Keyboard.KeyCodes.R,\n"
    "      back:Phaser.Input.Keyboard.KeyCodes.ESC,\n"
    "    });"
)
if old in html: html=html.replace(old,new); print("addKeys WASD back, Shift removed: OK")
else: print("FAIL addKeys")

# ── 3. 移動判斷：箭頭 OR WASD ─────────────────────────────────────────────
old = (
    "    let mx=0, my=0;\n"
    "    if(this.keys.left.isDown)  mx=-1;\n"
    "    if(this.keys.right.isDown) mx=1;\n"
    "    if(this.keys.up.isDown)    my=-1;\n"
    "    if(this.keys.down.isDown)  my=1;\n"
    "    // 按方向鍵立即取消衝刺（防止角色卡死）\n"
    "    if(isDash&&(mx!==0||my!==0)){this.dashState.active=false;}"
)
new = (
    "    let mx=0, my=0;\n"
    "    if(this.keys.left.isDown ||this.keys.left2.isDown)  mx=-1;\n"
    "    if(this.keys.right.isDown||this.keys.right2.isDown) mx=1;\n"
    "    if(this.keys.up.isDown   ||this.keys.up2.isDown)    my=-1;\n"
    "    if(this.keys.down.isDown ||this.keys.down2.isDown)  my=1;"
)
if old in html: html=html.replace(old,new); print("movement WASD+arrows: OK")
else: print("FAIL movement")

# ── 4. 修正 isDash 衝刺取消：玩家按方向鍵時直接跳過衝刺區塊 ───────────────
old = (
    "    if(mx&&my){mx*=0.707;my*=0.707;}\n"
    "    // 衝撞：覆蓋鍵盤方向，移動並碰撞敵人\n"
    "    if(isDash){"
)
new = (
    "    if(mx&&my){mx*=0.707;my*=0.707;}\n"
    "    // 玩家主動按鍵 → 立即取消衝刺（同幀生效，不再有延遲卡頓）\n"
    "    if(isDash&&(mx!==0||my!==0)){this.dashState.active=false;this.dashState=null;}\n"
    "    // 衝撞：覆蓋鍵盤方向，移動並碰撞敵人\n"
    "    if(isDash&&this.dashState){"
)
if old in html: html=html.replace(old,new); print("isDash cancel same-frame: OK")
else: print("FAIL isDash cancel")

# ── 5. push2 改用 left2/right2/up2/down2 的 lastDir 邏輯同步更新 ────────
old = (
    "    const kx=(this.keys.left.isDown?-1:this.keys.right.isDown?1:0);\n"
    "    const ky=(this.keys.up.isDown?-1:this.keys.down.isDown?1:0);"
)
new = (
    "    const kx=(this.keys.left.isDown||this.keys.left2.isDown?-1:this.keys.right.isDown||this.keys.right2.isDown?1:0);\n"
    "    const ky=(this.keys.up.isDown||this.keys.up2.isDown?-1:this.keys.down.isDown||this.keys.down2.isDown?1:0);"
)
if old in html: html=html.replace(old,new); print("lastDir WASD: OK")
else: print("FAIL lastDir")

# ── 6. push2 從 keys.push2 改回只用 keys.push ────────────────────────────
old = (
    "    const pushDown=this.keys.push.isDown||this.keys.push2.isDown;\n"
    "    if(pushDown&&!this.pushWas&&this.pushCD<=0) this.doPush();\n"
    "    this.pushWas=pushDown;"
)
new = (
    "    if(this.keys.push.isDown&&!this.pushWas&&this.pushCD<=0) this.doPush();\n"
    "    this.pushWas=this.keys.push.isDown;"
)
if old in html: html=html.replace(old,new); print("push back to S only: OK")
else: print("FAIL push")

# ── 7. 更新說明文字 ───────────────────────────────────────────────────────
old = "<div id=\"info\">↑↓←→ 移動 &nbsp;|&nbsp; S / Shift 推擠 &nbsp;|&nbsp; 空白 技能 &nbsp;|&nbsp; R 重開 &nbsp;|&nbsp; ESC 返回選角</div>"
new = "<div id=\"info\">↑↓←→ / WASD 移動 &nbsp;|&nbsp; S 推擠 &nbsp;|&nbsp; 空白 技能 &nbsp;|&nbsp; R 重開 &nbsp;|&nbsp; ESC 返回選角</div>"
if old in html: html=html.replace(old,new); print("info text: OK")
else: print("FAIL info text")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
print("no Shift(16) in capture:", ",16]" not in v and "16]" not in v.split("addCapture")[1][:50] if "addCapture" in v else True)
print("WASD in capture:", "65,68,87" in v)
print("up2 W in addKeys:", "up2:Phaser.Input.Keyboard.KeyCodes.W" in v)
print("down2 X in addKeys:", "down2:Phaser.Input.Keyboard.KeyCodes.X" in v)
print("no push2 SHIFT:", "push2:Phaser.Input.Keyboard.KeyCodes.SHIFT" not in v)
print("no keys.push2.isDown:", "keys.push2.isDown" not in v)
print("movement uses left2:", "keys.left2.isDown" in v)
print("isDash cancel same-frame:", "this.dashState=null;}" in v)
print("info WASD:", "WASD" in v)
