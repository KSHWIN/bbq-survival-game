# -*- coding: utf-8 -*-
# Patch 10: 關卡選擇 + 選角介面改版 (ability icons + level select)
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ══════════════════════════════════════════════════════════
# STEP 1 – Add LEVELS array before inGrill()
# ══════════════════════════════════════════════════════════
OLD_INGRILL = "function inGrill(x,y,m=0){ return x>=G.x+m&&x<=G.x+G.w-m&&y>=G.y+m&&y<=G.y+G.h-m; }"
NEW_INGRILL = """\
const LEVELS = [
  {key:'lv1',name:'家庭烤肉架',  sub:'初心者友好',       diff:1, timer:60, heatMod:1.0, forkMod:1.0, tiltMod:1.0, fireCnt:8 },
  {key:'lv2',name:'餐廳鐵板燒',  sub:'高溫快節奏',       diff:3, timer:75, heatMod:1.3, forkMod:1.5, tiltMod:1.0, fireCnt:10},
  {key:'lv3',name:'露營野火烤架', sub:'風向不定傾斜頻繁',  diff:4, timer:90, heatMod:1.1, forkMod:1.0, tiltMod:2.5, fireCnt:8 },
  {key:'lv4',name:'地獄料理直播', sub:'雙叉子超高溫',     diff:5, timer:45, heatMod:1.5, forkMod:2.5, tiltMod:1.5, fireCnt:12},
];

function inGrill(x,y,m=0){ return x>=G.x+m&&x<=G.x+G.w-m&&y>=G.y+m&&y<=G.y+G.h-m; }"""

if OLD_INGRILL in html:
    html = html.replace(OLD_INGRILL, NEW_INGRILL)
    print("LEVELS array: OK")
else:
    print("FAIL LEVELS array")

# ══════════════════════════════════════════════════════════
# STEP 2 – Replace entire SelectScene class
# ══════════════════════════════════════════════════════════
sel_cls_idx  = html.find('class SelectScene')
game_cls_idx = html.find('class GameScene')
# Walk back to the comment line before SelectScene
comment_idx = html.rfind('\n', 0, sel_cls_idx - 2) + 1   # start of "// ── Select Scene" line

