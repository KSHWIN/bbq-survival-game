# 伺服器 + 大廳 UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 實作 Socket.io 多人連線伺服器、房間系統、大廳 UI（選角 + 隊伍 + 設定），讓朋友可以用 6 碼房號加入同一場遊戲。

**Architecture:** `server.js` 用 Socket.io 管理房間狀態；`index.html` 在 Phaser canvas 前加入純 HTML/CSS 大廳 overlay；GameScene 加入 `initMultiplayer()`、`syncToServer(dt)` 與 `renderOtherPlayers()` 三個方法；主機負責執行 AI 並廣播 AI 狀態。

**Tech Stack:** Node.js + Socket.io 4.x（後端）、Socket.io client CDN（前端）、Render.com 免費方案（部署）、Phaser 3.60.0（既有）。

---

## 檔案結構

| 檔案 | 說明 |
|------|------|
| `server.js`（新建） | Socket.io 伺服器，房間管理，狀態廣播 |
| `package.json`（新建） | Node.js 依賴與 Render 啟動指令 |
| `index.html`（修改 × 5 處） | 1) Socket.io CDN、2) 大廳 CSS、3) 大廳 HTML div、4) 大廳 JS、5) GameScene 多人邏輯 |

---

### Task 1：建立 `package.json`

**Files:**
- Create: `package.json`

- [ ] **Step 1：建立 package.json**

```json
{
  "name": "bbq-survival-game",
  "version": "1.0.0",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "socket.io": "^4.7.5"
  }
}
```

- [ ] **Step 2：commit**

```bash
git add package.json
git commit -m "chore: add package.json for Socket.io server"
```

---

### Task 2：建立 `server.js`

**Files:**
- Create: `server.js`

- [ ] **Step 1：建立完整 server.js**

```js
const http = require('http');
const { Server } = require('socket.io');

const PORT = process.env.PORT || 3000;
const server = http.createServer((req, res) => {
  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.end('BBQ Survival Game Server');
});

const io = new Server(server, {
  cors: { origin: '*', methods: ['GET','POST'] }
});

// rooms: { [code]: { host, players: {[id]: {nickname, charKey, team, ready}}, settings, state } }
const rooms = {};

function genCode() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let code = '';
  for (let i = 0; i < 6; i++) code += chars[Math.floor(Math.random() * chars.length)];
  return rooms[code] ? genCode() : code;
}

io.on('connection', (socket) => {
  let myRoom = null;

  socket.on('create_room', ({ nickname, charKey }, cb) => {
    const code = genCode();
    rooms[code] = {
      host: socket.id,
      players: {
        [socket.id]: { nickname, charKey, team: 'red', ready: false }
      },
      settings: { maxPlayers: 4, gameMode: 'individual', ultFromStart: false },
      state: 'waiting',
      gameState: {}
    };
    myRoom = code;
    socket.join(code);
    cb({ ok: true, code, isHost: true, settings: rooms[code].settings });
    io.to(code).emit('player_list', buildPlayerList(rooms[code]));
  });

  socket.on('join_room', ({ code, nickname, charKey }, cb) => {
    const room = rooms[code];
    if (!room) return cb({ ok: false, err: '找不到此房間' });
    if (room.state !== 'waiting') return cb({ ok: false, err: '遊戲已開始' });
    const realCount = Object.values(room.players).length;
    if (realCount >= room.settings.maxPlayers) return cb({ ok: false, err: '房間已滿' });
    room.players[socket.id] = { nickname, charKey, team: 'blue', ready: false };
    myRoom = code;
    socket.join(code);
    cb({ ok: true, code, isHost: false, settings: room.settings, players: buildPlayerList(room) });
    io.to(code).emit('player_list', buildPlayerList(room));
  });

  socket.on('update_char', ({ charKey }) => {
    const room = rooms[myRoom]; if (!room) return;
    if (room.players[socket.id]) room.players[socket.id].charKey = charKey;
    io.to(myRoom).emit('player_list', buildPlayerList(room));
  });

  socket.on('update_team', ({ team }) => {
    const room = rooms[myRoom]; if (!room) return;
    if (room.players[socket.id]) room.players[socket.id].team = team;
    io.to(myRoom).emit('player_list', buildPlayerList(room));
  });

  socket.on('room_settings', (settings) => {
    const room = rooms[myRoom]; if (!room) return;
    if (room.host !== socket.id) return;
    room.settings = { ...room.settings, ...settings };
    io.to(myRoom).emit('settings_update', room.settings);
  });

  socket.on('start_game', () => {
    const room = rooms[myRoom]; if (!room) return;
    if (room.host !== socket.id) return;
    room.state = 'playing';
    io.to(myRoom).emit('game_start', { settings: room.settings, players: buildPlayerList(room) });
  });

  socket.on('player_update', (snapshot) => {
    const room = rooms[myRoom]; if (!room) return;
    if (!room.gameState) room.gameState = {};
    room.gameState[socket.id] = { ...snapshot, id: socket.id };
    socket.to(myRoom).emit('game_state', room.gameState);
  });

  socket.on('game_event', (evt) => {
    const room = rooms[myRoom]; if (!room) return;
    socket.to(myRoom).emit('game_event', { ...evt, from: socket.id });
  });

  socket.on('disconnect', () => {
    const room = rooms[myRoom]; if (!room) return;
    delete room.players[socket.id];
    if (room.gameState) delete room.gameState[socket.id];
    io.to(myRoom).emit('player_disconnected', { id: socket.id });
    // 若主機斷線，轉移給下一位
    if (room.host === socket.id) {
      const remaining = Object.keys(room.players);
      if (remaining.length > 0) {
        room.host = remaining[0];
        io.to(myRoom).emit('host_changed', { newHost: room.host });
      } else {
        delete rooms[myRoom];
      }
    }
    io.to(myRoom).emit('player_list', buildPlayerList(room));
  });
});

function buildPlayerList(room) {
  return Object.entries(room.players).map(([id, p]) => ({
    id, nickname: p.nickname, charKey: p.charKey, team: p.team,
    isHost: id === room.host
  }));
}

server.listen(PORT, () => console.log(`BBQ Server listening on port ${PORT}`));
```

