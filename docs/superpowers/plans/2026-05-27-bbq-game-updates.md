# 烤肉遊戲三項更新 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修正雞翅大絕落地位置 Bug、將青椒大絕改為辣椒素路徑減速機制、升級能量球視覺效果。

**Architecture:** 所有修改集中在單一檔案 `index.html`。雞翅為 Bug Fix（`_clearUltState` 加位置同步）；青椒大絕改寫 `fireUltimate`、`updateUltState`，並在敵人速度計算中加 `capsaicinTimer`；能量球在 `spawnUltOrb` 加入預兆旗標，`updateUltOrbs` 改寫繪圖邏輯。

**Tech Stack:** Phaser 3.60.0、vanilla JS、HTML Canvas（單一 index.html）

---

## Task 1: 雞翅大絕位置 Bug Fix

**Files:**
- Modify: `index.html` — `_clearUltState()` 約第 3261 行

### 背景
雞翅大絕（type:'wing'）結束有兩個路徑：
- 三顆炸彈投完 → `dropWingBomb` 裡的 `delayedCall(600ms)` → 設定 `p.x/p.y = aimX/aimY` → `_clearUltState()`
- 計時器 3.5 秒到期 → 直接 `_clearUltState()` → **aimX/aimY 從未套用 → Bug**

### 修法
在 `_clearUltState()` 清除 `ultState` 前，若 `type==='wing'` 且 `flying===true`，強制套用 aimX/aimY。

- [ ] **Step 1: 找到 `_clearUltState()` 開頭**

找到這段程式碼（約第 3261 行）：
```js
_clearUltState(){
  const us=this.ultState;
  if(!us) return;
  if(us.trailGfx) us.trailGfx.destroy();
  if(us.fogGfx) us.fogGfx.destroy();
  if(us.spinGfx) us.spinGfx.destroy();
  if(us.aimGfx) us.aimGfx.destroy();
```

- [ ] **Step 2: 在 `if(us.aimGfx)` 之後加入 wing 位置修正與 nodeGfx 清除**

將這段：
```js
  if(us.aimGfx) us.aimGfx.destroy();
  if(this.playerSprite){
```
改為：
```js
  if(us.aimGfx) us.aimGfx.destroy();
  if(us.nodeGfx) us.nodeGfx.destroy();
  if(us.type==='wing'&&us.flying){
    this.p.x=Phaser.Math.Clamp(us.aimX,G.x+25,G.x+G.w-25);
    this.p.y=Phaser.Math.Clamp(us.aimY,G.y+25,G.y+G.h-25);
    if(this.playerSprite)this.playerSprite.setPosition(this.p.x,this.p.y);
  }
  if(this.playerSprite){
```

- [ ] **Step 3: 手動測試雞翅大絕**

1. 開啟 `index.html`，選雞翅
2. 蓄滿大絕，按 Q 啟動
3. 用方向鍵把準心移到畫面邊角
4. **等計時器自然跑完**（不主動投彈或讓炸彈全投完後 delayedCall 跑完）
5. 預期結果：角色出現在準心最後位置，而非大絕啟動原點

- [ ] **Step 4: 確認 delayedCall 路徑仍正常**

選雞翅，快速投完 3 顆炸彈，確認角色也落在準心位置（原有邏輯不受影響）。

---

## Task 2: 青椒大絕 — 替換 `fireUltimate` 初始化

**Files:**
- Modify: `index.html` — `fireUltimate()` case 'pepper'，約第 2934 行

- [ ] **Step 1: 找到 pepper 大絕初始化程式碼**

