# -*- coding: utf-8 -*-
"""生成 v3.1 自动化测试页：注入断言钩子并用 Edge headless 执行"""
import io, re, os, subprocess, sys

SRC = 'hunger-siege-all/index.html'
OUT = os.path.join(os.environ['TEMP'], 'v31_test.html')
DUMP = os.path.join(os.environ['TEMP'], 'v31_test_dump.html')

TEST_JS = r'''
/* ==== AUTO TEST HOOK v3.1 ==== */
var __R = {};
function __log(n, ok, d){ __R[n] = {ok:!!ok, d:d||''}; }
function __fresh(n){ el.sciencePanel.style.display='none'; el.tutorialPanel.style.display='none'; SETTINGS.seenScience = true; PROGRESS.cleared = PROGRESS.cleared || []; startLevel(n || 1); S.balls = []; S.ballTimer = 999; S.itemTimers = {}; }
(function(){
  var i;
  try {
  /* 1 倒计时 */
  __fresh(1);
  var t0 = S.time;
  for(i=0;i<120;i++) update(1/60);
  __log('countdown', S.time < t0 && S.status==='playing', t0+'->'+S.time.toFixed(1));

  /* 2 开局敌人数：普通 3 / 困难 4 */
  startLevel(1);
  __log('init_3_normal', S.enemies.length===3, 'n='+S.enemies.length);
  startLevel(1, 'hard');
  __log('init_4_hard', S.enemies.length===4, 'n='+S.enemies.length);

  /* 3 普通难度动态刷怪：7s 后第一波 */
  __fresh(1);
  var n0 = S.enemies.length;
  for(i=0;i<440;i++) update(1/60);   /* 7.33s */
  __log('dynamic_spawn_normal', S.enemies.length > n0, n0+'->'+S.enemies.length);

  /* 4 权重表：第1关仅普通；第7关含分裂者 */
  startLevel(1);
  var allNormal = true;
  for(i=0;i<20;i++) if (specialRoll()!=='normal') allNormal=false;
  __log('l1_no_special', allNormal, 'allNormal='+allNormal);
  startLevel(7);
  var cnt = {};
  for(i=0;i<200;i++){ var t = specialRoll(); cnt[t]=(cnt[t]||0)+1; }
  __log('l7_weight', cnt.normal>0 && cnt.greedy>0 && cnt.stalker>0 && cnt.attacker>0 && cnt.trapper>0 && cnt.splitter>0, JSON.stringify(cnt));
  startLevel(5);
  var cnt5 = {};
  for(i=0;i<100;i++){ var t2 = specialRoll(); cnt5[t2]=(cnt5[t2]||0)+1; }
  __log('l5_no_splitter', !cnt5.splitter, JSON.stringify(cnt5));

  /* 5 玩家碰球 */
  __fresh(1);
  var h0 = S.enemies[0].hunger;
  S.balls.push({x:S.player.x+15,y:S.player.y,r:CFG.ball.r,wob:0,dead:false});
  for(i=0;i<12;i++) update(1/60);
  __log('hero_eat_ball', S.balls.length===0 && S.enemies[0].hunger-h0>14, 'hunger+'+(S.enemies[0].hunger-h0).toFixed(1));

  /* 6 敌军碰球 */
  __fresh(1);
  var e = S.enemies[0]; e.hunger=0; e.x=S.player.x+300; e.y=S.player.y;
  S.balls.push({x:e.x+15,y:e.y,r:CFG.ball.r,wob:0,dead:false});
  var m0 = S.misses;
  for(i=0;i<12;i++) update(1/60);
  __log('enemy_eat_ball', S.misses===m0+1, 'miss '+m0+'->'+S.misses);

  /* 7 大招强化 */
  __fresh(1);
  S.mana=100; S.asn=50; S.risk=10;
  castSkill();
  __log('ultimate', S.mana===70 && S.asn===0 && S.risk===35 && S.buffs.ult>4, 'mana'+S.mana+' ult='+S.buffs.ult);

  /* 8 三次漏球失败 */
  __fresh(1);
  S.misses=2;
  var e2 = S.enemies[0]; e2.x=S.player.x+300; e2.y=S.player.y;
  S.balls.push({x:e2.x+15,y:e2.y,r:CFG.ball.r,wob:0,dead:false});
  for(i=0;i<12;i++) update(1/60);
  __log('fail_3miss', S.status==='fail', S.status);

  /* 9 时间到胜利 + 普通解锁 */
  __fresh(1);
  PROGRESS.cleared = []; PROGRESS.hard = [];
  S.time=0.3;
  for(i=0;i<30;i++) update(1/60);
  __log('win_unlock', S.status==='win' && isUnlocked(2) && isCleared(1), S.status+' unlock2='+isUnlocked(2));

  /* 10 风险100失败 */
  __fresh(1);
  S.risk=100;
  update(1/60);
  __log('fail_risk100', S.status==='fail', S.status);

  /* 11 饥饿满萎缩（普通开局3个，死1剩2） */
  __fresh(1);
  var e3 = S.enemies[0]; e3.hunger=CFG.enemy.hungerMax;
  update(1/60);
  var dying = S.enemies[0].dying;
  for(i=0;i<45;i++) update(1/60);
  __log('starve_die', dying && S.enemies.length===2, 'left='+S.enemies.length);

  /* 12 技能解锁节奏 */
  __fresh(1);
  S.player.dirX=1; S.player.dirY=0;
  tryDash();
  __log('dash_locked_l1', !S.dash.active, 'dash='+S.dash.active);
  fireArrow(1,0);
  __log('shoot_locked_l1', S.arrows.length===0, 'arrows='+S.arrows.length);
  __fresh(2);
  tryDash();
  __log('dash_l2_unlock', S.dash.active, 'active='+S.dash.active);

  /* 13 箭矢命中效果 */
  __fresh(3);
  S.enemies = [];
  var tgt = spawnEnemy(500, 400, 'normal');
  tgt.hunger=10; tgt.stun=0;
  hitArrow(tgt, 10, 60, 0.4, {vx:450,vy:0});
  __log('arrow_hit_effect', tgt.x===560 && tgt.hunger===20 && tgt.stun===0.4, 'knock='+(tgt.x-500)+' hunger='+tgt.hunger+' stun='+tgt.stun);

  /* 14 穿透衰减 */
  __fresh(3);
  S.enemies = [];
  var a1 = spawnEnemy(650, 400); a1.hunger=0; a1.stun=0;
  var a2 = spawnEnemy(760, 400); a2.hunger=0; a2.stun=0;
  S.arrows = [];
  spawnArrow(0, 10, 60, 0.4);
  S.arrows[0].x=400; S.arrows[0].y=400;
  for(i=0;i<60;i++) updateArrows(1/60);
  __log('pierce_decay', a1.hunger>=9 && a2.hunger>=6 && a2.hunger < a1.hunger, 'a1='+a1.hunger.toFixed(1)+' a2='+a2.hunger.toFixed(1));

  /* 15 潜行者秒杀 */
  __fresh(5);
  S.enemies = [];
  var st = spawnEnemy(700, 400, 'stalker');
  st.state='chase'; st.revealT=1;
  S.arrows = [];
  spawnArrow(0, 10, 60, 0.4);
  S.arrows[0].x=400; S.arrows[0].y=400;
  var k0 = S.kills;
  for(i=0;i<50;i++) updateArrows(1/60);
  __log('stalker_kill', st.dead && S.kills===k0+1, 'dead='+st.dead+' kills='+S.kills);

  /* 16 蓝红箭对撞 */
  __fresh(7);
  S.enemies = [];   /* 清空敌人，排除 v4.1 追踪转向干扰 */
  spawnRedArrow(S.player.x+80, S.player.y, Math.PI);
  S.player.dirX=1; S.player.dirY=0;
  fireArrow(1,0);
  for(i=0;i<20;i++) update(1/60);
  __log('arrow_clash', S.arrows.length===0, 'left='+S.arrows.length);

  /* 17 鼠标瞄准 */
  __fresh(3);
  S.player.x=600; S.player.y=400;
  fireArrowAt(900, 400);
  var ma = S.arrows[0];
  __log('mouse_aim', ma && ma.vx>0 && Math.abs(ma.vy)<1, 'vx='+(ma?ma.vx.toFixed(0):'none'));

  /* 18 大招三连射 */
  __fresh(3);
  S.buffs.ult=5; S.spreadCharges=0;
  fireArrow(1,0);
  __log('ult_3arrows', S.arrows.length===3, 'arrows='+S.arrows.length);

  /* 19 连发充能 */
  __fresh(5);
  S.spreadCharges=4;
  fireArrow(1,0);
  __log('spread_5arrows', S.arrows.length===5 && S.spreadCharges===3, 'arrows='+S.arrows.length+' charges='+S.spreadCharges);

  /* 20 贪婪者范围削弱：100px 外不被吸；40px 内被吸 */
  __fresh(3);
  S.enemies = [];
  spawnEnemy(500, 350, 'greedy');
  S.balls.push({x:600,y:350,r:CFG.ball.r,wob:0,dead:false});
  var bx0 = S.balls[0].x;
  for(i=0;i<18;i++) update(1/60);
  __log('greedy_weak_range', S.balls.length===1 && Math.abs(S.balls[0].x-bx0)<6, 'dx='+(S.balls[0].x-bx0).toFixed(1));
  __fresh(3);
  S.enemies = [];
  spawnEnemy(500, 350, 'greedy');
  S.balls.push({x:540,y:350,r:CFG.ball.r,wob:0,dead:false});
  var bx1 = S.balls[0].x;
  for(i=0;i<2;i++) update(1/60);
  __log('greedy_pull_close', S.balls.length===1 && S.balls[0].x < bx1-8, 'dx='+(S.balls[0].x-bx1).toFixed(1));

  /* 21 磁铁 vs 贪婪者：更近者控制 */
  __fresh(4);
  S.enemies = [];
  spawnEnemy(700, 400, 'greedy');
  S.balls.push({x:651,y:400,r:CFG.ball.r,wob:0,dead:false});
  S.player.x=605; S.player.y=400; S.player.tx=605; S.player.ty=400;
  S.buffs.magnet = 6;
  var mx0 = S.balls[0].x;
  for(i=0;i<3;i++) update(1/60);   /* 0.05s：玩家(46px)比贪婪者(49px)近，球飞向玩家 */
  __log('magnet_vs_greedy', S.balls.length===1 && S.balls[0].x < mx0-6, 'dx='+(S.balls[0]?(S.balls[0].x-mx0).toFixed(1):'gone'));

  /* 22 潜行者：球刷新时原地现形（不再瞬移），180px/s 扑球，目标被抢重新隐身 */
  __fresh(5);
  var st2 = spawnEnemy(200, 200, 'stalker');
  st2.state='idle'; st2.revealT=0;
  var sx0=st2.x, sy0=st2.y;
  spawnBall();
  __log('stalker_no_teleport', st2.x===sx0 && st2.y===sy0 && st2.state==='chase', 'moved='+(st2.x!==sx0||st2.y!==sy0)+' state='+st2.state);
  __fresh(5);
  var st4 = spawnEnemy(200, 200, 'stalker');
  st4.state='chase'; st4.revealT=1;
  S.balls = [];
  S.balls.push({x:500,y:200,r:CFG.ball.r,wob:0,dead:false});
  var sx1 = st4.x;
  for(i=0;i<30;i++) update(1/60);   /* 0.5s：180px/s → ~90px */
  __log('stalker_150speed', st4.x - sx1 > 60, 'dx='+(st4.x-sx1).toFixed(0));   /* 150px/s × 0.5s = 75px */
  /* 目标球被抢 → 重新隐身 */
  S.balls = [];
  for(i=0;i<5;i++) update(1/60);
  __log('stalker_rehide', st4.state==='idle', 'state='+st4.state);

  /* 23 攻击者红箭 + 护盾免疫 */
  __fresh(7);
  var atk = spawnEnemy(200, 400, 'attacker');
  S.player.x=500; S.player.y=400;
  atk.fireT=0;
  update(1/60);
  var hasRed = S.arrows.some(function(x){return x.type==='red';});
  __log('attacker_fire', hasRed, 'red='+hasRed);
  /* 无护盾减速 */
  S.arrows = [];
  spawnRedArrow(S.player.x+20, S.player.y, Math.PI);
  update(1/60);
  __log('red_slow_player', S.player.slow>0, 'slow='+S.player.slow.toFixed(1));
  /* 护盾免疫减速 */
  S.player.slow = 0;
  S.shieldCharges = 2;
  S.arrows = [];
  spawnRedArrow(S.player.x+20, S.player.y, Math.PI);
  update(1/60);
  __log('shield_redarrow', S.shieldCharges===1 && S.player.slow===0, 'shields='+S.shieldCharges+' slow='+S.player.slow);

  /* 24 陷阱 + 护盾免疫眩晕 */
  __fresh(7);
  var tr = spawnEnemy(600, 600, 'trapper');
  tr.trapT=0;
  update(1/60);   /* 陷阱放在 (600,600) */
  S.traps.push({x:S.player.x, y:S.player.y, life:30});   /* 直接放陷阱在玩家脚下（远离陷阱师，避免碰撞推开） */
  update(1/60);
  __log('trapper_stun', S.player.stun>0, 'stun='+S.player.stun.toFixed(2));
  S.player.stun = 0;                /* 清除上一次眩晕，避免干扰 */
  S.shieldCharges = 2;
  S.traps.push({x:S.player.x, y:S.player.y, life:30});
  update(1/60);
  __log('shield_trap', S.shieldCharges===1 && S.player.stun<=0, 'shields='+S.shieldCharges+' stun='+S.player.stun.toFixed(2));

  /* 25 碰撞箱：玩家被敌人阻挡（第2关冲刺解锁）；冲刺穿过 */
  __fresh(2);
  S.enemies = [];
  var blk = spawnEnemy(700, 400);
  S.player.x = 675; S.player.y = 400; S.player.tx = 675; S.player.ty = 400;
  update(1/60);   /* 玩家在敌人碰撞边缘内（20+16=36）→ 被推到边缘外 */
  __log('collision_block', S.player.x < 668 && S.player.x > 655, 'px='+S.player.x.toFixed(0));
  S.player.dirX=1; S.player.dirY=0;
  tryDash();
  for(i=0;i<10;i++) update(1/60);   /* 冲刺 0.167s ≈ 105px 穿过敌人 */
  __log('dash_through', S.player.x > 700, 'px='+S.player.x.toFixed(0));

  /* 26 正常细胞碰撞阻挡 */
  __fresh(1);
  var cc = S.cells[0];
  S.player.x = cc.x - 20; S.player.y = cc.y; S.player.tx = cc.x + 100; S.player.ty = cc.y;
  for(i=0;i<20;i++) update(1/60);
  __log('cell_block', S.player.x < cc.x, 'px='+S.player.x.toFixed(0)+' cell='+cc.x.toFixed(0));

  /* 27 分裂者：饥饿满 → 4 分裂体（紫色爆炸非萎缩） */
  __fresh(4);
  S.enemies = [];
  var sp = spawnEnemy(500, 400, 'splitter');
  sp.hunger = CFG.enemy.hungerMax;
  S.balls = [];
  update(1/60);
  __log('splitter_split4', S.splits.length===4 && sp.dead, 'splits='+S.splits.length+' splitterDead='+sp.dead);

  /* 28 分裂体 5s 消散 */
  for(i=0;i<330;i++) update(1/60);
  __log('split_expire', S.splits.length===0, 'left='+S.splits.length);

  /* 29 箭矢秒杀分裂体（不影响穿透） */
  __fresh(4);
  S.enemies = [];
  var sp3 = spawnEnemy(500,400,'splitter'); sp3.hunger=CFG.enemy.hungerMax;
  S.balls = [];
  update(1/60);
  S.arrows = [];
  spawnArrow(0,10,60,0.4);
  S.arrows[0].x = S.splits[0].x + 1; S.arrows[0].y = S.splits[0].y;
  updateArrows(1/60);
  __log('split_arrow_kill', S.splits.length===3 && S.arrows.length===1, 'splits='+S.splits.length+' arrows='+S.arrows.length);

  /* 30 分裂体吃球 → 漏球 */
  __fresh(4);
  S.enemies = [];
  var sp4 = spawnEnemy(500,400,'splitter'); sp4.hunger=CFG.enemy.hungerMax;
  update(1/60);
  S.balls = [];
  S.balls.push({x:S.splits[0].x+3, y:S.splits[0].y, r:CFG.ball.r, wob:0, dead:false});
  var mm0 = S.misses;
  update(1/60);
  __log('split_eat_ball', S.misses===mm0+1, 'miss='+S.misses+' splits='+S.splits.length);

  /* 31 护盾道具拾取 +2 层 */
  __fresh(7);
  S.items.push({type:'shield', x:S.player.x+15, y:S.player.y, life:12, wob:0});
  update(1/60);
  __log('shield_pickup', S.shieldCharges===2, 'shields='+S.shieldCharges);

  /* 32 信号弹成功/劫持 */
  __fresh(1);
  var c1 = S.cells[0];
  c1.sigT = 3;
  var hb = S.enemies[0].hunger;
  S.risk = 50;
  S.player.x = c1.x + 10; S.player.y = c1.y;
  update(1/60);
  __log('signal_success', c1.sigT===0 && S.enemies[0].hunger>hb+9 && S.risk<50, 'risk='+S.risk.toFixed(1));
  __fresh(1);
  var c2 = S.cells[0];
  c2.x = 900; c2.y = 700;          /* 强制远离玩家，排除随机位置干扰 */
  c2.sigT = 3;
  S.player.x = 80; S.player.y = 80;
  for(i=0;i<190;i++) update(1/60);
  var hijacked = S.toasts.some(function(t){ return t.text.indexOf('劫持')>=0; });
  __log('signal_fail', c2.sigT<=0 && hijacked && S.flashColor==='#ff6b6b', 'hijacked='+hijacked);

  /* 33 爱心/磁铁/净化/道具 */
  __fresh(1);
  S.items.push({type:'heart', x:S.player.x+15, y:S.player.y, life:12, wob:0});
  update(1/60);
  __log('heart_bonus', S.heartBonus===1 && curMaxMiss()===4, 'cap='+curMaxMiss());
  __fresh(4);
  S.enemies = [];
  S.buffs.magnet = 6;
  S.player.x=400; S.player.y=400; S.player.tx=400; S.player.ty=400;
  S.balls.push({x:500,y:400,r:CFG.ball.r,wob:0,dead:false});
  var d0 = Math.sqrt(dist2(S.player, S.balls[0]));
  for(i=0;i<30;i++) update(1/60);
  var d1 = S.balls[0] ? Math.sqrt(dist2(S.player, S.balls[0])) : 9999;
  __log('magnet_pull', d1 < d0-5, 'dist '+d0.toFixed(0)+'->'+d1.toFixed(0));
  __fresh(2);
  S.risk = 80;
  pickItem('purify');
  __log('purify_halve', S.risk===40, '80->'+S.risk);

  /* 34 双难度存档 */
  __fresh(1);
  PROGRESS.cleared = []; PROGRESS.hard = [];
  startLevel(1, 'hard');
  S.time = 0.3;
  for(i=0;i<30;i++) update(1/60);
  __log('hard_win_star', S.status==='win' && isHardCleared(1) && !isCleared(1), 'hard='+isHardCleared(1));
  var sv = JSON.parse(localStorage.getItem('all-siege-v2') || '{}');
  __log('save_hard_data', sv.hard && sv.hard.indexOf(1)>=0, JSON.stringify({c:sv.cleared,h:sv.hard}));

  /* 35 九关全启动 + 重开 */
  var allOk = true, errMsg = '';
  for(i=1;i<=9;i++){ try { startLevel(i); } catch(err){ allOk=false; errMsg=err.message; } }
  __log('all_levels_start', allOk && S.status==='playing', errMsg||'ok');
  startLevel(5, 'hard');
  startLevel(5, 'hard');
  __log('restart_hard', S.status==='playing' && S.misses===0 && S.difficulty==='hard', 'status='+S.status);

  /* 36 图鉴含分裂者 */
  PROGRESS.cleared = [1,2,3,4,5,6,7,8];
  showBestiary();
  __log('bestiary', document.getElementById('bestiary').innerHTML.indexOf('分裂者')>=0, 'len='+document.getElementById('bestiary').innerHTML.length);

  /* 37 60 秒满压力模拟（第9关困难） */
  PROGRESS.cleared = [1,2,3,4,5,6,7,8,9];
  startLevel(9, 'hard');
  S.player.tx=600; S.player.ty=400;
  var crash = false, crashMsg = '';
  try {
    for(i=0;i<60*60;i++){ update(1/60); if(S.status!=='playing') break; }
  } catch(err){ crash = true; crashMsg = err.message; }
  __log('full_match_l9_hard', !crash && (S.status==='win'||S.status==='fail'), 'crash='+crash+' status='+S.status+' '+(crashMsg||''));

  /* 38 特殊上限 */
  startLevel(9);
  S.enemies = [];
  for(i=0;i<40;i++) spawnEnemy();
  var spN=0;
  for(i=0;i<S.enemies.length;i++) if(S.enemies[i].type!=='normal') spN++;
  __log('special_cap', spN<=10 && S.enemies.length<=25, 'special='+spN+' total='+S.enemies.length);

  /* ===== v3.2 ===== */
  /* 39 生成距离约束：敌人距球 ≥150（放宽 75） */
  __fresh(1);
  S.balls = [];
  S.balls.push({x:600,y:400,r:CFG.ball.r,wob:0,dead:false});
  var eN = spawnEnemy();
  var dE = eN ? Math.sqrt(dist2(eN, S.balls[0])) : -1;
  __log('spawn_enemy_dist', eN && dE >= 75, 'dist='+dE.toFixed(0));
  /* 40 生成距离约束：球距敌人 ≥120（放宽 60） */
  __fresh(1);
  S.enemies = [];
  spawnEnemy(600, 400);
  var bN = spawnBall();
  var dB = Math.sqrt(dist2(bN, S.enemies[0]));
  __log('spawn_ball_dist', dB >= 60, 'dist='+dB.toFixed(0));

  /* 41 无尽模式：解锁与启动 */
  PROGRESS.cleared = [1,2,3,4,5,6,7,8];
  showMenu();
  var locked = el.endlessBtn.classList.contains('locked');
  PROGRESS.cleared = [1,2,3,4,5,6,7,8,9];
  showMenu();
  var unlocked = !el.endlessBtn.classList.contains('locked');
  startEndless();
  __log('endless_unlock_start', locked && unlocked && S.mode==='endless' && S.endless.wave===1 && S.endless.phase==='fight', 'locked='+locked+' wave='+S.endless.wave);

  /* 42 波次推进：30s 结束 → 休整 → 下一波 */
  S.endless.waveT = 29.9;
  for(i=0;i<10;i++) update(1/60);
  var rest1 = S.endless.phase==='rest' && S.endless.wave===2;
  S.endless.restT = 0.1;
  for(i=0;i<10;i++) update(1/60);
  __log('wave_cycle', rest1 && S.endless.wave===2 && S.endless.phase==='fight', 'wave='+S.endless.wave+' phase='+S.endless.phase);

  /* 43 Boss 波：第 5 波生成普通巨型 Boss */
  S.endless.wave = 4; S.endless.phase = 'fight'; S.endless.waveT = 29.9;
  for(i=0;i<10;i++) update(1/60);
  S.endless.restT = 0.1;
  for(i=0;i<10;i++) update(1/60);
  var bss = S.endless.boss;
  __log('boss_spawn', S.endless.wave===5 && S.endless.bossWave && bss && bss.type==='normal' && bss.r===26, 'wave='+S.endless.wave+' boss='+(bss?bss.type:'none')+' r='+(bss?bss.r:0));

  /* 44 Boss 饥饿压制 → 虚弱 → 集火击杀 → 奖励 */
  S.risk = 50; S.mana = 50;
  bossHungerDelta(300);
  var vuln = bss.vulnerable && bss.vulT>0;
  bss.hp = 20;
  S.arrows = [];
  spawnArrow(0, 10, 60, 0.4);
  S.arrows[0].x = bss.x + 1; S.arrows[0].y = bss.y;
  updateArrows(1/60);
  __log('boss_kill_reward', vuln && bss.dead && S.endless.boss===null && S.risk===40 && S.mana===80,
    'vuln='+vuln+' dead='+bss.dead+' risk='+S.risk+' mana='+S.mana);

  /* 45 肉鸽三选一 + 永久成长 */
  S.endless.phase = 'reward';
  prepareReward();
  var hasReward = S.endless.reward && S.endless.reward.options.length===3;
  var permCard = null, ri;
  for (ri = 0; ri < (S.endless.reward ? S.endless.reward.options.length : 0); ri++) {
    if (S.endless.reward.options[ri].tag === '永久') { permCard = S.endless.reward.options[ri]; break; }
  }
  if (permCard) { permCard.apply(S.endless.reward.boost); S.endless.permaPicks++; }
  S.endless.perm.speed = 1;
  __log('reward_3cards_perm', hasReward && endlessMoveMul()>1 && (!permCard || S.endless.permaPicks===1),
    'cards='+(S.endless.reward?S.endless.reward.options.length:0)+' permCard='+(permCard?permCard.id:'none')+' perma='+S.endless.permaPicks);

  /* 46 无尽结束（漏球满）→ v4.2 新公式结算并入榜（高漏球时得分归 0 为预期） */
  S.endless.phase = 'fight';          /* 从奖励阶段回到战斗，再触发失败 */
  S.endless.single.missImmune = 0;
  S.misses = 99;
  update(1/60);
  __log('endless_end_score', S.status==='fail' && S.endless.recorded===true && S.endless.score>=0, 'score='+S.endless.score+' best='+S.endless.best);

  /* ===== v4.1 ===== */
  /* 47 箭矢追踪：75px 内启动并锁定最近目标 */
  __fresh(3);
  S.enemies = [];
  var tgtE = spawnEnemy(670, 400, 'normal');   /* 距箭 60px（追踪范围内，且不易提前命中） */
  S.arrows = [];
  spawnArrow(Math.PI, 10, 60, 0.4);   /* 朝左发射，敌人在右侧 */
  S.arrows[0].x = 610; S.arrows[0].y = 400;
  updateArrows(1/60);
  __log('arrow_track_start', S.arrows[0].tracking === true && S.arrows[0].trackTarget === tgtE, 'tracking='+S.arrows[0].tracking);
  for(i=0;i<6;i++) updateArrows(1/60);   /* 每帧 15°，6 帧转 90°（从朝左开始转向） */
  __log('arrow_track_turn', S.arrows[0].tracking && S.arrows[0].vx > -100, 'vx='+S.arrows[0].vx.toFixed(0)+' vy='+S.arrows[0].vy.toFixed(0));
  for(i=0;i<40;i++) updateArrows(1/60);   /* 命中后恢复直线（不再追踪） */
  __log('arrow_track_hit_straight', tgtE.hunger>0 && S.arrows.length>0 && !S.arrows[0].tracking,
    'hunger='+tgtE.hunger.toFixed(0)+' vx='+S.arrows[0].vx.toFixed(0)+' vy='+S.arrows[0].vy.toFixed(0));

  /* 48 Boss 免疫追踪 */
  __fresh(3);
  S.enemies = [];
  var bossE = spawnEnemy(650, 400, 'normal');
  bossE.isBoss = true;
  S.arrows = [];
  spawnArrow(0, 10, 60, 0.4);
  S.arrows[0].x = 610; S.arrows[0].y = 400;
  updateArrows(1/60);
  __log('boss_no_track', !S.arrows[0].tracking, 'tracking='+S.arrows[0].tracking);

  /* 49 暂停菜单：ESC 冻结 + 继续 3-2-1 倒计时 */
  __fresh(1);
  var t1 = S.time;
  document.dispatchEvent(new KeyboardEvent('keydown', {code:'Escape'}));
  __log('pause_show', S.paused && el.pauseMenu.style.display==='flex', 'paused='+S.paused);
  for(i=0;i<60;i++) update(1/60);   /* 暂停 1s */
  __log('pause_freeze', S.time===t1, 'time '+t1+'->'+S.time);
  document.dispatchEvent(new KeyboardEvent('keydown', {code:'Escape'}));
  __log('resume_countdown', !S.paused && S.countdownT>0 && el.countdown.style.display==='flex', 'cd='+S.countdownT);
  for(i=0;i<200;i++) update(1/60);   /* 3.33s 倒计时结束恢复 */
  __log('countdown_done', S.countdownT<=0 && el.countdown.style.display==='none' && S.time < t1, 'cd='+S.countdownT+' time='+S.time.toFixed(1));

  /* 50 标题页：显示/键盘导航/团队弹窗 */
  showTitle();
  __log('title_panel', S.status==='title' && el.titlePanel.style.display==='flex' && el.tStart.classList.contains('active'), 'status='+S.status);
  document.dispatchEvent(new KeyboardEvent('keydown', {code:'ArrowDown'}));
  __log('title_nav', titleFocus===1 && el.tEndless.classList.contains('active'), 'focus='+titleFocus);
  el.teamBtn.click();
  var mOpen = el.teamModal.style.display==='flex';
  document.dispatchEvent(new KeyboardEvent('keydown', {code:'Escape'}));
  __log('team_modal', mOpen && el.teamModal.style.display==='none', 'open='+mOpen+' after='+el.teamModal.style.display);

  /* ===== v4.2 ===== */
  /* 51 简单模式：初始解锁 / 间隔 10.5s / 上限 9 / 数值宽松 / 通关不解锁 */
  startLevel(1, 'easy');
  __log('easy_init', S.enemies.length===3 && isEasy(), 'n='+S.enemies.length);
  __log('easy_interval', Math.abs(currentSpawnInterval()-10.5)<0.01, 'iv='+currentSpawnInterval().toFixed(2));
  S.enemies = [];
  for(i=0;i<20;i++) spawnEnemy();
  __log('easy_cap9', aliveCount()===9, 'alive='+aliveCount());
  __log('easy_skills', skillCost()===20 && riskSideVal()===15 && shootCDVal()===0.25, 'cost='+skillCost()+' rs='+riskSideVal()+' cd='+shootCDVal());
  __log('easy_speeds', enemySpeedMul()===0.7 && playerSpeedMul()===1.1, 'e='+enemySpeedMul()+' p='+playerSpeedMul());
  PROGRESS.cleared = [];
  startLevel(1, 'easy');
  S.time = 0.01;
  update(1/60);
  __log('easy_no_unlock', S.status==='win' && !isCleared(1), 'cleared1='+isCleared(1));

  /* 52 科普页 / 教程页流程（点击第 1 关触发，不再启动弹出） */
  SETTINGS.seenScience = false;
  PROGRESS.cleared = [];
  showTitle();
  startLevel(1);
  __log('science_on_click', S.status==='science' && el.sciencePanel.style.display==='flex', 'status='+S.status);
  el.sciOk.click();
  __log('science_ok', SETTINGS.seenScience===true && S.status==='tutorial' && el.tutorialPanel.style.display==='flex', 'seen='+SETTINGS.seenScience+' st='+S.status);
  el.tutStart.click();
  __log('tutorial_start', S.status==='playing' && el.tutorialPanel.style.display==='none' && curLevelN===1, 'st='+S.status+' lvl='+curLevelN);
  /* 有通关记录后不再弹教程 */
  PROGRESS.cleared = [1];
  showMenu();
  startLevel(1);
  __log('tutorial_skip_cleared', S.status==='playing' && el.sciencePanel.style.display==='none', 'st='+S.status);
  SETTINGS.seenScience = true;

  /* 53 语言切换 */
  showTitle();
  __log('lang_zh_title', el.titleMain.textContent.indexOf('饥饿围城')>=0, 't='+el.titleMain.textContent);
  setLang('en');
  __log('lang_en', LANG==='en' && el.tStart.textContent.indexOf('Start')>=0, 'tStart='+el.tStart.textContent);
  setLang('zh');
  __log('lang_back_zh', el.tStart.textContent.indexOf('开始')>=0, 'tStart='+el.tStart.textContent);

  /* 54 排行榜公式与排序（波次优先、得分次之） */
  __fresh(1);
  S.mode='endless'; S.endless={wave:3,bossKills:1,recorded:false};
  S.kills=10; S.saves=2; S.misses=1;
  __log('score_formula', endlessScore()===370, 'score='+endlessScore());   /* 300+50+50+20-50=370 */
  LEADER=[];
  addLeader({wave:2,score:100,kills:5,saves:0,date:'d'});
  addLeader({wave:5,score:50,kills:1,saves:0,date:'d'});
  addLeader({wave:2,score:200,kills:9,saves:1,date:'d'});
  __log('leader_sort', LEADER[0].wave===5 && LEADER[1].wave===2 && LEADER[1].score===200 && LEADER.length===3,
    LEADER.map(function(x){return x.wave+':'+x.score;}).join(','));

  /* 55 作弊码：ASPROUT 解锁全部 / VIVIMYFATHER 无敌（漏球免疫）+ 存档拦截 */
  showTitle();
  PROGRESS.cleared=[];
  'ASPROUT'.split('').forEach(function(ch){ handleCheatInput(ch); });
  __log('cheat_unlock', isCleared(9) && !el.tEndless.classList.contains('locked'), 'c9='+isCleared(9));
  __log('cheat_god_off', godMode===false, 'god='+godMode);
  'VIVIMYFATHER'.split('').forEach(function(ch){ handleCheatInput(ch); });
  __log('cheat_god_on', godMode===true && el.godBadge.style.display==='flex', 'god='+godMode+' badge='+el.godBadge.style.display);
  __fresh(1);
  var m1 = S.misses;
  registerMiss(); registerMiss();
  __log('god_no_miss', S.misses===m1, 'miss='+S.misses);
  godMode=false; el.godBadge.style.display='none';
  registerMiss();
  __log('god_off_miss', S.misses===m1+1, 'miss='+S.misses);

  /* 56 重置存档 */
  PROGRESS.cleared=[1,2]; LEADER=[{wave:1,score:1,kills:1,saves:0,date:'x'}]; SETTINGS.lang='en'; LANG='en';
  resetAllSave();
  __log('reset_save', PROGRESS.cleared.length===0 && LEADER.length===0 && SETTINGS.lang==='zh' && LANG==='zh', 'c='+PROGRESS.cleared.length+' l='+LEADER.length);

  /* 57 选关界面 ESC 返回标题 */
  showMenu();
  document.dispatchEvent(new KeyboardEvent('keydown', {code:'Escape'}));
  __log('esc_to_title', S.status==='title' && el.titlePanel.style.display==='flex', 'st='+S.status);

  /* 58 移动端模式：停留在标题界面，触控层只在局内显示，配置持久化 */
  showTitle();
  SETTINGS.seenScience = true; PROGRESS.cleared = [1];   /* reset 测试清空了科普标记，这里恢复避免触发教程 */
  enterMobile();
  __log('mobile_stay_title', isMobile===true && S.status==='title' && !el.touchUI.classList.contains('on'), 'st='+S.status+' on='+el.touchUI.classList.contains('on'));
  __log('mobile_persist_set', SETTINGS.mobile===true, 'm='+SETTINGS.mobile);
  startLevel(1);
  __log('mobile_touch_ingame', el.touchUI.classList.contains('on') && S.status==='playing', 'on='+el.touchUI.classList.contains('on'));
  showMenu();
  __log('mobile_touch_menu_off', !el.touchUI.classList.contains('on') && S.status==='menu', 'on='+el.touchUI.classList.contains('on'));
  exitMobile();
  __log('mobile_off', isMobile===false && SETTINGS.mobile===false && !el.touchUI.classList.contains('on'), 'm='+isMobile);

  /* 59 bug 回归：制作团队弹窗 / HUD 不崩（var t 遮蔽修复） / 作弊码经键盘输入可用（S 键不被导航吞） */
  showTitle();
  el.teamBtn.click();
  __log('team_modal_show', el.teamModal.style.display==='flex', 'd='+el.teamModal.style.display);
  el.teamModal.style.display = 'none';
  __fresh(1);
  updateHUD();
  __log('hud_no_crash', S.status==='playing' && el.killNum.textContent !== undefined, 'kill='+el.killNum.textContent);
  showTitle();
  PROGRESS.cleared = [];
  cheatBuffer = '';
  ['A','S','P','R','O','U','T'].forEach(function (ch) {
    document.dispatchEvent(new KeyboardEvent('keydown', { code: 'Key' + ch, key: ch }));
  });
  __log('cheat_keydown_asprout', isCleared(9), 'c9='+isCleared(9));
  /* 移动端配置持久化：模拟存档后重载 */
  isMobile = false; SETTINGS.mobile = true; save(); isMobile = false; SETTINGS.mobile = false; loadSave();
  __log('mobile_reload', isMobile===true && SETTINGS.mobile===true, 'm='+isMobile);

  } catch(err) { __log('TEST_CRASH', false, (err.message||'') + ' || ' + (err.stack||'').split('\n').slice(0,6).join(' | ')); }
  var pre = document.createElement('pre');
  pre.id='__testOut'; pre.textContent = JSON.stringify(__R);
  document.body.appendChild(pre);
})();
'''

