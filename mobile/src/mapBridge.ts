import {Locale,POI,Position} from './types';
export type MapRegion={latitude:number;longitude:number;latitudeDelta:number;longitudeDelta:number};
export type MapHandle={animateToRegion:(region:MapRegion)=>void};
export function validCoordinates(p:Position):boolean {
 return Number.isFinite(p.latitude)&&Math.abs(p.latitude)<=90&&Number.isFinite(p.longitude)&&Math.abs(p.longitude)<=180;
}
export function mapState(pois:POI[],locale:Locale,position:Position|null) {
 return {type:'state',pois:pois.filter(validCoordinates).map(p=>({id:p.id,name:locale==='vi'?p.name:p.name_en,
  latitude:p.latitude,longitude:p.longitude,radius:Number.isFinite(p.radius)&&p.radius>0?Math.min(p.radius,500):0})),
  position:position&&validCoordinates(position)?{latitude:position.latitude,longitude:position.longitude,
   accuracy:position.accuracy!=null&&Number.isFinite(position.accuracy)&&position.accuracy>=0?position.accuracy:0}:null};
}
export function mapScript(command:unknown):string {
 const json=JSON.stringify(command).replace(/</g,'\\u003c').replace(/\u2028/g,'\\u2028').replace(/\u2029/g,'\\u2029');
 return `window.quan1Map && window.quan1Map.receive(${json}); true;`;
}
export function mapMessage(raw:string):{type:'ready'|'tilesLoaded'|'tileError'|'fatal'|'select';id?:string}|null {
 if(raw.length>2048)return null;
 try{const m=JSON.parse(raw);if(!m||typeof m!=='object')return null;
  if(m.type==='select')return typeof m.id==='string'&&m.id.length<=128?{type:'select',id:m.id}:null;
  if(['ready','tilesLoaded','tileError','fatal'].includes(m.type))return {type:m.type};
 }catch{}return null;
}
