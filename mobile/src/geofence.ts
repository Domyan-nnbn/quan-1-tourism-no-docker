import {POI,Position} from './types';
export function distance(a:Position,b:Position):number{
 const rad=Math.PI/180;
 const x=Math.sin((b.latitude-a.latitude)*rad/2)**2+Math.cos(a.latitude*rad)*Math.cos(b.latitude*rad)*Math.sin((b.longitude-a.longitude)*rad/2)**2;
 return 6371000*2*Math.atan2(Math.sqrt(x),Math.sqrt(Math.max(0,1-x)));
}
export function validFix(position:Position,measuredAt:number,now:number,maxAccuracy=25):boolean{
 return Number.isFinite(position.latitude)&&Math.abs(position.latitude)<=90&&
  Number.isFinite(position.longitude)&&Math.abs(position.longitude)<=180&&
  position.accuracy!=null&&Number.isFinite(position.accuracy)&&position.accuracy>=0&&position.accuracy<=maxAccuracy&&
  Number.isFinite(measuredAt)&&now-measuredAt<=15000&&measuredAt<=now+1000;
}
/** Polygon vertices use [latitude, longitude], as stored by the API. */
export function polygonMargin(position:Position, vertices:[number,number][]):number{
 if(vertices.length<3)return -Infinity;
 const latRad=position.latitude*Math.PI/180;
 const xy=vertices.map(([lat,lon])=>[(lon-position.longitude)*111320*Math.cos(latRad),(lat-position.latitude)*111320] as const);
 let inside=false, min=Infinity;
 for(let i=0,j=xy.length-1;i<xy.length;j=i++){
  const [ax,ay]=xy[j], [bx,by]=xy[i];
  if((ay>0)!==(by>0) && 0 < ax+(bx-ax)*(-ay)/(by-ay))inside=!inside;
  const dx=bx-ax,dy=by-ay, t=Math.max(0,Math.min(1,-(ax*dx+ay*dy)/(dx*dx+dy*dy||1)));
  min=Math.min(min,Math.hypot(ax+t*dx,ay+t*dy));
 }
 return inside?min:-min;
}
export function geofenceMargin(position:Position,poi:POI):number{
 if(poi.geofence_type==='polygon'&&poi.polygon_coordinates&&poi.polygon_coordinates.length>=3)
  return polygonMargin(position,poi.polygon_coordinates);
 return poi.radius-distance(position,poi);
}
// Require a fresh measured fix and an uncertainty circle entirely inside a POI.
export class GeofenceEngine{
 private candidate:string|null=null;
 private since=0;
 private cooldown=new Map<string,number>();
 private visited=new Set<string>();
 private maxAccuracy=25;
 private dwellMs=3000;
 private cooldownMs=300000;
 configure(options:{gps_accuracy_m?:number;activation_dwell_seconds?:number;repeat_cooldown_minutes?:number}){
  this.maxAccuracy=Math.max(5,Math.min(25,Number(options.gps_accuracy_m)||25));
  this.dwellMs=Math.max(1000,Math.min(30000,Number(options.activation_dwell_seconds||3)*1000));
  this.cooldownMs=Math.max(60000,Math.min(7200000,Number(options.repeat_cooldown_minutes||5)*60000));
 }
 resetCandidate(){this.candidate=null;this.since=0;}
 suppress(id:string,time:number){this.cooldown.set(id,time);this.visited.add(id);}
 update(position:Position,pois:POI[],time:number,measuredAt:number=time):POI|null{
  if(!validFix(position,measuredAt,time,this.maxAccuracy)){this.resetCandidate();return null;}
  const uncertainty=position.accuracy!;
  for(const p of pois)if(geofenceMargin(position,p)<-Math.max(5,p.exit_buffer_m??20)-uncertainty)this.visited.delete(p.id);
  const nearest=pois.filter(p=>p.content&&uncertainty<=Math.min(this.maxAccuracy,p.gps_accuracy_threshold_m??25)&&
    (p.geofence_type==='polygon'?geofenceMargin(position,p)>=uncertainty:uncertainty<=p.radius/2&&geofenceMargin(position,p)>=uncertainty))
   .sort((a,b)=>geofenceMargin(position,b)-geofenceMargin(position,a))[0];
  if(!nearest||this.visited.has(nearest.id)||time-(this.cooldown.get(nearest.id)??-Infinity)<this.cooldownMs){this.resetCandidate();return null;}
  if(this.candidate!==nearest.id){this.candidate=nearest.id;this.since=time;return null;}
  if(time-this.since<Math.max(this.dwellMs,(nearest.dwell_seconds??3)*1000))return null;
  this.suppress(nearest.id,time);this.resetCandidate();return nearest;
 }
}