找到這整段（約第 2934–2943 行）：
```js
      case 'pepper':{
        // 毒霧迷蹤：速度+50%＋噴綠毒氣＋敵人控制反轉 (6秒)
        this.ultState={type:'pepper',timer:6,reversed:false,spdMul:1.5,gasTimer:0,gasClouds:[]};
        for(let pi=0;pi<30;pi++){const ang=pi*Math.PI*2/30;const go={px:this.p.x,py:this.p.y,life:1};const gfx=this.add.graphics().setDepth(24);
          this.tweens.add({targets:go,px:this.p.x+Math.cos(ang)*(40+Math.random()*130),py:this.p.y+Math.sin(ang)*(40+Math.random()*130),life:0,duration:400+Math.random()*200,ease:'Quad.easeOut',
            onUpdate:()=>{gfx.clear();gfx.fillStyle(0x44ff44,go.life*0.85);gfx.fillCircle(go.px,go.py,3+go.life*3);},
            onComplete:()=>gfx.destroy()});}
        this.cameras.main.shake(150,0.010);
        this.showPop('🌶 毒霧迷蹤！速度+50%＋毒氣反轉操控！');
        break;}
```

- [ ] **Step 2: 替換為新的辣椒素路徑初始化**

替換成：
```js
      case 'pepper':{
        const _pepNodeGfx=this.add.graphics().setDepth(14);
        this.ultState={type:'pepper',timer:6,spdMul:1.5,nodes:[],nodeGfx:_pepNodeGfx,lastNX:this.p.x,lastNY:this.p.y};
        for(let pi=0;pi<18;pi++){const ang=pi*Math.PI*2/18;const go={px:this.p.x,py:this.p.y,life:1};const gfx=this.add.graphics().setDepth(24);
          this.tweens.add({targets:go,px:this.p.x+Math.cos(ang)*(30+Math.random()*70),py:this.p.y+Math.sin(ang)*(30+Math.random()*70),life:0,duration:350+Math.random()*150,ease:'Quad.easeOut',
            onUpdate:()=>{gfx.clear();gfx.fillStyle(0xff6600,go.life*0.9);gfx.fillCircle(go.px,go.py,3+go.life*4);},
            onComplete:()=>gfx.destroy()});}
        this.cameras.main.shake(150,0.010);
        this.showPop('🌶 辣椒素噴霧！速度+50%！沿路灑辣椒素！');
        break;}
```

**說明：**
- `nodes:[]` — 辣椒素節點陣列，每個 `{x, y, life:8.0, hitMap:{}}`
- `nodeGfx` — 專用繪圖物件，置於玩家圖層之下（depth 14）
- `lastNX/lastNY` — 上次生成節點的位置，用於計算移動距離
- 爆散粒子改為橘紅色（符合辣椒素感），數量從 30 減為 18

- [ ] **Step 3: 確認大絕啟動不報錯**

開啟 index.html，選青椒，蓄滿大絕後按 Q，確認不跳 console error，且出現橘紅色爆散粒子與新 showPop 文字。

---

## Task 3: 青椒大絕 — 替換 `updateUltState` 的 pepper 邏輯

**Files:**
- Modify: `index.html` — `updateUltState()` 內 `else if(us.type==='pepper')` 區塊，約第 3240 行

- [ ] **Step 1: 找到 pepper 的 updateUltState 區塊**

找到這整段（約第 3240–3256 行）：
```js
    } else if(us.type==='pepper'){
      us.gasTimer-=dt;
      if(us.gasTimer<=0){
        const _gx=this.p.x+(Math.random()-0.5)*65,_gy=this.p.y+(Math.random()-0.5)*65;
        const _gv={r:0,a:1};const _gfx=this.add.graphics().setDepth(23);
        this.tweens.add({targets:_gv,r:1,a:0,duration:1400,ease:'Quad.easeOut',
          onUpdate:()=>{_gfx.clear();_gfx.fillStyle(0x44ff44,_gv.a*0.22);_gfx.fillCircle(_gx,_gy,_gv.r*48);},
          onComplete:()=>_gfx.destroy()});
        us.gasClouds.push({x:_gx,y:_gy,r:48,life:1.4});
        us.gasTimer=0.18;
      }
      us.gasClouds=us.gasClouds.filter(c=>{c.life-=dt;return c.life>0;});
      this.enemies.filter(e=>e.alive).forEach(e=>{
        if(us.gasClouds.some(c=>Math.hypot(c.x-e.x,c.y-e.y)<c.r)){
          e.vx+=(Math.random()-0.5)*1.6;e.vy+=(Math.random()-0.5)*1.6;
        }
      });
    }
```

