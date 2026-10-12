import {validFix} from './geofence';
import {Position} from './types';

export type LocationState = 'off'|'starting'|'denied'|'disabled'|'error'|'waiting'|'stale'|'uncertain'|'ready';
export function locationStatus(running:boolean, starting:boolean, problem:LocationState|null,
 position:Position|null, measuredAt:number, now:number):LocationState {
 if(problem)return problem;
 if(starting)return 'starting';
 if(!running)return 'off';
 if(!position)return 'waiting';
 if(!Number.isFinite(measuredAt)||now-measuredAt>15000||measuredAt>now+1000)return 'stale';
 return validFix(position,measuredAt,now)?'ready':'uncertain';
}
export const locationMessages = {
 vi:{off:'GPS đang tắt.',starting:'Đang bật GPS…',denied:'Chưa được cấp quyền vị trí. Mở cài đặt để cho phép.',disabled:'Dịch vụ vị trí trên điện thoại đang tắt.',error:'Không mở được GPS. Hãy thử lại.',waiting:'Đang tìm vị trí. Bạn vẫn có thể nghe thủ công.',stale:'Vị trí đã cũ. Đang chờ tín hiệu mới.',uncertain:'Vị trí chưa đủ chính xác để tự phát.',ready:'Đã nhận vị trí chính xác. Tự phát còn phụ thuộc vùng của địa điểm.'},
 en:{off:'GPS is off.',starting:'Starting GPS…',denied:'Location permission is missing. Allow it in Settings.',disabled:'Device location services are off.',error:'Unable to start GPS. Please retry.',waiting:'Finding your location. Manual playback is available.',stale:'Location is old. Waiting for a fresh signal.',uncertain:'Location is not accurate enough for automatic playback.',ready:'An accurate location is available. Automatic playback also requires entering a place’s area.'},
};