- [ ] **Step 2：本機測試**

```bash
npm install
node server.js
```

預期輸出：`BBQ Server listening on port 3000`
用 Ctrl+C 停止。

- [ ] **Step 3：commit**

```bash
git add server.js
git commit -m "feat: add Socket.io server with room management"
```

---

### Task 3：Render.com 部署設定

**Files:**
- Create: `.gitignore`（若不存在）
- Modify: `package.json`（已存在，確認 start 指令）

- [ ] **Step 1：確認 .gitignore 排除 node_modules**

新建或確認 `.gitignore` 包含：
```
node_modules/
```

- [ ] **Step 2：commit 並 push**

```bash
git add .gitignore
git commit -m "chore: add .gitignore"
git push origin master
```

- [ ] **Step 3：在 Render.com 建立 Web Service（手動操作）**

1. 前往 https://render.com → New → Web Service
2. 連結 GitHub repo（`kshwin/bbq-survival-game`）
3. 設定：
   - **Name**: `bbq-survival-game`
   - **Build Command**: `npm install`
   - **Start Command**: `node server.js`
   - **Plan**: Free
4. 點 Create Web Service，等待部署完成
5. 記下服務 URL，格式為 `https://bbq-survival-game-xxxx.onrender.com`（後續 Step 要填入 index.html）

---

### Task 4：index.html — 加入 Socket.io CDN + 大廳 CSS

**Files:**
- Modify: `index.html`（在 `<head>` 區域加入 Socket.io client 與 CSS）

- [ ] **Step 1：找到 `<head>` 裡的 `<script>` 區塊**

搜尋（約第 1–10 行）：
```
<script src="https://cdn.jsdelivr.net/npm/phaser@3.60.0/dist/phaser.min.js"></script>
```

在這行**之前**插入 Socket.io CDN：
```html
<script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
```

- [ ] **Step 2：在 `<style>` 區塊末尾（`</style>` 之前）加入大廳 CSS**

找到 `</style>`，在它之前插入：

