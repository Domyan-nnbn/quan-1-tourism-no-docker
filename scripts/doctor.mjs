/** Local preflight checks; does not read or print passwords. No Docker/WSL. */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const has=p=>fs.existsSync(path.join(root,p));
let bad=false;
function report(label,ok,next){
 console.log(`${ok?'[OK]':'[CHECK]'} ${label}${ok?'':` → ${next}`}`);
 if(!ok)bad=true;
}
report('Node.js >= 22.13',Number(process.versions.node.split('.')[0])>=22,'Install Node.js 22+');
report('backend/.env',has('backend/.env'),'Run npm.cmd run setup and configure PostgreSQL');
report('mobile/.env',has('mobile/.env'),'Run npm.cmd run setup');
report('Python backend/.venv',has(process.platform==='win32'?'backend/.venv/Scripts/python.exe':'backend/.venv/bin/python'),'Run npm.cmd run install:backend');
report('Expo mobile/node_modules',has('mobile/node_modules/expo/package.json'),'Run npm.cmd run install:apps');
report('POI migration 0005',has('backend/app/migrations/0005_listen_sessions.sql'),'Restore complete source ZIP');
try{
 const response=await fetch('http://127.0.0.1:8000/health/ready',{signal:AbortSignal.timeout(3500)});
 report('Backend /health/ready',response.ok,'Run npm.cmd run db:migrate then npm.cmd run backend; inspect PostgreSQL');
 if(response.ok){const data=await response.json();console.log('  Status:',data.status,'DB:',data.checks?.database,'Schema:',data.checks?.schema,'Worker:',data.checks?.worker);}
}catch{report('Backend /health/ready',false,'Start PostgreSQL and npm.cmd run backend, then recheck');}
console.log('Note: [CHECK] before initial setup is expected; this diagnostic never modifies the database.');
process.exitCode=bad?1:0;