- [ ] **Step 2: 替換為辣椒素節點生成、碰撞、繪製邏輯**

替換成：
```js
    } else if(us.type==='pepper'){
      // 節點生成：每移動 20px 放一個節點
      const moved=Math.hypot(this.p.x-us.lastNX,this.p.y-us.lastNY);
      if(moved>=20){
        us.nodes.push({x:this.p.x,y:this.p.y,life:8.0,hitMap:{}});
        us.lastNX=this.p.x; us.lastNY=this.p.y;
      }
      // 節點倒計時（過期移除）
      us.nodes=us.nodes.filter(n=>{n.life-=dt;return n.life>0;});
      // 碰撞偵測：節點 vs 敵人
      us.nodes.forEach(n=>{
        this.enemies.forEach((e,i)=>{
          if(!e.alive) return;
          if((n.hitMap[i]||0)>0){n.hitMap[i]-=dt;return;}
          if(Math.hypot(n.x-e.x,n.y-e.y)<28){
            e.capsaicinTimer=3.0;
            n.hitMap[i]=3.0;
            if(this.enemySprites[i]){this.enemySprites[i].setTint(0xff8800);this.time.delayedCall(300,()=>{if(this.enemySprites[i])this.enemySprites[i].clearTint();});}
          }
        });
      });
      // 繪製節點（橘紅色圓點，透明度隨剩餘生命衰減）
      us.nodeGfx.clear();
      us.nodes.forEach(n=>{
        const alpha=(n.life/8)*0.85;
        us.nodeGfx.fillStyle(0xff6600,alpha);
        us.nodeGfx.fillCircle(n.x,n.y,10);
      });
    }
```

- [ ] **Step 3: 手動測試辣椒素路徑**

1. 選青椒，啟動大絕
2. 沿畫面走一段 S 形路徑
3. 預期：走過的地方留下橘紅色漸隱圓點軌跡
4. 讓 AI 敵人走過軌跡，觀察牠們是否明顯變慢並短暫閃橘色
5. 確認站著不動時不會持續生成節點

---

## Task 4: 敵人速度加入 `capsaicinTimer` 減速

**Files:**
- Modify: `index.html` — 敵人更新迴圈，約第 2021 行

- [ ] **Step 1: 找到敵人更新迴圈開頭**

找到這段（約第 2021–2034 行）：
```js
    this.enemies.forEach((e,i)=>{
      if(!e.alive){if(this.enemySprites[i])this.enemySprites[i].setVisible(false);return;}
      if((e.stunTimer||0)>0){
        e.stunTimer-=dt;
        e.vx*=0.88;e.vy*=0.88;e.x+=e.vx;e.y+=e.vy;
        if(this.enemySprites[i])this.enemySprites[i].setPosition(e.x,e.y).setVisible(true);
        return;
      }
      const sSlow=this.enemyCC.slow>0?0.5:1.0;
```

- [ ] **Step 2: 在 `if(!e.alive)` 之後加入 capsaicinTimer 倒計時**

將：
```js
      if(!e.alive){if(this.enemySprites[i])this.enemySprites[i].setVisible(false);return;}
      if((e.stunTimer||0)>0){
```
改為：
```js
      if(!e.alive){if(this.enemySprites[i])this.enemySprites[i].setVisible(false);return;}
      if((e.capsaicinTimer||0)>0) e.capsaicinTimer=Math.max(0,e.capsaicinTimer-dt);
      if((e.stunTimer||0)>0){
```

- [ ] **Step 3: 找到 maxSpd 計算**

找到（約第 2101–2103 行）：
```js
      const espd=Math.hypot(e.vx,e.vy)||1;
      const maxSpd=(e.charging?4.5:2.8)*sSlow*(onOil?0.7:1);
      if(espd>maxSpd){e.vx=(e.vx/espd)*maxSpd;e.vy=(e.vy/espd)*maxSpd;}
```

- [ ] **Step 4: 在 maxSpd 加入辣椒素乘數**

將：
```js
      const maxSpd=(e.charging?4.5:2.8)*sSlow*(onOil?0.7:1);
```
改為：
```js
      const capSlow=(e.capsaicinTimer||0)>0?0.25:1.0;
      const maxSpd=(e.charging?4.5:2.8)*sSlow*capSlow*(onOil?0.7:1);
```

