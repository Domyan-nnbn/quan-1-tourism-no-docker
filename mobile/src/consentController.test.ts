import test from 'node:test';
import assert from 'node:assert/strict';
import {ConsentController} from './consentController';
function store(){const data=new Map<string,string>();return {data,get:async(k:string)=>data.get(k)??null,set:async(k:string,v:string)=>{data.set(k,v);},remove:async(k:string)=>{data.delete(k);}};}
test('failed revocation retains origin token after another origin is used',async()=>{
 const publicStore=store(),secrets=store();let fail=false;const sent:{base:string;token:string|null;grant:boolean}[]=[];
 const manager=new ConsentController(publicStore,secrets,async(base,token,grant)=>{sent.push({base,token,grant});if(fail)throw new Error('network');return {token:token||base+'-token',granted:grant};});
 await manager.set('A',true);fail=true;await assert.rejects(manager.set('A',false));
 assert.equal(await manager.enabled('A'),false);assert.equal(await manager.pending('A'),true);
 assert.equal(await manager.flush('A'),false);fail=false;await manager.set('B',true);
 assert.equal(await manager.token('A'),'A-token');assert.equal(await manager.pending('A'),true);
 assert.equal(await manager.flush('A'),true);assert.equal(await manager.pending('A'),false);
 assert.deepEqual(sent.at(-1),{base:'A',token:'A-token',grant:false});
});
test('legacy consent token is scoped before preferences change',async()=>{
 const publicStore=store(),secrets=store();await secrets.set('consentToken','legacy');
 const manager=new ConsentController(publicStore,secrets,async(_,token,granted)=>({token:token||'new',granted}));
 await manager.migrate('A',true);await manager.migrate('B',false);
 assert.equal(await manager.token('A'),'legacy');assert.equal(await manager.token('B'),null);assert.equal(await secrets.get('consentToken'),null);
});
