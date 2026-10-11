import {POI,Position} from './types';
export function distance(a:Position,b:Position):number{
 const rad=Math.PI/180;
 const x=Math.sin((b.latitude-a.latitude)*rad/2)**2+Math.cos(a.latitude*rad)*Math.cos(b.latitude*rad)*Math.sin((b.longitude-a.longitude)*rad/2)**2;
 return 6371000*2*Math.atan2(Math.sqrt(x),Math.sqrt(Math.max(0,1-x)));
}
export function validFix(position:Position,measuredAt:number,now:number):boolean{
 return Number.isFinite(position.latitude)&&Math.abs(position.latitude)<=90&&
  Number.isFinite(position.longitude)&&Math.abs(position.longitude)<=180&&
  position.accuracy!=null&&Number.isFinite(position.accuracy)&&position.accuracy>=0&&position.accuracy<=25&&
  Number.isFinite(measuredAt)&&now-measuredAt<=15000&&measuredAt<=now+1000;
}
// Require a fresh measured fix and an uncertainty circle entirely inside a POI.
export class GeofenceEngine{
 private candidate:string|null=null;
 private since=0;
 private cooldown=new Map<string,number>();
 private visited=new Set<string>();
 resetCandidate(){this.candidate=null;this.since=0;}
 suppress(id:string,time:number){this.cooldown.set(id,time);this.visited.add(id);}
 update(position:Position,pois:POI[],time:number,measuredAt:number=time):POI|null{
  if(!validFix(position,measuredAt,time)){this.resetCandidate();return null;}
  const uncertainty=position.accuracy!;
  for(const p of pois)if(distance(position,p)-uncertainty>p.radius+20)this.visited.delete(p.id);
  const nearest=pois.filter(p=>p.content&&uncertainty<=p.radius/2&&distance(position,p)+uncertainty<=p.radius)
   .sort((a,b)=>distance(position,a)-distance(position,b))[0];
  if(!nearest||this.visited.has(nearest.id)||time-(this.cooldown.get(nearest.id)??-Infinity)<300000){this.resetCandidate();return null;}
  if(this.candidate!==nearest.id){this.candidate=nearest.id;this.since=time;return null;}
  if(time-this.since<3000)return null;
  this.suppress(nearest.id,time);this.resetCandidate();return nearest;
 }
}