```css
/* ── Lobby Overlay ─────────────────────────────────── */
#lobby-overlay {
  position: fixed; inset: 0; z-index: 9999;
  background: linear-gradient(135deg, #1a0500 0%, #330800 50%, #0d0200 100%);
  display: flex; align-items: center; justify-content: center;
  font-family: 'Microsoft JhengHei', 'Noto Sans TC', sans-serif;
  color: #f0d9b0;
}
#lobby-overlay.hidden { display: none; }
.lobby-card {
  background: rgba(30,8,0,0.95);
  border: 2px solid #ff6600;
  border-radius: 16px;
  padding: 32px 40px;
  min-width: 440px;
  max-width: 680px;
  width: 90%;
  box-shadow: 0 0 40px rgba(255,102,0,0.25);
}
.lobby-title {
  font-size: 2rem; font-weight: 700;
  color: #ffcc44; text-align: center;
  margin-bottom: 8px;
}
.lobby-sub { font-size: 0.88rem; color: #cc9966; text-align: center; margin-bottom: 28px; }
.lobby-btn {
  display: block; width: 100%;
  padding: 14px; margin-bottom: 12px;
  background: rgba(255,102,0,0.15);
  border: 2px solid #ff6600;
  border-radius: 10px;
  color: #ffcc44; font-size: 1.1rem; font-weight: 700;
  cursor: pointer; transition: background 0.2s;
}
.lobby-btn:hover { background: rgba(255,102,0,0.35); }
.lobby-btn.secondary { border-color: #886644; color: #cc9966; font-size: 0.95rem; font-weight: 400; }
.lobby-input {
  width: 100%; padding: 10px 14px; margin-bottom: 12px;
  background: rgba(0,0,0,0.5); border: 1px solid #664422;
  border-radius: 8px; color: #f0d9b0; font-size: 1rem;
  outline: none;
}
.lobby-input:focus { border-color: #ff6600; }
.lobby-input::placeholder { color: #664422; }
.lobby-label { font-size: 0.85rem; color: #cc9966; margin-bottom: 6px; display: block; }
.lobby-error { color: #ff6666; font-size: 0.88rem; margin-bottom: 10px; min-height: 20px; }
.lobby-section { margin-bottom: 20px; }
/* Waiting Room */
.wr-code {
  font-size: 2.2rem; font-weight: 900; color: #ffcc44; text-align: center;
  letter-spacing: 0.18em; background: rgba(0,0,0,0.4);
  border: 1px dashed #ff6600; border-radius: 8px;
  padding: 10px; margin-bottom: 6px; cursor: pointer;
}
.wr-code-hint { font-size: 0.78rem; color: #886644; text-align: center; margin-bottom: 16px; }
.wr-players { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
.wr-player {
  display: flex; align-items: center; gap: 6px;
  background: rgba(255,102,0,0.1); border: 1px solid #664422;
  border-radius: 8px; padding: 6px 10px; font-size: 0.88rem;
}
.wr-player .team-dot {
  width: 10px; height: 10px; border-radius: 50%;
}
.team-dot.red { background: #ff4444; }
.team-dot.blue { background: #4488ff; }
.wr-chars { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 16px; }
.wr-char-btn {
  padding: 6px 10px; border-radius: 6px;
  border: 2px solid #664422; background: rgba(0,0,0,0.4);
  color: #ddc499; font-size: 0.82rem; cursor: pointer; transition: all 0.15s;
}
.wr-char-btn.selected { border-color: #ff6600; background: rgba(255,102,0,0.2); color: #ffcc44; }
.wr-char-btn:hover { border-color: #aa6633; }
.wr-settings { border-top: 1px solid #3a1a00; padding-top: 14px; }
.wr-setting-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.wr-setting-label { font-size: 0.85rem; color: #cc9966; flex: 1; }
.wr-setting-val { font-size: 0.85rem; color: #ffcc44; min-width: 40px; text-align: right; }
.wr-toggle {
  background: rgba(0,0,0,0.4); border: 1px solid #664422; border-radius: 6px;
  padding: 4px 10px; color: #ddc499; font-size: 0.82rem; cursor: pointer;
}
.wr-toggle.on { border-color: #ff6600; color: #ffcc44; background: rgba(255,102,0,0.15); }
.team-toggle {
  padding: 4px 10px; border-radius: 6px; border: 1px solid #664422;
  font-size: 0.82rem; cursor: pointer;
}
.team-toggle.red { background: rgba(255,68,68,0.2); color: #ff8888; border-color: #ff4444; }
.team-toggle.blue { background: rgba(68,136,255,0.2); color: #88aaff; border-color: #4488ff; }
```

- [ ] **Step 3：驗證頁面能正常載入（無 console 錯誤）**

- [ ] **Step 4：commit**

```bash
git add index.html
git commit -m "feat: add Socket.io CDN and lobby CSS"
```

---

### Task 5：index.html — 加入大廳 HTML div

**Files:**
- Modify: `index.html`（在 `<body>` 開頭加入 overlay div）

- [ ] **Step 1：找到 `<body>` 標籤**

在 `<body>` 下方、`<canvas>` 或 Phaser 的容器之前，插入大廳 HTML：

