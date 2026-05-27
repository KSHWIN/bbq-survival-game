# -*- coding: utf-8 -*-
# Patch 37: 削弱脆化推力 + 大絕球加速 + 選單右下角 + hover 顯示大絕
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

# ── 1. 削弱受擊者脆化乘數（receiver heat）────────────────────────
rep("charBst weaken",
    "          const charBst=Math.min(2.5,1+(e.heat||0)/100*2);",
    "          const charBst=Math.min(1.5,1+(e.heat||0)/100*0.8);")

# ── 2. 削弱施力者脆化乘數（attacker heat）────────────────────────
rep("myBst weaken",
    "    const myBst=Math.min(2.0,1+this.heat/100*1.5); // 越熟衝得越遠越猛",
    "    const myBst=Math.min(1.5,1+this.heat/100*0.7); // 越熟衝得越遠越猛（已削弱）")

# ── 3. AI 推人脆化也削弱 ─────────────────────────────────────────
rep("ai push cBst weaken",
    "            const cBst=Math.min(2.5,1+this.heat/100*2);",
    "            const cBst=Math.min(1.5,1+this.heat/100*0.8);")

rep("ai push enemy cBst weaken",
    "            const cBst=Math.min(2.5,1+(eRef.heat||0)/100*2);",
    "            const cBst=Math.min(1.5,1+(eRef.heat||0)/100*0.8);")

# ── 4. 大絕球：初始快速生成（方便測試）────────────────────────────
rep("ult orb fast init",
    "    this.ultOrbs=[]; this.ultOrbTimer=12;",
    "    this.ultOrbs=[]; this.ultOrbTimer=2;")

rep("ult orb fast respawn",
    "    if(this.ultOrbTimer<=0&&this.ultCharge<this.ultMax){this.spawnUltOrb();this.ultOrbTimer=12+Math.random()*6;}",
    "    if(this.ultOrbTimer<=0&&this.ultCharge<this.ultMax){this.spawnUltOrb();this.ultOrbTimer=5+Math.random()*3;}")

# ── 5. 選單底部：左側技能面板 + 右側選項面板 ─────────────────────
rep("detail bar split",
    "    // ── Detail bar（技能預覽面板）─────────────────────────\n"
    "    this.add.rectangle(W/2,H-44,W-20,82,0x060400,0.94).setStrokeStyle(1,0x885522).setDepth(10);",
    "    // ── Detail bar（左）+ 選項面板（右）──────────────────\n"
    "    this.add.rectangle(244,H-44,480,82,0x060400,0.94).setStrokeStyle(1,0x885522).setDepth(10);\n"
    "    this.add.rectangle(644,H-44,296,82,0x040608,0.94).setStrokeStyle(1,0x445566).setDepth(10);")

# ── 6. 加大絕招預覽文字欄位 ──────────────────────────────────────
rep("ult preview txt",
    "    this.detailTxt  =this.add.text(110,H-24,'',{fontSize:'10px',color:'#887755',fontFamily:'sans-serif'}).setDepth(12);",
    "    this.ultPreviewTxt=this.add.text(110,H-40,'',{fontSize:'10px',color:'#ffaaff',fontFamily:'sans-serif',fontStyle:'italic'}).setDepth(12);\n"
    "    this.detailTxt  =this.add.text(110,H-24,'',{fontSize:'10px',color:'#887755',fontFamily:'sans-serif'}).setDepth(12);")

# ── 7. 對手數量移到右下 ───────────────────────────────────────────
rep("enemy count to right",
    "    const ECY=506;\n"
    "    this.add.text(498,ECY,'對手數量：',{fontSize:'11px',color:'#888888',fontFamily:'sans-serif'}).setOrigin(0,0.5);\n"
    "    this.ecBtns=[];\n"
    "    [1,2,3,4,5].forEach((n,bi)=>{\n"
    "      const bx=556+bi*44, by=ECY;",

    "    const ECY=513;\n"
    "    this.add.text(500,ECY,'對手數量：',{fontSize:'11px',color:'#888888',fontFamily:'sans-serif'}).setOrigin(0,0.5);\n"
    "    this.ecBtns=[];\n"
    "    [1,2,3,4,5].forEach((n,bi)=>{\n"
    "      const bx=557+bi*44, by=ECY;")

rep("enemy count old pos",
    "    const ECY=462;\n"
    "    this.add.text(W/2-154,ECY,'對手數量：',{fontSize:'12px',color:'#888888',fontFamily:'sans-serif'}).setOrigin(0,0.5);\n"
    "    this.ecBtns=[];\n"
    "    [1,2,3,4,5].forEach((n,bi)=>{\n"
    "      const bx=W/2-104+bi*52, by=ECY;",

    "    const ECY=513;\n"
    "    this.add.text(500,ECY,'對手數量：',{fontSize:'11px',color:'#888888',fontFamily:'sans-serif'}).setOrigin(0,0.5);\n"
    "    this.ecBtns=[];\n"
    "    [1,2,3,4,5].forEach((n,bi)=>{\n"
    "      const bx=557+bi*44, by=ECY;")

