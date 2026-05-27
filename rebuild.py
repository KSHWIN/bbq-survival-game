"""
把 IMG block 從舊 HTML 提取出來，接上全新的乾淨遊戲代碼。
"""
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    old = f.read()

img_start = old.find("const IMG = {")
img_end   = old.find("\n};", img_start) + 3
IMG_BLOCK = old[img_start:img_end]

GAME_CODE = r'''
const W = 800, H = 580;
const G = { x: 110, y: 85, w: 580, h: 410 };

const CHARS = [
  { key:'pork',     name:'五花肉', img:'char_pork',     speed:90,  heatMult:1.0, weight:1.5, ability:'滑油衝刺', abilityDesc:'推力×1.5，炸開周圍所有食材',        stats:{'血量':'★★★','速度':'★☆☆','耐熱':'★★☆'}, color:0xffbbaa },
  { key:'beef',     name:'牛小排', img:'char_beef',     speed:95,  heatMult:0.9, weight:1.3, ability:'厚實裝甲', abilityDesc:'短暫減少熟度累積50%',                stats:{'血量':'★★☆','速度':'★★☆','耐熱':'★☆☆'}, color:0xcc6633 },
  { key:'mushroom', name:'香菇',   img:'char_mushroom', speed:155, heatMult:1.3, weight:0.7, ability:'縮水跳躍', abilityDesc:'被推瞬間可反向彈跳脫逃',              stats:{'血量':'★☆☆','速度':'★★★','耐熱':'★★★'}, color:0xaa7744 },
  { key:'corn',     name:'玉米',   img:'char_corn',     speed:115, heatMult:1.0, weight:1.0, ability:'爆米花',   abilityDesc:'熟度≥70%按S引爆，炸飛周圍',          stats:{'血量':'★★☆','速度':'★★☆','耐熱':'★★☆'}, color:0xffee44 },
  { key:'wing',     name:'雞翅',   img:'char_wing',     speed:165, heatMult:1.2, weight:0.8, ability:'短距滑翔', abilityDesc:'可飛越火焰落到另一側',                stats:{'血量':'★☆☆','速度':'★★★','耐熱':'★★☆'}, color:0xddaa44 },
  { key:'shrimp',   name:'蝦子',   img:'char_shrimp',   speed:140, heatMult:1.0, weight:0.7, ability:'彎身彈射', abilityDesc:'蓄力後弧線彈射到指定位置',            stats:{'血量':'★☆☆','速度':'★★★','耐熱':'★★☆'}, color:0xff8866 },
  { key:'tofu',     name:'豆腐',   img:'char_tofu',     speed:80,  heatMult:0.8, weight:0.6, ability:'吸熱護盾', abilityDesc:'吸收周圍食材熟度，自身上限+30%',      stats:{'血量':'★★☆','速度':'★☆☆','耐熱':'★☆☆'}, color:0xeeeedd },
  { key:'bacon',    name:'培根',   img:'char_bacon',    speed:105, heatMult:1.4, weight:1.0, ability:'捲縮甩打', abilityDesc:'旋轉陀螺，甩飛周圍所有食材',          stats:{'血量':'★☆☆','速度':'★★☆','耐熱':'★★★'}, color:0xdd4422 },
  { key:'pepper',   name:'青椒',   img:'char_pepper',   speed:110, heatMult:1.25,weight:0.8, ability:'噴辣氣',   abilityDesc:'使接觸食材減速並附加熟度+10%',        stats:{'血量':'★★☆','速度':'★★☆','耐熱':'★★☆'}, color:0x44cc44 },
  { key:'saury',    name:'秋刀魚', img:'char_saury',    speed:125, heatMult:1.0, weight:1.2, ability:'刀型衝刺', abilityDesc:'沿長軸高速衝刺，撞飛沿路食材',        stats:{'血量':'★★☆','速度':'★★☆','耐熱':'★★☆'}, color:0x8899cc },
];

function inGrill(x,y,m=0){ return x>=G.x+m&&x<=G.x+G.w-m&&y>=G.y+m&&y<=G.y+G.h-m; }

// ── Boot Scene ──────────────────────────────────────────
class BootScene extends Phaser.Scene {
  constructor(){ super('Boot'); }
  create(){
    this.add.rectangle(W/2,H/2,W,H,0x0a0400);
    const txt = this.add.text(W/2,H/2-18,'載入中...',{fontSize:'20px',color:'#ff8800',fontFamily:'sans-serif'}).setOrigin(0.5);
    const bgBg = this.add.rectangle(W/2,H/2+16,300,14,0x332200).setOrigin(0.5);
    const bgFg = this.add.rectangle(W/2-150,H/2+16,0,12,0xff6600).setOrigin(0,0.5);
    const keys = Object.keys(IMG);
    let done=0;
    const onAdded=()=>{ done++; bgFg.width=(done/keys.length)*300; txt.setText('載入中 '+done+'/'+keys.length); if(done>=keys.length) this.scene.start('Select'); };
    keys.forEach(k=>{ if(this.textures.exists(k)){onAdded();return;} this.textures.once('addtexture-'+k,onAdded); this.textures.once('onerror-'+k,onAdded); this.textures.addBase64(k,IMG[k]); });
  }
}

// ── Select Scene ─────────────────────────────────────────
class SelectScene extends Phaser.Scene {
  constructor(){ super('Select'); }
  create(){
    this.sel=0;
    if(this.textures.exists('grill_bg')) this.add.image(W/2,H/2,'grill_bg').setDisplaySize(W,H).setAlpha(0.3);
    this.add.rectangle(W/2,H/2,W,H,0x000000,0.6);
    this.add.text(W/2,30,'烤肉求生',{fontSize:'40px',color:'#ff8800',fontFamily:'sans-serif',fontStyle:'bold',stroke:'#ff3300',strokeThickness:4}).setOrigin(0.5);
    this.add.text(W/2,72,'選擇你的食材——你不甘心就這樣被烤熟',{fontSize:'14px',color:'#cc8844',fontFamily:'sans-serif'}).setOrigin(0.5);
    const cols=5,cw=140,ch=195,gapX=10,gapY=12;
    const startX=(W-cols*cw-(cols-1)*gapX)/2+cw/2, startY=100+ch/2;
    this.cards=[];
    CHARS.forEach((c,i)=>{
      const x=startX+(i%cols)*(cw+gapX), y=startY+Math.floor(i/cols)*(ch+gapY);
      const card=this.add.container(x,y);
      const bg=this.add.rectangle(0,0,cw,ch,0x180d00,0.9).setStrokeStyle(2,0x664422);
      let portrait;
      if(this.textures.exists(c.img)) portrait=this.add.image(0,-52,c.img).setDisplaySize(110,110);
      else portrait=this.add.rectangle(0,-52,100,100,c.color,0.75).setStrokeStyle(2,0xffffff);
      const nameT=this.add.text(0,12,c.name,{fontSize:'16px',color:'#ffdd88',fontFamily:'sans-serif',fontStyle:'bold'}).setOrigin(0.5);
      const abilT=this.add.text(0,32,'✦ '+c.ability,{fontSize:'11px',color:'#66ccff',fontFamily:'sans-serif'}).setOrigin(0.5);
      const spdT =this.add.text(0,50,'速'+c.stats['速度']+' 熱'+c.stats['耐熱'],{fontSize:'11px',color:'#999988',fontFamily:'sans-serif'}).setOrigin(0.5);
      card.add([this.add.rectangle(3,3,cw,ch,0x000000,0.5),bg,portrait,nameT,abilT,spdT]);
      card.setInteractive(new Phaser.Geom.Rectangle(-cw/2,-ch/2,cw,ch),Phaser.Geom.Rectangle.Contains);
      card.on('pointerdown',()=>this.startGame(i));
      card.on('pointerover',()=>this.setSel(i));
      this.cards.push({container:card,bg});
    });
    this.detailTxt=this.add.text(W/2,H-28,'',{fontSize:'13px',color:'#ffcc88',fontFamily:'sans-serif',align:'center'}).setOrigin(0.5);
    this.add.rectangle(W/2,H-28,W-20,38,0x110800,0.85).setStrokeStyle(1,0x664422).setDepth(-1);
    this.input.keyboard.on('keydown-LEFT', ()=>this.setSel((this.sel+CHARS.length-1)%CHARS.length));
    this.input.keyboard.on('keydown-RIGHT',()=>this.setSel((this.sel+1)%CHARS.length));
    this.input.keyboard.on('keydown-UP',   ()=>this.setSel((this.sel+CHARS.length-5)%CHARS.length));
    this.input.keyboard.on('keydown-DOWN', ()=>this.setSel((this.sel+5)%CHARS.length));
    this.input.keyboard.on('keydown-ENTER',()=>this.startGame(this.sel));
    this.input.keyboard.on('keydown-SPACE',()=>this.startGame(this.sel));
    this.setSel(0);
  }
  setSel(i){
    this.sel=i;
    const c=CHARS[i];
    this.cards.forEach((card,idx)=>{ const a=idx===i; card.bg.setStrokeStyle(a?3:2,a?0xffaa00:0x664422); card.container.setScale(a?1.07:1).setDepth(a?10:0); });
    this.detailTxt.setText(c.name+' ✦ '+c.ability+'：'+c.abilityDesc+'  |  點擊或 Enter 出戰');
  }
  startGame(i){ this.scene.start('Game',{char:CHARS[i]}); }
}

// ── Game Scene ───────────────────────────────────────────
class GameScene extends Phaser.Scene {
  constructor(){ super('Game'); }
  init(data){ this.charData=data.char||CHARS[0]; }

  create(){
    const c=this.charData;
    this.heat=0; this.alive=true; this.pushCD=0; this.timeLeft=60;
    this.lastDir={x:1,y:0}; this.firePhase=0; this.pushWas=false; this.wobbleTween=null;
    this.forkTimer=4; this.fork=null;
    this.forkInterval=()=>5+Math.random()*4;

    // 火焰：各自獨立振盪 + 會移動到新位置
    const rndPos=()=>({ x:G.x+70+Math.random()*(G.w-140), y:G.y+70+Math.random()*(G.h-140) });
    this.firePts=[0,1,2,3,4].map((_,i)=>{
      const p=rndPos();
      return { x:p.x,y:p.y, tx:p.x,ty:p.y, state:'active', timer:3+i*1.2, r:40, spd:0.7+Math.random()*0.7, ph:Math.random()*Math.PI*2 };
    });
    this.FIRE_R_BASE=40; this.FIRE_R_AMP=18;

    // 圖層
    this.grillLayer=this.add.graphics();
    this.fireLayer =this.add.graphics();
    this.forkLayer =this.add.graphics();
    this.fxLayer   =this.add.graphics();
    this.drawGrill();

    // 玩家
    this.p={x:G.x+G.w/2, y:G.y+G.h/2+60};
    this.playerSprite=this.textures.exists(c.img)
      ? this.add.image(this.p.x,this.p.y,c.img).setDisplaySize(52,52).setDepth(10) : null;
    this.sweatTxt=this.add.text(0,0,'',{fontSize:'12px',fontFamily:'sans-serif'}).setDepth(20).setVisible(false);

    // 廚師
    this.chefSprite=this.textures.exists('chef')
      ? this.add.image(-100,-100,'chef').setDisplaySize(80,80).setDepth(25).setVisible(false) : null;

    // 敵人（選非玩家的前2個）
    const aiChars=CHARS.filter(ch=>ch.key!==c.key).slice(0,2);
    this.enemies=aiChars.map((ch,i)=>({
      x:i===0?240:510, y:i===0?220:340, r:18,
      vx:i===0?1.3:-1.1, vy:i===0?0.9:1.2,
      heat:0, alive:true, label:ch.name, img:ch.img,
    }));
    this.enemySprites=this.enemies.map(e=>
      this.textures.exists(e.img) ? this.add.image(e.x,e.y,e.img).setDisplaySize(44,44).setDepth(9) : null
    );
    this.enemyFx=this.enemies.map(()=>this.add.text(0,0,'').setFontSize(14).setDepth(20).setVisible(false));

    // UI
    const ts=(s,col='#ffcc66')=>({fontSize:s+'px',color:col,fontFamily:'sans-serif'});
    this.add.rectangle(0,0,320,78,0x000000,0.65).setOrigin(0,0);
    this.add.text(12,8,c.name,ts(14,'#ffaa44'));
    this.add.text(12,28,'熟度',ts(13));
    this.heatBarBg=this.add.rectangle(62,36,220,16,0x441100).setOrigin(0,0.5);
    this.heatBarFg=this.add.rectangle(62,36,0,14,0xff4400).setOrigin(0,0.5);
    this.heatTxt  =this.add.text(292,28,'0%',ts(12));
    this.add.text(12,50,'推擠[S]',ts(12,'#66ccff'));
    this.pushBarBg=this.add.rectangle(74,58,120,12,0x112244).setOrigin(0,0.5);
    this.pushBarFg=this.add.rectangle(74,58,120,10,0x44aaff).setOrigin(0,0.5);
    this.pushCdTxt=this.add.text(204,50,'Ready!',ts(11,'#66ccff'));
    this.timerTxt =this.add.text(W-14,14,'60s',ts(22)).setOrigin(1,0);
    this.popTxt   =this.add.text(W/2,G.y-28,'',ts(17,'#ffff44')).setOrigin(0.5).setDepth(30);
    this.statusTxt=this.add.text(W/2,H/2-30,'',{fontSize:'44px',color:'#ff3333',fontFamily:'sans-serif',fontStyle:'bold',stroke:'#000',strokeThickness:6}).setOrigin(0.5).setDepth(40);
    this.subTxt   =this.add.text(W/2,H/2+28,'',ts(20,'#ffaaaa')).setOrigin(0.5).setDepth(40);

    // 輸入（方向鍵移動，S 推擠）
    this.keys=this.input.keyboard.addKeys({
      up:Phaser.Input.Keyboard.KeyCodes.UP,
      down:Phaser.Input.Keyboard.KeyCodes.DOWN,
      left:Phaser.Input.Keyboard.KeyCodes.LEFT,
      right:Phaser.Input.Keyboard.KeyCodes.RIGHT,
      push:Phaser.Input.Keyboard.KeyCodes.S,
      restart:Phaser.Input.Keyboard.KeyCodes.R,
      back:Phaser.Input.Keyboard.KeyCodes.ESC,
    });

    this.time.addEvent({delay:1000,loop:true,callback:()=>{
      if(!this.alive) return;
      this.timeLeft--;
      if(this.timeLeft<=0) this.endGame(true);
    }});
  }

  drawGrill(){
    const g=this.grillLayer; g.clear();
    // 外框
    g.fillStyle(0x0d0600); g.fillRect(G.x-10,G.y-10,G.w+20,G.h+20);
    // 用 grill_bg 圖作底（如果存在）
    if(this.textures.exists('grill_bg')){
      this.grillBgImg=this.add.image(G.x+G.w/2,G.y+G.h/2,'grill_bg').setDisplaySize(G.w,G.h).setDepth(-1);
    } else {
      g.fillStyle(0x232323); g.fillRect(G.x,G.y,G.w,G.h);
      g.lineStyle(1.5,0x383838);
      for(let x=G.x;x<=G.x+G.w;x+=40) g.lineBetween(x,G.y,x,G.y+G.h);
      for(let y=G.y;y<=G.y+G.h;y+=40) g.lineBetween(G.x,y,G.x+G.w,y);
    }
    // 危險邊緣
    g.lineStyle(3,0xff5500,0.55); g.strokeRect(G.x,G.y,G.w,G.h);
  }

  drawFires(phase){
    const g=this.fireLayer; g.clear();
    this.firePts.forEach(f=>{
      // 預警位置（淡黃閃爍）
      if(f.state==='warning'){
        const a=0.15+0.10*Math.sin(phase*6);
        g.fillStyle(0xffee44,a); g.fillCircle(f.tx,f.ty,this.FIRE_R_BASE);
        g.lineStyle(2,0xffcc00,a*3); g.strokeCircle(f.tx,f.ty,this.FIRE_R_BASE);
      }
      // 活躍火焰
      const alpha=f.state==='active'?1.0:0.45;
      const s=this.FIRE_R_BASE+this.FIRE_R_AMP*Math.sin(phase*f.spd+f.ph);
      f.r=Math.max(10,s);
      g.fillStyle(0xff5500,0.50*alpha); g.fillCircle(f.x,f.y,f.r);
      g.fillStyle(0xffaa00,0.34*alpha); g.fillCircle(f.x,f.y,f.r*0.55);
      g.fillStyle(0xffffff,0.11*alpha); g.fillCircle(f.x,f.y,f.r*0.22);
    });
  }

  onFire(x,y){
    return this.firePts.some(f=>f.state==='active'&&Math.hypot(x-f.x,y-f.y)<(f.r||this.FIRE_R_BASE)+8);
  }

  updateHeatFx(sprite,heat,sweatTxt){
    if(!sprite) return;
    const t=heat/100;
    sprite.setTint(Phaser.Display.Color.GetColor(255,Math.floor(255*(1-t*0.75)),Math.floor(255*(1-t))));
    if(heat>85){
      if(!this.wobbleTween||!this.wobbleTween.isPlaying()){
        this.wobbleTween=this.tweens.add({targets:sprite,scaleX:{from:0.82,to:1.18},scaleY:{from:1.15,to:0.85},angle:{from:-7,to:7},duration:70,yoyo:true,repeat:-1});
      }
      if(sweatTxt) sweatTxt.setVisible(true).setPosition(sprite.x+16,sprite.y-20).setText('😱');
    } else if(heat>60){
      if(!this.wobbleTween||!this.wobbleTween.isPlaying()){
        this.wobbleTween=this.tweens.add({targets:sprite,scaleX:{from:0.93,to:1.07},scaleY:{from:1.06,to:0.94},duration:160,yoyo:true,repeat:-1});
      }
      if(sweatTxt) sweatTxt.setVisible(true).setPosition(sprite.x+14,sprite.y-18).setText('😰');
    } else {
      if(this.wobbleTween){ this.wobbleTween.stop(); this.wobbleTween=null; sprite.setScale(1).setAngle(0); }
      if(sweatTxt) sweatTxt.setVisible(false);
    }
  }

  // ── 叉子（九宮格）────────────────────────────────────
  spawnFork(){
    const CELL=40, ZONE=3, half=CELL*ZONE/2;
    const maxCol=Math.floor(G.w/CELL)-ZONE;
    const maxRow=Math.floor(G.h/CELL)-ZONE;
    const cx=G.x+(Math.floor(Math.random()*maxCol)+1.5)*CELL;
    const cy=G.y+(Math.floor(Math.random()*maxRow)+1.5)*CELL;
    this.fork={cx,cy,half,phase:'warn',timer:0};
    if(this.chefSprite){
      this.chefSprite.setPosition(cx,G.y-90).setAngle(90).setVisible(true).setAlpha(0);
      this.tweens.add({targets:this.chefSprite,y:G.y-8,alpha:1,duration:600,ease:'Back.easeOut'});
    }
  }

  checkForkHit(){
    if(!this.fork) return;
    const {cx,cy,half}=this.fork;
    if(Math.abs(this.p.x-cx)<half&&Math.abs(this.p.y-cy)<half){
      this.subTxt.setText('被叉子刺中！');
      this.endGame(false);
    }
    if(this.chefSprite&&this.chefSprite.visible){
      this.time.delayedCall(250,()=>{
        if(!this.chefSprite) return;
        this.tweens.add({targets:this.chefSprite,y:G.y-110,alpha:0,duration:400,
          onComplete:()=>{ if(this.chefSprite) this.chefSprite.setVisible(false); }});
      });
    }
  }

  drawFork(){
    const g=this.forkLayer; g.clear();
    if(!this.fork) return;
    const {cx,cy,half,phase,timer}=this.fork;
    const CELL=40, isWarn=phase==='warn';
    if(isWarn){
      const a=0.13+0.10*Math.sin(timer*7);
      g.fillStyle(0xffee44,a); g.fillRect(cx-half,cy-half,half*2,half*2);
      g.lineStyle(2,0xffcc00,a*3.5);
      for(let i=0;i<=3;i++){
        g.lineBetween(cx-half+i*CELL,cy-half,cx-half+i*CELL,cy+half);
        g.lineBetween(cx-half,cy-half+i*CELL,cx+half,cy-half+i*CELL);
      }
    } else {
      g.fillStyle(0xff2200,0.55); g.fillRect(cx-half,cy-half,half*2,half*2);
      g.lineStyle(2,0xff6600,0.85);
      for(let i=0;i<=3;i++){
        g.lineBetween(cx-half+i*CELL,cy-half,cx-half+i*CELL,cy+half);
        g.lineBetween(cx-half,cy-half+i*CELL,cx+half,cy-half+i*CELL);
      }
      for(let r=0;r<3;r++) for(let c=0;c<3;c++){
        const fx=cx-half+(c+0.5)*CELL, fy=cy-half+(r+0.5)*CELL;
        [-5,0,5].forEach(off=>{ g.lineStyle(3,0xffffff,0.75); g.lineBetween(fx+off,fy-14,fx+off,fy+14); });
      }
    }
  }

  doPush(){
    this.pushCD=2;
    const c=this.charData, RANGE=70, FORCE=c.key==='pork'?115:82;
    const dx=this.lastDir.x, dy=this.lastDir.y;
    let hit=false;
    // 玉米引爆
    if(c.key==='corn'&&this.heat>=70){
      this.showPop('💥 爆米花！');
      this.enemies.forEach((e,i)=>{
        if(!e.alive) return;
        const d=Math.hypot(this.p.x-e.x,this.p.y-e.y);
        if(d<150){ const nx=d>0?(e.x-this.p.x)/d:1, ny=d>0?(e.y-this.p.y)/d:0; e.x+=nx*120; e.y+=ny*120; this.checkEnemyFall(e,i); }
      });
      this.heat=Math.max(0,this.heat-28); return;
    }
    this.enemies.forEach((e,i)=>{
      if(!e.alive) return;
      if(Math.hypot(this.p.x-e.x,this.p.y-e.y)<RANGE){ hit=true; e.x+=dx*FORCE; e.y+=dy*FORCE; this.checkEnemyFall(e,i); }
    });
    if(!hit){ const nx=this.p.x+dx*24, ny=this.p.y+dy*24; if(inGrill(nx,ny)){this.p.x=nx;this.p.y=ny;} }
    this.fxLayer.clear();
    this.fxLayer.lineStyle(3,0xffffff,0.8);
    this.fxLayer.lineBetween(this.p.x,this.p.y,this.p.x+dx*60,this.p.y+dy*60);
    this.time.delayedCall(120,()=>this.fxLayer.clear());
  }

  checkEnemyFall(e,i){
    if(!inGrill(e.x,e.y)){
      e.alive=false;
      if(this.enemySprites[i]) this.enemySprites[i].setVisible(false);
      if(this.enemyFx[i])      this.enemyFx[i].setVisible(false);
      this.showPop(e.label+' 掉落！');
      if(this.enemies.every(en=>!en.alive)){ this.time.delayedCall(600,()=>this.endGame(true)); }
    } else if(this.onFire(e.x,e.y)){ e.heat=Math.min(100,e.heat+22); }
  }

  showPop(msg){ this.popTxt.setText(msg); this.time.delayedCall(1600,()=>this.popTxt.setText('')); }

  endGame(win){
    this.alive=false;
    if(this.wobbleTween){this.wobbleTween.stop();this.wobbleTween=null;}
    if(this.playerSprite){
      if(!win) this.tweens.add({targets:this.playerSprite,scaleY:0.1,scaleX:1.5,alpha:0.3,duration:400});
      else     this.tweens.add({targets:this.playerSprite,scaleX:1.2,scaleY:1.2,angle:360,duration:600});
    }
    this.statusTxt.setColor(win?'#44ff88':'#ff3333').setText(win?'撐過去了！':'你死了');
    this.time.delayedCall(500,()=>{
      this.add.text(W/2,H/2+75,'按 R 重開  |  ESC 選角',{fontSize:'16px',color:'#aaaaaa',fontFamily:'sans-serif'}).setOrigin(0.5).setDepth(40);
    });
  }

  update(_,delta){
    const dt=delta/1000;
    if(Phaser.Input.Keyboard.JustDown(this.keys.restart)){this.scene.restart();return;}
    if(Phaser.Input.Keyboard.JustDown(this.keys.back)){this.scene.start('Select');return;}
    if(!this.alive) return;

    // 移動（方向鍵）
    const SPD=this.charData.speed;
    let mx=0, my=0;
    if(this.keys.left.isDown)  mx=-1;
    if(this.keys.right.isDown) mx=1;
    if(this.keys.up.isDown)    my=-1;
    if(this.keys.down.isDown)  my=1;
    if(mx&&my){mx*=0.707;my*=0.707;}
    const nx=this.p.x+mx*SPD*dt, ny=this.p.y+my*SPD*dt;
    if(!inGrill(nx,ny)){this.subTxt.setText('掉落烤盤！');this.endGame(false);return;}
    this.p.x=nx; this.p.y=ny;
    if(mx||my){this.lastDir.x=mx;this.lastDir.y=my;}

    // 推擠（S）
    this.pushCD=Math.max(0,this.pushCD-dt);
    if(this.keys.push.isDown&&!this.pushWas&&this.pushCD<=0) this.doPush();
    this.pushWas=this.keys.push.isDown;

    // 熟度（只增不減）
    const mult=this.charData.heatMult;
    if(this.onFire(this.p.x,this.p.y)) this.heat=Math.min(100,this.heat+15*mult*dt);
    else                                this.heat=Math.min(100,this.heat+1.2*dt);
    if(this.heat>=100){this.subTxt.setText('被烤熟了！');this.endGame(false);return;}

    // 玩家 sprite
    if(this.playerSprite) this.playerSprite.setPosition(this.p.x,this.p.y);
    this.updateHeatFx(this.playerSprite,this.heat,this.sweatTxt);

    // 火焰移動
    this.firePts.forEach(f=>{
      f.timer-=dt;
      if(f.state==='active'&&f.timer<=0){
        f.state='warning'; f.timer=1.8;
        f.tx=G.x+70+Math.random()*(G.w-140);
        f.ty=G.y+70+Math.random()*(G.h-140);
      } else if(f.state==='warning'&&f.timer<=0){
        f.x=f.tx; f.y=f.ty; f.state='active'; f.timer=3+Math.random()*3;
      }
    });

    // 叉子計時
    this.forkTimer-=dt;
    if(this.forkTimer<=0&&!this.fork){ this.spawnFork(); this.forkTimer=this.forkInterval(); }
    if(this.fork){
      this.fork.timer+=dt;
      if(this.fork.phase==='warn'&&this.fork.timer>=1.5){ this.fork.phase='attack'; this.fork.timer=0; this.checkForkHit(); }
      else if(this.fork.phase==='attack'&&this.fork.timer>=0.55){ this.fork=null; this.forkLayer.clear(); }
      if(this.fork) this.drawFork();
    }

    // AI
    this.enemies.forEach((e,i)=>{
      if(!e.alive){if(this.enemySprites[i])this.enemySprites[i].setVisible(false);return;}
      e.x+=e.vx; e.y+=e.vy;
      if(e.x<G.x+e.r||e.x>G.x+G.w-e.r) e.vx*=-1;
      if(e.y<G.y+e.r||e.y>G.y+G.h-e.r) e.vy*=-1;
      if(this.onFire(e.x,e.y)) e.heat=Math.min(100,e.heat+14*dt);
      else                      e.heat=Math.min(100,e.heat+0.8*dt);
      if(e.heat>=100){
        e.alive=false;
        this.showPop(e.label+' 被烤熟！');
        if(this.enemies.every(en=>!en.alive)) this.time.delayedCall(600,()=>this.endGame(true));
      }
      if(this.enemySprites[i]){
        this.enemySprites[i].setPosition(e.x,e.y).setVisible(true);
        const t=e.heat/100;
        this.enemySprites[i].setTint(Phaser.Display.Color.GetColor(255,Math.floor(255*(1-t*0.7)),Math.floor(255*(1-t))));
        if(this.enemyFx[i]) this.enemyFx[i].setVisible(e.heat>70).setPosition(e.x+16,e.y-22).setText(e.heat>88?'😱':'😰');
      }
    });

    // 繪製
    this.firePhase+=dt*3;
    this.drawFires(this.firePhase);

    // UI
    this.heatBarFg.width=this.heat*2.2;
    this.heatTxt.setText(Math.floor(this.heat)+'%');
    this.timerTxt.setText(this.timeLeft+'s');
    const ready=this.pushCD<=0;
    this.pushBarFg.width=ready?120:(1-this.pushCD/2)*120;
    this.pushCdTxt.setText(ready?'Ready!':this.pushCD.toFixed(1)+'s');
  }
}

new Phaser.Game({
  type: Phaser.AUTO,
  width: W, height: H,
  backgroundColor: '#0a0400',
  scene: [BootScene, SelectScene, GameScene],
  parent: 'game',
});
'''

HTML = f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8" />
  <title>烤肉求生</title>
  <script src="https://cdn.jsdelivr.net/npm/phaser@3.60.0/dist/phaser.min.js"></script>
  <script>
{IMG_BLOCK}
  </script>
  <style>
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ background:#0a0400; display:flex; flex-direction:column; align-items:center; justify-content:center; height:100vh; }}
    #info {{ color:#664422; font-family:sans-serif; font-size:12px; margin-top:5px; }}
  </style>
</head>
<body>
<div id="game"></div>
<div id="info">↑↓←→ 移動 &nbsp;|&nbsp; S 推擠 &nbsp;|&nbsp; R 重開 &nbsp;|&nbsp; ESC 返回選角</div>
<script>
{GAME_CODE}
</script>
</body>
</html>'''

with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(HTML)

sz = len(HTML.encode('utf-8')) // 1024
print(f"Done! index.html = {sz}KB")
