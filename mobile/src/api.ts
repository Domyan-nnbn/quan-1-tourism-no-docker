import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';
import * as Crypto from 'expo-crypto';
import { Manifest } from './types';
export const DEFAULT_API = (process.env.EXPO_PUBLIC_API_URL || '').replace(/\/$/,'');
export async function request<T>(base:string,path:string,options:RequestInit={},token?:string):Promise<T> {
  if (!/^https?:\/\//.test(base)) throw new Error('Nhập địa chỉ API trong Cài đặt / Set API address in Settings.');
  const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),12000);
  try {
    const r=await fetch(base.replace(/\/$/,'')+'/api/v1'+path,{...options,signal:controller.signal,headers:{'Content-Type':'application/json',...(token?{Authorization:'Bearer '+token}:{}),...options.headers}});
    if(!r.ok){let message='HTTP '+r.status;try{const x=await r.json();message=x.error?.message || (Array.isArray(x.detail)?x.detail.map((e:any)=>`${e.loc.join('.')}: ${e.msg}`).join('\n'):x.detail)||message;}catch{}throw new Error(message);}
    return r.status===204?undefined as T:await r.json();
  } catch(e:any){if(e.name==='AbortError') throw new Error('API timeout. Kiểm tra IP, Wi-Fi và backend.');throw e;}finally{clearTimeout(timer);}
}
export const body=(value:unknown)=>JSON.stringify(value);
export const cacheKey=(base:string)=>'offline:'+base.replace(/\/$/,'');
export async function saveOffline(base:string,manifest:Manifest){
  const data=JSON.stringify(manifest);
  const checksum=await Crypto.digestStringAsync(Crypto.CryptoDigestAlgorithm.SHA256,data);
  await AsyncStorage.setItem(cacheKey(base),JSON.stringify({data,checksum}));
}
export async function readOffline(base:string):Promise<Manifest|null>{
  const value=await AsyncStorage.getItem(cacheKey(base));if(!value)return null;
  const x=JSON.parse(value);
  if(await Crypto.digestStringAsync(Crypto.CryptoDigestAlgorithm.SHA256,x.data)!==x.checksum)throw new Error('Offline package checksum mismatch');
  const result=JSON.parse(x.data);if(result.schema!==1||!Array.isArray(result.pois))throw new Error('Offline package format unsupported');return result;
}
export const vault={get:(key:string)=>SecureStore.getItemAsync(key),set:(key:string,value:string)=>SecureStore.setItemAsync(key,value),remove:(key:string)=>SecureStore.deleteItemAsync(key)};
