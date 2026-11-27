# 烤肉遊戲 — Claude 工作指引

## 專案架構
- 單一 HTML 檔：`index.html`（7000+ 行，CRLF 換行；有好幾個 `<script>` 區塊：圖片資料、遊戲本體、大廳 Lobby）
- 遊戲引擎：Phaser 3.60.0（WebGL）；畫面座標 W=960 / H≈680，烤盤範圍 `G={x,y,w,h}`
- Scene 順序：BootScene → SelectScene → TeamScene（賽前設定）→ GameScene
- 大廳 UI：`#lobby-overlay`（HTML + CSS，z-index: 9999，蓋在 Phaser canvas 上方）
  - 等待室 v2（夜市炭烤攤風）：CSS 在 `/* ══ 等待室 v2` 那段；字型 Google Fonts Huninn（中文）+ Bungee（房號、數字）；角色圖直接用 `IMG['char_'+key]`（`Lobby._charImg`）；房號是號碼牌 `#wr-ticket`，複製時蓋「已複製」章、不改房號文字；玩家用座位卡顯示，空位寫「AI 補上」；高度 ≤800px 有緊湊版。背景火星 `.lobby-embers`。
- **首頁 v3（美式後院 BBQ，2026-11）**：背景是 AI 生圖（`draw` 技能 gpt-image-2 → webp base64），存在全域 `TITLE_BG`（不放 `IMG`，不進 Phaser）。`#lobby-overlay::before` 用 `--title-bg`；首頁時 overlay 有 `ld-on`（亮一點），其他畫面變暗。CSS 在 `/* ══ 首頁 v3`（`.ld-*`）。Logo「烤肉求生」+ BBQ SURVIVAL 緞帶、大按鈕（單人 / 開房間 / 加入）、底部角色排排站（`Lobby._initTitle()` 從 CHARS 產生）、規則收進「📖 怎麼玩」彈窗（`Lobby.toggleHow`，Esc 關）。
- **選角 v3**：背景 `IMG.sel_bg`（美式燒烤小屋）；左邊 5×2 角色卡（`card.draw(0/1/2)`）+ 4 張烤盤卡 + 專屬機制一行（`mechTxt`）；右邊介紹看板（大頭像 `pBig`、數值條、S / D 說明、技能/大絕預覽：`prevG`/`ultPrevG` 用 setPosition 搬位置）。方向鍵直接聽 window（最上面的全域 keydown 會 preventDefault 方向鍵，Phaser 收不到 — 以前選角方向鍵一直沒作用）。測試 `uishot.js`、`selflow.js`、`keytest.js`。
- **賽前設定 v2（TeamScene，2026-11）**：背景同選角 `sel_bg`，標題下寫這局烤盤 + 機制；角色頭像卡（自己金框「⭐ 你」，>6 人排兩排；隊伍制是藍 / 待分配 / 紅三塊面板、小卡）；左下木板「比賽設定」（熱源 / 對手數 / 難度 / 道具，右邊一行小說明）；右下 AI 戰術、**場地組合**、⚙ 細調、震動、「▶ 開烤！」（Enter 也行，`_starting` 防連按）。按鈕共用 `this._mkBtn`。測試 `teamui.js`、`teammp.js`（假連線資料）。
- **場地效果一鍵組合**：`FX_PRESETS`（⭐推薦 / 🙂新手輕鬆 / ⚔純推擠 / 🌪大亂鬥）、`bbqFxPreset(id)`、`bbqFxWhich(fx)`（對不上 = 🛠 自訂）。賽前設定點「場地：…⟳」循環；細調面板底下「一鍵套用」。
- **鋁箔盔甲（2026-11 加強）**：`_drawFoilShield`（皺銀護罩 + 掃光 + 閃光點 + 倒數圈，最後 2.5 秒閃，剛反彈放大閃白），畫在 `_foilLayer`（depth 10），頭上「🛡 反彈盔甲 N」；撿到 `_foilBurst`（光圈 + 碎片 + 大字 + 'foil' 音效），反彈 `_foilClang`（叮！彈回去！+ 'clang'），沒了有碎片 + 提示。AI 也有。連線：快照 `fo`，客戶端 `_netFoil`。測試 `foiltest.js`。
- **背景音樂 `BBQMusic`（2026-11）**：獨立 `<script>`（在烤肉動畫 Modal 前），WebAudio 即時合成（不用音檔）。`menu`＝後院鄉村搖擺（G 大調 100 BPM，首頁 / 等待室 / 選角共用）、`game`＝E 小調 148 BPM 迪斯可搖滾；最後 20 秒 `setIntensity(1)` 加速＋琶音。`BBQMusic.play('menu'|'game'|null)`（交叉淡入淡出）；瀏覽器規定第一次點擊/按鍵才出聲（`unlock`）。接點：`Lobby._show`（overlay 沒隱藏才放）、`_initTitle`、SelectScene `_startSelBGM`、GameScene `startBGM()`（create 直接呼叫）、shutdown（`tok` 沒變才回選單曲 → 按 R 重開不會跳歌）、`endGame` 真的結束時先停 1.8 秒再回選單曲。首頁「🎵 音樂：開/關」（`.bgm-btn`，`localStorage bbq_music`）。音量 `VOL=0.22`（比音效小）。看烤肉動畫 `hold(true)`。測試 `musictest.js`（含 `_render` 離線算音量）。
- 連線伺服器：`server.js`（socket.io，部署在 Render Singapore `https://bbq-sg.onrender.com`，舊 Oregon 服務可刪，push 到 master 會自動重新部署；免費方案會休眠）
- 發布：GitHub Pages（https://kshwin.github.io/bbq-survival-game/），push 到 master 約 1 分鐘生效

