import {useEffect,useRef,useState} from 'react';
import {AppState} from 'react-native';
import {request,vault} from './api';
import {AccountController} from './accountController';
export {SESSION_KEY} from './accountController';
export type {Account,Session} from './accountController';
export function useAccount(base:string,ready:boolean,onError:(message:string)=>void){
 const error=useRef(onError);error.current=onError;
 const [controller]=useState(()=>new AccountController({request,vault,onError:message=>error.current(message)}));
 const [state,setState]=useState(controller.state);
 useEffect(()=>controller.subscribe(setState),[controller]);
 useEffect(()=>{
  controller.bind(base);
  if(!ready)return;
  void controller.restore();
  const listener=AppState.addEventListener('change',next=>{if(next==='active')void controller.restore();else controller.cancel();});
  return ()=>{listener.remove();controller.cancel();};
 },[base,ready,controller]);
 return {...state,accept:controller.accept.bind(controller),logout:controller.logout.bind(controller),
  toggle:controller.toggle.bind(controller),forget:controller.forget.bind(controller),refresh:controller.refresh.bind(controller)};
}