if sel_cls_idx != -1 and game_cls_idx != -1:
    NEW_SELECT = """\
// ── Select Scene ─────────────────────────────────────────
class SelectScene extends Phaser.Scene {
  constructor(){ super('Select'); }

  create(){
    this.sel=0; this.lvSel=0;
    // Background
    const selBg=this.textures.exists('cartoon_bg')?'cartoon_bg':'grill_bg';
    if(this.textures.exists(selBg)) this.add.image(W/2,H/2,selBg).setDisplaySize(W,H).setAlpha(0.45);
    this.add.rectangle(W/2,H/2,W,H,0x000000,0.62);
    // Title
    this.add.text(W/2,18,'烤肉求生',{fontSize:'36px',color:'#ff8800',fontFamily:'sans-serif',fontStyle:'bold',stroke:'#ff3300',strokeThickness:4}).setOrigin(0.5);
    this.add.text(W/2,50,'選擇食材  ●  選擇關卡  ●  出戰！',{fontSize:'13px',color:'#cc8844',fontFamily:'sans-serif'}).setOrigin(0.5);

    // ── Character Grid (5×2) ──────────────────────────────
    const CW=124,CH=145,GX=7,GY=6;
    const totalCW=5*CW+4*GX; // 648
    const sx=(W-totalCW)/2+CW/2;
    const sy=63+CH/2;
    this.charCards=[];
    CHARS.forEach((c,i)=>{
      const cx=sx+(i%5)*(CW+GX), cy=sy+Math.floor(i/5)*(CH+GY);
      const cont=this.add.container(cx,cy);
      const shadow=this.add.rectangle(3,3,CW,CH,0x000000,0.55);
      const bg=this.add.rectangle(0,0,CW,CH,0x180d00,0.93).setStrokeStyle(2,0x664422);
      let portrait;
      if(this.textures.exists(c.img)) portrait=this.add.image(0,-30,c.img).setDisplaySize(78,78);
      else portrait=this.add.rectangle(0,-30,72,72,c.color,0.75).setStrokeStyle(2,0xffffff);
      const nameT=this.add.text(0,+14,c.name,{fontSize:'14px',color:'#ffdd88',fontFamily:'sans-serif',fontStyle:'bold'}).setOrigin(0.5);
      const abilT=this.add.text(0,+30,'✦ '+c.ability,{fontSize:'10px',color:'#66ccff',fontFamily:'sans-serif'}).setOrigin(0.5);
      const iconG=this.drawAbilIcon(0,+50,c.key);
      cont.add([shadow,bg,portrait,nameT,abilT,iconG]);
      cont.setInteractive(new Phaser.Geom.Rectangle(-CW/2,-CH/2,CW,CH),Phaser.Geom.Rectangle.Contains);
      cont.on('pointerdown',()=>this.setSel(i));
      cont.on('pointerover',()=>this.setSel(i));
      this.charCards.push({cont,bg});
    });

    // ── Level Grid (4 cards) ──────────────────────────────
    const LW=168,LH=76,LG=9;
    const totalLW=4*LW+3*LG; // 699
    const lsx=(W-totalLW)/2+LW/2;
    const charGridBottom=sy+CH/2+CH+GY+GY; // approx
    const lsy=charGridBottom+LH/2+2;
    this.lvCards=[];
    const DCOLS=[0x44cc44,0x88cc44,0xff9900,0xff5500,0xff2200];
    LEVELS.forEach((lv,i)=>{
      const lx=lsx+i*(LW+LG), ly=lsy;
      const cont=this.add.container(lx,ly);
      const dc=DCOLS[Math.min(lv.diff-1,4)];
      const shadow=this.add.rectangle(3,3,LW,LH,0x000000,0.55);
      const bg=this.add.rectangle(0,0,LW,LH,0x080a12,0.95).setStrokeStyle(2,dc);
      const numT=this.add.text(-LW/2+10,-LH/2+10,(i+1)+'',{fontSize:'18px',color:'#'+dc.toString(16).padStart(6,'0'),fontFamily:'sans-serif',fontStyle:'bold'});
      const nameT=this.add.text(0,-12,lv.name,{fontSize:'12px',color:'#ffdd88',fontFamily:'sans-serif',fontStyle:'bold'}).setOrigin(0.5);
      const subT=this.add.text(0,+3,lv.sub,{fontSize:'10px',color:'#aaaaaa',fontFamily:'sans-serif'}).setOrigin(0.5);
      const diffStr='★'.repeat(lv.diff)+'☆'.repeat(5-lv.diff);
      const diffT=this.add.text(0,+17,diffStr,{fontSize:'12px',color:'#'+dc.toString(16).padStart(6,'0'),fontFamily:'sans-serif'}).setOrigin(0.5);
      const timeT=this.add.text(LW/2-8,LH/2-10,'⏱'+lv.timer+'s',{fontSize:'9px',color:'#777799',fontFamily:'sans-serif'}).setOrigin(1,1);
      cont.add([shadow,bg,numT,nameT,subT,diffT,timeT]);
      cont.setInteractive(new Phaser.Geom.Rectangle(-LW/2,-LH/2,LW,LH),Phaser.Geom.Rectangle.Contains);
      cont.on('pointerdown',()=>this.setLvSel(i));
      cont.on('pointerover',()=>this.setLvSel(i));
      this.lvCards.push({cont,bg,dc});
    });

    // ── Detail bar ───────────────────────────────────────
    this.add.rectangle(W/2,H-26,W-20,36,0x0a0600,0.9).setStrokeStyle(1,0x664422).setDepth(-1);
    this.detailTxt=this.add.text(W/2,H-26,'',{fontSize:'12px',color:'#ffcc88',fontFamily:'sans-serif',align:'center'}).setOrigin(0.5);

    // ── Keyboard ─────────────────────────────────────────
    this.input.keyboard.on('keydown-LEFT', ()=>this.setSel((this.sel+CHARS.length-1)%CHARS.length));
    this.input.keyboard.on('keydown-RIGHT',()=>this.setSel((this.sel+1)%CHARS.length));
    this.input.keyboard.on('keydown-UP',   ()=>this.setSel((this.sel+CHARS.length-5)%CHARS.length));
    this.input.keyboard.on('keydown-DOWN', ()=>this.setSel((this.sel+5)%CHARS.length));
    this.input.keyboard.on('keydown',      (ev)=>{ if(ev.keyCode>=49&&ev.keyCode<=52) this.setLvSel(ev.keyCode-49); });
    this.input.keyboard.on('keydown-ENTER',()=>this.startGame());
    this.input.keyboard.on('keydown-SPACE',()=>this.startGame());
    this.setSel(0); this.setLvSel(0);
  }

  // Draw a tiny ability-type icon inside a card container
  drawAbilIcon(cx, cy, key){
    const g=this.add.graphics();
    const COL={pork:0xff8800,beef:0x4488ff,mushroom:0xaa66dd,corn:0xddcc00,wing:0x00ccbb,
               shrimp:0x4466ff,tofu:0xddaa00,bacon:0xcc4400,pepper:0x44bb44,saury:0x8899cc};
    const col=COL[key]||0x888888;
    // Background pill
    g.fillStyle(col,0.2); g.fillRect(cx-50,cy-10,100,20);
    g.lineStyle(1,col,0.6); g.strokeRect(cx-50,cy-10,100,20);
    g.fillStyle(col,0.9);
    switch(key){
      case 'pork':   // Dash: dots → arrow
        [-22,-10,2].forEach(dx=>g.fillCircle(cx+dx,cy,3));
        g.fillTriangle(cx+22,cy,cx+13,cy-6,cx+13,cy+6); break;
      case 'beef':   // Shield: pentagon
        g.lineStyle(2,col,0.9);
        for(let i=0;i<5;i++){const a=i*Math.PI*2/5-Math.PI/2,b=(i+1)*Math.PI*2/5-Math.PI/2;
          g.lineBetween(cx+Math.cos(a)*11,cy+Math.sin(a)*11,cx+Math.cos(b)*11,cy+Math.sin(b)*11);} break;
      case 'mushroom': // Teleport: ○──→○
        g.lineStyle(1,col,0.8); g.strokeCircle(cx-18,cy,7); g.strokeCircle(cx+18,cy,7);
        [-5,0,5].forEach(dx=>g.fillCircle(cx+dx,cy,1.8));
        g.fillTriangle(cx+14,cy,cx+8,cy-5,cx+8,cy+5); break;
      case 'corn':   // Explosion: starburst
        for(let i=0;i<8;i++){const a=i*Math.PI/4;
          g.lineStyle(2,col,0.9); g.lineBetween(cx+Math.cos(a)*3,cy+Math.sin(a)*3,cx+Math.cos(a)*12,cy+Math.sin(a)*12);}
        g.fillCircle(cx,cy,4); break;
      case 'wing':   // Wings: two triangles
        g.fillStyle(col,0.65); g.fillTriangle(cx-4,cy,cx-22,cy-9,cx-16,cy+6);
        g.fillTriangle(cx+4,cy,cx+22,cy-9,cx+16,cy+6);
        g.fillStyle(col,0.9); g.fillCircle(cx,cy,3.5); break;
      case 'shrimp': // Long dash arrow
        g.lineStyle(2,col,0.9); g.lineBetween(cx-28,cy,cx+16,cy);
        g.fillTriangle(cx+24,cy,cx+15,cy-6,cx+15,cy+6); break;
      case 'tofu':   // Absorb ring: circle + orbiting dots
        g.lineStyle(1,col,0.8); g.strokeCircle(cx,cy,8);
        for(let i=0;i<5;i++){const a=i*Math.PI*2/5; g.fillCircle(cx+Math.cos(a)*16,cy+Math.sin(a)*16,3.5);} break;
      case 'bacon':  // Spin: rotating dots
        for(let i=0;i<10;i++){const a=i*Math.PI/5,r=7+5*(i%2);
          g.fillCircle(cx+Math.cos(a)*r,cy+Math.sin(a)*r,2.5);} break;
      case 'pepper': // Spray: fan of dots
        for(let i=0;i<7;i++){const a=(i-3)*0.38,r=8+i*2.5;
          g.fillCircle(cx+Math.cos(a)*r,cy+Math.sin(a)*r,2.5);} break;
      case 'saury':  // Slash: diagonal lines
        g.lineStyle(2.5,col,0.9); g.lineBetween(cx-20,cy+7,cx+14,cy-7);
        g.lineStyle(1.5,col,0.5); g.lineBetween(cx-26,cy+1,cx+8,cy-13);
        g.lineBetween(cx-14,cy+13,cx+20,cy-1); break;
    }
    return g;
  }

  setSel(i){
    this.sel=i;
    this.charCards.forEach((card,idx)=>{
      const a=idx===i;
      card.bg.setStrokeStyle(a?3:2,a?0xffaa00:0x664422);
      card.cont.setScale(a?1.07:1).setDepth(a?10:0);
    });
    this._updateDetail();
  }

  setLvSel(i){
    this.lvSel=i;
    const DCOLS=[0x44cc44,0x88cc44,0xff9900,0xff5500,0xff2200];
    this.lvCards.forEach((card,idx)=>{
      const a=idx===i;
      const dc=DCOLS[Math.min(LEVELS[idx].diff-1,4)];
      card.bg.setStrokeStyle(a?3:2,a?0xffffff:dc);
      card.cont.setScale(a?1.06:1).setDepth(a?5:0);
    });
    this._updateDetail();
  }

  _updateDetail(){
    if(!this.detailTxt) return;
    const c=CHARS[this.sel], lv=LEVELS[this.lvSel];
    this.detailTxt.setText(c.name+' ✦ '+c.ability+'：'+c.abilityDesc+'    |    關卡：'+lv.name+'（'+lv.sub+'）    |    Enter / 點擊開戰');
  }

  startGame(){
    this.scene.start('Game',{char:CHARS[this.sel], level:LEVELS[this.lvSel]});
  }
}

"""
    html = html[:comment_idx] + NEW_SELECT + html[game_cls_idx:]
    print("SelectScene: OK")
