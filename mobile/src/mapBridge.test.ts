import test from 'node:test';
import assert from 'node:assert/strict';
import {mapState,mapScript,mapMessage} from './mapBridge';
import {POI} from './types';
const p={id:'a',name:'Địa điểm',name_en:'Place',latitude:10.777,longitude:106.7,radius:30} as POI;
test('map filters invalid coordinates and clears the user marker when GPS is unavailable',()=>{
 const state=mapState([p,{...p,id:'bad',latitude:NaN}],'en',null);
 assert.equal(state.pois.length,1);assert.equal(state.pois[0].name,'Place');assert.equal(state.position,null);
 assert.equal(mapState([p],'vi',{latitude:91,longitude:0}).position,null);
});
test('POI text cannot become executable HTML or close an injected script',()=>{
 const command=mapState([{...p,name:'</script><img onerror=alert(1)>'}],'vi',null);
 const script=mapScript(command);assert.ok(!script.includes('</script>'));assert.ok(script.includes('\\u003c'));
});
test('map bridge rejects invalid, unsupported and oversized messages',()=>{
 assert.equal(mapMessage('not JSON'),null);assert.equal(mapMessage('{"type":"navigate","url":"file:///"}'),null);
 assert.equal(mapMessage('{"type":"select","id":42}'),null);assert.equal(mapMessage('x'.repeat(2049)),null);
 assert.deepEqual(mapMessage('{"type":"select","id":"a"}'),{type:'select',id:'a'});
 assert.deepEqual(mapMessage('{"type":"tilesLoaded"}'),{type:'tilesLoaded'});
});
