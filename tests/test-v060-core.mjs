import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const html=readFileSync(new URL('../src/index.template.html',import.meta.url),'utf8');
const source=html.match(/^\s*\/\/ GD:PROJECT:BEGIN[^\n]*\n([\s\S]*?)^\s*\/\/ GD:PROJECT:END/m)?.[1];
assert.ok(source,'project validation boundary');
const core=vm.runInNewContext(`${source};({PROJECT_FORMAT,PROJECT_FORMAT_VERSION,PROJECT_EXTENSION,validateProjectDocument})`);
const project={
  format:'browser-kitty.graph-digitizer',formatVersion:1,appVersion:'0.6.0',savedAt:'2026-09-24T00:00:00Z',
  workingImage:{name:'figure-p2',mime:'image/png',width:900,height:540,data:'data:image/png;base64,AA=='},
  calibration:{x:{p1:{px:96,py:420},p2:{px:770,py:420}},y:{p1:{px:96,py:420},p2:{px:96,py:85}}},
  values:{x1:'1',x2:'100',y1:'1',y2:'1000'},scales:{x:'log10',y:'log10'},
  series:[{id:'s-1',name:'Manual',color:'#16624f',visible:true},{id:'s-2',name:'Auto',color:'#aa5500',visible:false}],
  activeSeriesId:'s-2',seriesSequence:2,
  points:[
    {id:'p-1',seriesId:'s-1',segmentId:1,px:300,py:300,source:'manual',needsReview:false},
    {id:'p-2',seriesId:'s-2',segmentId:2,px:500,py:250,source:'auto',needsReview:true}
  ],idSequence:2,
  trace:{color:{r:22,g:98,b:79},colorPicked:true,range:{x:96,y:85,w:674,h:335,kind:'axis'},start:{px:430,py:300},tolerance:40,maxJump:12,step:2,maxGap:3},
  export:{csvBase:'graph-data',csvFormat:'standard'},workflowStep:'extract'
};
assert.equal(core.validateProjectDocument(project).ok,true);
assert.equal(core.PROJECT_FORMAT,'browser-kitty.graph-digitizer');
assert.equal(core.PROJECT_FORMAT_VERSION,1);assert.equal(core.PROJECT_EXTENSION,'.graphdigitizer.json');
const future=structuredClone(project);future.formatVersion=2;assert.equal(core.validateProjectDocument(future).reason,'unsupported');
const badPoint=structuredClone(project);badPoint.points[1].px=901;assert.equal(core.validateProjectDocument(badPoint).ok,false);
const dup=structuredClone(project);dup.points[1].id='p-1';assert.equal(core.validateProjectDocument(dup).ok,false);
const badSeries=structuredClone(project);badSeries.series[0].color='green';assert.equal(core.validateProjectDocument(badSeries).ok,false);
const foreign=structuredClone(project);foreign.format='another-app';assert.equal(core.validateProjectDocument(foreign).ok,false);
const badRange=structuredClone(project);badRange.trace.range.x=890;badRange.trace.range.w=20;assert.equal(core.validateProjectDocument(badRange).ok,false);
console.log('PASS v0.6 T11 core: versioned project schema, log axes, multiple series/segments, manual+auto points, future/corrupt rejection');