else:
    print("FAIL SelectScene (boundaries not found)")

# ══════════════════════════════════════════════════════════
# STEP 3 – GameScene.init: accept level data
# ══════════════════════════════════════════════════════════
old = "  init(data){ this.charData=data.char||CHARS[0]; }"
new = "  init(data){ this.charData=data.char||this.charData||CHARS[0]; this.levelData=data.level||this.levelData||LEVELS[0]; }"
if old in html: html=html.replace(old,new); print("GameScene init: OK")
else: print("FAIL GameScene init")

# ══════════════════════════════════════════════════════════
# STEP 4 – Use levelData.timer for timeLeft
# ══════════════════════════════════════════════════════════
old = "    this.heat=0; this.alive=true; this.pushCD=0; this.timeLeft=60;"
new = "    this.heat=0; this.alive=true; this.pushCD=0; this.timeLeft=this.levelData.timer;"
if old in html: html=html.replace(old,new); print("levelData.timer: OK")
else: print("FAIL levelData.timer")

# ══════════════════════════════════════════════════════════
# STEP 5 – Use levelData.fireCnt for fire points
# ══════════════════════════════════════════════════════════
old = "    this.firePts=[0,1,2,3,4,5,6,7].map((_,i)=>{"
new = "    this.firePts=Array.from({length:this.levelData.fireCnt},(_,i)=>{"
if old in html: html=html.replace(old,new); print("levelData.fireCnt: OK")
else: print("FAIL levelData.fireCnt")