```html
<!-- ── Lobby Overlay ─────────────────────────────── -->
<div id="lobby-overlay">
  <!-- Screen: Landing -->
  <div id="screen-landing" class="lobby-card">
    <div class="lobby-title">🥩 烤肉求生</div>
    <div class="lobby-sub">選擇遊戲模式</div>
    <button class="lobby-btn" onclick="Lobby.showSingle()">🎮 單人遊玩</button>
    <button class="lobby-btn" onclick="Lobby.showCreate()">🏠 開房間（主機）</button>
    <button class="lobby-btn secondary" onclick="Lobby.showJoin()">🚪 加入房間</button>
  </div>

  <!-- Screen: Create Room -->
  <div id="screen-create" class="lobby-card" style="display:none">
    <div class="lobby-title">開房間</div>
    <label class="lobby-label">你的暱稱</label>
    <input class="lobby-input" id="create-nickname" placeholder="輸入暱稱" maxlength="12">
    <label class="lobby-label">選擇角色</label>
    <div class="wr-chars" id="create-char-list"></div>
    <div class="lobby-error" id="create-error"></div>
    <button class="lobby-btn" onclick="Lobby.createRoom()">建立房間</button>
    <button class="lobby-btn secondary" onclick="Lobby.showLanding()">← 返回</button>
  </div>

  <!-- Screen: Join Room -->
  <div id="screen-join" class="lobby-card" style="display:none">
    <div class="lobby-title">加入房間</div>
    <label class="lobby-label">房間代碼（6碼）</label>
    <input class="lobby-input" id="join-code" placeholder="例：BBQ42K" maxlength="6"
      style="text-transform:uppercase;letter-spacing:0.15em;font-size:1.3rem">
    <label class="lobby-label">你的暱稱</label>
    <input class="lobby-input" id="join-nickname" placeholder="輸入暱稱" maxlength="12">
    <label class="lobby-label">選擇角色</label>
    <div class="wr-chars" id="join-char-list"></div>
    <div class="lobby-error" id="join-error"></div>
    <button class="lobby-btn" onclick="Lobby.joinRoom()">加入房間</button>
    <button class="lobby-btn secondary" onclick="Lobby.showLanding()">← 返回</button>
  </div>

  <!-- Screen: Waiting Room -->
  <div id="screen-waiting" class="lobby-card" style="display:none;max-width:600px">
    <div class="lobby-title">等待室</div>
    <div class="wr-code" id="wr-room-code" title="點擊複製" onclick="Lobby.copyCode()">------</div>
    <div class="wr-code-hint">點擊房間代碼可複製，分享給朋友</div>

    <label class="lobby-label">玩家列表</label>
    <div class="wr-players" id="wr-player-list"></div>

    <label class="lobby-label">選擇角色</label>
    <div class="wr-chars" id="wr-char-list"></div>

    <!-- 隊伍切換（只有隊伍制才顯示）-->
    <div id="wr-team-row" style="display:none;margin-bottom:14px">
      <label class="lobby-label">我的隊伍</label>
      <button class="team-toggle red" id="wr-team-btn" onclick="Lobby.toggleTeam()">紅隊</button>
    </div>

    <!-- 房間設定（主機才可操作）-->
    <div class="wr-settings" id="wr-settings">
      <label class="lobby-label">🔧 房間設定</label>
      <div class="wr-setting-row">
        <span class="wr-setting-label">人數上限（AI 補足空位）</span>
        <button class="wr-toggle" onclick="Lobby.adjMax(-1)">−</button>
        <span class="wr-setting-val" id="wr-max-val">4</span>
        <button class="wr-toggle" onclick="Lobby.adjMax(+1)">+</button>
      </div>
      <div class="wr-setting-row">
        <span class="wr-setting-label">遊戲模式</span>
        <button class="wr-toggle" id="wr-mode-btn" onclick="Lobby.toggleMode()">個人制</button>
      </div>
      <div class="wr-setting-row">
        <span class="wr-setting-label">大絕招（一開始就可用）</span>
        <button class="wr-toggle" id="wr-ult-btn" onclick="Lobby.toggleUlt()">關</button>
      </div>
    </div>

    <div class="lobby-error" id="wr-error"></div>
    <button class="lobby-btn" id="wr-start-btn" onclick="Lobby.startGame()" style="display:none">▶ 開始遊戲（主機）</button>
    <div id="wr-waiting-msg" style="text-align:center;color:#886644;font-size:0.9rem">等待主機開始遊戲…</div>
  </div>
</div>
<!-- ── / Lobby Overlay ─────────────────────────────── -->
```

- [ ] **Step 2：驗證 HTML 結構（瀏覽器能顯示 Landing 畫面）**

- [ ] **Step 3：commit**

```bash
git add index.html
git commit -m "feat: add lobby HTML overlay"
```

---

### Task 6：index.html — 大廳 JavaScript（Lobby 物件）

**Files:**
- Modify: `index.html`（在 `</body>` 之前加入 Lobby JS）

**注意：** `SERVER_URL` 要替換成 Task 3 取得的 Render.com URL。

- [ ] **Step 1：在 `</body>` 之前插入大廳 JS**

