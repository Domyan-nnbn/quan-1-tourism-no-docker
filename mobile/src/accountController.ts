import {isPaused} from './transport';
/** Session lifecycle independent of React Native so network/race failures are testable. */
export type Account={id:string;name:string;email:string;role:'user'|'admin'};
export type Session={base:string;access_token:string;account:Account};
export const SESSION_KEY='accountSessionV1';
type State={session:Session|null;favorites:string[];pending:boolean;favoriting:boolean};
type Dependencies={
 request:<T>(base:string,path:string,init?:RequestInit,token?:string)=>Promise<T>;
 vault:{get:(key:string)=>Promise<string|null>;set:(key:string,value:string)=>Promise<void>;remove:(key:string)=>Promise<void>};
 onError:(message:string)=>void;
};
function unauthorized(error:unknown){return (error as {status?:number})?.status===401;}
export class AccountController{
 state:State={session:null,favorites:[],pending:false,favoriting:false};
 private epoch=0;
 private base='';
 private favoriteLock=false;
 private syncVersion=0;
 private mutating=false;
 private listeners=new Set<(s:State)=>void>();
 private storage=Promise.resolve();
 constructor(private deps:Dependencies){}
 subscribe(fn:(s:State)=>void){this.listeners.add(fn);return ()=>{this.listeners.delete(fn);};}
 private update(p:Partial<State>){this.state={...this.state,...p};this.listeners.forEach(fn=>fn(this.state));}
 private save(value:Session|null){
  const action=()=>value?this.deps.vault.set(SESSION_KEY,JSON.stringify(value)):this.deps.vault.remove(SESSION_KEY);
  const next=this.storage.then(action);this.storage=next.catch(()=>{});return next;
 }
 bind(base:string){this.epoch++;this.base=base;this.update({session:null,favorites:[],pending:false});}
 cancel(){if(!this.mutating){this.epoch++;this.update({pending:false});}}
 private error(error:unknown){if(isPaused(error))return;this.deps.onError(error instanceof Error?error.message:String(error));}
 private async clear(epoch:number){
  if(epoch!==this.epoch)return;
  this.epoch++;this.update({session:null,favorites:[],pending:false});await this.save(null);
 }
 async restore(){
  if(this.mutating)return;
  const epoch=++this.epoch,base=this.base;
  this.update({pending:true});
  try{
   await this.storage;
   const raw=await this.deps.vault.get(SESSION_KEY);
   if(!raw||epoch!==this.epoch)return;
   let saved:Session;
   try{saved=JSON.parse(raw);}catch{await this.clear(epoch);return;}
   if(saved.base!==base||!saved.access_token)return;
   const account=await this.deps.request<Account>(base,'/session/me',{},saved.access_token);
   if(epoch!==this.epoch)return;
   this.update({session:{...saved,account}});
   await this.refresh();
  }catch(error){
   if(epoch!==this.epoch)return;
   if(unauthorized(error))await this.clear(epoch);
   // Transport failure retains the stored token so foreground/retry can restore it.
   if(!(error as {status?:number})?.status)this.update({favorites:[]});
   this.error(error);
  }finally{if(epoch===this.epoch)this.update({pending:false});}
 }
 async accept(session:Session){
  if(session.base!==this.base)throw new Error('Backend changed; please sign in again');
  const epoch=++this.epoch;
  await this.save(session);
  if(epoch!==this.epoch)return;
  this.update({session,favorites:[],pending:false});await this.refresh();
 }
 async refresh(){
  const session=this.state.session,epoch=this.epoch,sync=++this.syncVersion;
  if(!session){await this.restore();return;}
  if(session.account.role!=='user')return;
  try{
   const favorites=await this.deps.request<string[]>(session.base,'/users/me/favorites',{},session.access_token);
   if(epoch===this.epoch&&sync===this.syncVersion)this.update({favorites});
  }catch(error){
   if(epoch!==this.epoch||sync!==this.syncVersion)return;
   if(unauthorized(error))await this.clear(epoch);
   else if(!(error as {status?:number})?.status)this.update({favorites:[]});
   this.error(error);
  }
 }
 async logout(){
  const session=this.state.session,epoch=this.epoch;if(!session||this.mutating)return;
  this.mutating=true;
  this.update({pending:true});
  try{
   try{await this.deps.request(session.base,'/session/logout',{method:'POST'},session.access_token);}
   catch(error){if(!unauthorized(error))throw error;}
   await this.clear(epoch);
  }catch(error){if(epoch===this.epoch)this.error(error);}
  finally{this.mutating=false;if(epoch===this.epoch)this.update({pending:false});}
 }
 async forget(){await this.clear(this.epoch);}
 async toggle(id:string){
  const session=this.state.session,epoch=this.epoch;
  if(!session||session.account.role!=='user'||this.favoriteLock)return;
  this.favoriteLock=true;this.syncVersion++;this.update({favoriting:true});
  try{
   await this.deps.request(session.base,'/users/me/favorites/'+id,
    {method:this.state.favorites.includes(id)?'DELETE':'PUT'},session.access_token);
   if(epoch===this.epoch)await this.refresh();
  }catch(error){
   if(epoch!==this.epoch)return;
   if(unauthorized(error))await this.clear(epoch);
   this.error(error);
  }finally{this.favoriteLock=false;this.update({favoriting:false});}
 }
}
