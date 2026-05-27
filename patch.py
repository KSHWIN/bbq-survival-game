with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. 汗水表情縮小 ─────────────────────────────────────
html = html.replace(
    "      fontSize: '18px', fontFamily: 'sans-serif'\n    }).setDepth(20).setVisible(false);",
    "      fontSize: '12px', fontFamily: 'sans-serif'\n    }).setDepth(20).setVisible(false);"
)
html = html.replace(
    ".setPosition(sprite.x + 24, sprite.y - 30)",
    ".setPosition(sprite.x + 16, sprite.y - 20)"
)
html = html.replace(
    ".setPosition(sprite.x + 22, sprite.y - 26)",
    ".setPosition(sprite.x + 14, sprite.y - 18)"
)
print("sweat:", "12px" in html)

# ── 2. 叉子九宮格（找到 spawnFork 到 drawFork 結束，整塊換掉）
start = html.find("  spawnFork() {")
# find end of drawFork
df_start = html.find("  drawFork() {", start)
df_end   = html.find("\n  }", df_start) + 4  # include closing }

if start != -1 and df_start != -1:
    NEW_FORK = '''  spawnFork() {
    const CELL = 40, ZONE = 3, half = CELL * ZONE / 2;
    const maxCol = Math.floor(G.w / CELL) - ZONE;
    const maxRow = Math.floor(G.h / CELL) - ZONE;
    const cx = G.x + (Math.floor(Math.random() * maxCol) + 1.5) * CELL;
    const cy = G.y + (Math.floor(Math.random() * maxRow) + 1.5) * CELL;
    this.fork = { cx, cy, half, phase: "warn", timer: 0 };
    if (this.chefSprite) {
      this.chefSprite.setPosition(cx, G.y - 90).setAngle(90).setVisible(true).setAlpha(0);
      this.tweens.add({ targets: this.chefSprite, y: G.y - 8, alpha: 1,
        duration: 600, ease: "Back.easeOut" });
    }
  }

  checkForkHit() {
    if (!this.fork) return;
    const { cx, cy, half } = this.fork;
    if (Math.abs(this.p.x - cx) < half && Math.abs(this.p.y - cy) < half) {
      this.subTxt.setText("Fork hit!");
      this.endGame(false);
    }
    if (this.chefSprite && this.chefSprite.visible) {
      this.time.delayedCall(250, () => {
        if (!this.chefSprite) return;
        this.tweens.add({ targets: this.chefSprite, y: G.y - 110, alpha: 0, duration: 400,
          onComplete: () => { if (this.chefSprite) this.chefSprite.setVisible(false); } });
      });
    }
  }

  drawFork() {
    const g = this.forkLayer;
    g.clear();
    if (!this.fork) return;
    const { cx, cy, half, phase, timer } = this.fork;
    const CELL = 40, isWarn = phase === "warn";
    if (isWarn) {
      const a = 0.13 + 0.10 * Math.sin(timer * 7);
      g.fillStyle(0xffee44, a);
      g.fillRect(cx - half, cy - half, half * 2, half * 2);
      g.lineStyle(2, 0xffcc00, a * 3.5);
      for (let i = 0; i <= 3; i++) {
        g.lineBetween(cx - half + i*CELL, cy - half, cx - half + i*CELL, cy + half);
        g.lineBetween(cx - half, cy - half + i*CELL, cx + half, cy - half + i*CELL);
      }
    } else {
      g.fillStyle(0xff2200, 0.55);
      g.fillRect(cx - half, cy - half, half * 2, half * 2);
      g.lineStyle(2, 0xff6600, 0.85);
      for (let i = 0; i <= 3; i++) {
        g.lineBetween(cx - half + i*CELL, cy - half, cx - half + i*CELL, cy + half);
        g.lineBetween(cx - half, cy - half + i*CELL, cx + half, cy - half + i*CELL);
      }
      for (let r = 0; r < 3; r++) {
        for (let c = 0; c < 3; c++) {
          const fx = cx - half + (c + 0.5)*CELL;
          const fy = cy - half + (r + 0.5)*CELL;
          [-5, 0, 5].forEach(off => {
            g.lineStyle(3, 0xffffff, 0.75);
            g.lineBetween(fx + off, fy - 14, fx + off, fy + 14);
          });
        }
      }
    }
  }'''
    html = html[:start] + NEW_FORK + html[df_end:]
    print("fork block replaced: OK")
else:
    print("FAIL: fork block not found, start=", start, "df_start=", df_start)

# ── 3. 敵人死亡 → 全滅判斷 ─────────────────────────────
# Find the enemy heat death line
idx = html.find("if (e.heat >= 100) { e.alive = false;")
if idx != -1:
    end_idx = html.find("}", idx) + 1
    old_snip = html[idx:end_idx]
    new_snip = (
        "if (e.heat >= 100) {\n"
        "        e.alive = false;\n"
        "        this.showPop(e.label + ' cooked!');\n"
        "        if (this.enemies.every(en => !en.alive)) {\n"
        "          this.time.delayedCall(600, () => this.endGame(true));\n"
        "        }\n"
        "      }"
    )
    html = html[:idx] + new_snip + html[end_idx:]
    print("enemy death win: OK")
else:
    print("FAIL: enemy death not found")

# ── 4. checkEnemyFall 也加全滅判斷 ─────────────────────
html = html.replace(
    "this.showPop(`${e.label} 掌落！`);",
    "this.showPop(e.label + ' fell off!');\n        if (this.enemies.every(en => !en.alive)) { this.time.delayedCall(600, () => this.endGame(true)); }"
)
# ASCII fallback for the popText
fall_idx = html.find("this.showPop(e.label + ' fell off!')")
print("fall win:", fall_idx != -1)

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== Final Check ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
print("nine-grid half:", "CELL * ZONE / 2" in v)
print("warn color 0xffee44:", "0xffee44" in v)
print("grid lines in fork:", "cx - half + i*CELL" in v)
print("fork tines per cell:", "fx + off, fy - 14" in v)
print("win on all dead:", "enemies.every(en => !en.alive)" in v)
