import React, { useEffect, useState, useRef } from 'react';
import { View, Text, ScrollView, Pressable, Alert, ActivityIndicator, AppState } from 'react-native';
import * as Crypto from 'expo-crypto';
import { request, body } from './api';
import { POI, Job, Category } from './types';
import { Button, Field, C, u } from './ui';
const jobNames:Record<string,string>={PENDING:'Đang chờ worker',PROCESSING:'Đang nhập bài',RETRY_PENDING:'Đang chờ thử lại',COMPLETED:'Đã tạo bản nháp',FAILED:'Nhập thất bại'};
const blank={name:'',name_en:'',address:'',category:'heritage' as Category,latitude:'10.7769',longitude:'106.7009',radius:'30',source_url:''};
export default function Admin({base,token,onClose,onChanged,onLogout}:{base:string;token:string;onClose:()=>void;onChanged:()=>void;onLogout:()=>void}){
 const [pois,setPois]=useState<POI[]>([]),[jobs,setJobs]=useState<Job[]>([]),[stats,setStats]=useState<any>(null),[selected,setSelected]=useState<POI|null>(null),[editing,setEditing]=useState(false);
 const [form,setForm]=useState(blank),[vi,setVi]=useState(''),[en,setEn]=useState(''),[zh,setZh]=useState(''),[fr,setFr]=useState(''),[ja,setJa]=useState(''),[busy,setBusy]=useState(false),[error,setError]=useState('');
 const epoch=useRef(0),actionLock=useRef(false);
 const api=<T,>(path:string,options:RequestInit={})=>request<T>(base,path,options,token||undefined);
 async function refresh(){
   if(AppState.currentState!=='active')return;const version=++epoch.current;
   try{
    const [p,j,stats]=await Promise.all([api<POI[]>('/admin/pois'),api<Job[]>('/admin/jobs'),api('/admin/analytics')]);
    if(version!==epoch.current||AppState.currentState!=='active')return;
    if(!Array.isArray(p)||!Array.isArray(j))throw new Error('Phản hồi quản trị không hợp lệ');
    setPois(p);setJobs(j);setStats(stats);setError('');setSelected(old=>old?p.find(x=>x.id===old.id)||null:null);
   }catch(error){if(version===epoch.current&&AppState.currentState==='active')throw error;}
 }
 useEffect(()=>{if(!token)return;refresh().catch(e=>setError(e.message));const timer=setInterval(()=>refresh().catch(e=>{if(AppState.currentState==='active')setError(e.message);}),10000);const sub=AppState.addEventListener('change',state=>{if(state!=='active')epoch.current++;else refresh().catch(e=>setError(e.message));});return()=>{epoch.current++;clearInterval(timer);sub.remove();};},[token,base]);
 async function action(fn:()=>Promise<void>){if(actionLock.current)return;actionLock.current=true;setBusy(true);setError('');try{await fn();}catch(e:any){setError(e.message);}finally{actionLock.current=false;setBusy(false);}}
 function edit(p:POI|null){setSelected(p);setEditing(true);setForm(p?{name:p.name,name_en:p.name_en,address:p.address,category:p.category,latitude:String(p.latitude),longitude:String(p.longitude),radius:String(p.radius),source_url:p.source_url}:blank);setVi(p?.drafts?.[0]?.vi||'');setEn(p?.drafts?.[0]?.en||'');setZh(p?.drafts?.[0]?.zh||'');setFr(p?.drafts?.[0]?.fr||'');setJa(p?.drafts?.[0]?.ja||'');setError('');}
 async function mutate(path:string){await api(path,{method:'POST'});await refresh();onChanged();}
 return <ScrollView contentContainerStyle={{padding:22,gap:16,paddingBottom:60}} keyboardShouldPersistTaps="handled">
   <Button title="← Quay lại ứng dụng" onPress={onClose} secondary/>
   <Text style={u.h2}>Quản trị nội dung</Text><Text style={u.muted}>POI → bản nháp → duyệt 5 ngôn ngữ → xuất bản</Text>
   {!!error&&<Text accessibilityRole="alert" style={{color:C.red}}>{error}</Text>}{busy&&<ActivityIndicator color={C.green}/>}
   <>
   <View style={{flexDirection:'row',gap:10}}><View style={{flex:1}}><Button title="+ Thêm địa điểm" disabled={busy} onPress={()=>edit(null)}/></View><Button title="Đăng xuất" secondary disabled={busy} onPress={onLogout}/></View>
   <Text style={u.muted}>{stats?.published_pois||0} POI xuất bản · {(stats?.events||[]).map((e:any)=>`${e.kind}: ${e.count}`).join(' · ')||'Chưa có thống kê'}</Text>
   {editing?<>
   <View style={u.card}><Text style={u.h2}>{selected?'Sửa địa điểm':'Địa điểm mới'}</Text>
   {(['name','name_en','address','latitude','longitude','radius','source_url'] as const).map(k=><Field key={k} label={{name:'Tên tiếng Việt',name_en:'Tên tiếng Anh',address:'Địa chỉ',latitude:'Vĩ độ',longitude:'Kinh độ',radius:'Bán kính (m)',source_url:'Wikipedia URL (vi/en)'}[k]} value={form[k]} onChangeText={v=>setForm(f=>({...f,[k]:v}))} autoCapitalize={k==='source_url'?'none':'sentences'} keyboardType={['latitude','longitude','radius'].includes(k)?'decimal-pad':'default'}/>)}
   <Text style={u.label}>Danh mục</Text><View style={{flexDirection:'row',flexWrap:'wrap',gap:8}}>{(['heritage','culture','landmark','food','nature'] as Category[]).map(k=><Pressable key={k} onPress={()=>setForm(f=>({...f,category:k}))} style={{padding:10,borderRadius:10,backgroundColor:form.category===k?C.lime:C.bg}}><Text>{k}</Text></Pressable>)}</View>
   <Button title="Lưu thông tin POI" disabled={busy} onPress={()=>action(async()=>{if(!form.latitude.trim()||!form.longitude.trim()||!form.radius.trim())throw new Error('Nhập đủ tọa độ và bán kính');const value={...form,latitude:Number(form.latitude),longitude:Number(form.longitude),radius:Number(form.radius)};const p=await api<POI>(selected?'/admin/pois/'+selected.id:'/admin/pois',{method:selected?'PUT':'POST',body:body(value)});setSelected(p);await refresh();onChanged();})}/>
   </View>
   {selected&&<>
   <View style={u.card}><Text style={u.h2}>Nội dung thuyết minh</Text><Text style={u.muted}>Nhập Wikipedia sẽ tạo bản trích xuất để bạn biên tập. Bản này chưa tích hợp AI hoặc dịch tự động.</Text>
   <Button title="Nhập bài Wikipedia → bản nháp" secondary disabled={busy||!selected.source_url} onPress={()=>action(async()=>{await api('/admin/pois/'+selected.id+'/import-wikipedia',{method:'POST',headers:{'Idempotency-Key':Crypto.randomUUID()}});await refresh();})}/>
   <Field label="Kịch bản tiếng Việt" value={vi} onChangeText={setVi} multiline/><Field label="Kịch bản tiếng Anh" value={en} onChangeText={setEn} multiline/><Field label="Kịch bản tiếng Trung (giản thể)" value={zh} onChangeText={setZh} multiline/><Field label="Kịch bản tiếng Pháp" value={fr} onChangeText={setFr} multiline/><Field label="Kịch bản tiếng Nhật" value={ja} onChangeText={setJa} multiline/>
   <Button title="Lưu thành phiên bản nháp mới" disabled={busy} onPress={()=>action(async()=>{await api('/admin/pois/'+selected.id+'/drafts',{method:'POST',body:body({vi,en,zh,fr,ja})});await refresh();})}/>
   {selected.drafts?.map(d=><View key={d.id} style={{paddingTop:14,borderTopWidth:1,borderColor:C.line,gap:8}}><Text style={{fontWeight:'700',color:C.green}}>{d.state} · {d.id.slice(0,8)}</Text><Text numberOfLines={3} style={u.muted}>{d.vi||d.en}</Text><Text style={u.muted}>Nguồn: {d.source.type} {d.source.revision_id?`· revision ${d.source.revision_id}`:''}</Text>
   <Button title="Nạp vào trình soạn thảo" secondary disabled={busy} onPress={()=>{setVi(d.vi);setEn(d.en);setZh(d.zh||'');setFr(d.fr||'');setJa(d.ja||'');}}/>
   {d.state==='DRAFT'&&<Button title="Tôi đã kiểm tra cả 5 ngôn ngữ — Duyệt" disabled={busy} onPress={()=>action(()=>mutate('/admin/content/'+d.id+'/approve'))}/>}
   {d.state==='APPROVED'&&<Button title="Xuất bản phiên bản này" disabled={busy} onPress={()=>action(()=>mutate('/admin/content/'+d.id+'/publish'))}/>}
   </View>)}
   </View>
   <Button title="Gỡ xuất bản" secondary disabled={busy||!selected.published_version} onPress={()=>action(()=>mutate('/admin/pois/'+selected.id+'/unpublish'))}/>
   <Button title="Lưu trữ / xóa khỏi danh sách" secondary disabled={busy} onPress={()=>Alert.alert('Lưu trữ địa điểm?','Địa điểm sẽ biến mất khỏi danh sách công khai.',[{text:'Hủy',style:'cancel'},{text:'Lưu trữ',style:'destructive',onPress:()=>action(async()=>{await api('/admin/pois/'+selected.id,{method:'DELETE'});setEditing(false);setSelected(null);await refresh();onChanged();})}])}/>
   </>}
   <Button title="Về danh sách quản trị" secondary onPress={()=>setEditing(false)}/>
   </>:pois.map(p=><Pressable key={p.id} style={u.card} onPress={()=>edit(p)}><Text style={{fontSize:17,fontWeight:'700',color:C.ink}}>{p.name}</Text><Text style={u.muted}>{p.published_version?'Đang xuất bản':'Chưa xuất bản'} · {p.radius} m · {p.drafts?.length||0} phiên bản</Text></Pressable>)}
   <Text style={u.h2}>Tác vụ Wikipedia</Text><Text style={u.muted}>Cập nhật mỗi 10 giây. Nếu tác vụ chờ lâu, hãy kiểm tra worker đang chạy.</Text><Button secondary title="Làm mới tác vụ" disabled={busy} onPress={()=>action(refresh)}/>{jobs.length===0&&<Text style={u.muted}>Chưa có tác vụ.</Text>}{jobs.map(j=><View key={j.id} style={u.card}><Text style={{fontWeight:'700'}}>{pois.find(p=>p.id===j.poi_id)?.name||j.poi_id}</Text><Text style={u.muted}>{jobNames[j.state]||j.state} · lần thử {j.attempts}</Text>{j.state==='COMPLETED'&&<Text style={u.muted}>Bản nháp đã sẵn sàng. Mở địa điểm để biên tập, bổ sung ngôn ngữ và duyệt.</Text>}{!!j.error&&<Text style={{color:C.red}}>{j.error}</Text>}{j.state==='FAILED'&&<Button title="Thử lại" secondary disabled={busy} onPress={()=>action(()=>mutate('/admin/jobs/'+j.id+'/retry'))}/>}</View>)}
   </>
 </ScrollView>;
}
