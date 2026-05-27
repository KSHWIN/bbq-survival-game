# -*- coding: utf-8 -*-
# Patch 20: 方向鍵可取消卡死 + Shift 推擠 + 選角白底
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. 人像加白底 ────────────────────────────────────────────────────────
old = (
    "      let portrait;\n"
    "      if(this.textures.exists(c.img)) portrait=this.add.image(0,-30,c.img).setDisplaySize(78,78);\n"
    "      else portrait=this.add.rectangle(0,-30,72,72,c.color,0.75).setStrokeStyle(2,0xffffff);\n"
    "      const nameT=this.add.text(0,+14,c.name,{fontSize:'14px',color:'#ffdd88',fontFamily:'sans-serif',fontStyle:'bold'}).setOrigin(0.5);\n"
    "      const abilT=this.add.text(0,+30,'✦ '+c.ability,{fontSize:'10px',color:'#66ccff',fontFamily:'sans-serif'}).setOrigin(0.5);\n"
    "      const iconG=this.drawAbilIcon(0,+50,c.key);\n"
    "      cont.add([shadow,bg,portrait,nameT,abilT,iconG]);"
)
new = (
    "      const portraitBg=this.add.rectangle(0,-30,82,82,0xffffff,1); // 白底\n"
    "      let portrait;\n"
    "      if(this.textures.exists(c.img)) portrait=this.add.image(0,-30,c.img).setDisplaySize(78,78);\n"
    "      else portrait=this.add.rectangle(0,-30,72,72,c.color,0.75).setStrokeStyle(2,0xffffff);\n"
    "      const nameT=this.add.text(0,+14,c.name,{fontSize:'14px',color:'#ffdd88',fontFamily:'sans-serif',fontStyle:'bold'}).setOrigin(0.5);\n"
    "      const abilT=this.add.text(0,+30,'✦ '+c.ability,{fontSize:'10px',color:'#66ccff',fontFamily:'sans-serif'}).setOrigin(0.5);\n"
    "      const iconG=this.drawAbilIcon(0,+50,c.key);\n"
    "      cont.add([shadow,bg,portraitBg,portrait,nameT,abilT,iconG]);"
)
if old in html: html=html.replace(old,new); print("portrait white bg: OK")
else: print("FAIL portrait white bg")

# ── 2. addCapture 加入 Shift（16）────────────────────────────────────────
old = "    this.input.keyboard.addCapture([37,38,39,40,32,83,82,27]);"
new = "    this.input.keyboard.addCapture([37,38,39,40,32,83,82,27,16]); // 含 Shift"
if old in html: html=html.replace(old,new); print("capture Shift: OK")
else: print("FAIL capture Shift")

# ── 3. addKeys 加入 push2 = Shift ─────────────────────────────────────────
old = (
    "    this.keys=this.input.keyboard.addKeys({\n"
    "      up:Phaser.Input.Keyboard.KeyCodes.UP,\n"
    "      down:Phaser.Input.Keyboard.KeyCodes.DOWN,\n"
    "      left:Phaser.Input.Keyboard.KeyCodes.LEFT,\n"
    "      right:Phaser.Input.Keyboard.KeyCodes.RIGHT,\n"
    "      push:Phaser.Input.Keyboard.KeyCodes.S,\n"
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
    "      push:Phaser.Input.Keyboard.KeyCodes.S,\n"
    "      push2:Phaser.Input.Keyboard.KeyCodes.SHIFT, // Shift = 右手推擠（緊鄰方向鍵）\n"
    "      skill:Phaser.Input.Keyboard.KeyCodes.SPACE,\n"
    "      restart:Phaser.Input.Keyboard.KeyCodes.R,\n"
    "      back:Phaser.Input.Keyboard.KeyCodes.ESC,\n"
    "    });"
)
if old in html: html=html.replace(old,new); print("addKeys push2 Shift: OK")
else: print("FAIL addKeys push2")

# ── 4. 移動中按方向鍵立即取消 dashState（防卡死）───────────────────────────
old = (
    "    const isDash=!!(this.dashState&&this.dashState.active);\n"
    "    const SPD=isDash?320:this.charData.speed*(this.activeEffects.slowpow>0?0.5:1);\n"
    "    let mx=0, my=0;\n"
    "    if(this.keys.left.isDown)  mx=-1;\n"
    "    if(this.keys.right.isDown) mx=1;\n"
    "    if(this.keys.up.isDown)    my=-1;\n"
    "    if(this.keys.down.isDown)  my=1;"
)
new = (
    "    const isDash=!!(this.dashState&&this.dashState.active);\n"
    "    const SPD=isDash?320:this.charData.speed*(this.activeEffects.slowpow>0?0.5:1);\n"
    "    let mx=0, my=0;\n"
    "    if(this.keys.left.isDown)  mx=-1;\n"
    "    if(this.keys.right.isDown) mx=1;\n"
    "    if(this.keys.up.isDown)    my=-1;\n"
    "    if(this.keys.down.isDown)  my=1;\n"
    "    // 按方向鍵立即取消衝刺（防止角色卡死）\n"
    "    if(isDash&&(mx!==0||my!==0)){this.dashState.active=false;}"
)
if old in html: html=html.replace(old,new); print("dash cancel on arrow: OK")
else: print("FAIL dash cancel")

# ── 5. 推擠觸發也支援 push2（Shift）──────────────────────────────────────
old = "    if(this.keys.push.isDown&&!this.pushWas&&this.pushCD<=0) this.doPush();\n    this.pushWas=this.keys.push.isDown;"
new = (
    "    const pushDown=this.keys.push.isDown||this.keys.push2.isDown;\n"
    "    if(pushDown&&!this.pushWas&&this.pushCD<=0) this.doPush();\n"
    "    this.pushWas=pushDown;"
)
if old in html: html=html.replace(old,new); print("push2 trigger: OK")
else: print("FAIL push2 trigger")

# ── 6. 更新操作說明文字 ───────────────────────────────────────────────────
old = "<div id=\"info\">↑↓←→ 移動 &nbsp;|&nbsp; S 推擠 &nbsp;|&nbsp; 空白 技能 &nbsp;|&nbsp; R 重開 &nbsp;|&nbsp; ESC 返回選角</div>"
new = "<div id=\"info\">↑↓←→ 移動 &nbsp;|&nbsp; S / Shift 推擠 &nbsp;|&nbsp; 空白 技能 &nbsp;|&nbsp; R 重開 &nbsp;|&nbsp; ESC 返回選角</div>"
if old in html: html=html.replace(old,new); print("info text: OK")
else: print("FAIL info text")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
print("portrait white bg:", "const portraitBg=this.add.rectangle(0,-30,82,82,0xffffff,1)" in v)
print("capture Shift 16:", "82,27,16" in v)
print("push2 SHIFT key:", "push2:Phaser.Input.Keyboard.KeyCodes.SHIFT" in v)
print("dash cancel arrow:", "防止角色卡死" in v)
print("push2 trigger:", "keys.push2.isDown" in v)
print("info updated:", "S / Shift" in v)
