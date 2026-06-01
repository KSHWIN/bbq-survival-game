# 道具加強 + 場地事件加強 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 為烤肉遊戲加入 AI 撿道具系統、5 個道具機制升級、以及 5 個場地事件升級，讓遊戲節奏更具策略性。

**Architecture:** 所有變更集中在 `index.html` 單一檔案，在 `GameScene` class 內新增資料結構（陣列、flags）、修改現有 update/draw 方法、新增 helper 方法。分兩批：第一批（Task 1-6）為道具系統，第二批（Task 7-11）為場地事件。

**Tech Stack:** Phaser 3、純 JavaScript、單一 `index.html`（4.4MB）

---

## 關鍵行號速查（實作前確認）

| 位置 | 約行號 |
|------|--------|
| `activeEffects` 初始化 | ~1466 |
| enemy 物件建立 | ~1568 |
| `applyItem()` | ~2245 |
| `doPush()` | ~2278 |
| AI 推玩家程式碼 | ~2904 |
| AI 速度上限 `maxSpd` | ~2893 |
| 玩家速度計算 `SPD` | ~2490 |
| 玩家熱度計算 `mult` | ~2595 |
| `mapItems` 拾取迴圈 | ~3025 |
| 效果 HUD `eff2` | ~3034 |
| 叉子 update | ~3316 |
| 叉子 draw | ~3449 |
| 檸檬 update | ~3243 |
| 檸檬 draw | ~3371 |
| `updateShrink` | ~3472 |
| `drawShrinkLayer` | ~3517 |
| `updateHoles` | ~3546 |
| `drawHoles` | ~3592 |
| tilt update | ~2774 |

---

## BATCH 1：道具系統

---

### Task 1：AI activeEffects + 撿道具基礎

**Files:**
- Modify: `index.html` — enemy 初始化、mapItems 迴圈、新增 `applyItemToEnemy()`、AI activeEffects timer

- [ ] **Step 1：在 enemy 物件加入 `activeEffects`**

找到（~1568）：
```js
    this.enemies=aiChars.map((ch,i)=>({
      x:EPOS[i].x, y:EPOS[i].y, r:18,
      vx:EPOS[i].vx, vy:EPOS[i].vy,
      heat:0, alive:true, label:ch.name, img:ch.img, weight:ch.weight||1.0,
      chargeTimer:1.5+Math.random()*2, charging:false, chDx:1, chDy:0, chargeTime:0,
      pushTimer:3+Math.random()*3, abilTimer:5+Math.random()*4, abilActive:false,
      team:this.aiTeams['ai'+i]||'none',
    }));
```

替換成：
```js
    this.enemies=aiChars.map((ch,i)=>({
      x:EPOS[i].x, y:EPOS[i].y, r:18,
      vx:EPOS[i].vx, vy:EPOS[i].vy,
      heat:0, alive:true, label:ch.name, img:ch.img, weight:ch.weight||1.0,
      chargeTimer:1.5+Math.random()*2, charging:false, chDx:1, chDy:0, chargeTime:0,
      pushTimer:3+Math.random()*3, abilTimer:5+Math.random()*4, abilActive:false,
      team:this.aiTeams['ai'+i]||'none',
      activeEffects:{foil:0,garlic:0,sauceCharge:0,iceBoost:0,pepBoost:0,slip:0},
      slipLastVx:0, slipLastVy:0, iceLastX:0, iceLastY:0,
    }));
```

- [ ] **Step 2：在 `applyItem()` 後方新增 `applyItemToEnemy()` 方法**

找到 `applyItem(item){` 結束的 `}` 後（約 2252 行），在其後插入：

```js
  applyItemToEnemy(e, item){
    const ae=e.activeEffects;
    if(item.type==='ice')   { e.heat=Math.max(0,e.heat-42); ae.iceBoost=5; }
    if(item.type==='foil')  { ae.foil=item.dur+3; }
    if(item.type==='garlic'){ ae.garlic=item.dur+2; }
    if(item.type==='sauce') { ae.sauceCharge=5.0; }
    if(item.type==='pepper'){ ae.pepBoost=item.dur; }
  }
```

- [ ] **Step 3：擴充 `mapItems` 迴圈，讓 AI 也能撿道具**

找到（~3025）：
```js
    this.mapItems=this.mapItems.filter(item=>{
      item.life-=dt;
      if(Math.hypot(this.p.x-item.x,this.p.y-item.y)<24){this.applyItem(item);item.img.destroy();item.gfx.destroy();return false;}
      if(item.life<=0){item.img.destroy();item.gfx.destroy();return false;}
```

替換成：
```js
    this.mapItems=this.mapItems.filter(item=>{
      item.life-=dt;
      if(Math.hypot(this.p.x-item.x,this.p.y-item.y)<24){this.applyItem(item);item.img.destroy();item.gfx.destroy();return false;}
      // AI 撿道具
      let aiTook=false;
      this.enemies.forEach(e=>{
        if(!e.alive||aiTook) return;
        if(Math.hypot(e.x-item.x,e.y-item.y)<24){this.applyItemToEnemy(e,item);aiTook=true;}
      });
      if(aiTook){item.img.destroy();item.gfx.destroy();return false;}
      if(item.life<=0){item.img.destroy();item.gfx.destroy();return false;}
```

- [ ] **Step 4：在 AI update 迴圈中加入 activeEffects timer 遞減**

找到（~2993）AI 的效果遞減行（只有一行對 `ae2`），在其上方同一位置，為每個 enemy 加入遞減。

找到 enemies forEach 迴圈的開頭 `this.enemies.forEach((e,i)=>{`（在 AI update loop 裡，約 2806 行），找到迴圈內靠近結尾處（約行 2960 附近）有 `e.pushTimer` 等遞減的地方，加入：

```js
      // activeEffects 遞減
      if(e.activeEffects) Object.keys(e.activeEffects).forEach(k=>{
        if(e.activeEffects[k]>0) e.activeEffects[k]=Math.max(0,e.activeEffects[k]-dt);
      });
```

