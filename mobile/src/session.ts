import { useEffect, useRef, useState } from 'react';
import { request, vault, ApiError } from './api';
export type Account={id:string;name:string;email:string;role:'user'|'admin'};
export type Session={base:string;access_token:string;account:Account};
export const SESSION_KEY='accountSessionV1';
export function useAccount(base:string, ready:boolean, onError:(message:string)=>void){
 const [session,setSession]=useState<Session|null>(null),[favorites,setFavorites]=useState<string[]>([]),[pending,setPending]=useState(false);
 const version=useRef(0),current=useRef<Session|null>(null),favoriteLock=useRef(false);
 function assign(s:Session|null){version.current++;current.current=s;setSession(s);setFavorites([]);}
 async function clear(){assign(null);await vault.remove(SESSION_KEY);}
 async function sync(s:Session){
  const epoch=version.current;
  try{const ids=await request<string[]>(s.base,'/users/me/favorites',{},s.access_token);
   if(epoch===version.current&&current.current?.access_token===s.access_token)setFavorites(ids);
  }catch(e:any){if(epoch!==version.current)return;if(e instanceof ApiError&&e.status===401)await clear();onError(e.message);}
 }
 useEffect(()=>{
  if(!ready)return;let cancelled=false;const epoch=++version.current;current.current=null;setSession(null);setFavorites([]);setPending(true);
  (async()=>{try{
   const saved=await vault.get(SESSION_KEY);if(!saved)return;const s:Session=JSON.parse(saved);if(s.base!==base)return;
   const account=await request<Account>(base,'/session/me',{},s.access_token);
   if(cancelled||epoch!==version.current)return;
   const restored={...s,account};assign(restored);if(account.role==='user')await sync(restored);
  }catch(e:any){if(!cancelled&&epoch===version.current){if(e instanceof ApiError&&e.status===401)await clear();onError(e.message);}}
  finally{if(!cancelled)setPending(false);}})();
  return()=>{cancelled=true;version.current++;};
 },[base,ready]);
 async function accept(s:Session){await vault.set(SESSION_KEY,JSON.stringify(s));assign(s);if(s.account.role==='user')await sync(s);}
 async function logout(){
  const s=current.current;if(!s)return;setPending(true);
  try{try{await request(s.base,'/session/logout',{method:'POST'},s.access_token);}catch(e){if(!(e instanceof ApiError&&e.status===401))throw e;}await clear();}
  catch(e:any){onError(e.message+' · Cần kết nối để đăng xuất / Connect to sign out.');}
  finally{setPending(false);}
 }
 async function toggle(id:string){
  const s=current.current;if(!s||s.account.role!=='user'||favoriteLock.current)return;
  favoriteLock.current=true;const epoch=version.current;
  try{await request(s.base,'/users/me/favorites/'+id,{method:favorites.includes(id)?'DELETE':'PUT'},s.access_token);
   if(epoch===version.current)await sync(s);
  }catch(e:any){if(epoch!==version.current)return;if(e instanceof ApiError&&e.status===401)await clear();onError(e.message);}
  finally{favoriteLock.current=false;}
 }
 return {session,favorites,pending,accept,logout,toggle,refresh:async()=>{const s=current.current;if(s?.account.role==='user')await sync(s);}};
}
