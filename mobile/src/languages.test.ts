import test from 'node:test';
import assert from 'node:assert/strict';
import {narrationLanguages,speechTag,voiceFor} from './languages';
test('five distinct narration languages map to correct TTS tags',()=>{
 assert.deepEqual(narrationLanguages.map(x=>x.code),['vi','en','zh','fr','ja']);
 assert.equal(speechTag.zh,'zh-CN');assert.equal(speechTag.ja,'ja-JP');
});
test('voice matching uses correct language and does not substitute English',()=>{
 const voices=[{language:'en-US',id:1},{language:'fr_FR',id:2},{language:'ja-JP',id:3}];
 assert.equal(voiceFor(voices,'fr')?.id,2);assert.equal(voiceFor(voices,'ja')?.id,3);assert.equal(voiceFor(voices,'zh'),undefined);
});
test('Simplified Chinese prefers mainland Mandarin voice',()=>{
 const voices=[{language:'zh-TW',id:1},{language:'zh-CN',id:2}];assert.equal(voiceFor(voices,'zh')?.id,2);assert.equal(voiceFor([{language:'zh-HK'}],'zh'),undefined);
});
test('preferred voice must match narration language and falls back if removed',()=>{
 const voices=[{identifier:'en-voice',language:'en-US'},{identifier:'vi-one',language:'vi-VN'},{identifier:'vi-two',language:'vi-VN'}];
 assert.equal(voiceFor(voices,'vi','vi-two')?.identifier,'vi-two');
 assert.equal(voiceFor(voices,'vi','en-voice')?.identifier,'vi-one');
 assert.equal(voiceFor(voices,'vi','missing')?.identifier,'vi-one');
});