找法：在 enemies forEach 內找到 `e.chargeTimer-=dt;`（約 2808 行），在其後加入上面這段。

- [ ] **Step 5：AI maxSpd 套用 activeEffects（garlic、pepBoost、iceBoost、slip）**

找到（~2893）：
```js
      const maxSpd=(e.charging?4.5:2.8)*sSlow*capSlow*(onOil?0.7:1);
```

替換成：
```js
      const _eAE=e.activeEffects||{};
      const _eGarlicSpd=_eAE.garlic>0?1.0:1.0; // garlic 不改速度，只改推力
      const _ePepSpd=_eAE.pepBoost>0?1.5:1.0;
      const _eIceSpd=_eAE.iceBoost>0?1.5:1.0;
      const _eSlipSpd=_eAE.slip>0?1.0:1.0; // 打滑時不限速但不受控
      const maxSpd=(e.charging?4.5:2.8)*sSlow*capSlow*(onOil?0.7:1)*_ePepSpd*_eIceSpd;
```

- [ ] **Step 6：AI 推力套用 garlic 加成**

找到（~2903）：
```js
          const pForce=95*Math.min(2.0,1+e.heat/100*1.5); // AI 越熟推越猛
```

替換成：
```js
          const _eGarlicBst=(e.activeEffects&&e.activeEffects.garlic>0)?1.7:1.0;
          const pForce=95*Math.min(2.0,1+e.heat/100*1.5)*_eGarlicBst; // AI 越熟推越猛，大蒜加成
```

- [ ] **Step 7：測試**
開啟 `index.html`，打開遊戲，觀察：
- 場上道具出現後，AI 路過時是否撿走
- 撿走後 AI 名稱旁暫無 HUD（後續 task 會加），但 AI 行為應正常
- 無 JS 報錯（F12 console）

- [ ] **Step 8：Commit**
```bash
git add index.html
git commit -m "feat: AI item pickup system with activeEffects"
```

---

### Task 2：冰塊 → 寒冰路徑

**Files:**
- Modify: `index.html` — create() 初始化、iceBoost 留跡邏輯、slip 打滑邏輯、draw 繪製冰跡

- [ ] **Step 1：初始化新資料結構**

找到（~1466）：
```js
    this.activeEffects={foil:0,garlic:0,sauce:0,slowpow:0,pepBoost:0,stun:0,toxic:0,oilSlick:0,
```

替換成：
```js
    this.activeEffects={foil:0,garlic:0,sauce:0,slowpow:0,pepBoost:0,stun:0,toxic:0,oilSlick:0,slip:0,sauceCharge:0,
```

找到 `create()` 方法中 `this.oilSlicks=[];` 這行（~1478），在其後加入：
```js
    this.iceTrail=[]; this.iceLastPos={x:0,y:0};
    this.saucePools=[]; this.lemonPuddles=[];
    this.trailLayer=this.add.graphics().setDepth(6);
```

- [ ] **Step 2：玩家留下冰跡**

找到玩家速度/移動更新的末尾，約在 `this.p.x=...` 賦值之後（約 2565 行附近）。在 `// lastDir 只從鍵盤輸入更新` 前加入：

```js
    // 冰跡留下（iceBoost 期間）
    if(this.activeEffects.iceBoost>0){
      const _id=Math.hypot(this.p.x-this.iceLastPos.x,this.p.y-this.iceLastPos.y);
      if(_id>=15){
        this.iceTrail.push({x:this.p.x,y:this.p.y,life:3.0,ownerId:'player'});
        this.iceLastPos={x:this.p.x,y:this.p.y};
      }
    }
```

- [ ] **Step 3：AI 留下冰跡（在 AI forEach 迴圈內）**

找到 AI forEach 內 `e.x+=e.vx; e.y+=e.vy;`（~2946），在其後加入：
```js
      // AI 冰跡留下
      if(e.activeEffects&&e.activeEffects.iceBoost>0){
        const _eid=Math.hypot(e.x-(e.iceLastX||0),e.y-(e.iceLastY||0));
        if(_eid>=15){
          this.iceTrail.push({x:e.x,y:e.y,life:3.0,ownerId:e.label});
          e.iceLastX=e.x; e.iceLastY=e.y;
        }
      }
```

- [ ] **Step 4：冰跡 update（衰減 + 碰撞）**

在 `mapItems` 拾取迴圈之前（~3025），加入：

```js
    // 冰跡更新
    this.iceTrail=this.iceTrail.filter(t=>{
      t.life-=dt;
      if(t.life<=0) return false;
      // 玩家踩到（非留跡者）
      if(t.ownerId!=='player'&&Math.hypot(this.p.x-t.x,this.p.y-t.y)<22){
        this.activeEffects.slip=Math.max(this.activeEffects.slip,1.0);
        this.activeEffects.slip=Math.max(this.activeEffects.slip,1.0);
      }
      // AI 踩到
      this.enemies.forEach(e=>{
        if(!e.alive||t.ownerId===e.label) return;
        if(Math.hypot(e.x-t.x,e.y-t.y)<22){
          if(e.activeEffects) e.activeEffects.slip=Math.max(e.activeEffects.slip||0,1.0);
          e.slipLastVx=e.vx; e.slipLastVy=e.vy;
        }
      });
      return true;
    });
```

- [ ] **Step 5：打滑效果套用到玩家移動**

找到（~2490）：
```js
    const SPD=isDash?120:this.charData.speed*(this.activeEffects.pepBoost>0?1.5:1)*(this.activeEffects.slowpow>0?0.5:1)*ultSpd*_ultSpdMul*_goldenSpd*_iceSpd;
```

在其前加入打滑狀態儲存：
```js
    if(this.activeEffects.slip>0&&!this._slipInit){this._slipInit=true;this._slipVx=(this.p.x-this._lastPX||0);this._slipVy=(this.p.y-this._lastPY||0);}
    if(this.activeEffects.slip<=0) this._slipInit=false;
    this._lastPX=this.p.x; this._lastPY=this.p.y;
```

