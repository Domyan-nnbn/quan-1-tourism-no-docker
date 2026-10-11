import test from 'node:test';
import assert from 'node:assert/strict';
import {ForegroundLocation} from './foregroundLocation';
test('background removes watch and resume starts exactly one fresh watch',async()=>{
 let starts=0,removes=0;const received:number[]=[];let callback!:(v:number)=>void;
 const tracker=new ForegroundLocation<number>(async cb=>{starts++;callback=cb;return {remove:()=>{removes++;}};},v=>received.push(v),()=>{},()=>{});
 await tracker.enable();await tracker.enable();assert.equal(starts,1);callback(1);
 tracker.setActive(false);callback(2);assert.equal(removes,1);assert.deepEqual(received,[1]);
 tracker.setActive(true);await new Promise(r=>setImmediate(r));assert.equal(starts,2);callback(3);assert.deepEqual(received,[1,3]);
 tracker.disable();tracker.setActive(true);assert.equal(removes,2);assert.equal(starts,2);
});
test('watch resolving after pause is removed and never becomes active',async()=>{
 let resolve!:(v:{remove:()=>void})=>void,removed=0;const running:boolean[]=[];let signal!:AbortSignal;
 const tracker=new ForegroundLocation<number>((_,s)=>{signal=s;return new Promise(r=>{resolve=r;});},()=>{},value=>running.push(value),()=>{});
 const pending=tracker.enable();tracker.setActive(false);resolve({remove:()=>{removed++;}});await pending;
 assert.equal(removed,1);assert.ok(signal.aborted);assert.ok(!running.includes(true));
});
