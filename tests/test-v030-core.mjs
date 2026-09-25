import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const html=readFileSync(new URL('../src/index.template.html',import.meta.url),'utf8');
const source=html.match(/^\s*\/\/ GD:MATH:BEGIN[^\n]*\n([\s\S]*?)^\s*\/\/ GD:MATH:END/m)?.[1];
assert.ok(source,'source math boundary');
const core=vm.runInNewContext(`${source};({colorDistanceSq,colorRunsAtColumn,chooseTraceCandidate})`,{Blob,Map});
const target={r:22,g:98,b:79};
assert.ok(Math.sqrt(core.colorDistanceSq(40,61,53,target))>40,'default tolerance keeps dark axes separate from Browser Kitty green');
const w=24,h=20,data=new Uint8ClampedArray(w*h*4);data.fill(255);
// Opaque white background with a 3px green curve and a deliberate 4-column gap.
for(let y=0;y<h;y++)for(let x=0;x<w;x++)data[(y*w+x)*4+3]=255;
for(let x=0;x<w;x++){
  if(x>=9&&x<=12)continue;
  for(let y=8;y<=10;y++){
    const i=(y*w+x)*4;data[i]=target.r;data[i+1]=target.g;data[i+2]=target.b;data[i+3]=255;
  }
}
for(const x of [0,8,13,23]){
  const runs=core.colorRunsAtColumn(data,w,h,x,target,40);
  assert.equal(runs.length,1,`curve run at x=${x}`);assert.ok(Math.abs(runs[0].y-9)<1e-9);
}
for(const x of [9,10,11,12])assert.equal(core.colorRunsAtColumn(data,w,h,x,target,40).length,0,`gap at x=${x}`);
const chosen=core.chooseTraceCandidate([{y:20,distance:2,thickness:3},{y:22,distance:2.2,thickness:3}],21,12,null);
assert.equal(chosen.ambiguous,true,'near-equal branches are review candidates');
assert.equal(core.chooseTraceCandidate([{y:50,distance:0,thickness:3}],10,12,null),null,'discontinuous jump is rejected');
console.log('PASS v0.3 core: color mask, deliberate gaps, ambiguity flag and continuity rejection');
