/** Owns foreground subscriptions, including a watch promise resolving after pause. */
export class ForegroundLocation<T>{
 private active=true;
 private wanted=false;
 private epoch=0;
 private starting:number|null=null;
 private abort:AbortController|null=null;
 private subscription:{remove:()=>void}|null=null;
 constructor(private watch:(callback:(fix:T)=>void,signal:AbortSignal)=>Promise<{remove:()=>void}>,
  private onFix:(fix:T)=>void,private onRunning:(running:boolean)=>void,private onError:(error:unknown)=>void){}
 async enable(){this.wanted=true;await this.start();}
 private async start(){
  if(!this.active||!this.wanted||this.subscription||this.starting!==null)return;
  const epoch=++this.epoch;this.starting=epoch;const abort=new AbortController();this.abort=abort;
  try{
   const sub=await this.watch(fix=>{if(epoch===this.epoch&&this.active)this.onFix(fix);},abort.signal);
   if(epoch!==this.epoch||!this.active||!this.wanted){sub.remove();return;}
   this.subscription=sub;this.onRunning(true);
  }catch(error){if(epoch===this.epoch){this.wanted=false;this.onRunning(false);this.onError(error);}}
  finally{if(this.starting===epoch)this.starting=null;}
 }
 setActive(active:boolean){
  this.active=active;
  if(!active)this.pause();else void this.start();
 }
 private pause(){this.epoch++;this.abort?.abort();this.abort=null;this.starting=null;this.subscription?.remove();this.subscription=null;this.onRunning(false);}
 disable(){this.wanted=false;this.pause();}
}