找到移動輸入計算區段（約 2493）的 `let mx=0, my=0;` 後方，找到 `if(this.activeEffects.stun>0){mx=0;my=0;...}`（~2498），在該 if 下方加入：
```js
    if(this.activeEffects.slip>0){mx=0;my=0;} // 打滑：無法輸入
```

- [ ] **Step 6：打滑效果套用到 AI**

在 AI forEach 內，找到 `const onOil=...`（~2875）後，加入：
```js
      // 打滑判斷
      const onSlip=(e.activeEffects&&e.activeEffects.slip>0);
      if(onSlip){
        e.vx=e.slipLastVx||e.vx; e.vy=e.slipLastVy||e.vy; // 維持滑行速度
      }
```

然後在 AI 移動邏輯前（`if(e.chargeTimer<=0...`~2878）加上 `if(!onSlip){` 包住整段移動邏輯直到 `}`，並在移動邏輯後加 `}` 閉合。

- [ ] **Step 7：統一 trailLayer 繪製方法**

找到 `drawShrinkLayer()` 呼叫處（約 3515），在其前加入 `this.drawTrailEffects();`。

在 `drawShrinkLayer()` 定義前，新增方法（包含冰跡、醬油、檸檬、噴嚏，**Task 5/6/8 的繪圖都在此統一處理**，不需要獨立 draw 方法，也不各自 `g.clear()`）：

```js
  drawTrailEffects(){
    const g=this.trailLayer; g.clear(); // 只清一次
    this.iceTrail.forEach(t=>{
      const a=Math.min(0.55,t.life/3.0*0.55);
      g.fillStyle(0xaaddff,a); g.fillCircle(t.x,t.y,16);
      g.lineStyle(1,0xffffff,a*0.6); g.strokeCircle(t.x,t.y,16);
    });
    this.saucePools.forEach(sp=>{
      const a=Math.min(0.45,sp.life/8.0*0.45);
      g.fillStyle(0x5c3300,a); g.fillCircle(sp.x,sp.y,sp.r);
      g.lineStyle(2,0x3a1f00,a+0.2); g.strokeCircle(sp.x,sp.y,sp.r);
    });
    this.lemonPuddles.forEach(lp=>{
      const a=Math.min(0.5,lp.life/2.5*0.5);
      const wb=(Math.random()-0.5)*2;
      g.fillStyle(0xccdd22,a); g.fillCircle(lp.x+wb,lp.y+wb,lp.r);
      g.lineStyle(1,0x99aa00,a+0.1); g.strokeCircle(lp.x,lp.y,lp.r);
    });
    if(this._sneezeFx){
      const a=this._sneezeFx.life/0.3*0.7;
      const cx=this.p.x, cy=this.p.y;
      const ang=Math.atan2(this._sneezeFx.dy,this._sneezeFx.dx);
      const r=80*(1-this._sneezeFx.life/0.3)*0.8+20;
      g.fillStyle(0xffffff,a*0.35);
      g.beginPath(); g.moveTo(cx,cy);
      g.arc(cx,cy,r,ang-Math.PI/4,ang+Math.PI/4,false);
      g.closePath(); g.fillPath();
    }
  }
```

- [ ] **Step 8：HUD 顯示打滑狀態**

找到效果 HUD（~3034），在 `eff2` 陣列 push 的地方加：
```js
    if(ae2.slip>0)      eff2.push('⛸打滑 '+ae2.slip.toFixed(1)+'s');
    if(ae2.sauceCharge>0) eff2.push('🍶待佈陣 '+ae2.sauceCharge.toFixed(1)+'s');
```

- [ ] **Step 9：測試**
開啟遊戲，撿冰塊，在地圖上跑動 → 應留下藍白冰跡。讓 AI 走過冰跡 → AI 應短暫失控滑行。

- [ ] **Step 10：Commit**
```bash
git add index.html
git commit -m "feat: ice trail with slip effect"
```

---

### Task 3：鋁箔紙 → 反彈護盾

**Files:**
- Modify: `index.html` — `doPush()`、AI 推玩家程式碼、AI 推 AI 程式碼

- [ ] **Step 1：玩家 doPush 推敵時檢查 foil 反彈**

找到 `doPush()` 中玩家推人的衝刺判斷（在 `updatePush` 或 `dashState` 碰到敵人的地方，約 2905-2928），找到 AI 被玩家推到的 tween（`this.tweens.add({targets:eRef,...}`）後加入 foil 判斷：

在 AI 被推的程式碼塊（~2920-2927）：
```js
            const eRef=pTgt.ref, eIdx=pTgt.idx;
            const cBst=Math.min(1.5,1+(eRef.heat||0)/100*0.8);
            this.tweens.add({targets:eRef,
              x:eRef.x+pnx*pForce*cBst,y:eRef.y+pny*pForce*cBst,
              duration:240,ease:'Cubic.easeOut',
              onComplete:()=>this.checkEnemyFall(eRef,eIdx)});
```

替換成：
```js
            const eRef=pTgt.ref, eIdx=pTgt.idx;
            const cBst=Math.min(1.5,1+(eRef.heat||0)/100*0.8);
            // 鋁箔反彈：AI 有 foil 且玩家有 garlic → 玩家被彈回
            if((eRef.activeEffects&&eRef.activeEffects.foil>0)&&(ae&&ae.garlic>0)){
              const rx=this.p.x-pnx*pForce*cBst*2, ry=this.p.y-pny*pForce*cBst*2;
              this.tweens.add({targets:this.p,x:rx,y:ry,duration:240,ease:'Cubic.easeOut',
                onComplete:()=>{if(!inGrill(this.p.x,this.p.y)){this.subTxt.setText('反彈落下！');this.endGame(false);}}});
              this.showPop('🪞 反彈！');
              this.cameras.main.shake(200,0.012);
            } else {
              this.tweens.add({targets:eRef,
                x:eRef.x+pnx*pForce*cBst,y:eRef.y+pny*pForce*cBst,
                duration:240,ease:'Cubic.easeOut',
                onComplete:()=>this.checkEnemyFall(eRef,eIdx)});
            }
```

