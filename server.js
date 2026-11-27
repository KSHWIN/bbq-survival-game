const http = require('http');
const { Server } = require('socket.io');

const PORT = process.env.PORT || 3000;
const server = http.createServer((req, res) => {
  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.end('BBQ Survival Game Server v2 (host-authoritative)');
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

  // pid：玩家固定編號（網路斷線重連後 socket.id 會變，遊戲裡一律用 pid 認人）
  const pidOf = (room) => (room && room.players[socket.id] && room.players[socket.id].pid) || socket.id;
  socket.on('create_room', ({ nickname, charKey, pid }, cb) => {
    const code = genCode();
    rooms[code] = {
      host: socket.id,
      players: {
        [socket.id]: { nickname, charKey, team: 'red', ready: false, pid: pid || socket.id }
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

  socket.on('join_room', ({ code, nickname, charKey, pid }, cb) => {
    code = String(code || '').toUpperCase().replace(/[^A-Z0-9]/g, '');
    const room = rooms[code];
    if (!room) return cb({ ok: false, err: '找不到此房間：請確認代碼，或請房主回到等待室再看一次房號' });
    if (room.state !== 'waiting') return cb({ ok: false, err: '遊戲已開始' });
    const realCount = Object.values(room.players).length;
    if (realCount >= room.settings.maxPlayers) return cb({ ok: false, err: '房間已滿' });
    room.players[socket.id] = { nickname, charKey, team: 'blue', ready: false, pid: pid || socket.id };
    if (room._delT) { clearTimeout(room._delT); room._delT = null; }
    let tookHost = false;
    if (!room.players[room.host]) { room.host = socket.id; tookHost = true; } // 房主斷線中：先由你當房主
    myRoom = code;
    socket.join(code);
    cb({ ok: true, code, isHost: tookHost, settings: room.settings, players: buildPlayerList(room) });
    io.to(code).emit('player_list', buildPlayerList(room));
  });

  // 斷線重連（伺服器重開、網路閃斷、電腦睡眠）：回到同一個房號，房間不見了就用同一個房號重建
  socket.on('rejoin_room', ({ code, nickname, charKey, team, wasHost, settings, pid }, cb) => {
    code = String(code || '').toUpperCase().replace(/[^A-Z0-9]/g, '');
    if (!code) return cb && cb({ ok: false, err: 'no code' });
    let room = rooms[code];
    if (!room) room = rooms[code] = { host: socket.id, players: {}, state: 'waiting', gameState: {},
      settings: { maxPlayers: 4, gameMode: 'individual', ultFromStart: false, ...(wasHost && settings ? settings : {}) } };
    if (room._delT) { clearTimeout(room._delT); room._delT = null; }
    pid = pid || socket.id;
    for (const sid of Object.keys(room.players)) if (sid !== socket.id && room.players[sid].pid === pid) delete room.players[sid]; // 舊連線還沒被判定斷線
    room.players[socket.id] = { nickname, charKey, team: team || (wasHost ? 'red' : 'blue'), ready: false, pid };
    const oldHost = room.host;
    // 遊戲中只有原本的房主能拿回房主（其他人重連不能搶）
    if (wasHost || (!room.players[room.host] && room.state !== 'playing')) room.host = socket.id;
    if (room.host === socket.id && room._hostLeftT) { clearTimeout(room._hostLeftT); room._hostLeftT = null; }
    myRoom = code;
    socket.join(code);
    if (cb) cb({ ok: true, code, isHost: room.host === socket.id, settings: room.settings, players: buildPlayerList(room) });
    if (oldHost !== room.host) io.to(code).emit('host_changed', { newHost: room.host });
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

  // ── 房主當裁判（v2）────────────────────────────────────────
  // 客戶端按鍵 → 只送給房主
  socket.on('input', (inp) => {
    const room = rooms[myRoom]; if (!room || room.host === socket.id) return;
    io.to(room.host).emit('input', { ...inp, id: pidOf(room) });
  });
  // 房主的戰場快照 → 送給房間其他人（volatile：網路塞車時丟掉舊的，不要堆積）
  socket.on('snap', (snap) => {
    const room = rooms[myRoom]; if (!room || room.host !== socket.id) return;
    socket.volatile.to(myRoom).emit('snap', snap);
  });
  // 一局結束：房間回到等待狀態，可以再開一局
  socket.on('game_over', (data) => {
    const room = rooms[myRoom]; if (!room || room.host !== socket.id) return;
    room.state = 'waiting';
    socket.to(myRoom).emit('game_end', data || {}); // 結算一定要送到（不走可丟棄的快照）
  });

  socket.on('game_event', (evt) => {
    const room = rooms[myRoom]; if (!room) return;
    socket.to(myRoom).emit('game_event', { ...evt, from: socket.id });
  });

  socket.on('disconnect', () => {
    const room = rooms[myRoom]; if (!room) return;
    const gone = room.players[socket.id];
    delete room.players[socket.id];
    if (room.gameState) delete room.gameState[socket.id];
    io.to(myRoom).emit('player_disconnected', { id: (gone && gone.pid) || socket.id });
    if (room.host === socket.id) {
      const code = myRoom;
      const handOver = () => {
        const r = rooms[code]; if (!r || r.players[r.host]) return; // 房主已經重連回來
        if (r.state === 'playing') io.to(code).emit('host_left'); // 遊戲中房主沒回來：這局無法繼續
        r.state = 'waiting';
        const remaining = Object.keys(r.players);
        if (remaining.length > 0) { r.host = remaining[0]; io.to(code).emit('host_changed', { newHost: r.host }); }
        io.to(code).emit('player_list', buildPlayerList(r));
      };
      // 遊戲中房主斷線：等 10 秒（網路閃一下會自己重連），沒回來才結束這局
      if (room.state === 'playing') { if (room._hostLeftT) clearTimeout(room._hostLeftT); room._hostLeftT = setTimeout(handOver, 10000); }
      else handOver();
    }
    if (Object.keys(room.players).length === 0) { // 沒人了：留 3 分鐘給斷線的人重連，之後才刪
      const code = myRoom;
      if (room._delT) clearTimeout(room._delT);
      room._delT = setTimeout(() => { const r = rooms[code]; if (r && Object.keys(r.players).length === 0) delete rooms[code]; }, 180000);
    }
    io.to(myRoom).emit('player_list', buildPlayerList(room));
  });
});

function buildPlayerList(room) {
  return Object.entries(room.players).map(([sid, p]) => ({
    id: p.pid || sid, nickname: p.nickname, charKey: p.charKey, team: p.team,
    isHost: sid === room.host
  }));
}

server.listen(PORT, () => console.log(`BBQ Server listening on port ${PORT}`));