# ── 8. AI 難度移到右下 ────────────────────────────────────────────
rep("ai diff to right",
    "    const ADY=488;\n"
    "    this.add.text(W/2-104,ADY,'AI 難度：',{fontSize:'12px',color:'#888888',fontFamily:'sans-serif'}).setOrigin(0,0.5);\n"
    "    this.adBtns=[];\n"
    "    ['弱','中','強'].forEach((lbl,bi)=>{\n"
    "      const bx=W/2-4+bi*56, by=ADY;",

    "    const ADY=539;\n"
    "    this.add.text(500,ADY,'AI 難度：',{fontSize:'11px',color:'#888888',fontFamily:'sans-serif'}).setOrigin(0,0.5);\n"
    "    this.adBtns=[];\n"
    "    ['弱','中','強'].forEach((lbl,bi)=>{\n"
    "      const bx=563+bi*52, by=ADY;")

# ── 9. 開始按鈕移到右下角 ─────────────────────────────────────────
rep("start button to right",
    "    const btnW=200,btnH=44,btnX=W/2,btnY=H-58;",
    "    const btnW=152,btnH=34,btnX=640,btnY=H-22;")

# ── 10. _updateDetail 加大絕名稱 + hover 參數 ────────────────────
rep("update detail ult",
    "  _updateDetail(){\n"
    "    if(!this.detailTxt) return;\n"
    "    const c=CHARS[this.sel], lv=LEVELS[this.lvSel];\n"
    "    this.abilNameTxt.setText('❆ '+c.name+'「'+c.ability+'」');\n"
    "    this.abilDescTxt.setText(c.abilityDesc);\n"
    "    this.detailTxt.setText('關卡：'+lv.name+'　'+lv.sub+'　│　Enter / 點擊開戰');\n"
    "    this.previewKey=c.key;\n"
    "  }",

    "  _updateDetail(hoverIdx=null){\n"
    "    if(!this.detailTxt) return;\n"
    "    const isHov=hoverIdx!=null;\n"
    "    const c=CHARS[isHov?hoverIdx:this.sel], lv=LEVELS[this.lvSel];\n"
    "    const UN={pork:'油爆四濺',beef:'鐵板衝鋒',mushroom:'孢子迷霧',\n"
    "      corn:'爆米花連炸',wing:'旋風疾飛',shrimp:'衝擊浪潮',\n"
    "      tofu:'冷卻護盾',bacon:'煙燻覆蓋',pepper:'辣椒震波',saury:'魚骨連射'};\n"
    "    this.abilNameTxt.setText('❆ '+c.name+'「'+c.ability+'」');\n"
    "    this.abilDescTxt.setText(c.abilityDesc);\n"
    "    if(this.ultPreviewTxt) this.ultPreviewTxt.setText('✦ 大絕：'+(UN[c.key]||''));\n"
    "    if(!isHov) this.detailTxt.setText('關卡：'+lv.name+'　'+lv.sub+'　│　Enter / 點擊開戰');\n"
    "    this.previewKey=c.key;\n"
    "  }")

# ── 11. 角色卡片 hover 顯示大絕預覽 ──────────────────────────────
rep("char hover show ult",
    "      cont.on('pointerover',()=>{ if(this.sel!==i){bg.setStrokeStyle(2,0xbb7733);cont.setScale(1.03);} });\n"
    "      cont.on('pointerout', ()=>{ if(this.sel!==i){bg.setStrokeStyle(2,0x664422);cont.setScale(1);} });",
    "      cont.on('pointerover',()=>{ if(this.sel!==i){bg.setStrokeStyle(2,0xbb7733);cont.setScale(1.03);} this._updateDetail(i); });\n"
    "      cont.on('pointerout', ()=>{ if(this.sel!==i){bg.setStrokeStyle(2,0x664422);cont.setScale(1);} this._updateDetail(); });")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

for r in results:
    print(r)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
checks = [
    ("charBst=Math.min(1.5",  "charBst weakened"),
    ("myBst=Math.min(1.5",    "myBst weakened"),
    ("ultOrbTimer=2",         "fast orb init"),
    ("ultOrbTimer=5+",        "fast orb respawn"),
    ("rectangle(244,H-44",    "left panel"),
    ("rectangle(644,H-44",    "right panel"),
    ("ultPreviewTxt",         "ult preview txt"),
    ("ECY=513",               "enemy count y"),
    ("557+bi*44",             "enemy count x"),
    ("ADY=539",               "ai diff y"),
    ("563+bi*52",             "ai diff x"),
    ("btnX=640",              "start btn x"),
    ("UN={pork",              "ult names dict"),
    ("hoverIdx",              "hover param"),
    ("_updateDetail(i)",      "hover calls detail"),
]
for key, label in checks:
    print(f"{label}: {'OK' if key in v else 'MISSING'}")
