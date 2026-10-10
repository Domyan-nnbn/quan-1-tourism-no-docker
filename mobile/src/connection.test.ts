import test from 'node:test';
import assert from 'node:assert/strict';
import {initialApi,normalizeApi} from './connection';
test('API uses configured origin first; otherwise same LAN development host',()=>{
 assert.equal(initialApi('https://tourism.example/','http://192.168.1.31:8081/index.bundle'),'https://tourism.example');
 assert.equal(initialApi('','http://192.168.1.31:8081/index.bundle'),'http://192.168.1.31:8000');
 assert.equal(initialApi('','http://172.20.1.2:8081/index.bundle'),'http://172.20.1.2:8000');
 assert.equal(initialApi('','https://public-tunnel.example/index.bundle'),'');
 assert.equal(initialApi('',undefined),'');
});
test('manual API origins reject credentials and paths',()=>{
 assert.equal(normalizeApi(' http://192.168.1.31:8000/ '),'http://192.168.1.31:8000');
 for(const url of ['file:///test','https://name:secret@example.org','https://example.org/api/v1','https://example.org?token=a'])assert.throws(()=>normalizeApi(url));
});
