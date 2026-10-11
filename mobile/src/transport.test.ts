import test from 'node:test';
import assert from 'node:assert/strict';
import {request,ApiError,setNetworkActive} from './transport';
const base='https://api.example';
test('GET retries one transient error but POST is never replayed',async()=>{
 const original=globalThis.fetch;let calls=0;
 try{
  globalThis.fetch=async()=>{calls++;if(calls===1)throw new TypeError('network lost');return new Response('[]');};
  assert.deepEqual(await request(base,'/pois'),[]);assert.equal(calls,2);
  calls=0;globalThis.fetch=async()=>{calls++;throw new TypeError('response lost');};
  await assert.rejects(request(base,'/events',{method:'POST'}),(e:unknown)=>e instanceof ApiError&&e.code==='NETWORK');assert.equal(calls,1);
 }finally{globalThis.fetch=original;}
});
test('background cancels active requests and refuses new requests',async()=>{
 const original=globalThis.fetch;let started=false;
 try{
  globalThis.fetch=async(_input,options)=>new Promise((_resolve,reject)=>{started=true;options?.signal?.addEventListener('abort',()=>reject(new DOMException('aborted','AbortError')));});
  const pending=request(base,'/pois');assert.equal(started,true);setNetworkActive(false);
  await assert.rejects(pending,(e:unknown)=>e instanceof ApiError&&e.code==='PAUSED');
  await assert.rejects(request(base,'/pois'),(e:unknown)=>e instanceof ApiError&&e.code==='PAUSED');
 }finally{setNetworkActive(true);globalThis.fetch=original;}
});
test('Cloudflare 530 has useful guidance; request ID remains available',async()=>{
 const original=globalThis.fetch;
 try{
  globalThis.fetch=async()=>new Response('Cloudflare error',{status:530,headers:{'X-Request-ID':'trace-test'}});
  await assert.rejects(request(base,'/pois'),(e:unknown)=>e instanceof ApiError&&e.status===530&&e.message.includes('cloudflared')&&e.requestId==='trace-test');
 }finally{globalThis.fetch=original;}
});
test('invalid success response is classified without replaying mutations',async()=>{
 const original=globalThis.fetch;let calls=0;
 try{globalThis.fetch=async()=>{calls++;return new Response('<html>');};await assert.rejects(request(base,'/user-auth/login',{method:'POST'}),(e:unknown)=>e instanceof ApiError&&e.code==='FORMAT');assert.equal(calls,1);}
 finally{globalThis.fetch=original;}
});