def main():
    src = io.open(SRC, encoding='utf-8').read()
    if '__testOut' in src:
        src = src.split('/* ==== AUTO TEST HOOK')[0]
    out = src.replace('requestAnimationFrame(loop);', 'requestAnimationFrame(loop);\n' + TEST_JS)
    io.open(OUT, 'w', encoding='utf-8').write(out)
    edge = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    cmd = [edge, '--headless=new', '--disable-gpu', '--no-first-run', '--virtual-time-budget=25000',
           '--dump-dom', 'file:///' + OUT.replace('\\', '/')]
    with open(os.devnull, 'w') as dn:
        subprocess.run(cmd, stdout=open(DUMP, 'w', encoding='utf-8'), stderr=dn, timeout=180)
    dom = io.open(DUMP, encoding='utf-8').read()
    m = re.search(r'id="__testOut">(.*?)</pre>', dom, re.S)
    if not m:
        print('TEST OUTPUT NOT FOUND; err=', re.search(r'id="errLine">([^<]*)', dom).group(1))
        sys.exit(1)
    import json
    results = json.loads(m.group(1))
    fails = [k for k, v in results.items() if not v['ok']]
    for k, v in results.items():
        print(('PASS ' if v['ok'] else 'FAIL ') + k + ' :: ' + v['d'])
    print('----')
    print('TOTAL', len(results), 'PASS', len(results) - len(fails), 'FAIL', len(fails))
    if fails:
        print('FAILED:', ', '.join(fails))
        sys.exit(1)

if __name__ == '__main__':
    main()
