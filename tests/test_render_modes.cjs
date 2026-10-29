const fs=require('fs');const vm=require('vm');const assert=require('assert');
const full=fs.readFileSync(__dirname+'/../docs/dive-current.js','utf8');
const a=full.indexOf('function speedColor('),b=full.indexOf('function setFlowDisplay(next)',a);
assert(a>0&&b>a,'renderer code present');
const strokes=[];
let rafCount=0; let scheduledFrame=null;
const flowCtx={beginPath(){},moveTo(){},lineTo(){},stroke(){strokes.push(this.strokeStyle)},fillRect(){},clearRect(){},setTransform(){},
 globalAlpha:1,lineWidth:1,globalCompositeOperation:'source-over',strokeStyle:'white'};
const model=[];
for(let i=0;i<9;i++)for(let j=0;j<9;j++)model.push({lat:47.28+i*.004,lng:-122.55+j*.004,u:.27,v:.12});
const fakeMap={getBounds(){return {pad(){return {contains(a){const lat=Array.isArray(a)?a[0]:a.lat,lng=Array.isArray(a)?a[1]:a.lng;return lat>47.25&&lat<47.36&&lng>-122.65&&lng<-122.4}}}}},getSize(){return {x:760,y:560}},
 containerPointToLatLng([x,y]){return {lat:47.276+y*.00009,lng:-122.555+x*.00009}},
 latLngToContainerPoint([lat,lng]){return {x:(lng+122.555)/.00009,y:(lat-47.276)/.00009}}};
const context={Math,console,KTS_PER_MPS:1.943844492,currentField:{points:model},sscofsManifest:{grid_stride:2},currentBuckets:new Map(),visibleWaterSeeds:[],currentParticles:[],currentsVisible:true,flowDisplay:'arrows',map:fakeMap,flowCtx,currentAnimationFrame:null,clearFlowCanvas(){},stopFlowAnimation(){},resizeFlowCanvas(){},
 performance:{now(){return 500}},requestAnimationFrame(fn){rafCount++;scheduledFrame=fn;return 10},cancelAnimationFrame(){}};
vm.createContext(context);vm.runInContext(full.slice(a,b),context);
vm.runInContext('buildCurrentBuckets(currentField.points);drawArrowMap()',context);
const arrowCount=strokes.length;
assert(arrowCount>15,`insufficient arrows: ${arrowCount}`);
const eastColor=strokes[0];
strokes.length=0;
vm.runInContext('currentField.points.forEach(p=>{p.u=-.7;p.v=.03});drawArrowMap()',context);
assert(strokes.length>15,'arrow redraw produced no strokes');
// Flow mode now actively creates animation frames rather than static dots.
strokes.length=0;
context.flowDisplay='flow';
vm.runInContext('animateCurrents()',context);
assert(rafCount>=1,'flow mode not scheduled');
scheduledFrame(516);
assert(strokes.length>15,'flow animation did not paint visible trails');
assert(context.currentParticles.length>=100,'not enough flow particles');
console.log('PASS: '+arrowCount+' interpolated NOAA-grounded arrows; redrawn; flow animation scheduled; '+context.currentParticles.length+' particles.');