- [ ] **Step 2：AI 推玩家時檢查 foil 反彈**

找到（~2904-2918）AI 推玩家的程式碼塊，在 tween 前加入 foil 反彈判斷：

找到：
```js
          if(pd<44){
            e.pushTimer=pushCd+Math.random()*2;
            const pnx=(pTgt.x-e.x)/pd, pny=(pTgt.y-e.y)/pd;
            const _eGarlicBst=(e.activeEffects&&e.activeEffects.garlic>0)?1.7:1.0;
            const pForce=95*Math.min(2.0,1+e.heat/100*1.5)*_eGarlicBst;
            if(pTgt.isPlayer){
```

在 `if(pTgt.isPlayer){` 塊內，`this.tweens.add({targets:this.p,...` 前插入：
```js
              // foil 反彈：玩家有 foil 且 AI 有 garlic → AI 被彈回
              if(this.activeEffects.foil>0&&(e.activeEffects&&e.activeEffects.garlic>0)){
                const rnx=(e.x-this.p.x)/pd, rny=(e.y-this.p.y)/pd;
                this.tweens.add({targets:e,x:e.x+rnx*pForce*2,y:e.y+rny*pForce*2,
                  duration:240,ease:'Cubic.easeOut',
                  onComplete:()=>this.checkEnemyFall(e,i)});
                this.showPop('🪞 鋁箔反彈 '+e.label+'！');
                return; // 跳過後續推玩家邏輯
              }
```

- [ ] **Step 3：測試**
開啟遊戲，先撿鋁箔（有 foil），讓 AI 同時拿大蒜（可能需要多試幾局），被 AI 推時應看到「🪞 反彈！」且 AI 被彈出。

- [ ] **Step 4：Commit**
```bash
git add index.html
git commit -m "feat: foil reflect shield vs garlic push"
```

---

### Task 4：大蒜 → AOE 衝擊波

**Files:**
- Modify: `index.html` — `applyItem()`、update loop、新增 AOE 爆發視覺

- [ ] **Step 1：初始化 AOE flag**

找到 `create()` 中 `this.killCount=0;`（~1475），在其後加入：
```js
    this._garlicAoeDone=true; // 初始已觸發（防止開局誤發）
```

找到 `applyItem()` 中 `if(item.type==='garlic')` 那行（~2249）：
```js
    if(item.type==='garlic'){ae.garlic=item.dur+2; this.showPop('★ 大蒜！推力 ×1.7！'); this.playSound('good');}
```

替換成：
```js
    if(item.type==='garlic'){ae.garlic=item.dur+2; this._garlicAoeDone=false; this.showPop('★ 大蒜！推力 ×1.7！最後 1 秒會爆發！'); this.playSound('good');}
```

- [ ] **Step 2：AOE 觸發偵測**

在 mapItems 更新之後（~3032 後）、效果 HUD 之前，加入：

```js
    // 大蒜 AOE 衝擊波（最後 1 秒觸發）
    if(ae2.garlic>0&&ae2.garlic<=1.0&&!this._garlicAoeDone){
      this._garlicAoeDone=true;
      const aoeFx={r:0,life:0.35};
      this._garlicAoe=aoeFx;
      this.enemies.forEach((e,i)=>{
        if(!e.alive) return;
        const d=Math.hypot(e.x-this.p.x,e.y-this.p.y);
        if(d<100){
          const nx=(e.x-this.p.x)/(d||1), ny=(e.y-this.p.y)/(d||1);
          const force=130*(1-d/100);
          this.tweens.add({targets:e,x:e.x+nx*force,y:e.y+ny*force,
            duration:300,ease:'Cubic.easeOut',
            onComplete:()=>this.checkEnemyFall(e,i)});
        }
      });
      this.showPop('💥 大蒜爆發！');
      this.cameras.main.flash(120,255,230,100,false);
    }
    if(this._garlicAoe){
      this._garlicAoe.r+=(110-this._garlicAoe.r)*dt*8;
      this._garlicAoe.life-=dt;
      if(this._garlicAoe.life<=0) this._garlicAoe=null;
    }
```

- [ ] **Step 3：AOE 視覺繪製**

找到 `drawEventFx()` 方法內（~3344），在最後 `}` 前加入：

```js
    // 大蒜 AOE 擴散環
    if(this._garlicAoe){
      const a=Math.max(0,this._garlicAoe.life/0.35*0.7);
      g.lineStyle(3,0xffee44,a);
      g.strokeCircle(this.p.x,this.p.y,this._garlicAoe.r);
      g.fillStyle(0xffee44,a*0.15);
      g.fillCircle(this.p.x,this.p.y,this._garlicAoe.r);
    }
```

- [ ] **Step 4：AI 大蒜 AOE**

在 `applyItemToEnemy()` 中大蒜那行（Task 1 新增的）加入：
```js
    if(item.type==='garlic'){ ae.garlic=item.dur+2; e._garlicAoeDone=false; }
```

在 AI forEach 迴圈末尾（`e.activeEffects` timer 遞減旁），加入：
```js
      // AI 大蒜 AOE
      if(e.activeEffects&&e.activeEffects.garlic>0&&e.activeEffects.garlic<=1.0&&!e._garlicAoeDone){
        e._garlicAoeDone=true;
        // 推開玩家
        const _agd=Math.hypot(this.p.x-e.x,this.p.y-e.y);
        if(_agd<100){
          const _anx=(this.p.x-e.x)/(_agd||1),_any=(this.p.y-e.y)/(_agd||1);
          const _af=130*(1-_agd/100);
          const _nx=this.p.x+_anx*_af, _ny=this.p.y+_any*_af;
          this.tweens.add({targets:this.p,x:_nx,y:_ny,duration:300,ease:'Cubic.easeOut',
            onComplete:()=>{if(!inGrill(this.p.x,this.p.y)){this.subTxt.setText('被大蒜爆發推落！');this.endGame(false);}}});
          this.showPop('💥 '+e.label+' 大蒜爆發！');
        }
      }
```