```html
<script>
// ── Lobby ──────────────────────────────────────────
const SERVER_URL = 'https://bbq-survival-game-xxxx.onrender.com'; // 替換為真實 URL

// 全局多人狀態（GameScene 會讀取）
window.MP = {
  enabled: false,
  socket: null,
  roomCode: null,
  isHost: false,
  myId: null,
  settings: { maxPlayers: 4, gameMode: 'individual', ultFromStart: false },
  players: [],           // 等待室玩家列表
  myCharKey: 'bacon',
  myTeam: 'red',
  myNickname: '',
};

const Lobby = {
  _socket: null,
  _myTeam: 'red',
  _myChar: 'bacon',
  _settings: { maxPlayers: 4, gameMode: 'individual', ultFromStart: false },
  _isHost: false,
  _roomCode: '',

  _show(id) {
    ['screen-landing','screen-create','screen-join','screen-waiting'].forEach(s => {
      document.getElementById(s).style.display = s === id ? '' : 'none';
    });
  },

  showLanding() { this._show('screen-landing'); },
  showCreate()  {
    this._buildCharList('create-char-list', this._myChar, (k) => {
      this._myChar = k;
      if (this._socket) this._socket.emit('update_char', { charKey: k });
    });
    this._show('screen-create');
  },
  showJoin() {
    this._buildCharList('join-char-list', this._myChar, (k) => {
      this._myChar = k;
      if (this._socket) this._socket.emit('update_char', { charKey: k });
    });
    this._show('screen-join');
  },

  showSingle() {
    document.getElementById('lobby-overlay').classList.add('hidden');
    // 直接以預設設定啟動 Phaser（已在 window.onload 中等待 overlay hidden）
  },

  _buildCharList(containerId, selected, onSelect) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    // CHARS 是 Phaser 遊戲裡定義的全局角色列表，這裡用備用列表防止 CHARS 尚未載入
    const charKeys = typeof CHARS !== 'undefined'
      ? CHARS.map(c => ({ key: c.key, name: c.name }))
      : [{key:'bacon',name:'培根'},{key:'beef',name:'牛小排'},{key:'pork',name:'五花肉'},
         {key:'wing',name:'雞翅'},{key:'shrimp',name:'蝦子'},{key:'pepper',name:'青椒'},
         {key:'mushroom',name:'香菇'},{key:'corn',name:'玉米'},{key:'saury',name:'秋刀魚'},{key:'tofu',name:'豆腐'}];
    charKeys.forEach(({ key, name }) => {
      const btn = document.createElement('button');
      btn.className = 'wr-char-btn' + (key === selected ? ' selected' : '');
      btn.textContent = name;
      btn.onclick = () => {
        container.querySelectorAll('.wr-char-btn').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        onSelect(key);
      };
      container.appendChild(btn);
    });
  },

  _buildWrCharList() {
    this._buildCharList('wr-char-list', this._myChar, (k) => {
      this._myChar = k;
      window.MP.myCharKey = k;
      if (this._socket) this._socket.emit('update_char', { charKey: k });
    });
  },

  _connectSocket(cb) {
    if (this._socket && this._socket.connected) return cb(this._socket);
    const s = io(SERVER_URL);
    s.on('connect', () => { this._socket = s; window.MP.socket = s; window.MP.myId = s.id; cb(s); });
    s.on('connect_error', () => { document.getElementById('create-error').textContent = '無法連線到伺服器'; });
  },

  createRoom() {
    const nickname = document.getElementById('create-nickname').value.trim();
    if (!nickname) { document.getElementById('create-error').textContent = '請輸入暱稱'; return; }
    this._connectSocket(s => {
      s.emit('create_room', { nickname, charKey: this._myChar }, (res) => {
        if (!res.ok) { document.getElementById('create-error').textContent = res.err; return; }
        this._roomCode = res.code;
        this._isHost = true;
        this._settings = { ...res.settings };
        window.MP.roomCode = res.code;
        window.MP.isHost = true;
        window.MP.myNickname = nickname;
        window.MP.myCharKey = this._myChar;
        window.MP.myTeam = 'red';
        this._setupSocketListeners(s);
        this._showWaitingRoom();
      });
    });
  },

  joinRoom() {
    const code = document.getElementById('join-code').value.trim().toUpperCase();
    const nickname = document.getElementById('join-nickname').value.trim();
    if (code.length !== 6) { document.getElementById('join-error').textContent = '請輸入 6 碼房間代碼'; return; }
    if (!nickname) { document.getElementById('join-error').textContent = '請輸入暱稱'; return; }
    this._connectSocket(s => {
      s.emit('join_room', { code, nickname, charKey: this._myChar }, (res) => {
        if (!res.ok) { document.getElementById('join-error').textContent = res.err; return; }
        this._roomCode = res.code;
        this._isHost = false;
        this._settings = { ...res.settings };
        window.MP.roomCode = res.code;
        window.MP.isHost = false;
        window.MP.myNickname = nickname;
        window.MP.myCharKey = this._myChar;
        window.MP.myTeam = 'blue';
        this._setupSocketListeners(s);
        this._updatePlayerList(res.players);
        this._showWaitingRoom();
      });
    });
  },

  _setupSocketListeners(s) {
    s.off('player_list'); s.off('settings_update'); s.off('game_start'); s.off('host_changed');
    s.on('player_list', (players) => { window.MP.players = players; this._updatePlayerList(players); });
    s.on('settings_update', (settings) => { this._settings = { ...settings }; window.MP.settings = settings; this._renderSettings(); });
    s.on('game_start', ({ settings, players }) => {
      window.MP.enabled = true;
      window.MP.settings = settings;
      window.MP.players = players;
      this._launchGame();
    });
    s.on('host_changed', ({ newHost }) => {
      if (newHost === s.id) { this._isHost = true; window.MP.isHost = true; this._renderHostControls(); }
    });
  },

  _showWaitingRoom() {
    document.getElementById('wr-room-code').textContent = this._roomCode;
    this._buildWrCharList();
    this._renderSettings();
    this._renderHostControls();
    this._show('screen-waiting');
  },

  _updatePlayerList(players) {
    const el = document.getElementById('wr-player-list');
    el.innerHTML = players.map(p =>
      `<div class="wr-player">
        <span class="team-dot ${p.team || 'red'}"></span>
        <span>${p.nickname}${p.isHost ? ' 👑' : ''}</span>
        <span style="font-size:0.75rem;color:#886644">${p.charKey || ''}</span>
      </div>`
    ).join('');
  },

  _renderSettings() {
    document.getElementById('wr-max-val').textContent = this._settings.maxPlayers;
    const modeBtn = document.getElementById('wr-mode-btn');
    modeBtn.textContent = this._settings.gameMode === 'team' ? '隊伍制' : '個人制';
    modeBtn.classList.toggle('on', this._settings.gameMode === 'team');
    const ultBtn = document.getElementById('wr-ult-btn');
    ultBtn.textContent = this._settings.ultFromStart ? '開' : '關';
    ultBtn.classList.toggle('on', this._settings.ultFromStart);
    // 顯示/隱藏隊伍切換
    document.getElementById('wr-team-row').style.display =
      this._settings.gameMode === 'team' ? '' : 'none';
  },

  _renderHostControls() {
    const settingsEl = document.getElementById('wr-settings');
    const startBtn = document.getElementById('wr-start-btn');
    const waitMsg = document.getElementById('wr-waiting-msg');
    if (this._isHost) {
      settingsEl.style.opacity = '1'; settingsEl.style.pointerEvents = 'auto';
      startBtn.style.display = ''; waitMsg.style.display = 'none';
    } else {
      settingsEl.style.opacity = '0.5'; settingsEl.style.pointerEvents = 'none';
      startBtn.style.display = 'none'; waitMsg.style.display = '';
    }
  },

  adjMax(delta) {
    if (!this._isHost) return;
    const val = Math.max(1, Math.min(8, this._settings.maxPlayers + delta));
    this._settings.maxPlayers = val;
    window.MP.settings.maxPlayers = val;
    document.getElementById('wr-max-val').textContent = val;
    this._socket.emit('room_settings', this._settings);
  },

  toggleMode() {
    if (!this._isHost) return;
    this._settings.gameMode = this._settings.gameMode === 'team' ? 'individual' : 'team';
    window.MP.settings.gameMode = this._settings.gameMode;
    this._renderSettings();
    this._socket.emit('room_settings', this._settings);
  },

  toggleUlt() {
    if (!this._isHost) return;
    this._settings.ultFromStart = !this._settings.ultFromStart;
    window.MP.settings.ultFromStart = this._settings.ultFromStart;
    this._renderSettings();
    this._socket.emit('room_settings', this._settings);
  },

  toggleTeam() {
    this._myTeam = this._myTeam === 'red' ? 'blue' : 'red';
    window.MP.myTeam = this._myTeam;
    const btn = document.getElementById('wr-team-btn');
    btn.textContent = this._myTeam === 'red' ? '紅隊' : '藍隊';
    btn.className = 'team-toggle ' + this._myTeam;
    if (this._socket) this._socket.emit('update_team', { team: this._myTeam });
  },

  copyCode() {
    navigator.clipboard.writeText(this._roomCode).then(() => {
      document.getElementById('wr-room-code').title = '已複製！';
      setTimeout(() => { document.getElementById('wr-room-code').title = '點擊複製'; }, 1500);
    });
  },

  startGame() {
    if (!this._isHost || !this._socket) return;
    this._socket.emit('start_game');
  },

  _launchGame() {
    document.getElementById('lobby-overlay').classList.add('hidden');
    // Phaser 遊戲已在 window.onload 啟動，這裡觸發 SelectScene → Game 轉場
    const game = window._phaserGame;
    if (!game) return;
    // 找到自己的角色資料
    const myPlayer = window.MP.players.find(p => p.id === window.MP.myId);
    const charKey = myPlayer ? myPlayer.charKey : window.MP.myCharKey;
    const charData = (typeof CHARS !== 'undefined' ? CHARS : []).find(c => c.key === charKey) || (typeof CHARS !== 'undefined' ? CHARS[0] : null);
    game.scene.start('Game', {
      char: charData,
      level: (typeof LEVELS !== 'undefined' ? LEVELS[0] : null),
      enemyCnt: window.MP.settings.maxPlayers - window.MP.players.length,
      aiDiff: 1,
      multiplay: true,
    });
  },
};
</script>
```