## 目前的遊戲規則（2026-11 定案）
- **預設模式：三條命計分賽**（場地效果 `respawn`，預設開）。一局 60 秒，或只剩一人時結束；**比分數**。
  - 出局 -1 ❤，3 秒後回場（2 秒無敵，有「⬇ 你在這裡」光柱）。命用完 → **鬼魂**：沿烤盤外圈走、按 A 丟**炭火彈**（1 秒預告、炸飛 + 熟度 +15%、冷卻 6 秒）；炸彈炸下一個人 → 復活一次（1 條命）。鬼魂不能得分。
  - 計分：**往外撞中** +0.5（`_outHit`：推的方向跟「中心→他」同向，或他離中心 <40px；往中間撞不算，跳 `_tip('inhit')`；3 秒內連撞同一人不加分也不傳熱 `e._pHitT`）、擊落 +3、擊落 🎯（熟度 ≥70%）再 +2、**⚔ 復仇 +2**（擊落「上次撞飛你的人」，`_nem` / `_koPair`，`_addScore` 第 8 參數 vic='P' 或 label；頭上「⚔ 仇人」；結算畫面一行冤家/剋星 `_rivalText()`，連線經 board 的 `rv`）、🍶 醬油助攻 +1、活到最後 +3。遠端真人也套往外撞規則，AI 不套。
  - **撲空**（`_dashWhiff`）：衝刺沒撞到人 → 冷卻 +0.5 秒、0.7 秒破綻（`_openUntil`，黃圈），這時被撞 ×1.35；附近 AI 可能趁機衝。AI / 遠端衝刺結束也有破綻。模擬（fire、16 局）：亂衝 18.4 分 / 挑時機 22.6 分（以前亂衝 > 挑時機）。擊落另給：熟度 -30%、大絕 +1。結算畫面會列出每人的算式（`_bd` 分數明細）。