- [ ] **Step 5：測試**
撿大蒜，等倒數到 1 秒時應看到黃色擴散環 + AI 被推開。

- [ ] **Step 6：Commit**
```bash
git add index.html
git commit -m "feat: garlic AOE shockwave at final second"
```

---

### Task 5：醬油 → 黏滯陷阱（S 鍵佈陣）

**Files:**
- Modify: `index.html` — `applyItem()` 醬油邏輯改為 sauceCharge、S 鍵 override、saucePools update/draw

- [ ] **Step 1：修改 `applyItem` 醬油**

找到（~2250）：
```js
    if(item.type==='sauce') {ae.sauce=item.dur;   this.showPop('🍶 醬油！降熱減半 5 秒！'); this.playSound('good');}
```

替換成：
```js
    if(item.type==='sauce') {ae.sauceCharge=5.0; this.showPop('🍶 醬油！按 S 佈陣！5 秒後自動！'); this.playSound('good');}
```

同時移除熱度乘算（找到 ~2595）：
```js
    const mult=_hsMul*this.charData.heatMult*(ae.sauce>0?0.5:1)*(armorOn?0.5:1)*this.levelData.heatMod;
```
替換成：
```js
    const mult=_hsMul*this.charData.heatMult*(armorOn?0.5:1)*this.levelData.heatMod;
```

- [ ] **Step 2：S 鍵 override（持有 sauceCharge 時佈陣）**

找到推擠按鍵判斷（~2576）：
```js
    if(this.keys.push.isDown&&!this.pushWas&&this.pushCD<=0) this.doPush();
```

替換成：
```js
    if(this.keys.push.isDown&&!this.pushWas){
      if(this.activeEffects.sauceCharge>0){ this._deploySaucePool('player'); }
      else if(this.pushCD<=0){ this.doPush(); }
    }
```

- [ ] **Step 3：新增 `_deploySaucePool()` 方法**

在 `doPush()` 前加入：
```js
  _deploySaucePool(ownerId){
    const ox=ownerId==='player'?this.p.x:null; // AI 另外傳 x,y
    const _x=arguments[1]||this.p.x, _y=arguments[2]||this.p.y;
    if(this.saucePools.length>=2) this.saucePools.shift();
    this.saucePools.push({x:_x,y:_y,r:55,life:8.0,ownerId});
    if(ownerId==='player'){
      this.activeEffects.sauceCharge=0;
      this.showPop('🍶 醬油灘！');
    }
  }
```

- [ ] **Step 4：自動佈陣（5 秒倒數完）**

在 mapItems 更新區段前，加入：
```js
    // 醬油自動佈陣（倒數歸零）
    if(ae2.sauceCharge>0&&ae2.sauceCharge-dt<=0){
      this._deploySaucePool('player');
    }
```

- [ ] **Step 5：AI 醬油佈陣**

在 AI forEach 迴圈內 activeEffects 遞減後加入：
```js
      // AI 醬油自動佈陣：靠近玩家 60px 或倒數歸零
      if(e.activeEffects&&e.activeEffects.sauceCharge>0){
        const _sdist=Math.hypot(this.p.x-e.x,this.p.y-e.y);
        if(_sdist<60||e.activeEffects.sauceCharge<=dt){
          if(this.saucePools.length>=2) this.saucePools.shift();
          this.saucePools.push({x:e.x,y:e.y,r:55,life:8.0,ownerId:e.label});
          e.activeEffects.sauceCharge=0;
        }
      }
```

- [ ] **Step 6：saucePools update（減速效果）**

在冰跡更新後，加入：
```js
    // 醬油灘更新
    this.saucePools=this.saucePools.filter(sp=>{
      sp.life-=dt;
      if(sp.life<=0) return false;
      // 玩家（非佈陣者）踩到
      if(sp.ownerId!=='player'&&Math.hypot(this.p.x-sp.x,this.p.y-sp.y)<sp.r){
        this.activeEffects.slowpow=Math.max(this.activeEffects.slowpow,0.3);
      }
      // AI 踩到
      this.enemies.forEach(e=>{
        if(!e.alive||sp.ownerId===e.label) return;
        if(Math.hypot(e.x-sp.x,e.y-sp.y)<sp.r){
          if(e.activeEffects) e.activeEffects.slip=0; // 不打滑
          e._sauceSlow=0.7; // 在 maxSpd 那行用這個乘數
        }
      });
      return true;
    });
```

找到 AI maxSpd（Task 1 修改過的）加入醬油慢速：
```js
      const _eSauceSlow=(e._sauceSlow&&e._sauceSlow<1)?e._sauceSlow:1.0;
      const maxSpd=(e.charging?4.5:2.8)*sSlow*capSlow*(onOil?0.7:1)*_ePepSpd*_eIceSpd*_eSauceSlow;
      e._sauceSlow=1.0; // 每幀重置，下幀重新判斷
```

- [ ] **Step 7：醬油繪製（已整合到 Task 2 的 `drawTrailEffects()`）**

無需額外步驟——`saucePools` 的繪製已包含在 Task 2 Step 7 的 `drawTrailEffects()` 方法內，`this.saucePools` 陣列存在即自動繪製。

- [ ] **Step 8：測試**
撿醬油 → HUD 顯示「🍶待佈陣 5s」→ 按 S 應在腳下出現褐色圓圈 → AI 走過應明顯變慢。

- [ ] **Step 9：Commit**
```bash
git add index.html
git commit -m "feat: sauce deployable trap with 5s countdown"
```

---

### Task 6：胡椒粉 → 打噴嚏擊退

