import React,{useState} from 'react';
import {ScrollView,Text,View} from 'react-native';
import {Button,Field,u,C} from './ui';
import {request,body} from './api';
import {Session} from './accountController';
import {Locale} from './types';
export default function ChangePasswordScreen({session,locale,onClose,onChanged}:{session:Session;locale:Locale;onClose:()=>void;onChanged:()=>Promise<void>}){
 const [current,setCurrent]=useState(''),[next,setNext]=useState(''),[confirm,setConfirm]=useState(''),[busy,setBusy]=useState(false),[error,setError]=useState(''),[done,setDone]=useState(false);
 const vi=locale==='vi',minimum=session.account.role==='admin'?12:8;
 async function submit(){
  setError('');
  if(!current||next.length<minimum||next!==confirm||next===current){setError(vi?`Nhập mật khẩu hiện tại và mật khẩu mới khác, ít nhất ${minimum} ký tự; xác nhận phải trùng khớp.`:`Enter your current password and a different new password of at least ${minimum} characters with matching confirmation.`);return;}
  setBusy(true);
  try{await request(session.base,'/session/password',{method:'POST',body:body({current_password:current,new_password:next})},session.access_token);setCurrent('');setNext('');setConfirm('');setDone(true);await onChanged();}
  catch(e:any){setError(e.message);}finally{setBusy(false);}
 }
 return <ScrollView keyboardShouldPersistTaps="handled" contentContainerStyle={{padding:24,gap:18}}>
 <Button secondary title={vi?'← Quay lại':'← Back'} onPress={onClose} disabled={busy}/>
 <Text style={u.h2}>{vi?'Đổi mật khẩu':'Change password'}</Text>
 <Text style={u.muted}>{vi?'Đổi mật khẩu sẽ đăng xuất các phiên khác. Thiết bị này vẫn đăng nhập.':'Changing your password signs out other sessions. This device stays signed in.'}</Text>
 {done?<Text style={u.text}>{vi?'Đã đổi mật khẩu.':'Password changed.'}</Text>:<View style={u.card}>
 <Field label={vi?'Mật khẩu hiện tại':'Current password'} value={current} onChangeText={setCurrent} secureTextEntry maxLength={200} editable={!busy}/>
 <Field label={vi?'Mật khẩu mới':'New password'} value={next} onChangeText={setNext} secureTextEntry maxLength={200} editable={!busy}/>
 <Field label={vi?'Nhập lại mật khẩu mới':'Confirm new password'} value={confirm} onChangeText={setConfirm} secureTextEntry maxLength={200} editable={!busy}/>
 {!!error&&<Text style={{color:C.red}} accessibilityRole="alert">{error}</Text>}
 <Button title={busy?(vi?'Đang xử lý…':'Please wait…'):(vi?'Lưu mật khẩu mới':'Save new password')} disabled={busy} onPress={submit}/>
 </View>}</ScrollView>;
}
