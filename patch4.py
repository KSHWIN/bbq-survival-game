from PIL import Image
import base64, io, os, glob

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. Embed restaurant_bg into IMG dict ─────────────────────────────────
files = sorted(glob.glob("c:/Users/User/Desktop/烤肉遊戲/assets/restaurant_bg_*.png"))
if files:
    img_path = files[-1]
    img = Image.open(img_path).convert("RGB").resize((800, 580), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=72, optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode()
    data_url = f"data:image/jpeg;base64,{b64}"
    print(f"restaurant_bg: {len(b64)//1024}KB")

    # Insert before closing }; of IMG dict
    old_img_end = '\n};'
    idx = html.find(old_img_end)
    if idx != -1:
        html = html[:idx] + f',\n  "restaurant_bg": "{data_url}"' + html[idx:]
        print("OK: restaurant_bg added to IMG")
    else:
        print("FAIL: IMG end not found")
else:
    print("FAIL: restaurant_bg file not found")

# ── 2. Add restaurant_bg to GameScene create() ────────────────────────────
old_layers = (
    "    this.grillLayer=this.add.graphics();\n"
    "    this.fireLayer =this.add.graphics();\n"
    "    this.forkLayer =this.add.graphics();\n"
    "    this.fxLayer   =this.add.graphics();\n"
    "    this.drawGrill();"
)
new_layers = (
    "    this.grillLayer=this.add.graphics();\n"
    "    this.fireLayer =this.add.graphics();\n"
    "    this.forkLayer =this.add.graphics();\n"
    "    this.fxLayer   =this.add.graphics();\n"
    "    // 餐廳背景\n"
    "    if(this.textures.exists('restaurant_bg')){\n"
    "      this.add.image(W/2,H/2,'restaurant_bg').setDisplaySize(W,H).setDepth(-15).setAlpha(0.90);\n"
    "    }\n"
    "    this.drawGrill();"
)
if old_layers in html:
    html = html.replace(old_layers, new_layers)
    print("OK: restaurant_bg layer added")
else:
    print("FAIL: layers block not found")

# ── 3. Overhaul drawGrill: remove solid dark fill, add grill bars ─────────
old_grill = (
    "  drawGrill(){\n"
    "    const g=this.grillLayer; g.clear();\n"
    "    // 外框\n"
    "    g.fillStyle(0x0d0600); g.fillRect(G.x-10,G.y-10,G.w+20,G.h+20);\n"
    "    // 用 grill_bg 圖作底（如果存在）\n"
    "    if(this.textures.exists('grill_bg')){\n"
    "      this.grillBgImg=this.add.image(G.x+G.w/2,G.y+G.h/2,'grill_bg').setDisplaySize(G.w,G.h).setDepth(-1);\n"
    "    } else {\n"
    "      g.fillStyle(0x232323); g.fillRect(G.x,G.y,G.w,G.h);\n"
    "      g.lineStyle(1.5,0x383838);\n"
    "      for(let x=G.x;x<=G.x+G.w;x+=40) g.lineBetween(x,G.y,x,G.y+G.h);\n"
    "      for(let y=G.y;y<=G.y+G.h;y+=40) g.lineBetween(G.x,y,G.x+G.w,y);\n"
    "    }\n"
    "    // 危險邊緣\n"
    "    g.lineStyle(3,0xff5500,0.55); g.strokeRect(G.x,G.y,G.w,G.h);\n"
    "  }"
)
new_grill = (
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
if old_grill in html:
    html = html.replace(old_grill, new_grill)
    print("OK: drawGrill overhauled")
else:
    print("FAIL: drawGrill not found exactly - trying partial")
    idx = html.find("  drawGrill(){")
    print("drawGrill at:", idx)

# ── 4. Increase CHARS speeds (×1.35) ─────────────────────────────────────
speed_map = [
    ("speed:90,",  "speed:122,"),
    ("speed:95,",  "speed:128,"),
    ("speed:155,", "speed:210,"),
    ("speed:115,", "speed:155,"),
    ("speed:165,", "speed:223,"),
    ("speed:140,", "speed:189,"),
    ("speed:80,",  "speed:108,"),
    ("speed:105,", "speed:142,"),
    ("speed:110,", "speed:149,"),
    ("speed:125,", "speed:169,"),
]
for old_s, new_s in speed_map:
    if old_s in html:
        html = html.replace(old_s, new_s)
        print(f"OK speed: {old_s}->{new_s}")
    else:
        print(f"FAIL speed: {old_s}")

# ── 5. Speed up fire movement ─────────────────────────────────────────────
# Active state: reduce active dwell time (3-6s → 1.5-3s)
if "f.state='active'; f.timer=3+Math.random()*3;" in html:
    html = html.replace(
        "f.state='active'; f.timer=3+Math.random()*3;",
        "f.state='active'; f.timer=1.4+Math.random()*1.4;"
    )
    print("OK: fire active timer reduced")
else:
    print("FAIL: fire active timer")

# Warning duration: 1.8s → 1.0s
if "f.state='warning'; f.timer=1.8;" in html:
    html = html.replace(
        "f.state='warning'; f.timer=1.8;",
        "f.state='warning'; f.timer=1.0;"
    )
    print("OK: fire warning timer reduced")
else:
    print("FAIL: fire warning timer")

# Fire oscillation speed: 0.7+rand(0.7) → 2.2+rand(1.8)
if "spd:0.7+Math.random()*0.7" in html:
    html = html.replace(
        "spd:0.7+Math.random()*0.7",
        "spd:2.2+Math.random()*1.8"
    )
    print("OK: fire oscillation spd increased")
else:
    print("FAIL: fire spd")

# Initial timers: 3+i*1.2 → 0.8+i*0.5
if "timer:3+i*1.2" in html:
    html = html.replace("timer:3+i*1.2", "timer:0.8+i*0.5")
    print("OK: fire init timer")
else:
    print("FAIL: fire init timer")

# ── 6. Speed up enemy AI ──────────────────────────────────────────────────
if "vx:i===0?1.3:-1.1, vy:i===0?0.9:1.2," in html:
    html = html.replace(
        "vx:i===0?1.3:-1.1, vy:i===0?0.9:1.2,",
        "vx:i===0?2.1:-1.8, vy:i===0?1.5:2.0,"
    )
    print("OK: enemy speed increased")
else:
    print("FAIL: enemy speed")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== Verification ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
print("restaurant_bg in IMG:", '"restaurant_bg"' in v)
print("restaurant layer:", "restaurant_bg" in v and "setDepth(-15)" in v)
print("grill bars:", "BAR=22" in v)
print("fire fast:", "f.timer=1.4+Math.random()*1.4" in v)
print("fire spd:", "spd:2.2+Math.random()*1.8" in v)
print("enemy fast:", "vx:i===0?2.1:-1.8" in v)
print("speed 122:", "speed:122," in v)
