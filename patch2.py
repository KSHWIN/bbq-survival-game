with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Fix checkEnemyFall to add win check
old = (
    "    if (!inGrill(e.x, e.y)) {\n"
    "      e.alive = false;\n"
    "      if (this.enemySprites[i]) this.enemySprites[i].setVisible(false);\n"
    "      if (this.enemyFx[i])      this.enemyFx[i].setVisible(false);\n"
    "      this.showPop(`${e.label} 掉落！\U0001f4a8`);\n"
    "    } else if (this.onFire(e.x, e.y)) {"
)
new = (
    "    if (!inGrill(e.x, e.y)) {\n"
    "      e.alive = false;\n"
    "      if (this.enemySprites[i]) this.enemySprites[i].setVisible(false);\n"
    "      if (this.enemyFx[i])      this.enemyFx[i].setVisible(false);\n"
    "      this.showPop(e.label + ' 掉落！');\n"
    "      if (this.enemies.every(en => !en.alive)) {\n"
    "        this.time.delayedCall(600, () => this.endGame(true));\n"
    "      }\n"
    "    } else if (this.onFire(e.x, e.y)) {"
)

if old in html:
    html = html.replace(old, new)
    print("OK fall win check added")
else:
    print("FAIL - trying byte search")
    idx = html.find("if (this.enemySprites[i]) this.enemySprites[i].setVisible(false);")
    if idx != -1:
        end = html.find("} else if (this.onFire", idx)
        snippet = html[idx:end]
        print("found snippet:", repr(snippet))

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

# Now handle the new grill background image
from PIL import Image
import base64, io, os

path = "c:/Users/User/Desktop/烤肉遊戲/assets/"
# find the new grill bg
files = [f for f in os.listdir(path) if f.startswith("grill_bg2_")]
if files:
    img_path = path + sorted(files)[-1]
    img = Image.open(img_path).convert("RGBA").resize((800, 580), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode()
    data_url = f"data:image/png;base64,{b64}"
    print(f"New grill bg: {len(b64)//1024}KB")

    with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Replace old grill_bg data URL with new one
    old_start = html.find('"grill_bg": "data:image/png;base64,')
    if old_start != -1:
        old_end = html.find('",', old_start) + 2
        html = html[:old_start] + f'"grill_bg": "{data_url}",' + html[old_end:]
        print("OK grill_bg replaced")
    else:
        # Maybe it's at the end without comma
        old_start = html.find('"grill_bg": "data:image/png;base64,')
        print("grill_bg not found in expected format")

    with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
        f.write(html)
else:
    print("No grill_bg2 file found")

print("\nDone")