- [ ] **Step 5: 手動驗證減速強度**

啟動青椒大絕，走過 AI 敵人前方，確認敵人被辣到後移動速度肉眼明顯下降（約剩 25%），3 秒後恢復正常速度。

---

## Task 5: 能量球 — 加入預兆旗標

**Files:**
- Modify: `index.html` — `spawnUltOrb()`，約第 3337 行

- [ ] **Step 1: 找到 `spawnUltOrb()`**

找到（約第 3337–3343 行）：
```js
  spawnUltOrb(){
    const margin=70;
    const x=G.x+margin+Math.random()*(G.w-margin*2);
    const y=G.y+margin+Math.random()*(G.h-margin*2);
    const gfx=this.add.graphics().setDepth(17);
    this.ultOrbs.push({x,y,gfx,life:18,ph:Math.random()*Math.PI*2});
  }
```

- [ ] **Step 2: 加入預兆欄位**

替換成：
```js
  spawnUltOrb(){
    const margin=70;
    const x=G.x+margin+Math.random()*(G.w-margin*2);
    const y=G.y+margin+Math.random()*(G.h-margin*2);
    const gfx=this.add.graphics().setDepth(17);
    this.ultOrbs.push({x,y,gfx,life:18,ph:Math.random()*Math.PI*2,preSpawn:true,preTimer:3.0,particleAngle:0});
  }
```

---

## Task 6: 能量球 — 升級 `updateUltOrbs` 繪圖

**Files:**
- Modify: `index.html` — `updateUltOrbs()`，約第 3345 行

- [ ] **Step 1: 找到 `updateUltOrbs()` 完整內容**

找到（約第 3345–3368 行）：
```js
  updateUltOrbs(dt){
    this.ultOrbs=this.ultOrbs.filter(orb=>{
      orb.life-=dt; orb.ph+=dt*3;
      const glow=0.5+0.5*Math.sin(orb.ph);
      orb.gfx.clear();
      orb.gfx.fillStyle(0xdd88ff,0.2+glow*0.3); orb.gfx.fillCircle(orb.x,orb.y,18+glow*4);
      orb.gfx.fillStyle(0xffffff,0.95);          orb.gfx.fillCircle(orb.x,orb.y,6);
      orb.gfx.lineStyle(2,0xff88ff,0.55+glow*0.45);
      orb.gfx.strokeCircle(orb.x,orb.y,13+glow*3);
      if(orb.life<=0){orb.gfx.destroy();return false;}
      if(Math.hypot(this.p.x-orb.x,this.p.y-orb.y)<22&&this.ultCharge<this.ultMax){
        this.ultCharge++;
        this.updateUltUI();
        const msg=this.ultCharge>=this.ultMax?'✦ 大絕蓄滿！按 [Q] 釋放！':'✦ 大絕充能 '+this.ultCharge+'/'+this.ultMax;
        this.showPop(msg);
        const fx=this.add.graphics().setDepth(28); const fo={v:0};
        this.tweens.add({targets:fo,v:1,duration:300,
          onUpdate:()=>{fx.clear();fx.lineStyle(4*(1-fo.v),0xff88ff,1-fo.v);fx.strokeCircle(orb.x,orb.y,42*fo.v);},
          onComplete:()=>fx.destroy()});
        orb.gfx.destroy(); return false;
      }
      return true;
    });
  }
```

- [ ] **Step 2: 替換為支援預兆與粒子的新版本**

