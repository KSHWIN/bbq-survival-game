# 烤肉遊戲 — Claude 工作指引

## 專案架構
- 單一 HTML 檔：`index.html`（7000+ 行，CRLF 換行；有好幾個 `<script>` 區塊：圖片資料、遊戲本體、大廳 Lobby）
- 遊戲引擎：Phaser 3.60.0（WebGL）；畫面座標 W=960 / H≈680，烤盤範圍 `G={x,y,w,h}`
- Scene 順序：BootScene → SelectScene → TeamScene（賽前設定）→ GameScene
- 大廳 UI：`#lobby-overlay`（HTML + CSS，z-index: 9999，蓋在 Phaser canvas 上方）
- 連線伺服器：`server.js`（socket.io，部署在 Render，push 到 master 會自動重新部署；免費方案會休眠）
- 發布：GitHub Pages（https://kshwin.github.io/bbq-survival-game/），push 到 master 約 1 分鐘生效

## 目前的遊戲規則（2026-11 定案）
- **預設模式：三條命計分賽**（場地效果 `respawn`，預設開）。一局 60 秒，或只剩一人時結束；**比分數**。
  - 出局 -1 ❤，3 秒後回場（2 秒無敵，有「⬇ 你在這裡」光柱）。命用完 → **鬼魂**：沿烤盤外圈走、按 A 丟**炭火彈**（1 秒預告、炸飛 + 熟度 +15%、冷卻 6 秒）；炸彈炸下一個人 → 復活一次（1 條命）。鬼魂不能得分。
  - 計分：撞中 +0.5、擊落 +3、擊落 🎯（熟度 ≥70%）再 +2、🍶 醬油助攻 +1、活到最後 +3。擊落另給：熟度 -30%、大絕 +1。結算畫面會列出每人的算式（`_bd` 分數明細）。
- 撞人傳熱：對方 +10%、自己 -5%。站著不動 1.5 秒會焦（`stillBurn`）。熟度 ≥70% 頭上出現 🎯，AI 會圍攻。
- 道具：冰塊（-42% 熟度、加速）、鋁箔（10 秒反彈）、大蒜（推力 ×1.7、身體變大）、**滾燙醬油**（按 A 往前丟 150px；踩到的人變慢、每秒 +8%、**不能衝刺**；4 秒內出局算丟的人擊落，被別人推下去則丟的人拿助攻）、**胡椒粉**（15 秒；身上有火紅光環；撞到人 → 對方打噴嚏定住 1 秒 +8%）。
- 大絕：開局 0 格，能量球每 7 秒一顆，集 3 格按 D。
- 畫面震動：所有震動都進 `_addTrauma()`（創傷值，最大 12px），撞人只在 `_hitFeel()` 算一次；跟玩家無關的事不震。賽前設定有「強/中/關」（`localStorage bbq_shake`）。
- 開場 3-2-1 倒數 `_countdown()`：倒數時遊戲暫停（tween 也停），所以用 requestAnimationFrame + 真實時間做動畫；目前只在第一局（看完說明卡後）出現。
- 尚未決定：檸檬汁（變快）跟檸檬雨（炸飛、變慢）性格矛盾，可能統一成「速度」道具；每局都要倒數嗎；模擬中「亂衝」略強於「挑時機」。

## 重要函式位置（用 Grep 找）
- 三條命 / 鬼魂：`_respawnPlayer`、`_becomeGhostPlayer`、`_ghostPlayerTick`、`_ghostEnemyTick`、`_onEnemyOut`、`_bombCredit`、`_checkLivesEnd`、`_throwBomb` / `_bombBoom`
- 計分：`_addScore(who,n,x,y,ko,vh,raw)`（who=null 是玩家）、`_finalScores`、`_soyCredit`、`_showResult`
- 頭上標記（🎯、❤、💨、🍶黏住、胡椒光環）：`_updateLivesFx`；`endGame(win,final)`：三條命模式只有 `final=true` 才真的結束