**Files:**
- Modify: `index.html` — 每幀追蹤 pepBoost 轉換、噴嚏擊退邏輯、視覺

- [ ] **Step 1：初始化 flag**

在 `create()` `this._garlicAoeDone=true;` 旁加入：
```js
    this._pepWas=false;
```

- [ ] **Step 2：噴嚏偵測與觸發**

在大蒜 AOE 偵測程式碼後，加入：
```js
    // 胡椒噴嚏（pepBoost 結束瞬間）
    if(this._pepWas&&ae2.pepBoost<=0){
      const _snDir=this.lastDir||{x:1,y:0};
      this.enemies.forEach((e,i)=>{
        if(!e.alive) return;
        const dx=e.x-this.p.x, dy=e.y-this.p.y;
        const dist=Math.hypot(dx,dy)||1;
        if(dist>80) return;
        // 扇形判斷（±45° = 點積 > cos(45°) ≈ 0.707）
        const dot=(dx/dist)*_snDir.x+(dy/dist)*_snDir.y;
        if(dot<0.707) return;
        const force=160*(1-dist/80);
        const nx=dx/dist, ny=dy/dist;
        this.tweens.add({targets:e,x:e.x+nx*force,y:e.y+ny*force,
          duration:280,ease:'Cubic.easeOut',
          onComplete:()=>this.checkEnemyFall(e,i)});
      });
      this.showPop('💨 哈啾！');
      this._sneezeFx={dx:_snDir.x,dy:_snDir.y,life:0.3};
    }
    this._pepWas=ae2.pepBoost>0;
    // 噴嚏 fx 倒計時
    if(this._sneezeFx) this._sneezeFx.life-=dt;
    if(this._sneezeFx&&this._sneezeFx.life<=0) this._sneezeFx=null;
```

- [ ] **Step 3：噴嚏視覺繪製（已整合到 `drawTrailEffects()`）**

`_sneezeFx` 的扇形繪製已包含在 Task 2 Step 7 的 `drawTrailEffects()` 方法內，無需獨立方法。

確認 Task 6 Step 1 的初始化區段加入：
```js
    this._sneezeFx=null;
    this._pepWas=false;
```

- [ ] **Step 4：測試**
撿胡椒粉，速度加成結束瞬間（3 秒後）應對面前敵人產生白色扇形 + 敵人被推飛，console 無報錯。

- [ ] **Step 5：Commit**
```bash
git add index.html
git commit -m "feat: pepper sneeze AOE knockback on expiry"
```

---

## BATCH 2：場地事件

---

### Task 7：廚師叉子 → 紅色軌跡線 + 插地牆壁

**Files:**
- Modify: `index.html` — 叉子 draw（紅線）、叉子 update（stuck 延長 + 碰撞）

- [ ] **Step 1：延長 stuck 時間**

找到（~3324）：
```js
            ev.state='stuck'; ev.timer=1.8; ev.curY=ev.targetY;
```

替換成：
```js
            ev.state='stuck'; ev.timer=3.0; ev.curY=ev.targetY;
```

- [ ] **Step 2：stuck 碰撞（插地牆壁）**

在叉子 update 的 `else if(ev.state==='stuck'){` 塊內（~3331），在 `if(ev.timer<=0)` 前加入：
```js
          // 插地牆壁：玩家被推到叉子 → 反彈
          const _skd=Math.abs(this.p.x-ev.x);
          if(_skd<28&&Math.abs(this.p.y-ev.targetY)<32){
            const _skDir=this.p.x>ev.x?1:-1;
            const _nx=this.p.x+_skDir*50;
            if(inGrill(_nx,this.p.y)){
              this.p.x=_nx;
              this.showPop('⚡ 撞到叉子！');
            }
          }
```

- [ ] **Step 3：紅色軌跡線（warn 狀態繪製）**

找到叉子 draw 區段（~3449，在 `drawEventFx()` 內找到 `if(ev.type==='skewer')`）：

在 `warn` 狀態繪製前加入紅色雷射線：
```js
        if(ev.state==='warn'){
          // 紅色軌跡線
          const _rt=1-ev.timer/1.6;
          g.lineStyle(2,0xff2200,0.3+0.5*_rt);
          g.lineBetween(ev.x,G.y-10,ev.x,ev.targetY);
```

- [ ] **Step 4：測試**
觀察叉子落下前有紅色虛線 → 插地後停留 3 秒 → 走到叉子旁會被彈開。

- [ ] **Step 5：Commit**
```bash
git add index.html
git commit -m "feat: skewer red warning line and ground wall"
```

---

### Task 8：檸檬雨 → 擠檸檬感酸汁殘留

**Files:**
- Modify: `index.html` — 落地後產生 `lemonPuddles`、puddle update/draw

- [ ] **Step 1：lemonPuddles update**

在 saucePools 更新後加入：
```js
    // 檸檬酸汁殘留更新
    this.lemonPuddles=this.lemonPuddles.filter(lp=>{
      lp.life-=dt;
      if(lp.life<=0) return false;
      if(Math.hypot(this.p.x-lp.x,this.p.y-lp.y)<lp.r){
        this.activeEffects.slowpow=Math.max(this.activeEffects.slowpow,0.3);
        this.heat=Math.min(100,this.heat+6*dt);
      }
      this.enemies.forEach(e=>{
        if(!e.alive) return;
        if(Math.hypot(e.x-lp.x,e.y-lp.y)<lp.r){
          if(e.activeEffects) e.activeEffects.slowpow=Math.max(e.activeEffects.slowpow||0,0.3);
          e.heat=Math.min(100,(e.heat||0)+6*dt);
        }
      });
      return true;
    });
```

- [ ] **Step 2：落地時產生濺射酸汁點**

找到（~3252）檸檬落地時 `ev.state='splash'` 那行：
```js
            ev.state='splash'; ev.splashR=8; ev.timer=0.55;
```

