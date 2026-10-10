import {distance} from './geofence';
import {Position} from './types';
// Product-defined proximity to the historic District 1 tourism centre, not an administrative polygon.
export const DISTRICT_CENTER={latitude:10.777,longitude:106.700};
export const DISTRICT_FAR_METERS=5000;
export function districtStatus(position:Position|null,measuredAt:number,now:number):'unknown'|'near'|'far'{
 if(!position||!Number.isFinite(position.latitude)||!Number.isFinite(position.longitude)||position.accuracy==null||!Number.isFinite(position.accuracy)||position.accuracy<0||position.accuracy>100||now-measuredAt>30000||now<measuredAt)return 'unknown';
 return distance(position,DISTRICT_CENTER)-position.accuracy>DISTRICT_FAR_METERS?'far':'near';
}
