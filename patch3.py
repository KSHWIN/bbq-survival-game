with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Fix 1: store baseScale on playerSprite after creation
old1 = (
    "    this.playerSprite=this.textures.exists(c.img)\n"
    "      ? this.add.image(this.p.x,this.p.y,c.img).setScale(SS).setDepth(10) : null;\n"
    "    this.sweatTxt="
)
new1 = (
    "    this.playerSprite=this.textures.exists(c.img)\n"
    "      ? this.add.image(this.p.x,this.p.y,c.img).setScale(SS).setDepth(10) : null;\n"
    "    if(this.playerSprite) this.playerSprite.baseScale=SS;\n"
    "    this.sweatTxt="
)
if old1 in html:
    html = html.replace(old1, new1)
    print("OK fix1: baseScale stored")
else:
    print("FAIL fix1")

# Fix 2: updateHeatFx - use baseScale for wobble tween values
old2 = (
    "  updateHeatFx(sprite,heat,sweatTxt){\n"
    "    if(!sprite) return;\n"
    "    const t=heat/100;\n"
    "    sprite.setTint(Phaser.Display.Color.GetColor(255,Math.floor(255*(1-t*0.75)),Math.floor(255*(1-t))));\n"
    "    if(heat>85){\n"
    "      if(!this.wobbleTween||!this.wobbleTween.isPlaying()){\n"
    "        this.wobbleTween=this.tweens.add({targets:sprite,scaleX:{from:0.82,to:1.18},scaleY:{from:1.15,to:0.85},angle:{from:-7,to:7},duration:70,yoyo:true,repeat:-1});\n"
    "      }\n"
    "      if(sweatTxt) sweatTxt.setVisible(true).setPosition(sprite.x+16,sprite.y-20).setText('\U0001f631');\n"
    "    } else if(heat>60){\n"
    "      if(!this.wobbleTween||!this.wobbleTween.isPlaying()){\n"
    "        this.wobbleTween=this.tweens.add({targets:sprite,scaleX:{from:0.93,to:1.07},scaleY:{from:1.06,to:0.94},duration:160,yoyo:true,repeat:-1});\n"
    "      }\n"
    "      if(sweatTxt) sweatTxt.setVisible(true).setPosition(sprite.x+14,sprite.y-18).setText('\U0001f630');\n"
    "    } else {\n"
    "      if(this.wobbleTween){ this.wobbleTween.stop(); this.wobbleTween=null; sprite.setScale(1).setAngle(0); }\n"
    "      if(sweatTxt) sweatTxt.setVisible(false);\n"
    "    }\n"
    "  }"
)
new2 = (
    "  updateHeatFx(sprite,heat,sweatTxt){\n"
    "    if(!sprite) return;\n"
    "    const t=heat/100;\n"
    "    const bs=sprite.baseScale||0.16;\n"
    "    sprite.setTint(Phaser.Display.Color.GetColor(255,Math.floor(255*(1-t*0.75)),Math.floor(255*(1-t))));\n"
    "    if(heat>85){\n"
    "      if(!this.wobbleTween||!this.wobbleTween.isPlaying()){\n"
    "        this.wobbleTween=this.tweens.add({targets:sprite,scaleX:{from:bs*0.82,to:bs*1.18},scaleY:{from:bs*1.15,to:bs*0.85},angle:{from:-7,to:7},duration:70,yoyo:true,repeat:-1});\n"
    "      }\n"
    "      if(sweatTxt) sweatTxt.setVisible(true).setPosition(sprite.x+16,sprite.y-20).setText('\U0001f631');\n"
    "    } else if(heat>60){\n"
    "      if(!this.wobbleTween||!this.wobbleTween.isPlaying()){\n"
    "        this.wobbleTween=this.tweens.add({targets:sprite,scaleX:{from:bs*0.93,to:bs*1.07},scaleY:{from:bs*1.06,to:bs*0.94},duration:160,yoyo:true,repeat:-1});\n"
    "      }\n"
    "      if(sweatTxt) sweatTxt.setVisible(true).setPosition(sprite.x+14,sprite.y-18).setText('\U0001f630');\n"
    "    } else {\n"
    "      if(this.wobbleTween){ this.wobbleTween.stop(); this.wobbleTween=null; sprite.setScale(bs).setAngle(0); }\n"
    "      if(sweatTxt) sweatTxt.setVisible(false);\n"
    "    }\n"
    "  }"
)
if old2 in html:
    html = html.replace(old2, new2)
    print("OK fix2: wobble tween uses baseScale")
else:
    print("FAIL fix2 - trying partial match")
    idx = html.find("updateHeatFx(sprite,heat,sweatTxt)")
    if idx != -1:
        print("Found updateHeatFx at:", idx)
        print("snippet:", repr(html[idx:idx+500]))

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Done")
print("baseScale check:", "sprite.baseScale=SS" in html)
print("bs in tween check:", "bs*0.82" in html)
print("bs reset check:", "sprite.setScale(bs)" in html)