- 撞人傳熱：對方 +10%、自己 -5%。站著不動 1.5 秒會焦（`stillBurn`）。熟度 ≥70% 頭上出現 🎯，AI 會圍攻。
- 道具：冰塊（-42% 熟度、5 秒加速 ×1.9）、鋁箔（10 秒反彈）、大蒜（7 秒身體 ×1.6、推力 ×2、撞得到的距離 54px；**沒有範圍爆發**，一次只撞一個人）、**滾燙醬油**（按 A 往前丟 150px；踩到的人變慢、每秒 +8%、**不能衝刺**；4 秒內出局算丟的人擊落，被別人推下去則丟的人拿助攻）、**胡椒粉**（15 秒內有效；身上有火紅光環；**第一次**撞到人 → 撞擊點 140px 內所有人（含被撞的、不含自己）定住 **3 秒** +8%，胡椒用掉。`_scatterPepper(cx,cy,fromAI,tgt,att)`，測試 `peptest.js`）。
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
- 第 1 關烤盤是 AI 生圖 `IMG.grill_lv1`（webp，`this._grillImg`，depth -1），`drawGrill` 只在圖外加暗；程式畫的舊烤盤留作備援。**2026-11 試玩回饋「畫面太紅」→ 圖已重新調色：烤網下的紅炭改成灰黑炭灰**（只有火焰圈 / 熱區才是紅的）。
- **第 2–4 關烤盤（2026-11，免費版）**：開局用 canvas 程式畫一次（`bbqMakeGrillTex(scene,lk)`，2 倍解析度，texture `grilltex_lvN`，比 G 外擴 `GRILL_TEX_M`=40），當成 `this._grillImg`（depth -1），`drawGrill` 有圖就只壓暗外面。lv2 不鏽鋼拉絲鐵板 + 中間回火色 + 螺絲；lv3 炭灰餘燼 + 歪鐵網 + 一圈石頭；lv4 黑鑄鐵斜紋 + 淡紫粉裂縫 + 直播取景框「● LIVE」。之後人多了可以換成 AI 圖。測試 `grillshot.js`（LVS / T）。
- AI 選角：`bbqPickAi(n,takenKeys)` 隨機洗牌（以前固定 `CHARS.slice` → 永遠五花肉+牛小排）；TeamScene 單人/連線都用，改敵人數只隨機新加的。
- S 技能（`useAbility`，2026-11 平衡）：CD 豬6 牛6 香菇5 玉米6 雞翅6 蝦5 豆腐7 培根6 青椒7 秋刀魚5。擊退一律走 `_skillHit(e,i,nx,ny,F,dur)`（記成玩家打的 → 擊落算你的分、跳過鬼魂、熟度越高飛越遠），圈圈特效 `_skillRing`。牛：5 秒熟度減半 + 110px 震開 100；香菇：瞬移後原地孢子雲 85px 定住 1 秒 +6%；玉米：5 顆散射、命中定身 + 小擊退；雞翅：起飛往前扇形 170px 吹開 130；秋刀魚維持原本強度（使用者：不是太強，只是剛好玩得好）。測試 `skilltest.js`。
- **每張地圖的專屬機制**（2026-11，`LEVELS[i].mech` 一行說明；`shrinkMax` 每張自己的剝落上限）：
  - lv1 家庭烤肉架：外圈剝落。
  - lv2 鐵板燒：**中心燒穿**（`core:{start,first,step,gap,max}`，不剝落）：12 秒後中間破洞 60 → 每 8 秒 +22，最大 170；變大前 2.5 秒預告（下一圈閃焦黑）。全域 `_gCore` 讓 `inGrill()` 把洞算成場外；站在新範圍裡的人掉下去；洞邊 20px +10%/秒。`updateCore` / `drawCore` / `_coreR` / `_corePush`，快照 `co`。往洞的方向撞也算「往外撞」（`_outHit`）。AI 會躲洞、不會背對洞。
  - lv3 露營野火：**野風**（`wind:{str:46}`，翻面頻率降回 1.0）：一直被往箭頭方向吹（不會直接被吹下去，離邊 14px 就停），9–12 秒換風向（至少轉 90°、預告 1.6 秒大箭頭）；順風撞人最多飛遠 30%（`_windMul`）。`updateWind` / `drawWind` / `_windParts`，快照 `wd`。被風吹不算「有在動」。
  - lv4：中心燒穿（最大 100）+ 外圈剝落 72，兩頭夾擊。
  - **能量球、道具偏外圈**（防止大家一直躲中間）：`_outerSpot(margin,minN)`（矩形正規化距離 ≥ minN，避開剝落區和洞）。能量球 80% 外圈；道具 50% 外圈。
  - 連線：等待室「地圖」按鈕（房主 `Lobby.cycleMap()`，`settings.level`），`_launchGame` 用房主選的地圖（以前連線永遠是第 1 張）。
  - 測試：`coretest.js`、`windtest.js`、`mpcore.js`（連線同步洞 / 風）、`mpmap.js`（等待室選地圖）。
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
- **連線品質（2026-11 試玩「好卡、我角色很難動」）**：
  - GameScene 改成固定步長：`update()` 累積時間、每 1/60 秒跑一次 `_step()`（最多補 4 步）。以前邏輯是「每幀」（`e.x+=e.vx`），房主電腦慢（24fps）時遠端玩家只剩一半速度、客戶端一直被拉回去；144Hz 螢幕的 AI 也會變快。
  - 房主分頁被切走 / 最小化時 requestAnimationFrame 會停 → 整局凍住。`_netKeepAlive()` 用 Worker 計時器（33ms）代跑 `sys.step`（250ms 內有真的畫面就不代跑，避免跑兩次）。
  - 客戶端輸入帶序號 `q`；房主快照回傳 `q`（最後收到的輸入）+ `qa`（收到後過了幾秒），客戶端用歷史位置比對再平滑修正（誤差 >110 才瞬移）。以前直接往「舊的」房主位置拉 → 一直被拉回。
  - 穩定玩家 id：`window.MP.myId` 只在第一次連線設定，送 `pid` 給伺服器；伺服器轉送 input 用 pid（以前重連後 socket.id 換掉，房主就不理你的按鍵）。房主比賽中斷線等 10 秒（`room._hostLeftT`）才換房主。
  - `_netStatus()`：斷線或 1.5 秒沒收到快照就顯示警告。連線模式開場有按鍵說明橫幅（`_banner(...,true)` 第 3 參數 = 只在本機顯示，不廣播）。
  - 測試：`lagtest.js`（LAG=毫秒，`mklag.py` 產生延遲伺服器 `lagserver.js`）、`nettest2.js`（重連 + 房主分頁隱藏）、`nettest3.js`（Phaser loop 睡著）。
  - 建議 Render 服務開在 Singapore 區（台灣延遲比 Oregon 低很多；區域不能改，要新建服務再改 `SERVER_URL`）。
- **斷線重連**：socket.io 每次重連都會再觸發 `connect`。`Lobby._connectSocket` 只在第一次連上時執行動作，之後重連走 `_rejoin()` → 伺服器 `rejoin_room` 回到同一個房號（房間不見了就用同一個房號重建，房主保留設定）。房間沒人時保留 3 分鐘（`room._delT`）才刪。以前每次重連都重新「建立房間」→ 房號一直變、朋友找不到房間。測試：`rejointest.js`（會自己開關本機伺服器）。
- Render 每次 push 都會重開伺服器（記憶體裡的房間全清）：建議在 Render 設 Build Filters 只看 `server.js` / `package.json`。
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
