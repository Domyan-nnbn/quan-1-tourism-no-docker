/** Pending revocations are server control messages, never downloaded app content. */
type Store={get:(key:string)=>Promise<string|null>;set:(key:string,value:string)=>Promise<void>;remove:(key:string)=>Promise<void>};
type Result={token:string;granted:boolean};
export class ConsentController{
 private locks=new Map<string,Promise<unknown>>();
 constructor(private store:Store,private secret:Store,
  private send:(base:string,token:string|null,granted:boolean)=>Promise<Result>){}
 private tokenKey(base:string){return 'consentV2_'+Array.from(base).map(c=>c.codePointAt(0)!.toString(16)).join('_');}
 token(base:string){return this.secret.get(this.tokenKey(base));}
 async migrate(base:string,legacyGranted:boolean){
  const old=await this.secret.get('consentToken');
  if(old){
   if(!await this.token(base))await this.secret.set(this.tokenKey(base),old);
   if(await this.store.get('consentFlag:'+base)===null)await this.store.set('consentFlag:'+base,legacyGranted?'1':'0');
   await this.secret.remove('consentToken');
  }
 }
 async enabled(base:string){return await this.store.get('consentFlag:'+base)==='1'&&!await this.pending(base);}
 async pending(base:string){return await this.store.get('revoke:'+base)==='1';}
 private serial<T>(base:string,action:()=>Promise<T>):Promise<T>{
  const next=(this.locks.get(base)||Promise.resolve()).catch(()=>{}).then(action);
  this.locks.set(base,next);return next.finally(()=>{if(this.locks.get(base)===next)this.locks.delete(base);});
 }
 set(base:string,granted:boolean){return this.serial(base,async()=>{
  if(!granted){await this.store.set('consentFlag:'+base,'0');await this.store.set('revoke:'+base,'1');}
  const result=await this.send(base,await this.token(base),granted);
  await this.secret.set(this.tokenKey(base),result.token);
  await this.store.set('consentFlag:'+base,result.granted?'1':'0');
  await this.store.remove('revoke:'+base);
  return result.granted;
 });}
 async flush(base:string):Promise<boolean>{
  if(!await this.pending(base))return true;
  try{await this.set(base,false);return true;}catch{return false;}
 }
}
