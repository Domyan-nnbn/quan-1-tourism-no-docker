import test from 'node:test';
import assert from 'node:assert/strict';
import {districtStatus,DISTRICT_CENTER} from './district';
test('far warning uses 5 km threshold and GPS uncertainty',()=>{
 assert.equal(districtStatus({...DISTRICT_CENTER,accuracy:10},1000,1000),'near');
 assert.equal(districtStatus({latitude:10.9,longitude:106.7,accuracy:10},1000,1000),'far');
 // Around the threshold, uncertainty keeps us from claiming the user is certainly far.
 assert.equal(districtStatus({latitude:DISTRICT_CENTER.latitude+0.045,longitude:106.7,accuracy:100},1000,1000),'near');
});
test('missing, inaccurate and stale location never triggers far warning',()=>{
 assert.equal(districtStatus(null,1000,1000),'unknown');
 for(const accuracy of [null,undefined,101,NaN,-1])assert.equal(districtStatus({latitude:11,longitude:106.7,accuracy},1000,1000),'unknown');
 assert.equal(districtStatus({latitude:11,longitude:106.7,accuracy:5},1000,32000),'unknown');
});