在其後加入：
```js
            // 濺射酸汁點（擠檸檬感）
            const _cnt=4+Math.floor(Math.random()*3);
            for(let _li=0;_li<_cnt;_li++){
              const _ang=Math.random()*Math.PI*2;
              const _dst=20+Math.random()*40;
              this.lemonPuddles.push({
                x:ev.x+Math.cos(_ang)*_dst, y:ev.y+Math.sin(_ang)*_dst,
                r:18+Math.random()*8, life:2.5
              });
            }
```

- [ ] **Step 3：lemonPuddles 繪製（已整合到 `drawTrailEffects()`）**

`lemonPuddles` 繪製已包含在 Task 2 Step 7 的 `drawTrailEffects()` 方法內，無需獨立步驟。

- [ ] **Step 4：AI 受 lemonPuddles 影響**

在 AI maxSpd 區段加入 lemonPuddles 慢速（找到 `_eSauceSlow`）：
```js
      const _eLemonSlow=this.lemonPuddles.some(lp=>Math.hypot(e.x-lp.x,e.y-lp.y)<lp.r)?0.7:1.0;
      const maxSpd=(e.charging?4.5:2.8)*sSlow*capSlow*(onOil?0.7:1)*_ePepSpd*_eIceSpd*_eSauceSlow*_eLemonSlow;
```

- [ ] **Step 5：測試**
等待檸檬雨事件，觀察落地後出現多個黃綠色小水坑，走入後速度下降 + 熱度緩慢上升。

- [ ] **Step 6：Commit**
```bash
git add index.html
git commit -m "feat: lemon puddles splash effect"
```

---

### Task 9：烤盤破洞 → 發紅預警 + 連鎖崩塌

**Files:**
- Modify: `index.html` — `drawHoles()`（warn 視覺）、`updateHoles()`（連鎖崩塌）

- [ ] **Step 1：連鎖崩塌（叉子加速破洞）**

在 `updateHoles()` 內、`this.holes=this.holes.filter(h=>{` 迴圈中，找到 `if(h.state==='warn'){` 塊（~3564）：

```js
      if(h.state==='warn'){
        if(h.timer<=0){h.state='active';h.timer=4+Math.random()*3;h.alpha=0;}
        return true;
      }
```

替換成：
```js
      if(h.state==='warn'){
        // 連鎖崩塌：stuck 叉子在洞上方 → 加速崩塌
        const skNear=this.evtQueue.some(ev=>ev.type==='skewer'&&ev.state==='stuck'&&
          Math.hypot(ev.x-h.x,ev.targetY-h.y)<40);
        if(h.timer<=0||skNear){h.state='active';h.timer=4+Math.random()*3;h.alpha=0;}
        return true;
      }
```

- [ ] **Step 2：發紅預警視覺**

找到 `drawHoles()` 方法（~3592），在現有洞繪製前找到 warn 狀態的繪製（或沒有，則新增）：

在洞的 forEach 內，找到 `h.state==='warn'` 的視覺處理（若沒有明確 warn 繪製則在 forEach 開頭加）：

```js
    this.holes.forEach(h=>{
      if(h.state==='warn'){
        // 發紅預警：脈動橘紅光暈 + 抖動
        const pulse=0.3+0.4*Math.sin(ph*8);
        const wx=h.x+(Math.random()-0.5)*2, wy=h.y+(Math.random()-0.5)*2;
        g.fillStyle(0xff3300,pulse*0.5);
        g.fillCircle(wx,wy,h.r+4);
        g.lineStyle(2,0xff6600,pulse);
        g.strokeCircle(wx,wy,h.r+4);
        return;
      }
```

（在 `return;` 後繼續原有的 active/closing 繪製邏輯）

- [ ] **Step 3：測試**
等待破洞事件 → 應看到橘紅脈動預警（2.2 秒）→ 若叉子剛好插在附近，洞直接加速出現。

- [ ] **Step 4：Commit**
```bash
git add index.html
git commit -m "feat: hole red warning pulse and skewer chain collapse"
```

---

### Task 10：場地縮小 → 邊緣火圈

**Files:**
- Modify: `index.html` — `updateShrink()` 加熱邏輯、`drawShrinkLayer()` 火焰粒子

- [ ] **Step 1：邊緣加熱**

在 `updateShrink()` 方法內（~3472），在 shrinkPad 更新邏輯後（~3487 後）加入：

```js
    // 邊緣火圈：靠近縮圈邊界加熱
    if(this.shrinkPad>0&&this.alive){
      const pad=this.shrinkPad;
      const edgeDist=Math.min(
        this.p.x-(G.x+pad), (G.x+G.w-pad)-this.p.x,
        this.p.y-(G.y+pad), (G.y+G.h-pad)-this.p.y
      );
      if(edgeDist<30) this.heat=Math.min(100,this.heat+35*dt);
      // AI 邊緣加熱
      this.enemies.forEach(e=>{
        if(!e.alive) return;
        const eDist=Math.min(e.x-(G.x+pad),(G.x+G.w-pad)-e.x,e.y-(G.y+pad),(G.y+G.h-pad)-e.y);
        if(eDist<30) e.heat=Math.min(100,e.heat+35*dt);
      });
    }
```

- [ ] **Step 2：火焰粒子視覺**

在 `drawShrinkLayer()` 方法（~3517）內，找到 shrinkPad>0 的繪製邏輯後，加入火焰粒子：

在 `if(this.shrinkWarning){` 塊（~3531）後加入：

