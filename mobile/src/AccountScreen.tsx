import React,{useState} from 'react';
import {ScrollView,Text,View} from 'react-native';
import {Button,Field,u,C} from './ui';
import {request,body} from './api';
import {Session} from './session';
import {Locale} from './types';
export default function AccountScreen({base,locale,onSuccess,onClose,onConnection}:{base:string;locale:Locale;onSuccess:(s:Session)=>Promise<void>;onClose:()=>void;onConnection:()=>void}){
 const [mode,setMode]=useState<'login'|'register'|'admin'>('login');
 const [email,setEmail]=useState(''),[password,setPassword]=useState(''),[confirm,setConfirm]=useState(''),[name,setName]=useState(''),[busy,setBusy]=useState(false),[error,setError]=useState('');
 const vi=locale==='vi',label=(a:string,b:string)=>vi?a:b;
 function switchMode(m:typeof mode){setMode(m);setError('');setPassword('');setConfirm('');}
 async function submit(){
  setError('');if(!email.trim()||!password||(mode==='register'&&!name.trim())){setError(label('Vui lòng nhập đủ thông tin.','Complete all required fields.'));return;}
  if(mode==='register'&&(password.length<8||password!==confirm)){setError(label('Mật khẩu ít nhất 8 ký tự; xác nhận phải trùng khớp.','Use at least 8 characters and matching passwords.'));return;}
  setBusy(true);try{
   const path=mode==='admin'?'/auth/login':mode==='register'?'/user-auth/register':'/user-auth/login';
   const result=await request<Omit<Session,'base'>>(base,path,{method:'POST',body:body({email:email.trim(),password,...(mode==='register'?{name:name.trim()}: {})})});
   await onSuccess({...result,base});
  }catch(e:any){setError(e.message);}finally{setBusy(false);}
 }
 return <ScrollView keyboardShouldPersistTaps="handled" contentContainerStyle={{padding:24,gap:20,paddingBottom:50}}>
 <Button secondary title={label('← Quay lại','← Back')} onPress={onClose} disabled={busy}/>
 <Text style={u.h2}>{mode==='admin'?label('Đăng nhập quản trị','Administrator sign in'):mode==='register'?label('Tạo tài khoản','Create account'):label('Đăng nhập','Sign in')}</Text>
 <Text style={u.muted}>{mode==='admin'?label('Tài khoản quản trị được cấp riêng.','Use your assigned administrator account.'):label('Lưu địa điểm yêu thích và đồng bộ trên các thiết bị.','Save your favourite places across devices.')}</Text>
 <View style={u.card}>
 {mode==='register'&&<Field label={label('Họ tên','Name')} value={name} onChangeText={setName} maxLength={100} editable={!busy}/>}
 <Field label="Email" value={email} onChangeText={setEmail} keyboardType="email-address" autoCapitalize="none" autoCorrect={false} editable={!busy}/>
 <Field label={label('Mật khẩu','Password')} value={password} onChangeText={setPassword} secureTextEntry editable={!busy} maxLength={200}/>
 {mode==='register'&&<Field label={label('Nhập lại mật khẩu','Confirm password')} value={confirm} onChangeText={setConfirm} secureTextEntry editable={!busy}/>}
 {!!error&&<Text accessibilityRole="alert" style={{color:C.red}}>{error}</Text>}
 <Button title={busy?label('Đang xử lý…','Please wait…'):mode==='register'?label('Đăng ký','Register'):label('Đăng nhập','Sign in')} onPress={submit} disabled={busy}/>
 </View>
 {mode==='login'?<><Button secondary title={label('Chưa có tài khoản? Đăng ký','Create a new account')} onPress={()=>switchMode('register')} disabled={busy}/><Button secondary icon="shield-checkmark-outline" title={label('Đăng nhập dành cho admin','Administrator sign in')} onPress={()=>switchMode('admin')} disabled={busy}/></>:<Button secondary title={label('Về đăng nhập người dùng','Back to user sign in')} onPress={()=>switchMode('login')} disabled={busy}/>}
 <Text style={u.muted}>{base?label('Đã điền kết nối máy chủ.','Server connection is filled in.'):label('Chưa có kết nối máy chủ.','Server connection is missing.')}</Text>
 <Button secondary title={label('Cài đặt kết nối','Connection settings')} onPress={onConnection} disabled={busy}/>
 </ScrollView>;
}