# ══════════════════════════════════════════════════════════
# STEP 6 – Use levelData modifiers for intervals
# ══════════════════════════════════════════════════════════
old = "    this.tiltInterval=()=>11+Math.random()*8;"
new = "    this.tiltInterval=()=>(11+Math.random()*8)/this.levelData.tiltMod;"
if old in html: html=html.replace(old,new); print("levelData.tiltMod: OK")
else: print("FAIL levelData.tiltMod")

old = "    this.forkInterval=()=>5+Math.random()*4;"
new = "    this.forkInterval=()=>(5+Math.random()*4)/this.levelData.forkMod;"
if old in html: html=html.replace(old,new); print("levelData.forkMod: OK")
else: print("FAIL levelData.forkMod")

# ══════════════════════════════════════════════════════════
# STEP 7 – Apply levelData.heatMod to heat accumulation
# ══════════════════════════════════════════════════════════
old = "    const mult=this.charData.heatMult*(ae.sauce>0?2:1)*(armorOn?0.5:1);"
new = "    const mult=this.charData.heatMult*(ae.sauce>0?2:1)*(armorOn?0.5:1)*this.levelData.heatMod;"
if old in html: html=html.replace(old,new); print("levelData.heatMod: OK")
else: print("FAIL levelData.heatMod")

# ══════════════════════════════════════════════════════════
# STEP 8 – Show level name in game UI timer area
# ══════════════════════════════════════════════════════════
old = (
    "    this.timerTxt =this.add.text(W-14,14,'60s',ts(22)).setOrigin(1,0);\n"
    "    this.popTxt   =this.add.text(W/2,G.y-28,'',ts(17,'#ffff44')).setOrigin(0.5).setDepth(30);"
)
new = (
    "    this.timerTxt =this.add.text(W-14,14,this.levelData.timer+'s',ts(22)).setOrigin(1,0);\n"
    "    this.add.text(W-14,44,this.levelData.name,ts(10,'#886644')).setOrigin(1,0);\n"
    "    this.popTxt   =this.add.text(W/2,G.y-28,'',ts(17,'#ffff44')).setOrigin(0.5).setDepth(30);"
)
if old in html: html=html.replace(old,new); print("level name in UI: OK")
else: print("FAIL level name in UI")

# ══════════════════════════════════════════════════════════
# WRITE
# ══════════════════════════════════════════════════════════
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== Verify ===")
with open("c:/Users/User/Desktop/烤肉遊戲/index.html", "r", encoding="utf-8") as f:
    v = f.read()
print("LEVELS array:", "const LEVELS" in v)
print("diff:1:", "diff:1" in v)
print("SelectScene rewrite:", "drawAbilIcon" in v)
print("setLvSel:", "setLvSel" in v)
print("level passed to Game:", "level:LEVELS" in v)
print("levelData in init:", "this.levelData=data.level" in v)
print("levelData.timer:", "this.levelData.timer" in v)
print("levelData.fireCnt:", "this.levelData.fireCnt" in v)
print("levelData.tiltMod:", "this.levelData.tiltMod" in v)
print("levelData.forkMod:", "this.levelData.forkMod" in v)
print("levelData.heatMod:", "this.levelData.heatMod" in v)
print("level name UI:", "this.levelData.name" in v)
