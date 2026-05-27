# -*- coding: utf-8 -*-
# Patch 30: 選角只能點選不跟滑鼠 + 整體速度降低 ~25%
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

# ── 1. 選角卡片：移除 pointerover 改選，改為 hover 只閃光 ─────────
rep("char card hover fix",
    "      cont.on('pointerdown',()=>this.setSel(i));\n"
    "      cont.on('pointerover',()=>this.setSel(i));",
    "      cont.on('pointerdown',()=>this.setSel(i));\n"
    "      cont.on('pointerover',()=>{ if(this.sel!==i){bg.setStrokeStyle(2,0xbb7733);cont.setScale(1.03);} });\n"
    "      cont.on('pointerout', ()=>{ if(this.sel!==i){bg.setStrokeStyle(2,0x664422);cont.setScale(1);} });")

# ── 2. 關卡卡片：同樣只 pointerdown 改選 ────────────────────────────
rep("level card hover fix",
    "      cont.on('pointerdown',()=>this.setLvSel(i));\n"
    "      cont.on('pointerover',()=>this.setLvSel(i));",
    "      cont.on('pointerdown',()=>this.setLvSel(i));\n"
    "      cont.on('pointerover',()=>{ if(this.lvSel!==i){card.bg.setStrokeStyle(2,0x888888);} });\n"
    "      cont.on('pointerout', ()=>{ if(this.lvSel!==i){const dc2=DCOLS[Math.min(LEVELS[i].diff-1,4)];card.bg.setStrokeStyle(2,dc2);} });")

# ── 3. 角色速度降低 ~25% ──────────────────────────────────────────
SPEEDS = [
    ("name:'五花肉', img:'char_pork',     speed:122,",  "name:'五花肉', img:'char_pork',     speed:90,"),
    ("name:'牛小排', img:'char_beef',     speed:128,",  "name:'牛小排', img:'char_beef',     speed:95,"),
    ("name:'香菇',   img:'char_mushroom', speed:210,",  "name:'香菇',   img:'char_mushroom', speed:155,"),
    ("name:'玉米',   img:'char_corn',     speed:155,",  "name:'玉米',   img:'char_corn',     speed:115,"),
    ("name:'雞翅',   img:'char_wing',     speed:223,",  "name:'雞翅',   img:'char_wing',     speed:165,"),
    ("name:'蝦子',   img:'char_shrimp',   speed:189,",  "name:'蝦子',   img:'char_shrimp',   speed:140,"),
    ("name:'豆腐',   img:'char_tofu',     speed:108,",  "name:'豆腐',   img:'char_tofu',     speed:80,"),
    ("name:'培根',   img:'char_bacon',    speed:142,",  "name:'培根',   img:'char_bacon',    speed:105,"),
    ("name:'青椒',   img:'char_pepper',   speed:149,",  "name:'青椒',   img:'char_pepper',   speed:110,"),
    ("name:'秋刀魚', img:'char_saury',    speed:169,",  "name:'秋刀魚', img:'char_saury',    speed:125,"),
]
for old, new in SPEEDS:
    rep("speed " + old.split("speed:")[1].rstrip(","), old, new)

# ── 4. AI 速度降低 ────────────────────────────────────────────────
rep("AI charge speed",
    "        e.vx=e.chDx*9.5; e.vy=e.chDy*9.5;",
    "        e.vx=e.chDx*7.0; e.vy=e.chDy*7.0;")

rep("AI max speed cap",
    "      const maxSpd=e.charging?9.5:5.5;",
    "      const maxSpd=e.charging?7.0:4.0;")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

for r in results:
    print(r)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
checks = [
    ("pointerout",      "hover out handler"),
    ("speed:90,",       "pork 90"),
    ("speed:95,",       "beef 95"),
    ("speed:155,",      "mushroom 155"),
    ("speed:115,",      "corn 115"),
    ("speed:165,",      "wing 165"),
    ("speed:140,",      "shrimp 140"),
    ("speed:80,",       "tofu 80"),
    ("speed:105,",      "bacon 105"),
    ("speed:110,",      "pepper 110"),
    ("speed:125,",      "saury 125"),
    ("chDx*7.0",        "AI charge 7.0"),
    ("charging?7.0:4.0","AI max speed"),
]
for key, label in checks:
    print(f"{label}: {'OK' if key in v else 'MISSING'}")
