import test from 'node:test';
import assert from 'node:assert/strict';
import {AccountController,Session,SESSION_KEY} from './accountController';
const session:Session={base:'https://api.example',access_token:'test-token',account:{id:'a',name:'A',email:'a@example.test',role:'user'}};
function fixture(){
 const storage=new Map<string,string>([[SESSION_KEY,JSON.stringify(session)]]),errors:string[]=[];
 const transport={run:async(path:string):Promise<unknown>=>path==='/session/me'?session.account:['poi-a']};
 const c=new AccountController({vault:{get:async k=>storage.get(k)??null,set:async(k,v)=>{storage.set(k,v);},remove:async k=>{storage.delete(k);}},
  request:async<T>(_base:string,path:string)=>await transport.run(path) as T,onError:m=>errors.push(m)});
 c.bind(session.base);return {c,storage,errors,transport};
}
test('network loss preserves token; foreground retry restores session and favorites',async()=>{
 const {c,storage,transport}=fixture();transport.run=async()=>{throw new Error('offline');};
 await c.restore();assert.equal(c.state.session,null);assert.ok(storage.has(SESSION_KEY));assert.equal(c.state.pending,false);
 transport.run=async path=>path==='/session/me'?session.account:['poi-a'];
 await c.restore();assert.deepEqual(c.state.session,session);assert.deepEqual(c.state.favorites,['poi-a']);
});
test('expired session clears persisted token and favorites',async()=>{
 const {c,storage,transport}=fixture();await c.restore();
 transport.run=async()=>{throw Object.assign(new Error('expired'),{status:401});};await c.restore();
 assert.equal(c.state.session,null);assert.deepEqual(c.state.favorites,[]);assert.equal(storage.has(SESSION_KEY),false);
});
test('late restore cannot sign user into a different backend',async()=>{
 const {c,transport}=fixture();let resolve!:(v:unknown)=>void;
 transport.run=()=>new Promise(r=>{resolve=r;});const pending=c.restore();
 await new Promise(r=>setImmediate(r));c.bind('https://other.example');resolve(session.account);await pending;
 assert.equal(c.state.session,null);
});
test('offline logout retains session; successful retry revokes and clears',async()=>{
 const {c,storage,transport}=fixture();await c.restore();
 transport.run=async()=>{throw new Error('offline');};await c.logout();assert.ok(c.state.session);assert.ok(storage.has(SESSION_KEY));
 transport.run=async()=>undefined;await c.logout();assert.equal(c.state.session,null);assert.equal(storage.has(SESSION_KEY),false);
});
test('old favorite response cannot overwrite the newly accepted user',async()=>{
 const {c,transport}=fixture();await c.restore();let resolve!:(v:unknown)=>void;
 transport.run=()=>new Promise(r=>{resolve=r;});const pending=c.refresh();
 transport.run=async()=>['poi-b'];await c.accept({...session,access_token:'token-b',account:{...session.account,id:'b'}});
 resolve(['poi-a']);await pending;assert.deepEqual(c.state.favorites,['poi-b']);
});
test('lost favorite response is reconciled by refresh without optimistic corruption',async()=>{
 const {c,transport}=fixture();await c.restore();transport.run=async()=>{throw new Error('response lost');};
 await c.toggle('poi-b');assert.deepEqual(c.state.favorites,['poi-a']);
 transport.run=async()=>['poi-a','poi-b'];await c.refresh();assert.deepEqual(c.state.favorites,['poi-a','poi-b']);
});
test('late favorite refresh of same user cannot overwrite a newer refresh',async()=>{
 const {c,transport}=fixture();await c.restore();let resolve!:(v:unknown)=>void;
 transport.run=()=>new Promise(r=>{resolve=r;});const pending=c.refresh();
 transport.run=async()=>['latest'];await c.refresh();resolve(['stale']);await pending;assert.deepEqual(c.state.favorites,['latest']);
});
test('foreground restore cannot interrupt logout and revive revoked session',async()=>{
 const {c,storage,transport}=fixture();await c.restore();let resolve!:(v:unknown)=>void;
 transport.run=()=>new Promise(r=>{resolve=r;});const pending=c.logout();await c.restore();resolve(undefined);await pending;
 assert.equal(c.state.session,null);assert.equal(storage.has(SESSION_KEY),false);
});
test('local session recovery works when old backend cannot be reached',async()=>{
 const {c,storage}=fixture();await c.restore();await c.forget();assert.equal(c.state.session,null);assert.equal(storage.has(SESSION_KEY),false);
 c.bind('https://new.example');assert.equal(c.state.pending,false);
});