- [ ] **Step 2：commit**

```bash
git add index.html
git commit -m "feat: add Lobby JavaScript with Socket.io integration"
```

---

### Task 7：index.html — Phaser 啟動調整（讓 `window._phaserGame` 可用）

**Files:**
- Modify: `index.html`（找到 Phaser 遊戲初始化的 `new Phaser.Game(...)` 呼叫）

- [ ] **Step 1：找到 `new Phaser.Game(config)` 呼叫**

搜尋：
```
new Phaser.Game(
```

找到後，將：
```js
new Phaser.Game(config);
```
改成：
```js
window._phaserGame = new Phaser.Game(config);
```

- [ ] **Step 2：commit**

```bash
git add index.html
git commit -m "feat: expose Phaser game instance as window._phaserGame"
```

---

### Task 8：GameScene — 接收 `multiplay` 參數 + 初始化網路層

**Files:**
- Modify: `index.html`（GameScene 的 `init()` 方法，約 line 902）

- [ ] **Step 1：修改 `init()` 方法接收 multiplay 資訊**

找到（約 line 902）：
```js
init(data){ this.charData=data.char||this.charData||CHARS[0]; this.levelData=data.level||this.levelData||LEVELS[0]; this.enemyCnt=data.enemyCnt||2; this.aiDiff=data.aiDiff??1; }
```
改成：
```js
init(data){
  this.charData=data.char||this.charData||CHARS[0];
  this.levelData=data.level||this.levelData||LEVELS[0];
  this.enemyCnt=data.enemyCnt||2;
  this.aiDiff=data.aiDiff??1;
  this.multiplay=data.multiplay||false;
  this.syncTimer=0;
}
```

