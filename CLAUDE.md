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
  - 計分：**往外撞中** +0.5（`_outHit`：推的方向跟「中心→他」同向，或他離中心 <40px；往中間撞不算，跳 `_tip('inhit')`；3 秒內連撞同一人不加分也不傳熱 `e._pHitT`）、擊落 +3、擊落 🎯（熟度 ≥70%）再 +2、**⚔ 復仇 +2**（擊落「上次撞飛你的人」，`_nem` / `_koPair`，`_addScore` 第 8 參數 vic='P' 或 label；頭上「⚔ 仇人」；結算畫面一行冤家/剋星 `_rivalText()`，連線經 board 的 `rv`）、🍶 醬油助攻 +1、活到最後 +3。遠端真人也套往外撞規則，AI 不套。
  - **撲空**（`_dashWhiff`）：衝刺沒撞到人 → 冷卻 +0.5 秒、0.7 秒破綻（`_openUntil`，黃圈），這時被撞 ×1.35；附近 AI 可能趁機衝。AI / 遠端衝刺結束也有破綻。模擬（fire、16 局）：亂衝 18.4 分 / 挑時機 22.6 分（以前亂衝 > 挑時機）。擊落另給：熟度 -30%、大絕 +1。結算畫面會列出每人的算式（`_bd` 分數明細）。
