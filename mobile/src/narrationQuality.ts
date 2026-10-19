import {NarrationLocale} from './types';

/** Guidance only: TTS voices/rates vary; this is not a verified audio duration. */
export function approximateSeconds(script:string,locale:NarrationLocale):number{
 const text=script.trim();
 if(!text)return 0;
 if(locale==='zh'||locale==='ja'){
  // Approximate CJK characters per minute for a measured tour guide voice.
  const chars=Array.from(text).filter(ch=>/[\u3400-\u9fff\u3040-\u30ff\uac00-\ud7afA-Za-z0-9]/u.test(ch)).length;
  return Math.ceil(chars/3.7);
 }
 // Vietnamese words are often individual syllables; use a higher speaking rate.
 const words=text.split(/\s+/u).filter(Boolean).length;
 return Math.ceil(words*60/(locale==='vi'?155:130));
}

export type NarrationGuidance='missing'|'short'|'long'|'target';
export function narrationGuidance(script:string,locale:NarrationLocale):NarrationGuidance{
 if(script.trim().length<20)return 'missing';
 const seconds=approximateSeconds(script,locale);
 if(seconds<45)return 'short';
 if(seconds>85)return 'long';
 return 'target';
}
