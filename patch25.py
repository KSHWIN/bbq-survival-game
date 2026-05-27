# -*- coding: utf-8 -*-
# Patch 25: 修飛撲 bug（同幀取消）+ 慢速可見飛撲動畫
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. 移除同幀取消 bug ─────────────────────────────────────────────────────
# 原本只要按著方向鍵同時按 J，isDash=true 同幀 mx/my!=0 就立刻取消，
# 導致飛撲完全沒作用。直接移除這行，讓飛撲自然跑完到底。
old = "    // 玩家主動按鍵 → 立即取消衝刺（同幀生效，不再有延遲卡頓）\n    if(isDash&&(mx!==0||my!==0)){this.dashState.active=false;this.dashState=null;}\n"
new = ""
if old in html: html=html.replace(old,new); print("remove same-frame cancel: OK")
else: print("FAIL same-frame cancel")

# ── 2. 飛撲速度 320 → 165（看得到跳出去的過程）───────────────────────────
old = "    const SPD=isDash?320:this.charData.speed*(this.activeEffects.slowpow>0?0.5:1);"
new = "    const SPD=isDash?165:this.charData.speed*(this.activeEffects.slowpow>0?0.5:1);"
if old in html: html=html.replace(old,new); print("dash speed 165: OK")
else: print("FAIL dash speed")

# ── 3. dist 追蹤同步改為 165（跟 SPD 一致）────────────────────────────────
old = "      this.dashState.dist+=320*dt;"
new = "      this.dashState.dist+=165*dt;"
if old in html: html=html.replace(old,new); print("dist tracking 165: OK")
else: print("FAIL dist tracking")

# ── 4. 最大飛撲距離 70 → 95（夠遠、能撞到人）──────────────────────────────
old = "    const DIST=Math.round(70*spd)*boost;   // 快→遠"
new = "    const DIST=Math.round(95*spd)*boost;   // 快→遠"
if old in html: html=html.replace(old,new); print("maxDist 95: OK")
else: print("FAIL maxDist")

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
print("no same-frame cancel:", "if(isDash&&(mx!==0||my!==0)){this.dashState.active=false" not in v)
print("dash SPD 165:", "isDash?165:" in v)
print("dist 165:", "dashState.dist+=165*dt" in v)
print("maxDist 95:", "Math.round(95*spd)" in v)
