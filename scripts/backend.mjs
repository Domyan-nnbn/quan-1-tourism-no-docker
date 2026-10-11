import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const cwd=path.join(root,'backend');
const venv=path.join(cwd,'.venv');
const python=path.join(venv,process.platform==='win32'?'Scripts/python.exe':'bin/python');
const mode=process.argv[2];
function run(exe,args){
 const result=spawnSync(exe,args,{cwd,stdio:'inherit'});
 if(result.error){console.error(result.error.message);process.exit(1);}
 if(result.status!==0)process.exit(result.status||1);
}
if(mode==='install'){
 if(!fs.existsSync(python)){
  const candidates=process.platform==='win32'?[['py','-3.13'],['py','-3.12'],['python']]:[['python3.13'],['python3.12'],['python3'],['python']];
  const selected=candidates.find(([exe,...args])=>spawnSync(exe,[...args,'-c','import sys;sys.exit(0 if sys.version_info[:2] in [(3,12),(3,13)] else 1)'],{stdio:'ignore'}).status===0);
  if(!selected){console.error('Install Python 3.12 or 3.13, reopen VS Code, then run this command again. On Windows: py -0p');process.exit(1);}
  const [exe,...args]=selected;run(exe,[...args,'-m','venv',venv]);
 }
 run(python,['-m','pip','install','-r','requirements.lock']);
 console.log('Backend installed. Next: npm run db:init');
}else{
 if(!fs.existsSync(python)){console.error('Run npm run install:backend first.');process.exit(1);}
 if(!fs.existsSync(path.join(cwd,'.env'))){console.error('Run npm run setup, then configure backend/.env first.');process.exit(1);}
 const commands={accounts:['-m','app.migrate'],translations:['-m','app.import_demo_translations'],migrate:['-m','app.migrate'],seed:['-m','app.seed'],api:['-m','uvicorn','app.main:app','--host','0.0.0.0','--port','8000'],worker:['-m','app.worker'],reset:['-m','app.reset_admin']};
 if(!commands[mode]){console.error('Use install, seed, api, worker or reset.');process.exit(1);}
 run(python,commands[mode]);
}