- [ ] **Step 2：在 `create()` 末尾加入網路層初始化**

找到 `create()` 函式的最後一個初始化區塊（搜尋 `this.flareLayer =this.add.graphics`，約在 create 末尾附近）。
在 create() 函式結尾（`}` 之前）加入：

```js
    // 多人網路層
    this.otherPlayers={};  // { [id]: { sprite, nameText, data } }
    this.otherLayer=this.add.graphics().setDepth(18);
    if(this.multiplay) this._initMultiplayer();
```

- [ ] **Step 3：在 GameScene class 中加入 `_initMultiplayer()` 方法**

找到（約 line 3566）`spawnRandOilSlick(){` 之前，插入：

```js
  _initMultiplayer(){
    const s=window.MP.socket; if(!s) return;
    s.off('game_state'); s.off('game_event'); s.off('player_disconnected');
    s.on('game_state',(stateMap)=>{
      Object.entries(stateMap).forEach(([id,snap])=>{
        if(id===s.id) return;
        if(!this.otherPlayers[id]){
          // 建立他人的視覺代表
          const gfx=this.add.graphics().setDepth(18);
          const nm=this.add.text(0,-30,snap.nickname||'?',{fontSize:'11px',color:'#ffdd88',fontFamily:'sans-serif',stroke:'#000000',strokeThickness:3}).setOrigin(0.5).setDepth(19);
          this.otherPlayers[id]={gfx,nm,data:snap};
        } else {
          this.otherPlayers[id].data=snap;
        }
      });
      // 清除已離線玩家
      Object.keys(this.otherPlayers).forEach(id=>{
        if(!stateMap[id]){ this.otherPlayers[id].gfx.destroy(); this.otherPlayers[id].nm.destroy(); delete this.otherPlayers[id]; }
      });
    });
    s.on('player_disconnected',({id})=>{
      if(this.otherPlayers[id]){ this.otherPlayers[id].gfx.destroy(); this.otherPlayers[id].nm.destroy(); delete this.otherPlayers[id]; }
    });
    // 大絕若設定一開始就可用
    if(window.MP.settings.ultFromStart) this.ultReady=true;
  }
```

- [ ] **Step 4：commit**

```bash
git add index.html
git commit -m "feat: GameScene init multiplay flag and network layer"
```

---

### Task 9：GameScene — 同步廣播 + 繪製其他玩家

**Files:**
- Modify: `index.html`（GameScene 的 `update()` 函式，約 line 1713）

- [ ] **Step 1：在 `update()` 的 `if(!this.alive) return;` 之後加入同步廣播**

找到（約 line 1717）：
```js
    if(!this.alive) return;
```

在它之後（在原有邏輯之前）插入：

