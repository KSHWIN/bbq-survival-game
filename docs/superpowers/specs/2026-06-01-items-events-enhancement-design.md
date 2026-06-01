# 烤肉遊戲：道具加強 + 場地事件加強 設計規格

## 範圍

分兩批實作：
- **第一批**：5 個道具加強 + AI 撿道具系統
- **第二批**：5 個場地事件加強（含地圖傾斜）

---

## 第一批：道具加強

### 前提：AI 撿道具系統

**目標**：讓 AI 和玩家平等地撿取場上道具，道具效果雙向有效。

**資料結構變更**：
每個 enemy 物件加入 `activeEffects`：
```js
e.activeEffects = { foil:0, garlic:0, sauce:0, sauceCharge:0, iceBoost:0, pepBoost:0 }
```

**撿取邏輯**：
在 `mapItems` 更新迴圈（目前只檢查玩家）新增對所有 alive AI 的距離檢查。AI 靠近 24px 自動撿起，呼叫 `applyItemToEnemy(e, item)`。

**效果套用**：
- `foil`：AI 的熱度累積計算加入隔熱判斷
- `garlic`：AI 的推力計算乘 1.7（現有推力邏輯）
- `iceBoost`：AI 速度 ×1.5，並留下冰跡
- `pepBoost`：AI 速度 ×1.5
- `sauceCharge`：AI 持有醬油後，接近玩家 60px 內自動佈陣（AI 不需要按鍵）

---

### 1. 冰塊 → 寒冰路徑

**觸發條件**：撿起冰塊後 `iceBoost` 計時期間（5 秒）

**新增資料**：
```js
this.iceTrail = []  // [{x, y, life:3.0, id}]
```

**留跡邏輯**：
- 當 `ae.iceBoost > 0`，每當玩家移動超過 15px（與上一個跡點距離）就新增一個冰跡點
- AI 同理

**冰跡效果**：
- 其他玩家/AI 進入冰跡點 r=22px 範圍 → 觸發 `ae.slip = 1.0`（加入 `activeEffects`）
- `ae.slip > 0`：玩家輸入方向無效，只能慣性滑行（速度不衰減）
- AI 打滑時 `e.slipTimer = 1.0`，期間跳過 AI 轉向邏輯
- 冰跡 life 3.0 秒後消失
- 冰跡留存者自身**免疫**自己的冰跡（不會滑）

**視覺**：
- 半透明白藍色小圓（r=16，alpha=0.5 隨 life 衰減）
- 繪製在 `itemLayer` 或新的 `trailLayer`（depth 14）

---

### 2. 鋁箔紙 → 反彈護盾

**觸發條件**：持有 `ae.foil > 0` 的一方被持有 `ae.garlic > 0` 的一方推擠

**推擠來源追蹤**：
在 `doPush()` 中標記 `this._pushingWithGarlic = (ae.garlic > 0)`。
在 AI 推擠玩家的碰撞解析中，標記 `e._pushingWithGarlic = (e.activeEffects.garlic > 0)`。

**反彈判斷**（在推擠力解析時）：
- 攻擊方 `garlic > 0` **且** 被攻擊方 `foil > 0`
- → 取消對被攻擊方的位移，改對攻擊方施加 2× 推力向後彈飛
- 彈出文字：「🪞 反彈！」
- 邊緣案例：雙方都有 garlic + foil 時，以被攻擊方的 foil 為準，攻擊方仍被彈回

**單人模式**：AI 拿大蒜推有鋁箔的玩家 → AI 被彈回（有效）

---

### 3. 大蒜 → AOE 衝擊波

**觸發條件**：`ae.garlic` 從 `>1.0` 降至 `≤1.0`，且 `_garlicAoeDone === false`

**狀態管理**：
- 撿起大蒜時：`_garlicAoeDone = false`
- 觸發後：`_garlicAoeDone = true`（避免同一次大蒜重複觸發）

**AOE 效果**：
- 範圍：r = 100px
- 對範圍內所有敵人施加徑向擊退（力道 = 1.2× 正常推力）
- 彈出文字：「💥 大蒜爆發！」

**視覺**：
- 一個從玩家中心向外擴散的環形光波（r 從 0 到 110，0.35 秒，alpha 從 0.8 衰減到 0）
- 顏色：淡黃色 `0xffee88`

---

### 4. 醬油 → 黏滯陷阱

**撿起後狀態**：
- `ae.sauceCharge = 5.0`（倒數計時）
- 此期間**S 鍵（push）佈陣而非推擠**
- 5 秒到未按 → 自動在當前位置佈陣

**HUD 顯示**：
- `sauceCharge > 0` 時顯示「🍶 醬油 Xs」倒數

**佈陣效果**：
```js
this.saucePools.push({ x, y, r:55, life:8.0, ownerId:'player' })
```
- 最多同時 2 個（超過時移除最舊的）
- 陷阱內敵人速度 ×0.7（持續），玩家本人免疫