- 撞人傳熱：對方 +10%、自己 -5%。站著不動 1.5 秒會焦（`stillBurn`）。熟度 ≥70% 頭上出現 🎯，AI 會圍攻。
- 道具：冰塊（-42% 熟度、加速）、鋁箔（10 秒反彈）、大蒜（7 秒身體 ×1.6、推力 ×2、撞得到的距離 54px；**沒有範圍爆發**，一次只撞一個人）、**滾燙醬油**（按 A 往前丟 150px；踩到的人變慢、每秒 +8%、**不能衝刺**；4 秒內出局算丟的人擊落，被別人推下去則丟的人拿助攻）、**胡椒粉**（15 秒；身上有火紅光環；撞到人 → **只有被撞的那個人**打噴嚏定住 1 秒 +8%，胡椒煙只是特效）。
- 大絕：開局 0 格（勾「⚡ 開局送一發大絕」`fx.ultStart` 則開局滿格，預設關），能量球每 7 秒一顆，集 3 格按 D。吃到能量球 → 球飛向左上能量條（`_ultFly`），旁邊跳說明（`_ultCallout`）；滿格時能量條閃、「◀ 按 D 放大絕！」、頭上 D 轉盤發光（`_ultHudTick`）。**AI 也會放大絕**：搶到球 +1，集滿 → 紫色光環；附近有人就紅圈蓄力 0.9 秒 → 半徑 170 範圍爆炸（`_aiUltTick` / `_aiUltStart` / `_aiUltBoom` / `_drawAiUlt`，快照 `uw`）。遠端真人按 D 也是放這招。
- 弱大絕加強（`_ultKnockMul`，只影響玩家衝刺撞飛距離）：豆腐 → 附近的人凍脆 6 秒（×2.5，冰藍圈）；培根 → 全場煙燻 9 秒（×1.6）；香菇 → 霧裡 1 秒就定身、霧裡 ×1.6；辣椒 → 踩到辣椒素嗆到彈開 85px + 3 秒 ×1.6（紫圈）。
- 廚師翻面（傾斜）：預告 1.5 秒（整片箭頭）→ 翻的瞬間所有人急停、衝刺中斷 → 3 秒一直往下滑（130px/秒）。按反方向撐住（快的角色能慢慢爬上去），橫向只剩 35% 速度；衝刺不受影響。`_tiltF` / `_tiltVel` / `_tiltVisual` / `_drawTilt`；快照 `ti` 同步給客戶端。
- 叉子（廚師）完全不震畫面。
- 胡椒辣到眼睛（AI 拿胡椒撞你 → `pepperVision` 5 秒）：畫面是平滑暗角（`pepVig` 放射漸層圖 + 外圈整片蓋暗）。以前是 20 圈粗黑線，看起來像一堆同心圓。
- 外圈剝落後邊緣很燙：`drawShrinkRing` 在內側畫 22px 橘紅發燙帶；場地效果說明、開始剝落的橫幅都有寫「每秒 +10%」。
- 測試小技巧：Playwright 可以用 `headless: true` + `--use-gl=swiftshader` 跑（不會跳出視窗），截圖判斷不準時用 PIL 讀像素比較。
- 熱源模式（賽前設定）：🔥 火焰圈 `fire`（預設）/ 🎯 中心熱區 `ring` / **👥 人多變熱 `crowd`**：3 人（局裡少於 4 人時 2 人）擠在 130px 內超過 1 秒 → 那裡預告 1.2 秒 → 熱區燒 4.5 秒（半徑約 120，每秒 +13%，最後 20 秒 ×1.35）；9–13 秒沒冒就隨機冒一個；最多 3 個，不會冒在冷卻圈上。AI 會躲。`_updateCrowdHeat` / `_crowdHeat` / `_drawCrowdZones`（邊框在 `_drawFireRims`），快照 `cz`。被定住的 AI 不會被加熱（舊行為：定住時整段 AI 更新都跳過）。
- 烤盤破洞：半徑 32–46（圓形判定 0.8r）；預告 2.2 秒畫面是烤焦（橘紅 → 焦黑、裂痕、冒煙），破了是邊緣還在燒的焦黑洞（`_drawHole`，房主客戶端共用，快照 `ho` 帶狀態+進度）。`checkEnemyFall(e,i,natural,force)`：force=掉進洞（以前 AI 永遠不會掉進洞）。
- 加熱來源（玩家）：火焰圈 +26%/秒、中心熱區、待著會熟 +0.7%/秒、站著不動、被撞 +10%、滾燙醬油 +8%/秒、炭火彈 +15%、叉子 +20%、胡椒噴嚏 +8%、被推進火裡 +15%、火柱 +20%、AI 大絕 +10%、**外圈剝落邊緣 22px 內 +10%/秒**（以前 30px 內 +35%、10px 內再 +24%，又沒提示）、**撞人噴的小油漬聚 5 塊以上變熱區 +8%/秒**。**玩家加熱一律走 `_hAdd(來源,量,上限,quiet)`**（記在 `_heatLog`，每條命重算；復活記「復活時就有 30」）。熟度數字旁顯示前兩名（`heatSrcTxt`），被烤熟的出局原因列前三名（`_heatSummary`）；每秒升超過 3% 時腳下顯示原因（`_heatWhy`）。站著不動的判定看「實際位移 > 25px/秒 或有按方向鍵」（以前只看自己的速度，被推飛、撐住傾斜都算不動）。身上起火 = 站在火焰圈 / 中心高溫區（`_updateBurn`）。火焰預告 1.5–2 秒（`f.warnMax`）；火圈邊框畫在角色上面（`_drawFireRims`：預告 = 虛線圈 + 倒數弧，燒起來 = 實線框，房主畫在 burnLayer、客戶端畫在 _netLayer）。
- 畫面震動：所有震動都進 `_addTrauma()`（創傷值，最大 12px），撞人只在 `_hitFeel()` 算一次；跟玩家無關的事不震。賽前設定有「強/中/關」（`localStorage bbq_shake`）。
- 開場 3-2-1 倒數 `_countdown()`：倒數時遊戲暫停（tween 也停），所以用 requestAnimationFrame + 真實時間做動畫；目前只在第一局（看完說明卡後）出現。
- **隨機事件導演**（`_dirTick` / `_dirBusy`，2026-11）：各事件自己的計時器都停用（1e9），改由導演一次只放一個：場上有事件就等，結束後隔 6–9 秒（最後 20 秒 4–6 秒）再抽；第一個在 8–10 秒。權重：破洞 3、翻面 2、冰塊空投 2、叉子 2、火柱 1、竹簽/醬油/檸檬各 1（只抽有開的、不連續重複）。以前一分鐘約 20 個事件疊在一起，現在約 5 個。預設關：灑醬油、檸檬汁、竹簽、噴油（隨機油漬也歸 `oilFire`）；舊存檔沒有 `_ev2` 會遷移一次。
- 外圈剝落：全域 `_gPad`（= shrinkPad，客戶端從快照設）讓 `inGrill()` 跟著縮，掉出去的判定就是剝落後的邊；鍵盤頂牆夾在縮小的邊；AI 走到縮小的邊只擋往外的速度（傾斜、被撞照樣掉）。
- 玉米大絕（加特林）：5 秒、每 0.08 秒一顆（約 60 顆），2/3 瞄最近的人 ±20°；射中彈飛 95×`_ultKnockMul`、定住 +0.45（上限 1.6）、+3%；移動速度 ×0.75。測試命中約 11–13 次（舊版約 4 次）。
- 第 1 關烤盤是 AI 生圖 `IMG.grill_lv1`（webp，`this._grillImg`，depth -1），`drawGrill` 只在圖外加暗；程式畫的舊烤盤留作備援。
- 尚未決定：檸檬汁（變快）跟檸檬雨（炸飛、變慢）性格矛盾，可能統一成「速度」道具；每局都要倒數嗎；模擬中「亂衝」略強於「挑時機」。