## 工作流程
- 改完、測過就 commit + push 到 master（不用再問）；只提交相關檔案（不要提交 `assets/* - 複製.png`、`docs/superpowers/` 草稿、`.superpowers/`、`.m4a`）。
- 修改方式：用 Python 腳本把整個檔案讀成字串、`\r\n`→`\n` 後做「必須剛好出現一次」的取代，再寫回 CRLF。
- 測試工具放在 `C:\Users\User\AppData\Local\Temp\bbqtools\`（暫存資料夾，可能被清掉）：`checkall.py`（每個 script 區塊語法檢查）、`loadcheck.js`、`sim3.js` / `simdbg.js`（快轉模擬，三種打法 passive/aggro/smart）、`an3.py`（模擬統計）、`mptest.js`（雙視窗連線測試，要先開本機 `server.js`）、`livestest.js`、`soytest.js`、`bdtest.js`、`shaketest.js`、`cdtest.js`。執行：`PW_PATH="C:/Users/User/AppData/Roaming/npm/node_modules/playwright" node xxx.js "D:/烤肉遊戲/index.html" <截圖資料夾>`。
- 關測試伺服器只關 port 3000 那個 process，**不要** `taskkill /IM node.exe`（會把 Claude Code 自己也關掉）。
- 省 token：少截圖（只截局部）、測試只印結果。

## 遊戲啟動 / 關閉邏輯
- `gameInstance` 是全域變數，管理單一 Phaser 實例
- `createGame()` 在建新實例之前會先 destroy 舊的
- ESC 離開遊戲時呼叫 `gameInstance.destroy(true)` + `gameInstance = null`
- 再次「單人遊玩」時，`showSingle()` 偵測到 `gameInstance === null` 才重建
- BootScene 支援 `window._PENDING_GAME_START`，供多人模式 destroy/recreate 後直接跳 TeamScene

## 連線模式（房主當裁判）
- 房主跑完整遊戲；其他人只送按鍵（`input`），房主每秒送 15 次快照（`snap`，可丟棄）；結算走 `game_over` → `game_end`（一定送到）。
- GameScene 的 `netRole`：`'host'` / `'client'` / `null`（單人）。遠端真人在房主那邊是 `enemies` 裡 `remote:true` 的角色，由 `_remoteControl()` 操控。
- 客戶端 `_clientUpdate()` 只畫畫面，自己的角色本地先動再對齊房主位置。
- 本機測試：`node server.js` 後開 `index.html?server=http://localhost:3000`。
- 已同步：命數、鬼魂（遠端玩家變鬼魂也能丟炸彈）、炸彈、胡椒光環、醬油黏住、復活光柱、結算算式。
- 尚未支援（第二階段）：遠端玩家的 S 技能 / D 大絕、客戶端的打擊特效與音效、斷線由 AI 接手；「一條命」模式房主出局整局就結束。

## 語法檢查
- `index.html` 有好幾個 `<script>` 區塊，改完要**每一塊**都檢查（只查最大那塊會漏掉遊戲邏輯）。

## 美術素材
- 角色/道具/廚師圖已預先去背成透明 PNG 再嵌入 `IMG`（300px / 道具 80px）。**不要再加執行期「去白」**：它會把角色身上的白色（豆腐、眼睛反光）一起挖空。
- 新圖流程：`python tools/cutout.py assets/原圖.png 輸出.png 300` → base64 換進 `IMG`。只去「跟邊框連通的白底」，角色內部白色保留。
- 只有正面圖，所以移動不換貼圖；轉身/跳步/前傾/Q 彈/陰影都在 `GameScene._animChar()`（玩家與 AI 共用）。
- 打擊感集中在 `_hitFeel()`：頓幀（`_hitStop` + `tweens.timeScale=0`）、閃白、擠壓、衝擊星、重擊音。

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
