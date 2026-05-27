# -*- coding: utf-8 -*-
from PIL import Image
import base64, io, glob, os

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

assets = "c:/Users/User/Desktop/烤肉遊戲/assets/"

def embed_img(path, key, size, fmt="PNG", quality=85):
    img = Image.open(path).convert("RGBA")
    img = img.resize(size, Image.LANCZOS)
    buf = io.BytesIO()
    if fmt == "JPEG":
        img = img.convert("RGB")
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        mime = "image/jpeg"
    else:
        img.save(buf, format="PNG", optimize=True)
        mime = "image/png"
    b64 = base64.b64encode(buf.getvalue()).decode()
    print(f"  {key}: {len(b64)//1024}KB")
    return f'"data:{mime};base64,{b64}"'

# ── 1. Find latest files ───────────────────────────────────────────────────
def latest(prefix):
    files = sorted(glob.glob(assets + prefix + "_*.png"))
    return files[-1] if files else None

bg_file     = latest("cartoon_bg")
ice_file    = latest("item_ice")
foil_file   = latest("item_foil")
garlic_file = latest("item_garlic")
sauce_file  = latest("item_sauce")
pepper_file = latest("item_pepper")

print("Files found:")
for f in [bg_file, ice_file, foil_file, garlic_file, sauce_file, pepper_file]:
    print(" ", f)

# ── 2. Encode all images ───────────────────────────────────────────────────
print("\nEncoding:")
items_to_embed = []
if bg_file:
    items_to_embed.append(("cartoon_bg", embed_img(bg_file, "cartoon_bg", (800, 580), "JPEG", 72)))
if ice_file:
    items_to_embed.append(("item_ice",    embed_img(ice_file,    "item_ice",    (80, 80))))
if foil_file:
    items_to_embed.append(("item_foil",   embed_img(foil_file,   "item_foil",   (80, 80))))
if garlic_file:
    items_to_embed.append(("item_garlic", embed_img(garlic_file, "item_garlic", (80, 80))))
if sauce_file:
    items_to_embed.append(("item_sauce",  embed_img(sauce_file,  "item_sauce",  (80, 80))))
if pepper_file:
    items_to_embed.append(("item_pepper", embed_img(pepper_file, "item_pepper", (80, 80))))

# ── 3. Insert into IMG dict ────────────────────────────────────────────────
# Find end of IMG dict
img_end_idx = html.find('\n};')
for key, data_url in items_to_embed:
    # Remove old entry if exists
    old_key_start = html.find(f'"{key}"')
    if old_key_start != -1 and old_key_start < img_end_idx + 10:
        # Find and remove old entry
        entry_end = html.find('",', old_key_start)
        if entry_end != -1:
            # Remove comma-to-comma block
            entry_start = html.rfind(',\n', 0, old_key_start)
            if entry_start != -1:
                html = html[:entry_start] + html[entry_end+2:]
                img_end_idx = html.find('\n};')
                print(f"  Removed old {key}")

    # Insert new entry
    img_end_idx = html.find('\n};')
    html = html[:img_end_idx] + f',\n  "{key}": {data_url}' + html[img_end_idx:]
    img_end_idx = html.find('\n};')  # update after insert
    print(f"  Inserted {key}")

# ── 4. Replace restaurant_bg with cartoon_bg in game code ────────────────
html = html.replace("'restaurant_bg'", "'cartoon_bg'")
print("Replaced restaurant_bg -> cartoon_bg:", "'cartoon_bg'" in html)

# Also update SelectScene background to use cartoon_bg
old_sel_bg = (
    "    if(this.textures.exists('grill_bg')) this.add.image(W/2,H/2,'grill_bg').setDisplaySize(W,H).setAlpha(0.3);"
)
new_sel_bg = (
    "    const selBg=this.textures.exists('cartoon_bg')?'cartoon_bg':'grill_bg';\n"
    "    if(this.textures.exists(selBg)) this.add.image(W/2,H/2,selBg).setDisplaySize(W,H).setAlpha(0.45);"
)
if old_sel_bg in html:
    html = html.replace(old_sel_bg, new_sel_bg)
    print("SelectScene bg: OK")
else:
    print("FAIL SelectScene bg")

# ── 5. Update spawnItem to use image sprites instead of text labels ───────
old_spawn_txt = (
    "    const col=tp.good?'#88ffcc':'#ff8888';\n"
    "    const bg=tp.good?'#0a3322':'#440000';\n"
    "    const txt=this.add.text(x,y,tp.label,{\n"
    "      fontSize:'14px',fontFamily:'sans-serif',color:col,\n"
    "      backgroundColor:bg,padding:{x:5,y:3}\n"
    "    }).setOrigin(0.5).setDepth(16);\n"
    "    this.mapItems.push({x,y,type:tp.type,good:tp.good,dur:tp.dur,txt,life:12});"
)
new_spawn_img = (
    "    // Glow ring behind item\n"
    "    const gfx=this.add.graphics().setDepth(15);\n"
    "    gfx.fillStyle(tp.good?0x00ccff:0xff3300,0.45);\n"
    "    gfx.fillCircle(x,y,23);\n"
    "    gfx.lineStyle(2,tp.good?0x88ffff:0xff8800,0.9);\n"
    "    gfx.strokeCircle(x,y,23);\n"
    "    // Item image\n"
    "    const imgKey='item_'+tp.type;\n"
    "    const img=this.textures.exists(imgKey)\n"
    "      ? this.add.image(x,y,imgKey).setDisplaySize(36,36).setDepth(16)\n"
    "      : this.add.text(x,y,tp.label,{fontSize:'12px',color:tp.good?'#88ffcc':'#ff8888',backgroundColor:tp.good?'#0a3322':'#440000',padding:{x:3,y:2}}).setOrigin(0.5).setDepth(16);\n"
    "    this.mapItems.push({x,y,type:tp.type,good:tp.good,dur:tp.dur,img,gfx,life:12});"
)
if old_spawn_txt in html:
    html = html.replace(old_spawn_txt, new_spawn_img)
    print("spawnItem image: OK")
else:
    print("FAIL spawnItem image")

# ── 6. Update item filter to destroy img+gfx instead of txt ─────────────
old_filter = (
    "      if(Math.hypot(this.p.x-item.x,this.p.y-item.y)<24){this.applyItem(item);item.txt.destroy();return false;}\n"
    "      if(item.life<=0){item.txt.destroy();return false;}\n"
    "      item.txt.setAlpha(item.life<3&&Math.floor(item.life*5)%2===0?0.3:1);"
)
new_filter = (
    "      if(Math.hypot(this.p.x-item.x,this.p.y-item.y)<24){this.applyItem(item);item.img.destroy();item.gfx.destroy();return false;}\n"
    "      if(item.life<=0){item.img.destroy();item.gfx.destroy();return false;}\n"
    "      const blink=item.life<3&&Math.floor(item.life*5)%2===0;\n"
    "      item.img.setAlpha(blink?0.25:1); item.gfx.setAlpha(blink?0.25:1);"
)
if old_filter in html:
    html = html.replace(old_filter, new_filter)
    print("item filter: OK")
else:
    print("FAIL item filter")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
print("cartoon_bg in IMG:", '"cartoon_bg"' in v)
print("item_ice in IMG:", '"item_ice"' in v)
print("item_sauce in IMG:", '"item_sauce"' in v)
print("item img key:", "'item_'+tp.type" in v)
print("gfx ring:", "strokeCircle" in v)
print("img destroy:", "item.img.destroy()" in v)
print("no double comma:", ',,' not in v[:img_end_idx+200])
