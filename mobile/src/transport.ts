export class ApiError extends Error{
 constructor(message:string,public status:number,public code='HTTP',public requestId=''){super(message);}
}
let active=true;
const controllers=new Set<AbortController>();
export function setNetworkActive(value:boolean){active=value;if(!value)for(const controller of controllers)controller.abort();}
export function isPaused(error:unknown){return error instanceof ApiError&&error.code==='PAUSED';}
function httpMessage(status:number,detail:unknown):string{
 if(status===530)return 'Backend tunnel không hoạt động. Kiểm tra URL HTTPS và cloudflared / Backend tunnel is unavailable.';
 if(status===502||status===503||status===504)return 'Backend chưa sẵn sàng. Kiểm tra API, database và worker / Backend is not ready.';
 if(status===429)return 'Quá nhiều yêu cầu. Vui lòng chờ rồi thử lại / Please wait and retry.';
 if(status>=500)return 'Máy chủ gặp lỗi. Thử lại sau / Server error. Please retry.';
 if(typeof detail==='string')return detail;
 if(Array.isArray(detail))return detail.map((e:any)=>`${e.loc?.join('.')||''}: ${e.msg||''}`).join('\n');
 return 'HTTP '+status;
}
export async function request<T>(base:string,path:string,options:RequestInit={},token?:string):Promise<T>{
 if(!active)throw new ApiError('Ứng dụng đang tạm dừng / App is paused',0,'PAUSED');
 if(!/^https?:\/\//.test(base))throw new ApiError('Nhập địa chỉ API trong Cài đặt / Set API address in Settings.',0,'CONFIG');
 const controller=new AbortController();controllers.add(controller);
 const timer=setTimeout(()=>controller.abort(),12000);
 const abort=()=>controller.abort();options.signal?.addEventListener('abort',abort,{once:true});
 if(options.signal?.aborted)controller.abort();
 const replaySafeListen=(options.method||'GET').toUpperCase()==='POST'
   && /^\/pois\/[^/]+\/listen$/.test(path)
   && Boolean(new Headers(options.headers).get('X-Listen-ID'));
 const canRetry=(options.method||'GET').toUpperCase()==='GET'||replaySafeListen;
 try{
  for(let attempt=0;attempt<(canRetry?2:1);attempt++){
   try{
    const response=await fetch(base.replace(/\/$/,'')+'/api/v1'+path,{...options,signal:controller.signal,
     headers:{'Content-Type':'application/json',...(token?{Authorization:'Bearer '+token}:{}),...options.headers}});
    if(!response.ok){
     let detail:unknown;try{const data=await response.json();detail=data.error?.message??data.detail;}catch{}
     throw new ApiError(httpMessage(response.status,detail),response.status,'HTTP',response.headers.get('X-Request-ID')||'');
    }
    if(response.status===204)return undefined as T;
    try{return await response.json() as T;}catch(error){if(controller.signal.aborted)throw error;throw new ApiError('Phản hồi máy chủ không hợp lệ / Invalid server response',response.status,'FORMAT');}
   }catch(error){
    if(controller.signal.aborted)throw error;
    const retryable=error instanceof TypeError||(error instanceof ApiError&&[502,503,504].includes(error.status));
    if(!canRetry||attempt!==0||!retryable)throw error;
    await new Promise<void>((resolve,reject)=>{
     const cancel=()=>{clearTimeout(delay);reject(new Error('aborted'));};
     const delay=setTimeout(()=>{controller.signal.removeEventListener('abort',cancel);resolve();},350);
     controller.signal.addEventListener('abort',cancel,{once:true});
    });
   }
  }
  throw new Error('unreachable');
 }catch(error){
  if(controller.signal.aborted)throw new ApiError(active?'Kết nối bị gián đoạn hoặc quá thời gian / Connection interrupted or timed out':'Ứng dụng đang tạm dừng / App is paused',0,active?'TIMEOUT':'PAUSED');
  if(error instanceof ApiError)throw error;
  throw new ApiError('Không kết nối được backend. Kiểm tra mạng và API URL / Unable to reach backend.',0,'NETWORK');
 }finally{clearTimeout(timer);controllers.delete(controller);options.signal?.removeEventListener('abort',abort);}
}
