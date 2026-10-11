import { NarrationLocale } from './types';
export const narrationLanguages: {code:NarrationLocale;label:string}[]=[
 {code:'vi',label:'Tiếng Việt'}, {code:'en',label:'English'}, {code:'zh',label:'中文'}, {code:'fr',label:'Français'}, {code:'ja',label:'日本語'}
];
export const speechTag:Record<NarrationLocale,string>={vi:'vi-VN',en:'en-US',zh:'zh-CN',fr:'fr-FR',ja:'ja-JP'};
export function voiceFor<T extends {language:string;identifier?:string}>(voices:T[],locale:NarrationLocale,preferred?:string):T|undefined{
 const tag=speechTag[locale].toLowerCase();
 const normalized=(v:T)=>v.language.replace(/_/g,'-').toLowerCase();
 const compatible=voices.filter(v=>normalized(v).split('-')[0]===locale && (locale!=='zh'||!/(tw|hk|hant)/.test(normalized(v))));
 const chosen=compatible.find(v=>v.identifier===preferred);if(chosen)return chosen;
 return compatible.find(v=>normalized(v)===tag) || compatible.find(v=>normalized(v).split('-')[0]===locale && (locale!=='zh'||!/(tw|hk|hant)/.test(normalized(v))));
}
