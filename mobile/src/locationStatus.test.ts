import test from 'node:test';
import assert from 'node:assert/strict';
import {locationStatus} from './locationStatus';
const p={latitude:10.777,longitude:106.7,accuracy:10};
test('cached coordinates cannot report ready when GPS is off or permission is denied',()=>{
 assert.equal(locationStatus(false,false,null,p,100000,100001),'off');
 assert.equal(locationStatus(true,false,'denied',p,100000,100001),'denied');
});
test('GPS distinguishes waiting, old fixes, poor accuracy and valid fixes',()=>{
 assert.equal(locationStatus(false,true,null,null,0,100000),'starting');
 assert.equal(locationStatus(true,false,null,null,0,100000),'waiting');
 assert.equal(locationStatus(true,false,null,p,80000,100000),'stale');
 assert.equal(locationStatus(true,false,null,p,102000,100000),'stale');
 assert.equal(locationStatus(true,false,null,{...p,accuracy:null},100000,100001),'uncertain');
 assert.equal(locationStatus(true,false,null,p,100000,100001),'ready');
});
