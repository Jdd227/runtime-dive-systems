const assert = require('node:assert/strict');
const e = require('./runtime-blender-core.js');
const E = 1e-6;
function near(a,b,label,tol=E){ assert.ok(Math.abs(a-b) < tol, `${label}: expected ${b}, got ${a}`); }
function config(overrides={}) {return {units:'psi',basis:'gauge',startO2:21,startHe:0,startPressure:0,targetO2:18,targetHe:45,finalPressure:3000,topO2:21,topHe:0,o2Purity:100,hePurity:100,autoBleed:true,...overrides}}
let testCount=0;
function test(name, callback) { try {callback(); testCount++; console.log('PASS',name)} catch(e) {console.error('FAIL',name,e.message);process.exitCode=1;} }
test('Empty cylinder trimix 18/45: independent N2/O2/He hand calculation',()=>{
  const r=e.blend(config()); assert.ok(r.ok); const [he,o2,air]=r.stages;
  near(he.added, 3000*.45,'He'); near(air.added,3000*.37/.79,'air');
  near(o2.added,3000*.18 - air.added*.21,'O2');
  near(r.stages[2].stop,3000,'final stop'); near(r.produced.o,18,'final O2');near(r.produced.h,45,'final He');
});
test('Residual 500 PSI air -> 18/45',()=>{
  const r=e.blend(config({startPressure:500})); assert.ok(r.ok);
  near(r.stages[0].stop,1850,'He stop'); near(r.stages[1].stop,2094.9367088607596,'O2 stop');
  near(r.stages[2].stop,3000,'final stop');
});
test('From 500 PSI air to nitrox 32',()=>{
  const r=e.blend(config({startPressure:500,targetO2:32,targetHe:0})); assert.ok(r.ok);
  near(r.stages[0].added,0,'He'); near(r.stages[2].added,(3000*.68-500*.79)/.79,'air');
  near(r.stages[1].added,3000*.32-500*.21-r.stages[2].added*.21,'O2');
});
test('Nominal zero pressure trimix 21/35',()=>{
  const r=e.blend(config({targetO2:21,targetHe:35})); assert.ok(r.ok);
  near(r.stages[0].added,1050,'He'); near(r.stages[2].added,3000*.44/.79,'air');
  near(r.stages[1].added,630 - r.stages[2].added*.21,'O2');
});
test('Bleed down preserves maximum starting air without over-retaining N2',()=>{
  const r=e.blend(config({startPressure:2500})); assert.ok(r.ok); assert.ok(r.bledDown);
  near(r.retainedPressure, 3000*.37/.79,'retained'); near(r.stages[2].added,0,'air');
  near(r.produced.o,18,'O2');near(r.produced.h,45,'He');
});
test('Bleed disallowed returns an explicit block',()=>{
  const r=e.blend(config({startPressure:2500,autoBleed:false}));assert.equal(r.kind,'bleed_required');
});
test('Unattainable mixture with air top is rejected',()=>{
  const r=e.blend(config({targetO2:10,targetHe:0}));assert.equal(r.kind,'impossible');
});
test('Pure nitrogen bank permits low-O2 mixture (10/0)',()=>{
  const r=e.blend(config({targetO2:10,targetHe:0,topO2:0}));assert.ok(r.ok);
  near(r.stages[1].added,300,'O2');near(r.stages[2].added,2700,'N2 bank');
});
test('Source purity corrections still close each gas balance',()=>{
  const r=e.blend(config({o2Purity:99.5,hePurity:99.9}));assert.ok(r.ok);
  near(r.produced.o,18,'O2');near(r.produced.h,45,'He');near(r.produced.n,37,'N2');
});
test('Gauge/absolute modes agree on final pressure but show slightly different stops',()=>{
  const g=e.blend(config({startPressure:0})),a=e.blend(config({startPressure:0,basis:'absolute'}));
  near(a.stages[2].stop,3000,'final pressure');assert.ok(Math.abs(g.stages[0].stop-a.stages[0].stop) > 1);
  near(a.produced.o,18,'final O2');
});
test('PSI/bar equivalence',()=>{
  const psi=e.blend(config({startPressure:500}));
  const bar=e.blend(config({units:'bar',startPressure:500*e.BAR_PER_PSI,finalPressure:3000*e.BAR_PER_PSI}));
  for(let i=0;i<3;i++)near(psi.stages[i].stop,bar.stages[i].stop*e.PSI_PER_BAR,'stage '+i);
});
test('Cylinder volume and working pressure are not required for pressure-based blending',()=>{
  const a=e.blend(config()), b=e.blend(config({volumeL:3,ratedPressure:1500}));
  assert.ok(a.ok && b.ok);
  for(let i=0;i<3;i++) near(a.stages[i].stop,b.stages[i].stop,'independent pressure '+i);
  assert.ok(!('freeGasLiters' in a.stages[0]));
});
test('User-selected final pressure is independent of a default cylinder rating',()=>{
  const r=e.blend(config({finalPressure:4000})); assert.ok(r.ok);
  near(r.stages[2].stop,4000,'custom target');
  const t=e.topOff({startO2:21,startHe:0,startPressure:3000,finalPressure:4000,topO2:21,topHe:0});
  near(t.finalPressure,4000,'custom top-off target');
});
test('Source composition over 100% blocks',()=>{
  assert.throws(()=>e.blend(config({topO2:40,topHe:70})),/exceed 100/);
});
test('Top off composition weighted by amounts',()=>{
  const r=e.topOff({units:'psi',basis:'gauge',startO2:21,startHe:0,startPressure:1000,finalPressure:3000,topO2:32,topHe:0});
  near(r.result.o,(1000*21+2000*32)/3000,'O2'); near(r.result.h,0,'He');
});
test('Temperature correction uses absolute Kelvin',()=>{
  const r=e.temperature({units:'psi',pressure:3500,fromTemp:95,toTemp:68,tempUnits:'F'});
  const x=(3500*e.BAR_PER_PSI+e.ATM_BAR)*((68-32)*5/9+273.15)/((95-32)*5/9+273.15)-e.ATM_BAR;
  near(r.settledPressure,x*e.PSI_PER_BAR,'settled PSI');
});
test('Open-circuit MOD and density calculation',()=>{
  const m=e.metrics({o2:18,he:45,depth:200,depthUnits:'ft',mode:'oc',modPO2:1.4});
  near(m.mod,(1.4/.18-1)*33,'MOD');near(m.po2,.18*(1+200/33),'depth PPO2');
  assert.ok(m.rho > 0);
});
test('CCR loop mix uses setpoint and preserves inert ratio',()=>{
  const m=e.metrics({o2:12,he:60,depth:300,depthUnits:'ft',mode:'ccr',setpoint:1.3});
  near(m.working.o,1.3/(1+300/33),'loop oxygen');near(m.working.h/m.working.n,60/28,'inert He:N2');
});
test('Exact no-addition edge case',()=>{
  const r=e.blend(config({startPressure:3000,startO2:18,startHe:45}));assert.ok(r.ok);
  r.stages.forEach(x=>near(x.added,0,'zero addition'));
});
console.log(`\n${testCount} tests passed`);if(process.exitCode)process.exit(1);
// Deterministic property-based mass-balance checks: known-source additions ->
// target composition -> inverse solver should recover all three sources.
function rngFactory(seed) {return ()=>{seed=(1664525*seed+1013904223)>>>0;return seed/4294967296;};}
const rand=rngFactory(492836);
test('500 randomized 3-component inverse solves (gauge and absolute)',()=>{
  for(let k=0;k<500;k++){
    const units=k%2?'psi':'bar',basis=k%3?'gauge':'absolute';
    const startP=10+rand()*30;
    const startO=10+rand()*30,startH=rand()*40;
    const oxygenSource=99.5+rand()*.5, heliumSource=99.8+rand()*.2;
    const topO=16+rand()*40,topH=rand()*20;
    const xHe=5+rand()*40,xOx=3+rand()*15,xTop=20+rand()*60;
    const offset=basis==='absolute'?(units==='psi'?e.ATM_BAR*e.PSI_PER_BAR:e.ATM_BAR):0;
    const P1=startP+xHe+xOx+xTop;
    const srcHe={o:0,h:heliumSource/100,n:1-heliumSource/100};
    const srcOx={o:oxygenSource/100,h:0,n:1-oxygenSource/100};
    const srcTop={o:topO/100,h:topH/100,n:1-(topO+topH)/100};
    const total=P1+offset;
    const ftO=100*((startP+offset)*startO/100+xHe*srcHe.o+xOx*srcOx.o+xTop*srcTop.o)/total;
    const ftH=100*((startP+offset)*startH/100+xHe*srcHe.h+xOx*srcOx.h+xTop*srcTop.h)/total;
    const r=e.blend({units,basis,startPressure:startP,startO2:startO,startHe:startH,finalPressure:P1,targetO2:ftO,targetHe:ftH,topO2:topO,topHe:topH,hePurity:heliumSource,o2Purity:oxygenSource});
    assert.ok(r.ok,`test ${k}`);
    near(r.stages[0].added,xHe,'random He '+k,1e-5);
    near(r.stages[1].added,xOx,'random O2 '+k,1e-5);
    near(r.stages[2].added,xTop,'random top '+k,1e-5);
  }
});
console.log('Final regression status:',testCount,'named test groups (including 500 randomized cases)');
if(process.exitCode)process.exit(1);
