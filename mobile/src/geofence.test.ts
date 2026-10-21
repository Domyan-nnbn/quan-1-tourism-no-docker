import test from 'node:test';
import assert from 'node:assert/strict';
import { distance,GeofenceEngine } from './geofence';
import { POI } from './types';
const poi={dwell_seconds:3,accuracy:3,id:'one',latitude:10,longitude:106,radius:30,content:{vi:'x',en:'y'}} as POI & {accuracy:number};
test('Haversine is in metres',()=>{assert.equal(distance(poi,poi),0);assert.ok(Math.abs(distance(poi,{latitude:10.001,longitude:106})-111.19)<1);});
test('debounce, dwell, exit and cooldown',()=>{const e=new GeofenceEngine();assert.equal(e.update(poi,[poi],0),null);assert.equal(e.update(poi,[poi],2999),null);assert.equal(e.update(poi,[poi],3000)?.id,'one');assert.equal(e.update(poi,[poi],400000),null);e.update({...poi,latitude:11},[poi],401000);assert.equal(e.update(poi,[poi],402000),null);assert.equal(e.update(poi,[poi],405000)?.id,'one');});
test('poor accuracy and leaving radius reset debounce',()=>{const e=new GeofenceEngine();e.update(poi,[poi],0);assert.equal(e.update({...poi,accuracy:100},[poi],4000),null);assert.equal(e.update(poi,[poi],5000),null);assert.equal(e.update(poi,[poi],8000)?.id,'one');});
test('overlapping regions choose closest only',()=>{const e=new GeofenceEngine();const far={...poi,id:'two',latitude:10.0001};e.update(poi,[far,poi],0);assert.equal(e.update(poi,[far,poi],3000)?.id,'one');assert.equal(e.update(poi,[far,poi],10000),null);});
test('manual stop suppression does not auto replay',()=>{const e=new GeofenceEngine();e.suppress(poi.id,0);assert.equal(e.update(poi,[poi],10000),null);e.update({...poi,latitude:11},[poi],11000);assert.equal(e.update(poi,[poi],12000),null);});
test('unknown, invalid and excessive accuracy never auto triggers',()=>{
 for(const accuracy of [null,undefined,NaN,-1,40]){
  const e=new GeofenceEngine(),p={...poi,accuracy};e.update(p,[poi],10000,10000);
  assert.equal(e.update(p,[poi],14000,14000),null);
 }
});
test('10 metre radius rejects 6m error and accepts 3m centred fix',()=>{
 const small={...poi,radius:10};const e=new GeofenceEngine();
 e.update({...poi,accuracy:6},[small],0);assert.equal(e.update({...poi,accuracy:6},[small],4000),null);
 e.update(poi,[small],5000);assert.equal(e.update(poi,[small],8000)?.id,'one');
});
test('uncertainty overlapping POI boundary resets dwell',()=>{
 const e=new GeofenceEngine(),edge={...poi,latitude:poi.latitude+.00025};
 e.update(poi,[poi],0);assert.equal(e.update(edge,[poi],3000),null);
 assert.equal(e.update(poi,[poi],4000),null);assert.equal(e.update(poi,[poi],7000)?.id,'one');
});
test('old measured fixes and future timestamps are rejected despite fresh reception',()=>{
 const e=new GeofenceEngine();assert.equal(e.update(poi,[poi],20000,0),null);
 assert.equal(e.update(poi,[poi],24000,0),null);
 assert.equal(e.update(poi,[poi],25000,30000),null);
 e.update(poi,[poi],30000,30000);assert.equal(e.update(poi,[poi],33000,33000)?.id,'one');
});

test('polygon includes interior with conservative GPS margin',()=>{
 const poly={...poi,geofence_type:'polygon' as const,polygon_coordinates:[[9.9997,105.9997],[9.9997,106.0003],[10.0003,106.0003],[10.0003,105.9997]] as [number,number][]};
 const e=new GeofenceEngine();e.update(poi,[poly],0);assert.equal(e.update(poi,[poly],3000)?.id,'one');
});
test('polygon rejects outside and near-edge uncertainty',()=>{
 const poly={...poi,geofence_type:'polygon' as const,polygon_coordinates:[[9.9999,105.9999],[9.9999,106.0001],[10.0001,106.0001],[10.0001,105.9999]] as [number,number][]};
 const e=new GeofenceEngine();
 assert.equal(e.update({...poi,longitude:106.0002},[poly],0),null);
 assert.equal(e.update({...poi,longitude:106.00009,accuracy:5},[poly],3000),null);
});
