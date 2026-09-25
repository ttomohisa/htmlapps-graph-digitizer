import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const html=readFileSync(new URL('../src/index.template.html',import.meta.url),'utf8');
const source=html.match(/^\s*\/\/ GD:MATH:BEGIN[^\n]*\n([\s\S]*?)^\s*\/\/ GD:MATH:END/m)?.[1];
assert.ok(source,'source math boundary');
const core=vm.runInNewContext(`${source};({axisTransform,axisUntransform,calibrationFrame,mapImagePoint,mapDataPoint,axisValueOutside})`,{Blob,Map});
const near=(a,b,tol=1e-9)=>assert.ok(Math.abs(a-b)<=tol*Math.max(1,Math.abs(b)),`${a} != ${b}`);

// T03: semilog X and log-log calibration use equal log10 spacing.
const semi={
  x:{scale:'log10',p1:{px:100,py:400,value:1},p2:{px:300,py:400,value:100}},
  y:{scale:'linear',p1:{px:100,py:400,value:0},p2:{px:100,py:100,value:60}}
};
near(core.mapImagePoint(semi,200,250).x,10);
near(core.mapImagePoint(semi,200,250).y,30);
const dbl={
  x:{scale:'log10',p1:{px:100,py:400,value:1},p2:{px:300,py:400,value:100}},
  y:{scale:'log10',p1:{px:100,py:400,value:1},p2:{px:100,py:100,value:1000}}
};
near(core.mapImagePoint(dbl,200,300).x,10);
near(core.mapImagePoint(dbl,200,300).y,10);
assert.throws(()=>core.mapImagePoint({...semi,x:{...semi.x,p1:{...semi.x.p1,value:0}}},200,250),/positive/i);
assert.equal(core.axisValueOutside(10,semi.x),false);
assert.equal(core.axisValueOutside(1000,semi.x),true);

// T04: rotate both straight axes by 7 degrees and retain known values.
const rad=7*Math.PI/180,cs=Math.cos(rad),sn=Math.sin(rad);
const O={px:180,py:390};
const ex={x:520*cs,y:520*sn};
const ey={x:300*sn,y:-300*cs};
const pt=(a,b)=>({px:O.px+a*ex.x+b*ey.x,py:O.py+a*ex.y+b*ey.y});
const xp1=pt(.1,0),xp2=pt(.9,0),yp1=pt(0,.2),yp2=pt(0,.8);
const rotated={x:{scale:'linear',p1:{...xp1,value:0},p2:{...xp2,value:100}},y:{scale:'linear',p1:{...yp1,value:0},p2:{...yp2,value:50}}};
const known=pt(.5,.5),mapped=core.mapImagePoint(rotated,known.px,known.py);
near(mapped.x,50);near(mapped.y,25);
const back=core.mapDataPoint(rotated,50,25);near(back.px,known.px);near(back.py,known.py);
const frame=core.calibrationFrame(rotated);assert.ok(frame.separation>.99,'rotated orthogonal axes remain stable');

// Inverted numerical directions remain valid after rotation.
const reversed={x:{...rotated.x,p1:{...xp1,value:100},p2:{...xp2,value:0}},y:{...rotated.y,p1:{...yp1,value:50},p2:{...yp2,value:0}}};
const rev=core.mapImagePoint(reversed,known.px,known.py);near(rev.x,50);near(rev.y,25);

// Nearly parallel lines must be rejected rather than produce unstable coordinates.
const bad={x:{scale:'linear',p1:{px:0,py:0,value:0},p2:{px:100,py:0,value:1}},y:{scale:'linear',p1:{px:0,py:10,value:0},p2:{px:100,py:11,value:1}}};
assert.throws(()=>core.calibrationFrame(bad),/parallel/i);

console.log('PASS v0.4 T03: linear/log10 mixed and log-log calibration, positive-value validation');
console.log('PASS v0.4 T04: 7-degree rotated affine axes, inverse mapping, reversed values, near-parallel rejection');