```js
    // 縮圈邊緣火焰粒子
    if(pad>0){
      const _fp=10+Math.floor(Math.random()*4);
      for(let _fi=0;_fi<_fp;_fi++){
        const _fa=0.3+Math.random()*0.5;
        const _fr=3+Math.random()*4;
        g.fillStyle(Math.random()<0.5?0xff6600:0xff3300,_fa);
        // 沿四邊隨機分布
        let _fx,_fy;
        const _side=Math.floor(Math.random()*4);
        if(_side===0){_fx=G.x+pad+Math.random()*(G.w-pad*2);_fy=G.y+pad+Math.random()*20-10;}
        else if(_side===1){_fx=G.x+pad+Math.random()*(G.w-pad*2);_fy=G.y+G.h-pad+Math.random()*20-10;}
        else if(_side===2){_fx=G.x+pad+Math.random()*20-10;_fy=G.y+pad+Math.random()*(G.h-pad*2);}
        else{_fx=G.x+G.w-pad+Math.random()*20-10;_fy=G.y+pad+Math.random()*(G.h-pad*2);}
        g.fillCircle(_fx,_fy,_fr);
      }
    }
```

- [ ] **Step 3：測試**
等 30 秒後場地縮圈，靠近縮圈邊緣應看到橘紅粒子，熱度條迅速上升。

- [ ] **Step 4：Commit**
```bash
git add index.html
git commit -m "feat: shrink edge fire ring with heat damage"
```

---

### Task 11：地圖傾斜 → 視覺強化 + 低側加速帶

**Files:**
- Modify: `index.html` — tilt update（低側加速帶）、draw（warn 警示帶、道具滑動）

- [ ] **Step 1：低側加速帶**

找到 tilt active 狀態處理（~2797-2804），在玩家受傾斜力計算（~2552）後加入：

```js
    // 傾斜低側加速帶
    if(this.tilt&&this.tilt.state==='active'){
      const _tf=this.tilt;
      const _lowEdgeX=_tf.x>0?G.x+G.w-this.shrinkPad:G.x+this.shrinkPad;
      const _lowEdgeY=_tf.y>0?G.y+G.h-this.shrinkPad:G.y+this.shrinkPad;
      const _distToLow=_tf.x!==0?
        Math.abs(this.p.x-_lowEdgeX):Math.abs(this.p.y-_lowEdgeY);
      if(_distToLow<35){
        // 加速帶：額外 ×1.5 傾斜力
        this.p.x+=_tf.x*_tf.force*0.5*dt;
        this.p.y+=_tf.y*_tf.force*0.5*dt;
      }
    }
```

- [ ] **Step 2：道具跟著傾斜滑動**

在 tilt active 狀態更新中（~2797）加入：
```js
      // 道具跟著傾斜力滑動
      if(this.tilt.state==='active'){
        this.mapItems.forEach(item=>{
          item.x=Phaser.Math.Clamp(item.x+this.tilt.x*15*dt,G.x+30,G.x+G.w-30);
          item.y=Phaser.Math.Clamp(item.y+this.tilt.y*15*dt,G.y+30,G.y+G.h-30);
          item.img.setPosition(item.x,item.y);
          item.gfx.clear();
          item.gfx.fillStyle(item.good?0x00ccff:0xff3300,0.45);
          item.gfx.fillCircle(item.x,item.y,23);
        });
      }
```

- [ ] **Step 3：warn 階段橘紅警示帶繪製**

找到 tilt 相關繪圖（沒有獨立 draw 方法，在 `updateTilt` 或 `drawEventFx` 裡）。找到 tiltTxt 的設定（~2793），在其後加入警示帶繪製：

在 `drawEventFx()` 最後加入：
```js
    // 傾斜警示帶
    if(this.tilt&&this.tilt.state==='warn'){
      const _t=this.tilt;
      const blink=0.25+0.35*Math.sin(ph*6);
      g.fillStyle(0xff4400,blink*0.5);
      if(_t.x>0)      g.fillRect(G.x+G.w-20,G.y,20,G.h); // 右側危險
      else if(_t.x<0) g.fillRect(G.x,G.y,20,G.h);         // 左側危險
      else if(_t.y>0) g.fillRect(G.x,G.y+G.h-20,G.w,20);  // 下側危險
      else            g.fillRect(G.x,G.y,G.w,20);          // 上側危險
    }
```

- [ ] **Step 4：測試**
等待傾斜事件（lv3 最常出現），warn 時應在低側邊緣看到橘紅閃爍帶，active 時靠近低側邊緣會感受到額外推力，道具也跟著滑動。

- [ ] **Step 5：Commit**
```bash
git add index.html
git commit -m "feat: tilt warning band, low-side acceleration, item sliding"
```

---

## 清理與整合

### Task 12：收尾清理

- [ ] **Step 1：確認 `endGame()` 清空新陣列**

找到 `endGame()` 方法（~2339），在其開頭加入：
```js
    this.iceTrail=[]; this.saucePools=[]; this.lemonPuddles=[];
    this._garlicAoe=null; this._sneezeFx=null;
```

- [ ] **Step 2：確認說明面板更新**

找到說明面板（Guide overlay）中 GOODS 陣列（~1404），更新道具說明：
```js
    const GOODS=[
      {icon:'❄️',name:'冰塊',     eff:'降熱 -42%＋留下結冰路徑，他人踩到打滑 1 秒'},
      {icon:'◎', name:'鋁箔紙',   eff:'7 秒隔熱；被大蒜玩家推 → 攻擊者反彈'},
      {icon:'★', name:'大蒜',     eff:'5 秒推力 ×1.7；最後 1 秒自動 AOE 爆發'},
      {icon:'🍶',name:'醬油',     eff:'持有 5 秒，按 S 在腳下佈黏滯陷阱'},
      {icon:'🌶',name:'胡椒粉',   eff:'3 秒加速 ×1.5；結束時哈啾！擊退前方敵人'},
    ];
```

- [ ] **Step 3：全局測試（完整一局）**
開一局 3 分鐘遊戲，確認：
- AI 會撿道具（觀察他們的行為變化）
- 冰跡留下且打滑有效
- 大蒜最後 1 秒爆炸
- 醬油可 S 鍵佈陣
- 叉子有紅線且插地有彈力
- 縮圈邊緣有火粒子且熱度上升
- F12 無報錯

- [ ] **Step 4：最終 Commit**
```bash
git add index.html
git commit -m "feat: complete items+events enhancement batch 1 & 2"
```
