// Pure function: configured URL wins; LAN inference is only for initial development setup.
export function initialApi(configured:string|undefined, scriptUrl:string|undefined):string {
 const explicit=(configured||'').trim().replace(/\/+$/,'');
 if(explicit)return explicit;
 try {const host=new URL(scriptUrl||'').hostname;
  if(host==='localhost'||host==='127.0.0.1'||/^10\./.test(host)||/^192\.168\./.test(host)||/^172\.(1[6-9]|2\d|3[01])\./.test(host))return `http://${host}:8000`;
 }catch{}
 return '';
}
export function normalizeApi(value:string):string {
 const url=new URL(value.trim());
 if(!['http:','https:'].includes(url.protocol)||url.username||url.password||url.search||url.hash||!['','/'].includes(url.pathname))throw new Error('Nhập URL gốc http(s)://host:port / Enter the API origin URL');
 return url.origin;
}
