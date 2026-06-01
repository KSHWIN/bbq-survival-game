# 烤肉遊戲 — Claude 工作指引

## 專案架構
- 單一 HTML 檔：`index.html`（4000+ 行，全部在同一個 `<script>` 裡）
- 遊戲引擎：Phaser 3.60.0（WebGL）
- Scene 順序：BootScene → SelectScene → TeamScene → GameScene
- 大廳 UI：`#lobby-overlay`（HTML + CSS，z-index: 9999，蓋在 Phaser canvas 上方）

## 遊戲啟動 / 關閉邏輯
- `gameInstance` 是全域變數，管理單一 Phaser 實例
- `createGame()` 在建新實例之前會先 destroy 舊的
- ESC 離開遊戲時呼叫 `gameInstance.destroy(true)` + `gameInstance = null`
- 再次「單人遊玩」時，`showSingle()` 偵測到 `gameInstance === null` 才重建
- BootScene 支援 `window._PENDING_GAME_START`，供多人模式 destroy/recreate 後直接跳 TeamScene

---

## Phaser 除錯速查

### 症狀 → 原因 → 修法

| 症狀 | 最可能原因 | 快速確認 | 修法 |
|------|-----------|---------|------|
| 畫面全凍（動畫+音樂都停） | `update()` 裡有未被 catch 的 exception → rAF loop 停止 | F12 看有無紅字 Uncaught Error | 在 `update()` 邏輯主體包 `try{...}catch(e){console.error('[tag]',e)}` |
| 移動滑鼠就噴錯 | tween callback 對已銷毀的 Graphics 呼叫 `.clear()` 等 | F12 看 `null (reading 'xxx')` in phaser.min.js | tween onUpdate: `if(!gfx.scene) return;` |
| 第二場異常（第一場正常） | Phaser scene 狀態殘留 | 看 Console 有無 `[game update crash]` | `gameInstance.destroy(true)` 後重建（已實作） |
| `ReferenceError: xxx is not defined` | 事件 handler 裡用了 closure 外的變數 | F12 直接指向行號 | 改用 closure 內已有的變數 |

### Phaser 物件安全使用原則

```javascript
// ❌ 危險：destroy 後的物件 JS 引用仍為 truthy
if (this.layer) this.layer.clear();

// ✅ 安全：destroy 後 .scene 會變成 null
if (this.layer && this.layer.scene) this.layer.clear();

// ✅ Tween callback 必加
this.tweens.add({
  onUpdate: () => { if (!gfx.scene) return; gfx.clear(); ... },
  onComplete: () => { if (gfx.scene) gfx.destroy(); }
});
```

### Phaser 物件生命週期
1. `create()` 建立物件 → 加入 scene display list
2. scene 切換時 Phaser 自動 destroy display list 內所有物件
3. destroy 後：JS reference 仍存在（truthy），但 `obj.scene === null`
4. `if(obj)` 仍通過 → 必須用 `if(obj && obj.scene)`

### 決策樹：修補 vs. 重建

```
Bug 只在特定 scene 順序出現？
  ├─ 是 → 先加 try/catch + console.error 看真正錯誤
  │         修 1-2 輪後還沒解決？
  │           └─ 是 → 考慮 destroy(true) + recreate（終極解法）
  └─ 否 → 找純邏輯 bug，看 F12 Console 行號
```

---

## 除錯時給 Claude 看的資訊

請把 **F12 → Console** 截圖，特別注意：
1. 紅色 `✕ Uncaught Error` 訊息全文
2. 錯誤右邊的檔案名稱 + 行號（`index.html:834`）
3. 錯誤出現的時機（載入？按 ESC？點按鈕？）
4. 「A 情況正常，B 情況出問題，兩者差別是 XXX」

這樣可以省掉至少一半的來回時間。
