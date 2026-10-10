import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
let ips=[];
try{ips=Object.values(os.networkInterfaces()).flat().filter(x=>x&&x.family==='IPv4'&&!x.internal).map(x=>x.address);}catch{console.log('Cannot detect LAN IP; use ipconfig and set the API address in app Settings.');}
const lan=process.argv[2]||ips.find(x=>x.startsWith('192.168.'))||ips.find(x=>x.startsWith('10.'))||ips[0]||'127.0.0.1';
const envPath=path.join(root,'backend','.env');
if(!fs.existsSync(envPath)){
 fs.writeFileSync(envPath,`DATABASE_URL=postgresql+psycopg://postgres:CHANGE_ME@localhost:5432/tourism\nJWT_SECRET=${crypto.randomBytes(36).toString('hex')}\nADMIN_EMAIL=admin@quan1.local\nADMIN_PASSWORD=${crypto.randomBytes(18).toString('hex')}\nSEED_DEMO=true\n`,{mode:0o600});
 console.log('Created backend/.env. Set DATABASE_URL to your local PostgreSQL connection.');
 console.log('Admin password is in backend/.env (ADMIN_PASSWORD). Do not share or commit this file.');
}else console.log('backend/.env already exists; preserved.');
const mobile=path.join(root,'mobile','.env');
if(!fs.existsSync(mobile))fs.writeFileSync(mobile,`EXPO_PUBLIC_API_URL=http://${lan}:8000\n`);
console.log(`LAN candidates: ${ips.join(', ')}. Phone API address: http://${lan}:8000`);
console.log('Next: create tourism database in pgAdmin, edit backend/.env, then npm run install:backend and npm run install:apps.');