替換成：
```js
  updateUltOrbs(dt){
    this.ultOrbs=this.ultOrbs.filter(orb=>{
      orb.gfx.clear();
      // 預兆階段：只顯示地板呼吸光暈，不可拾取
      if(orb.preSpawn){
        orb.preTimer-=dt;
        if(orb.preTimer<=0) orb.preSpawn=false;
        const freq=0.8+(1.2*(1-Math.max(0,orb.preTimer)/3.0));
        orb.ph=(orb.ph||0)+dt*freq*Math.PI*2;
        const glow=0.5+0.5*Math.sin(orb.ph);
        orb.gfx.fillStyle(0xcc88ff,glow*0.45);
        orb.gfx.fillCircle(orb.x,orb.y,24+glow*6);
        return true;
      }
      // 正式出現階段
      orb.life-=dt;
      if(orb.life<=0){orb.gfx.destroy();return false;}
      orb.ph+=dt*3;
      orb.particleAngle+=dt*2;
      const glow=0.5+0.5*Math.sin(orb.ph);
      // 外層發光暈圈
      orb.gfx.fillStyle(0xdd88ff,0.15+glow*0.25); orb.gfx.fillCircle(orb.x,orb.y,22+glow*5);
      // 白色中心
      orb.gfx.fillStyle(0xffffff,0.95); orb.gfx.fillCircle(orb.x,orb.y,6);
      // 外環
      orb.gfx.lineStyle(2,0xff88ff,0.55+glow*0.45); orb.gfx.strokeCircle(orb.x,orb.y,13+glow*3);
      // 6顆旋轉粒子
      for(let pi=0;pi<6;pi++){
        const a=orb.particleAngle+pi*Math.PI*2/6;
        orb.gfx.fillStyle(0xffffff,0.7+glow*0.25);
        orb.gfx.fillCircle(orb.x+Math.cos(a)*30,orb.y+Math.sin(a)*30,4);
      }
      if(Math.hypot(this.p.x-orb.x,this.p.y-orb.y)<22&&this.ultCharge<this.ultMax){
        this.ultCharge++;
        this.updateUltUI();
        const msg=this.ultCharge>=this.ultMax?'✦ 大絕蓄滿！按 [Q] 釋放！':'✦ 大絕充能 '+this.ultCharge+'/'+this.ultMax;
        this.showPop(msg);
        const fx=this.add.graphics().setDepth(28); const fo={v:0};
        this.tweens.add({targets:fo,v:1,duration:300,
          onUpdate:()=>{fx.clear();fx.lineStyle(4*(1-fo.v),0xff88ff,1-fo.v);fx.strokeCircle(orb.x,orb.y,42*fo.v);},
          onComplete:()=>fx.destroy()});
        orb.gfx.destroy(); return false;
      }
      return true;
    });
  }
```

- [ ] **Step 3: 手動測試能量球視覺**

1. 開啟遊戲，等待大約 2–5 秒（ultOrbTimer 初始為 2）
2. 預期：先看到一個紫色呼吸地光（預兆），節奏從慢到快
3. 3 秒後：地光消失，完整能量球出現 — 有外層光暈 + 中心白點 + 6 顆白色粒子繞轉
4. 走近拾取，確認收取音效與 UI 正常更新
5. 確認在 `ultCharge >= ultMax` 時不再生成（已有的邏輯，確認未被破壞）

---

## 自我審查（Spec Coverage）

| 需求 | 對應 Task |
|------|-----------|
| 雞翅落點 Bug 修正 | Task 1 |
| 青椒大絕速度加成保留 | Task 2（`spdMul:1.5` 保留）|
| 青椒大絕啟動爆散改橘紅 | Task 2（粒子顏色改 `0xff6600`）|
| 走路留下辣椒素軌跡 | Task 3（節點生成）|
| 軌跡持續 8 秒 | Task 3（`life:8.0`）|
| 碰到軌跡減速 75% | Task 3 + Task 4（`capSlow=0.25`）|
| 減速持續 3 秒 | Task 3（`capsaicinTimer=3.0`）|
| 3 秒 cooldown 防 spam | Task 3（`hitMap[i]=3.0`）|
| 中招閃橘色視覺 | Task 3（`setTint(0xff8800)`）|
| `nodeGfx` cleanup | Task 1 Step 2（`_clearUltState` 加 `nodeGfx.destroy()`）|
| 能量球預兆地光 | Task 5 + Task 6 |
| 預兆呼吸節奏加速 | Task 6（`freq` 線性遞增）|
| 能量球粒子環繞 | Task 6（6 顆旋轉粒子）|
| 能量球持續發光 | Task 6（外層暈圈 + `glow` pulsing）|
