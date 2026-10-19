import test from 'node:test';
import assert from 'node:assert/strict';
import {approximateSeconds,narrationGuidance} from './narrationQuality';

test('guidance detects incomplete and short narration without blocking publication',()=>{
 assert.equal(approximateSeconds('','vi'),0);
 assert.equal(narrationGuidance('short','vi'),'missing');
 assert.equal(narrationGuidance('Đây là một câu chuyện rất ngắn về một địa danh lịch sử.','vi'),'short');
});
test('VN and English estimates distinguish a one-minute script',()=>{
 const script=Array.from({length:135},(_,i)=>'word').join(' ');
 assert.equal(narrationGuidance(script,'en'),'target');
 assert.equal(narrationGuidance(script,'fr'),'target');
 assert.equal(narrationGuidance(Array.from({length:250},()=> 'word').join(' '),'en'),'long');
});
test('CJK scripts work without spaces',()=>{
 assert.equal(narrationGuidance('漢字'.repeat(100),'zh'),'target');
 assert.equal(narrationGuidance('日本語'.repeat(78),'ja'),'target');
});
