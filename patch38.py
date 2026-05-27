# -*- coding: utf-8 -*-
# Patch 38: 嵌入 lv2/lv3/lv4 地圖背景圖，顯示在關卡選擇卡片上
import base64, io, os, glob
from PIL import Image

# ── 1. 找圖檔 + 縮圖 → base64 ────────────────────────────────────
def img_to_b64(path, w, h):
    img = Image.open(path).convert("RGBA").resize((w, h), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

LVIMGS = {}
for key in ["lv2_bg", "lv3_bg", "lv4_bg"]:
    files = glob.glob(f"c:/Users/User/Desktop/烤肉遊戲/{key}_*.png")
    if not files:
        print(f"FAIL: {key} 找不到圖片")
        exit(1)
    # 縮圖到 336×152 (2× 卡片尺寸，保留細節)
    LVIMGS[key] = img_to_b64(sorted(files)[-1], 336, 152)
    print(f"{key}: {len(LVIMGS[key])//1024} KB")

# ── 2. 注入 IMG 物件 ─────────────────────────────────────────────
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

# 在 IMG 物件最後一個 key 後面加入新 key
# 找到 const IMG = { 的結尾 }; 前一行插入
insert_str = ""
for key, val in LVIMGS.items():
    insert_str += f'  "{key}": "{val}",\n'

rep("img inject",
    'const IMG = {',
    'const IMG = {\n' + insert_str)

# ── 3. 關卡卡片：加入背景圖 ──────────────────────────────────────
rep("lv card image",
    "      const cont=this.add.container(lx,ly);\n"
    "      const dc=DCOLS[Math.min(lv.diff-1,4)];\n"
    "      const shadow=this.add.rectangle(3,3,LW,LH,0x000000,0.55);\n"
    "      const bg=this.add.rectangle(0,0,LW,LH,0x080a12,0.95).setStrokeStyle(2,dc);",

    "      const cont=this.add.container(lx,ly);\n"
    "      const dc=DCOLS[Math.min(lv.diff-1,4)];\n"
    "      const shadow=this.add.rectangle(3,3,LW,LH,0x000000,0.55);\n"
    "      const bg=this.add.rectangle(0,0,LW,LH,0x080a12,0.95).setStrokeStyle(2,dc);\n"
    "      const lvImgKey='lv'+(i+1)+'_bg';\n"
    "      if(this.textures.exists(lvImgKey)){\n"
    "        const lvImg=this.add.image(0,0,lvImgKey).setDisplaySize(LW,LH).setAlpha(0.45);\n"
    "        cont.add(lvImg);\n"
    "      }")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

for r in results:
    print(r)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
for key in ["lv2_bg", "lv3_bg", "lv4_bg"]:
    print(f'{key} in IMG: {"OK" if f'"{key}"' in v else "MISSING"}')
print(f'lv card image code: {"OK" if "lvImgKey" in v else "MISSING"}')
