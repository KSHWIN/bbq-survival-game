# 烤肉遊戲 更新設計文件

Date: 2026-05-27

---

## 任務 1 — 青椒大絕「辣椒素路徑」重設計

### 目標
將青椒大絕從「控制反轉」改為「沿路留下辣椒素軌跡，敵人碰到後大幅減速」，呼應辛吉德（Singed）沿路放毒素的玩法，製造追逃攻防感。

### 現有效果（移除）
- 啟動時爆散初始效果（30 個粒子爆散）
- 敵人控制反轉（6 秒）

### 新效果
- 速度加成 +50% 保留（維持現有 `spdMul: 1.5`）
- 移動時沿路生成辣椒素節點
- 敵人碰到節點後大幅減速

### 辣椒素節點規格

**生成條件**
- 玩家每移動累積 ≥ 20px 距離，在當前位置生成一個節點
- 站定不動時不生成（防止定點刷滿）
- 存放於 `ultState.nodes[]`

**節點資料結構**
```js
{ x, y, life: 8.0 }  // life 單位：秒
```

**消亡**
- 每幀減少 `life += -delta`
- `life <= 0` 時從陣列移除

**碰撞偵測**
- 每幀遍歷所有存活節點，對每個存活敵人檢查距離 < 28px
- 命中後對敵人施加 `capsaicin` 狀態

**`capsaicin` 狀態**
- 速度乘數：0.25（減速 75%）
- 持續時間：3 秒
- 同一節點對同一敵人觸發後，該組合進入 3 秒 cooldown（節點上存 `hitMap: { enemyIndex: cooldownTimer }`，用 `this.enemies` 陣列的 index 作為 key），避免每幀重複觸發

### 視覺效果

**節點外觀**
- 橘紅色實心圓，半徑 10px
- `alpha = life / 8`（隨生命週期線性衰減，出現時不透明，消失前透明）
- 繪製於 `drawEffects()` 中，在玩家層之下

**敵人中招回饋**
- 敵人角色短暫閃橘色（`tintFlash`，0.3 秒）

### 大絕名稱
「辣椒素噴霧」（或保留「毒霧迷蹤」，依現有文字位置決定）

---

## 任務 2 — 雞翅大絕位置 Bug 修正

### 問題描述
雞翅大絕「旋風疾飛」結束後，角色位置回到大絕啟動時的原始座標，而非飛行路徑的終點位置。

### 根本原因
大絕結束的 cleanup 邏輯恢復了原始座標，而非保留飛行終點。

### 修法

**`ultState` 初始化時加入終點追蹤**
```js
ultState.endX = this.p.x;
ultState.endY = this.p.y;
```

**飛行過程中每幀更新**
```js
ultState.endX = this.p.x;
ultState.endY = this.p.y;
```

**大絕結束 cleanup 時**
```js
this.p.x = this.ultState.endX;
this.p.y = this.ultState.endY;
// 不恢復原始 startX / startY
```

---

## 任務 3 — 能量球視覺升級

### 目標
讓能量球更顯眼、更有搶奪感：出現前地板預兆讓玩家提前聚集，出現後粒子環繞讓玩家一眼認出目標。

### 預兆地光（出現前 3 秒）

**觸發時機**
能量球 spawn 前 3 秒，在預定座標啟動預兆動畫（`orb.preSpawn = true`）

**視覺**
- 紫色光暈圓形，半徑 24px
- `alpha` 用 `Math.sin(time * freq) * 0.5 + 0.5` 做呼吸動畫
- `freq`：從 0.8Hz 線性增加至 2Hz（隨倒數時間接近，節奏加快）
- 顏色：`#cc88ff`（紫色）

### 能量球本體升級

**外層發光暈圈**
- 半透明紫色圓，半徑 22px，`alpha: 0.35`
- 持續呼吸脈衝（`Math.sin` 讓 alpha 在 0.2 ~ 0.5 之間浮動）

**旋轉粒子**
- 6 顆小圓粒子，半徑 4px，顏色白色或淡紫
- 以半徑 30px 繞能量球中心旋轉
- 每幀 `orb.particleAngle += delta * 2`（約 2 rad/s）
- 粒子位置：`angle + i * (Math.PI * 2 / 6)` 均勻分佈

### 狀態欄位（新增至 orb 物件）
```js
{
  preSpawnTimer: 3.0,   // 預兆倒數（出現前 3 秒開始）
  preSpawn: false,      // 是否在預兆狀態
  particleAngle: 0,     // 旋轉粒子當前角度
  glowPhase: 0          // 呼吸動畫 phase
}
```

---

## 影響範圍

| 檔案 | 修改區域 |
|------|----------|
| `index.html` | `fireUltimate()` case 'pepper'（約第 2934 行） |
| `index.html` | `updateUltState()` — 新增 capsaicin 節點邏輯 |
| `index.html` | `drawEffects()` — 新增節點繪製 |
| `index.html` | `activeEffects` — 新增 `capsaicin` 狀態處理 |
| `index.html` | 雞翅大絕 `ultState` 初始化與 cleanup（約第 2880 行） |
| `index.html` | orb spawn 邏輯 — 新增 `preSpawnTimer` |
| `index.html` | orb 繪製邏輯 — 新增粒子與發光 |
