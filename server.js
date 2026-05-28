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