```js
    // 多人同步（20Hz）
    if(this.multiplay&&window.MP.socket){
      this.syncTimer=(this.syncTimer||0)+dt;
      if(this.syncTimer>=0.05){
        this.syncTimer=0;
        window.MP.socket.emit('player_update',{
          x:this.p.x, y:this.p.y,
          alive:this.alive, hp:100-this.heat,
          charKey:this.charData.key,
          team:window.MP.myTeam,
          nickname:window.MP.myNickname,
          facing:this.lastDir,
          ultActive:!!(this.ultActive),
          effects:{
            foil:this.activeEffects.foil>0,
            stun:this.activeEffects.stun>0,
            oilSlick:this.activeEffects.oilSlick>0,
          }
        });
      }
      // 繪製其他玩家
      this.otherLayer.clear();
      Object.values(this.otherPlayers).forEach(op=>{
        const d=op.data; if(!d||!d.alive) return;
        const col=d.team==='blue'?0x4488ff:d.team==='red'?0xff4444:0xffdd88;
        this.otherLayer.fillStyle(col,0.85);
        this.otherLayer.fillCircle(d.x,d.y,16);
        this.otherLayer.lineStyle(2,0xffffff,0.6);
        this.otherLayer.strokeCircle(d.x,d.y,16);
        // 暱稱跟隨
        op.nm.setPosition(d.x,d.y-26);
        op.gfx.clear();
        // 血量條
        const hpFrac=Math.max(0,(d.hp||100))/100;
        op.gfx.fillStyle(0x000000,0.5); op.gfx.fillRect(d.x-18,d.y-38,36,5);
        op.gfx.fillStyle(hpFrac>0.5?0x44ff88:0xffaa00,0.9); op.gfx.fillRect(d.x-18,d.y-38,Math.round(36*hpFrac),5);
      });
    }
```

- [ ] **Step 2：測試多人顯示**

開啟兩個瀏覽器視窗，一個開房間、一個加入，確認：
1. 兩個視窗都進入遊戲
2. 各自操作時，對方能看到自己的角色移動
3. 暱稱與血量條正確顯示

- [ ] **Step 3：commit**

```bash
git add index.html
git commit -m "feat: add 20Hz sync broadcast and other-player rendering"
```

---

### Task 10：隊伍制勝負判定

**Files:**
- Modify: `index.html`（找到遊戲結束判定邏輯）

- [ ] **Step 1：找到 `checkWin` 或最後存活判定**

搜尋：
```
this.enemies.filter(e=>e.alive
```
找到淘汰判定區塊（約在 `update()` 內）。

- [ ] **Step 2：在隊伍制時加入隊伍勝負判定**

在找到的 `checkWin` 邏輯之後加入（或覆蓋原邏輯）：

找到（搜尋 `aliveEnemies` 或最後存活者判定）：

在結束判定觸發時（例如 `if(aliveCount===0)`），加入隊伍制檢查：

```js
        // 隊伍制：發出 game_event 讓全員知道結果
        if(this.multiplay&&window.MP.settings.gameMode==='team'&&window.MP.socket){
          window.MP.socket.emit('game_event',{type:'player_eliminated',team:window.MP.myTeam,nickname:window.MP.myNickname});
        }
```

- [ ] **Step 3：監聽 `game_event` 的 player_eliminated（已在 _initMultiplayer 中設定）**

在 `_initMultiplayer()` 的 `s.off('game_event')` 之後加入：

```js
    s.on('game_event',(evt)=>{
      if(evt.type==='player_eliminated'){
        // 顯示淘汰提示
        this.add.text(W/2,H/2-50,`${evt.nickname} 淘汰！`,{
          fontSize:'22px',color:'#ff4444',fontFamily:'sans-serif',stroke:'#000',strokeThickness:4
        }).setOrigin(0.5).setDepth(50);
      }
    });
```

- [ ] **Step 4：commit**

```bash
git add index.html
git commit -m "feat: add team game_event for player elimination notification"
```

---

### Task 11：Push 到 GitHub + 確認

- [ ] **Step 1：確認 server.js 中 SERVER_URL 已填入真實 Render URL**

開啟 index.html，搜尋 `SERVER_URL`，確認已替換為 Render 提供的真實 URL：
```js
const SERVER_URL = 'https://bbq-survival-game-xxxx.onrender.com';
```

- [ ] **Step 2：push**

```bash
git push origin master
```

- [ ] **Step 3：功能確認清單**

- [ ] 開啟 `https://kshwin.github.io/bbq-survival-game/`，看到大廳 Landing 畫面
- [ ] 「開房間」流程：輸入暱稱 → 選角色 → 建立 → 看到 6 碼房號
- [ ] 「加入房間」流程：輸入房號 + 暱稱 + 角色 → 加入等待室
- [ ] 等待室：玩家列表即時更新
- [ ] 主機可調整人數、模式、大絕設定
- [ ] 點擊「開始遊戲」後雙方進入 GameScene
- [ ] 遊戲中可看到對方角色移動（暱稱 + 血量條）
- [ ] 「單人遊玩」不走多人流程，直接進入選角

---

## 注意事項

- **Render 免費方案**：閒置 30 分鐘後休眠，首位玩家進入時需等待約 30 秒喚醒。可在大廳 JS 加入「伺服器預熱」提示。
- **GitHub Pages 只能跑靜態檔**：`server.js` 不會在 GitHub Pages 上執行，只在 Render.com 上執行。
- **`SERVER_URL` 填錯**：`io()` 連線失敗時，Socket.io 會在 console 顯示 `xhr poll error`；檢查 Render.com 上的 URL 是否正確。
- **CHARS 全局變數**：大廳 JS 在 Phaser 尚未載入時執行，`CHARS` 可能是 undefined；`_buildCharList` 已有備用列表。