## 重要函式位置（用 Grep 找）
- 三條命 / 鬼魂：`_respawnPlayer`、`_becomeGhostPlayer`、`_ghostPlayerTick`、`_ghostEnemyTick`、`_onEnemyOut`、`_bombCredit`、`_checkLivesEnd`、`_throwBomb` / `_bombBoom`
- 計分：`_addScore(who,n,x,y,ko,vh,raw)`（who=null 是玩家）、`_finalScores`、`_soyCredit`、`_showResult`
- 頭上標記（🎯、❤、💨、🍶黏住、胡椒光環）：`_updateLivesFx`；`endGame(win,final)`：三條命模式只有 `final=true` 才真的結束

## 工作流程
- 改完、測過就 commit + push 到 master（不用再問）；只提交相關檔案（不要提交 `assets/* - 複製.png`、`docs/superpowers/` 草稿、`.superpowers/`、`.m4a`）。
- 修改方式：用 Python 腳本把整個檔案讀成字串、`\r\n`→`\n` 後做「必須剛好出現一次」的取代，再寫回 CRLF。
- 測試工具放在 `C:\Users\User\AppData\Local\Temp\bbqtools\`（暫存資料夾，可能被清掉）：`checkall.py`（每個 script 區塊語法檢查）、`loadcheck.js`、`sim3.js` / `simdbg.js`（快轉模擬，三種打法 passive/aggro/smart）、`an3.py`（模擬統計）、`mptest.js`（雙視窗連線測試，要先開本機 `server.js`）、`livestest.js`、`soytest.js`、`bdtest.js`、`shaketest.js`、`cdtest.js`、`tilttest.js`（胡椒/大蒜/叉子/傾斜/大絕 UI）、`mptilt.js`（mptest + 傾斜 / 遠端大絕 / 破洞同步）、`aiulttest.js`（AI 大絕、外圈加熱、破洞、豆腐凍脆）、`heatlogtest.js`（加熱記帳、站著不動判定、烤熟原因）、`crowdtest.js`（人多變熱）、`firerimtest.js`（火圈預告 / 邊框）。本機伺服器要在 `C:\Users\User\AppData\Local\Temp\bbqsrv\` 跑（那裡才有 node_modules；先把 `server.js` 複製過去）。執行：`PW_PATH="C:/Users/User/AppData/Roaming/npm/node_modules/playwright" node xxx.js "D:/烤肉遊戲/index.html" <截圖資料夾>`。
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