**AI 行為**：
- AI `sauceCharge > 0` 時，靠近玩家 60px 內自動佈陣

**視覺**：
- 深褐色半透明圓（alpha 0.4，邊緣深色輪廓）
- life 隨時間衰減 alpha

---

### 5. 胡椒粉 → 打噴嚏擊退

**觸發條件**：`ae.pepBoost` 從 `>0` 降為 `0` 的那一幀

**偵測方式**：
每幀記錄 `_pepWas = ae.pepBoost > 0`，下幀檢測轉換點。

**噴嚏效果**：
- 偵測 `lastDir` 方向 ±45° 扇形、80px 範圍內的所有敵人
- 施加 1.8× 正常推力（方向 = lastDir）
- 彈出文字：「💨 哈啾！」

**視覺**：
- 在 `lastDir` 方向畫一個短暫的白色扇形（alpha 從 0.8 降到 0，0.3 秒）

---

## 第二批：場地事件加強

### 1. 廚師叉子 → 紅色軌跡線 + 插地牆壁

**紅色雷射線**：
- `warn` 狀態期間，從叉子入射起點到 `targetY` 畫一條紅線
- alpha = `0.3 + 0.5 * (1 - timer/1.6)`（越接近落下越明顯）

**插地牆壁**：
- `stuck` 狀態延長至 **3.0 秒**（原 1.8s）
- 每幀：若玩家或 AI 距叉子 x 中心 <28px 且速度方向朝向叉子，施加反方向彈力（1.6× 推力）
- 彈出文字：「⚡ 撞到叉子！」

---

### 2. 檸檬雨 → 密集酸汁殘留（擠檸檬感）

**落地後產生濺射**：
每顆檸檬落地，向 4~6 個隨機方向濺射小酸汁點：
```js
for(let i=0; i<4+Math.floor(Math.random()*3); i++){
  const ang = Math.random()*Math.PI*2;
  const dist = 20 + Math.random()*40;
  lemonPuddles.push({ x: ev.x + cos(ang)*dist, y: ev.y + sin(ang)*dist,
                      r: 18+Math.random()*8, life:2.5 })
}
```

**酸汁效果**（任一酸汁點內）：
- 玩家/AI：`slowpow += 0.4` 每秒（持續補慢）+ 加熱 +6/s
- 視覺：黃綠色半透明小水坑，邊緣有隨機 ±2px 抖動，alpha 隨 life 衰減

---

### 3. 烤盤破洞 → 發紅預警 + 連鎖崩塌

**warn 狀態視覺加強**：
- 在洞的位置畫脈動橘紅色光暈（`sin(ph*8)` 控制脈動）
- 洞的渲染位置加上 ±2px 隨機抖動（每幀新 offset）

**連鎖崩塌**：
- 每幀：若有 `state === 'stuck'` 的叉子，其 `x` 與 `targetY` 距洞中心 <40px
- → 立刻將 `h.timer = 0`，跳過剩餘 warn 時間直接進入 `active`

---

### 4. 場地縮小 → 邊緣火圈

**加熱觸發**：
`shrinkPad > 0` 時，每幀計算玩家距有效邊界距離：
```js
const edgeDist = Math.min(p.x - (G.x+pad), (G.x+G.w-pad) - p.x,
                          p.y - (G.y+pad), (G.y+G.h-pad) - p.y);
if(edgeDist < 30) heat += 35 * dt;
```
AI 同樣適用。

**視覺**：
- 在縮圈邊緣內側畫橘紅粒子環（每幀隨機 8~12 個小圓，沿邊緣分布，alpha 隨機 0.3~0.7）

---

### 5. 地圖傾斜 → 視覺強化 + 低側加速帶

**warn 階段加強**：
- 在傾斜方向的邊緣畫橘紅警示帶（閃爍 `sin(ph*6)` 控制）
- 警示帶寬度 20px，沿低側邊緣全長

**active 階段加強**：
- 距低側邊緣 35px 內，額外傾斜力 ×1.5（`tilt.force * 1.5`）
- 地圖上的道具也以 `tilt.x * 15 * dt, tilt.y * 15 * dt` 緩慢滑動

---

## 實作注意事項

- `iceTrail`、`saucePools`、`lemonPuddles` 在 `create()` 初始化為 `[]`，`update()` 每幀衰減 life
- 玩家 `activeEffects` 加入 `slip:0`（配合冰跡打滑）
- AI `activeEffects` 的 timer 遞減使用與玩家相同的 `Object.keys` 迴圈模式
- AI 建立的 saucePool 用 `ownerId: e.label`（AI 本身免疫自己的池子）
- 所有新效果（iceTrail、saucePools、lemonPuddles）在 `endGame()` 與 `scene.restart()` 時清空
- 效果 HUD（`effectTxt`）加入 `slip`（⛸打滑）、`sauceCharge`（🍶倒數）的顯示
- 第一批完成後先打開遊戲測試，確認 AI 撿道具、冰跡、反彈邏輯，再進行第二批
