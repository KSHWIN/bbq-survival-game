# -*- coding: utf-8 -*-
# Patch 39: 嵌入 lv2/lv3/lv4 全景背景圖（480×272），用於遊戲進行畫面
import base64, io, glob
from PIL import Image

def img_to_b64(path, w, h):
    img = Image.open(path).convert("RGBA").resize((w, h), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True, compress_level=9)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

LVFULL = {}
for key in ["lv2_bg", "lv3_bg", "lv4_bg"]:
    files = glob.glob(f"c:/Users/User/Desktop/烤肉遊戲/{key}_*.png")
    if not files:
        print(f"FAIL: {key} 找不到圖片"); exit(1)
    fkey = key + "_full"
    LVFULL[fkey] = img_to_b64(sorted(files)[-1], 480, 272)
    print(f"{fkey}: {len(LVFULL[fkey])//1024} KB")

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

# 若已存在則跳過，否則注入
if 'lv2_bg_full' not in html:
    insert_str = "".join(f'  "{k}": "{v}",\n' for k, v in LVFULL.items())
    rep("inject lv_full", "const IMG = {", "const IMG = {\n" + insert_str)
else:
    results.append("lv_full 已存在，跳過注入")

# GameScene 背景：改為依關卡顯示對應圖
rep("game bg",
    "    // 餐廳背景\n"
    "    if(this.textures.exists('cartoon_bg')){\n"
    "      this.add.image(W/2,H/2,'cartoon_bg').setDisplaySize(W,H).setDepth(-15).setAlpha(0.90);\n"
    "    }",

    "    // 關卡專屬背景（lv2_bg_full / lv3_bg_full / lv4_bg_full），fallback 通用背景\n"
    "    const _lvBgKey=this.levelData.key+'_full';\n"
    "    const _bgKey=this.textures.exists(_lvBgKey)?_lvBgKey\n"
    "      :this.textures.exists('cartoon_bg')?'cartoon_bg':null;\n"
    "    if(_bgKey) this.add.image(W/2,H/2,_bgKey).setDisplaySize(W,H).setDepth(-15).setAlpha(0.85);"
)

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

for r in results:
    print(r)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
for key in ["lv2_bg_full","lv3_bg_full","lv4_bg_full"]:
    print(f'{key}: {"OK" if key in v else "MISSING"}')
print(f'game bg code: {"OK" if "_lvBgKey" in v else "MISSING"}')
