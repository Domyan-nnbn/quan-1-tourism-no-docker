import React, { useEffect, useMemo, useRef, useState } from 'react';
import { ActivityIndicator, Alert, AppState, FlatList, Linking, Modal, Pressable, ScrollView, StyleSheet, Switch, Text, TextInput, View, Image } from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import {MapHandle} from './src/mapBridge';
import PlaceMap from './src/PlaceMap';
import {locationStatus,locationMessages,LocationState} from './src/locationStatus';
import * as Location from 'expo-location';
import * as Speech from 'expo-speech';
import * as Crypto from 'expo-crypto';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { request, body, DEFAULT_API, CONFIGURED_API, API_LOCKED, API_AUTO, vault, setNetworkActive, isPaused } from './src/api';
import { Category, Locale, NarrationLocale, POI, Position } from './src/types';
import { distance, GeofenceEngine, validFix } from './src/geofence';
import { words } from './src/i18n';
import { Button, Field, C, u } from './src/ui';
import Admin from './src/Admin';
import AccountScreen from './src/AccountScreen';
import { useAccount, SESSION_KEY, Session } from './src/session';
import { normalizeApi } from './src/connection';
import { districtStatus, DISTRICT_CENTER } from './src/district';
import { narrationLanguages, speechTag, voiceFor } from './src/languages';
import {ForegroundLocation} from './src/foregroundLocation';
import {ConsentController} from './src/consentController';
import {approximateSeconds} from './src/narrationQuality';
import ChangePasswordScreen from './src/ChangePasswordScreen';
type Tab='explore'|'map'|'saved'|'settings';
const categoryIcon:Record<Category,React.ComponentProps<typeof Ionicons>['name']>={heritage:'business-outline',culture:'library-outline',landmark:'compass-outline',food:'restaurant-outline',nature:'leaf-outline'};
const shades:Record<Category,string>={heritage:'#EAE3D3',culture:'#E4E2F0',landmark:'#DCE8EF',food:'#F2E0CF',nature:'#DDE9D8'};
export default function App(){return <SafeAreaProvider><Tourism/></SafeAreaProvider>}
function Tourism(){
 const [voiceChoices,setVoiceChoices]=useState<Partial<Record<NarrationLocale,string>>>({});
 const [narrationLocale,setNarrationLocale]=useState<NarrationLocale>('vi'),[voices,setVoices]=useState<Speech.Voice[]>([]);
 const [locale,setLocale]=useState<Locale>('vi'),[tab,setTab]=useState<Tab>('explore'),[base,setBase]=useState(DEFAULT_API),[apiDraft,setApiDraft]=useState(DEFAULT_API),[ready,setReady]=useState(false);
 const [pois,setPois]=useState<POI[]>([]),[loading,setLoading]=useState(false),[error,setError]=useState(''),[online,setOnline]=useState(false),[busy,setBusy]=useState(false);
 const [query,setQuery]=useState(''),[category,setCategory]=useState<Category|'all'>('all'),[selected,setSelected]=useState<POI|null>(null);
 const [gpsStarting,setGpsStarting]=useState(false),[gpsProblem,setGpsProblem]=useState<LocationState|null>(null);
 const [advancedConnection,setAdvancedConnection]=useState(false);
 const [position,setPosition]=useState<Position|null>(null),[gps,setGps]=useState(false),[auto,setAuto]=useState(false),[playing,setPlaying]=useState<POI|null>(null),[speed,setSpeed]=useState(0.9),[admin,setAdmin]=useState(false);
 const [consent,setConsent]=useState(false),[consentPending,setConsentPending]=useState(false),[showPassword,setShowPassword]=useState(false),[deleteAccountPrompt,setDeleteAccountPrompt]=useState(false),[deleteAccountPassword,setDeleteAccountPassword]=useState('');
 const [consents]=useState(()=>new ConsentController({get:k=>AsyncStorage.getItem(k),set:(k,v)=>AsyncStorage.setItem(k,v),remove:k=>AsyncStorage.removeItem(k)},vault,
  (origin,token,granted)=>request(origin,'/consent',{method:'POST',headers:token?{'X-Consent-Token':token}:{},body:body({granted,policy:'2026-01'})}))); 
 const [showAccount,setShowAccount]=useState(false),[clock,setClock]=useState(Date.now()),[measuredAt,setMeasuredAt]=useState(0);
 const account=useAccount(base,ready,message=>{if(AppState.currentState==='active')Alert.alert('Quận 1 Tourism',message);});
 const favorites=account.favorites;
 const farStatus=districtStatus(position,measuredAt,clock);
 const gpsState=locationStatus(gps,gpsStarting,gpsProblem,position,measuredAt,clock);
 const usablePosition=gps&&position&&validFix(position,measuredAt,clock)?position:null;
 useEffect(()=>{const timer=setInterval(()=>{if(AppState.currentState==='active')setClock(Date.now());},5000);return()=>clearInterval(timer);},[]);
 useEffect(()=>{if(!account.session){setAdmin(false);setShowPassword(false);setDeleteAccountPrompt(false);setDeleteAccountPassword('');}},[account.session]);
 useEffect(()=>{Speech.getAvailableVoicesAsync().then(setVoices).catch(()=>{});},[]);
 const t=words[locale], engine=useRef(new GeofenceEngine()), active=useRef(AppState.currentState==='active'),loadBusy=useRef(false), speechEpoch=useRef(0),isPlaying=useRef(false),map=useRef<MapHandle|null>(null),loadEpoch=useRef(0);
 const latest=useRef({pois,locale,narrationLocale,voices,auto,consent,base,speed,online,voiceChoices}); latest.current={pois,locale,narrationLocale,voices,auto,consent,base,speed,online,voiceChoices};
 const fix=useRef<{p:Position;time:number}|null>(null);
 const [tracking]=useState(()=>new ForegroundLocation<Location.LocationObject>(async (callback,signal)=>{
  setGpsStarting(true);setGpsProblem(null);
  if(!await Location.hasServicesEnabledAsync())throw new Error('GPS_DISABLED');
  const permission=await Location.requestForegroundPermissionsAsync();
  if(signal.aborted||!active.current)throw new Error('Location request cancelled');
  if(permission.status!=='granted')throw new Error('GPS_DENIED');
  return Location.watchPositionAsync({accuracy:Location.Accuracy.High,timeInterval:5000,distanceInterval:0},callback);
 },loc=>{const p=loc.coords;setPosition(p);setMeasuredAt(loc.timestamp);setClock(Date.now());fix.current={p,time:loc.timestamp};},
 running=>{setGps(running);setGpsStarting(false);},error=>{setAuto(false);setGpsStarting(false);setGpsProblem(error instanceof Error&&error.message==='GPS_DENIED'?'denied':error instanceof Error&&error.message==='GPS_DISABLED'?'disabled':'error');}));
 async function notify(message:string){if(active.current)Alert.alert('Quận 1 Tourism',message);}
 const taskLock=useRef(false);
 async function task(fn:()=>Promise<void>){if(taskLock.current)return;taskLock.current=true;setBusy(true);try{await fn();}catch(e:any){if(!isPaused(e))notify(e.message);}finally{taskLock.current=false;setBusy(false);}}
 useEffect(()=>{(async()=>{try{
  const settings=JSON.parse(await AsyncStorage.getItem('preferences')||'{}');
  const saved=await vault.get(SESSION_KEY);let remembered:Session|null=null;try{remembered=saved?JSON.parse(saved):null;}catch{await vault.remove(SESSION_KEY);}
  const previous=API_AUTO?CONFIGURED_API:(remembered?.base||settings.base||DEFAULT_API);
  if(API_AUTO&&remembered?.base&&remembered.base!==CONFIGURED_API){await vault.remove(SESSION_KEY);await vault.remove('adminToken');}
  const remoteConfig=previous?await request<any>(previous,'/app/config').catch(()=>null):null;
  await consents.migrate(previous,!!settings.consent);
  // Remove legacy downloaded packages once; account tokens/preferences are retained.
  const keys=await AsyncStorage.getAllKeys();await AsyncStorage.multiRemove(keys.filter(k=>k.startsWith('offline:')));
  const b=API_LOCKED?CONFIGURED_API:previous;setBase(b);setApiDraft(b);
  const defaultLocale=settings.locale==='vi'||settings.locale==='en'?settings.locale:remoteConfig?.default_language==='en'?'en':'vi';
  setLocale(defaultLocale);
  setNarrationLocale(narrationLanguages.some(x=>x.code===settings.narrationLocale)?settings.narrationLocale:defaultLocale);
  setSpeed([.75,.9,1.05].includes(settings.speed)?settings.speed:.9);
  if(settings.voiceChoices&&typeof settings.voiceChoices==='object')setVoiceChoices(settings.voiceChoices);
 }catch{}finally{setReady(true);}})();return()=>{tracking.disable();Speech.stop();};},[]);
 useEffect(()=>{if(ready)AsyncStorage.setItem('preferences',JSON.stringify({base,locale,narrationLocale,speed,voiceChoices})).catch(()=>{});},[base,locale,narrationLocale,speed,voiceChoices,ready]);
 useEffect(()=>{if(ready)load();},[base,ready]);
 useEffect(()=>{
  setNetworkActive(active.current);tracking.setActive(active.current);
  const sub=AppState.addEventListener('change',state=>{
   active.current=state==='active';setNetworkActive(active.current);tracking.setActive(active.current);
   engine.current.resetCandidate();fix.current=null;setPosition(null);setMeasuredAt(0);
   if(!active.current){loadEpoch.current++;loadBusy.current=false;setLoading(false);stop();}
   else{Speech.getAvailableVoicesAsync().then(setVoices).catch(()=>{});void load();}
  });
  const timer=setInterval(()=>{if(active.current&&!loadBusy.current)void load(true);},30000);
  return()=>{sub.remove();clearInterval(timer);};
 },[]);
 async function load(quiet=false){
  if(!active.current||loadBusy.current)return;
  const epoch=++loadEpoch.current,origin=latest.current.base;loadBusy.current=true;
  if(!quiet)setLoading(true);setError('');
  try{
   const enabled=await consents.enabled(origin),pending=await consents.pending(origin);
   if(epoch!==loadEpoch.current)return;setConsent(enabled);setConsentPending(pending);
   const p=await request<POI[]>(origin,'/pois');
   if(epoch!==loadEpoch.current)return;
   if(!Array.isArray(p))throw new Error('Phản hồi địa điểm không hợp lệ / Invalid catalog response');
   try{const config=await request<any>(origin,'/app/config');engine.current.configure(config);}catch{}
   setPois(p);setOnline(true);void account.refresh();
   setSelected(old=>old?p.find(item=>item.id===old.id)||null:null);
   await consents.flush(origin);
   if(epoch===loadEpoch.current){setConsent(await consents.enabled(origin));setConsentPending(await consents.pending(origin));}
  }catch(e:any){
   if(epoch!==loadEpoch.current||isPaused(e))return;
   setOnline(false);setPois([]);setSelected(null);stop();engine.current.resetCandidate();setError(e.message);
  }finally{if(epoch===loadEpoch.current){loadBusy.current=false;setLoading(false);}}
 }
 async function sendEvent(p:POI,kind:string){
   const s=latest.current;if(!s.consent)return;
   try{if(await consents.pending(s.base))return;const token=await consents.token(s.base);if(!token)return;await request(s.base,'/events',{method:'POST',headers:{'X-Consent-Token':token},body:body({id:Crypto.randomUUID(),poi_id:p.id,kind,locale:s.narrationLocale})});}catch{} // Best effort; never queue without current consent.
 }
 function stop(){speechEpoch.current++;Speech.stop();isPlaying.current=false;setPlaying(null);}
 async function play(p:POI){
   if(!active.current||!latest.current.online){notify(words[latest.current.locale].networkRequired);return;}
   stop();const epoch=speechEpoch.current;const listenId=Crypto.randomUUID();const settings=latest.current;const text=p.content?.[settings.narrationLocale];if(!text?.trim()){notify(words[settings.locale].missingScript);return;}
   let available=latest.current.voices;
   if(!available.length){try{available=await Speech.getAvailableVoicesAsync();setVoices(available);}catch{}}
   const voice=voiceFor(available,settings.narrationLocale,settings.voiceChoices[settings.narrationLocale]);
   if(!voice){notify(words[settings.locale].missingVoice);return;}
   if(epoch!==speechEpoch.current)return;await Speech.stop();if(epoch!==speechEpoch.current)return;
   isPlaying.current=true;setPlaying(p);engine.current.suppress(p.id,Date.now());
   Speech.speak(text,{language:speechTag[settings.narrationLocale],voice:voice.identifier,rate:settings.speed,onStart:()=>{if(epoch===speechEpoch.current){void request(settings.base,`/pois/${p.id}/listen`,{method:'POST',headers:{'X-Listen-ID':listenId}}).catch(()=>{});sendEvent(p,'narration_started');}},onDone:()=>{if(epoch===speechEpoch.current){isPlaying.current=false;setPlaying(null);sendEvent(p,'narration_completed');}},onStopped:()=>{if(epoch===speechEpoch.current){isPlaying.current=false;setPlaying(null);}},onError:()=>{if(epoch===speechEpoch.current){isPlaying.current=false;setPlaying(null);sendEvent(p,'narration_error');notify('Không đọc được. Kiểm tra giọng TTS đã cài trên máy / Check installed TTS voices.');}}});
 }
 async function enableGps(){await tracking.enable();}
 function gpsFeedback(){return <View style={{gap:6}}><Text accessibilityLiveRegion="polite" style={u.muted}>{locationMessages[locale][gpsState]}</Text>{gpsState==='denied'&&<Button secondary title={locale==='vi'?'Mở cài đặt quyền':'Open permission settings'} onPress={()=>task(()=>Linking.openSettings())}/>}</View>;}
 useEffect(()=>{const timer=setInterval(()=>{const s=latest.current;if(!s.auto||!s.online||!active.current||isPlaying.current||!fix.current)return;const candidate=engine.current.update(fix.current.p,s.pois.filter(p=>!!p.content?.[s.narrationLocale]?.trim() && !!voiceFor(s.voices,s.narrationLocale,s.voiceChoices[s.narrationLocale])),Date.now(),fix.current.time);if(candidate)play(candidate);},1000);return()=>clearInterval(timer);},[]);
 function toggleFavorite(id:string){if(!online){notify(t.networkRequired);return;}if(account.pending||account.favoriting)return;if(account.session?.account.role!=='user'){setSelected(null);if(account.session){notify(locale==='vi'?'Hãy đăng xuất admin rồi đăng nhập tài khoản người dùng để lưu yêu thích.':'Sign out of admin and sign in as a user to save favourites.');}else setShowAccount(true);return;}account.toggle(id);}
 const visible=useMemo(()=>pois.filter(p=>(tab!=='saved'||favorites.includes(p.id))&&(category==='all'||p.category===category)&&(`${p.name} ${p.name_en} ${p.address}`).toLocaleLowerCase().includes(query.toLocaleLowerCase())).sort((a,b)=>usablePosition?distance(usablePosition,a)-distance(usablePosition,b):a.name.localeCompare(b.name)),[pois,tab,favorites,category,query,usablePosition]);
 const name=(p:POI)=>locale==='vi'?p.name:p.name_en;
 function meters(p:POI){if(!usablePosition)return t[p.category];const m=distance(usablePosition,p);return m<1000?`${Math.round(m)} m`:`${(m/1000).toFixed(1)} km`;}
 function card(p:POI){return <Pressable onPress={()=>setSelected(p)} accessibilityRole="button" accessibilityLabel={name(p)} style={s.poiCard}>
   <View style={[s.tile,{backgroundColor:shades[p.category]}]}>{p.image_url?<Image source={{uri:p.image_url}} resizeMode="cover" style={{width:68,height:76,borderRadius:14}}/>:<Ionicons name={categoryIcon[p.category]} color={C.green} size={33}/>}</View>
   <View style={{flex:1,gap:5}}><Text style={s.poiName}>{name(p)}</Text><Text style={u.muted} numberOfLines={1}>{p.address}</Text><Text style={{fontSize:12,color:C.green,fontWeight:'600'}}>{meters(p)} · {p.content?.[narrationLocale]?.trim()?narrationLanguages.find(x=>x.code===narrationLocale)?.label:t.missingScript}</Text>{!!p.opening_hours&&<Text numberOfLines={1} style={u.muted}>Giờ mở cửa: {p.opening_hours}</Text>}</View>
   <Pressable hitSlop={12} onPress={()=>toggleFavorite(p.id)} accessibilityRole="button" accessibilityLabel={favorites.includes(p.id)?t.unfavorite:t.favorite} style={{padding:8}}><Ionicons name={favorites.includes(p.id)?'heart':'heart-outline'} size={22} color={C.green}/></Pressable>
 </Pressable>}
 function narrationSelector(){return <View style={{gap:10}}><Text style={u.label}>{t.narrationLanguage}</Text><View style={{flexDirection:'row',flexWrap:'wrap',gap:8}}>{narrationLanguages.map(l=><Pressable key={l.code} accessibilityRole="button" accessibilityState={{selected:narrationLocale===l.code}} onPress={()=>{stop();engine.current.resetCandidate();setNarrationLocale(l.code);}} style={[s.chip,narrationLocale===l.code&&{backgroundColor:C.green}]}><Text style={{color:narrationLocale===l.code?'white':C.green,fontWeight:'600'}}>{l.label}</Text></Pressable>)}</View><Text style={u.muted}>{voiceFor(voices,narrationLocale)?t.voiceStatus:t.voiceMissing}</Text>{voices.filter(v=>!!voiceFor([v],narrationLocale)).length>1&&<ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{gap:8}}>{voices.filter(v=>!!voiceFor([v],narrationLocale)).map(v=><Pressable key={v.identifier} accessibilityRole="button" accessibilityState={{selected:voiceFor(voices,narrationLocale,voiceChoices[narrationLocale])?.identifier===v.identifier}} onPress={()=>{stop();setVoiceChoices(old=>({...old,[narrationLocale]:v.identifier}));}} style={[s.chip,voiceFor(voices,narrationLocale,voiceChoices[narrationLocale])?.identifier===v.identifier&&{backgroundColor:C.lime}]}><Text style={{color:C.green}}>{v.name}</Text></Pressable>)}</ScrollView>}</View>}
 const header=<View style={{gap:18}}>
   <View style={s.topLine}><View><Text style={s.brand}>quận 1<Text style={{color:'#8DA375'}}> /</Text></Text><Text style={s.eyebrow}>{t.eyebrow}</Text></View><Pressable onPress={()=>{stop();setLocale(locale==='vi'?'en':'vi');}} style={s.language}><Ionicons name="globe-outline" size={17} color={C.green}/><Text style={{color:C.green,fontWeight:'700'}}>{locale.toUpperCase()}</Text></Pressable></View>
   {tab==='explore'&&<View style={s.hero}><View style={s.orbit}/><View style={s.orbit2}/><Text style={s.heroTitle}>{t.title}</Text><Text style={s.heroSubtitle}>{t.subtitle}</Text><Pressable onPress={()=>{setTab('map');enableGps();}} style={s.heroButton}><Ionicons name="navigate-outline" size={18} color={C.ink}/><Text style={{fontWeight:'700',color:C.ink}}>{t.map} ↗</Text></Pressable><Ionicons name="business-outline" size={110} color="#B5CAA2" style={{position:'absolute',right:15,bottom:15,opacity:.3}}/></View>}
   {tab==='saved'&&<><Text style={s.screenTitle}>{t.saved}</Text>{account.session?.account.role!=='user'&&<View style={u.card}><Text style={u.muted}>{locale==='vi'?'Đăng nhập tài khoản người dùng để xem và lưu yêu thích riêng.':'Sign in as a user to save your favourite places.'}</Text>{!account.session&&<Button title={locale==='vi'?'Đăng nhập / Đăng ký':'Sign in / Register'} onPress={()=>setShowAccount(true)}/>}</View>}</>}
   <View style={s.search}><Ionicons name="search-outline" color={C.muted} size={21}/><TextInput style={{flex:1,fontSize:15,color:C.ink}} placeholder={t.search} placeholderTextColor={C.muted} value={query} onChangeText={setQuery} accessibilityLabel={t.search}/>{!!query&&<Pressable onPress={()=>setQuery('')}><Ionicons name="close-circle" size={20} color={C.muted}/></Pressable>}</View>
   <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{gap:8}}>{(['all','heritage','culture','landmark','food','nature'] as const).map(k=><Pressable key={k} onPress={()=>setCategory(k)} style={[s.chip,category===k&&{backgroundColor:C.green,borderColor:C.green}]}><Text style={{fontSize:13,fontWeight:'600',color:category===k?'white':C.muted}}>{t[k]}</Text></Pressable>)}</ScrollView>
   <View style={s.topLine}><Text style={s.sectionLabel}>{t.near}</Text><Text style={u.muted}>{visible.length} {t.count}</Text></View>
 </View>;
 if(!ready)return <SafeAreaView style={s.root}><ActivityIndicator color={C.green}/></SafeAreaView>;
 return <SafeAreaView style={s.root} edges={['top','bottom']}><StatusBar style="dark"/>{!online&&<View style={[s.notice,{marginHorizontal:16,marginVertical:6}]}><Text style={u.muted}>{loading?t.connecting:error||t.networkRequired}</Text><Button title={t.retry} secondary disabled={loading} onPress={()=>{load();account.refresh();}}/></View>}
 {showPassword&&account.session?<ChangePasswordScreen session={account.session} locale={locale} onClose={()=>setShowPassword(false)} onChanged={account.refresh}/>:showAccount?<AccountScreen base={base} locale={locale} onClose={()=>setShowAccount(false)} onConnection={()=>{setShowAccount(false);setTab('settings');}} onSuccess={async session=>{await account.accept(session);setShowAccount(false);setAdmin(session.account.role==='admin');}}/>:admin&&account.session?.account.role==='admin'?<Admin key={base} base={base} token={account.session.access_token} onClose={()=>setAdmin(false)} onChanged={()=>load()} onLogout={account.logout}/>:<>
 {(tab==='explore'||tab==='saved')&&<FlatList data={visible} keyExtractor={p=>p.id} renderItem={({item})=>card(item)} ListHeaderComponent={header} contentContainerStyle={{padding:22,gap:12,paddingBottom:22}} refreshing={loading} onRefresh={()=>{load();account.refresh();}} ListEmptyComponent={<Text style={[u.muted,{textAlign:'center',padding:20}]}>{pois.length?(tab==='saved'?t.emptySaved:t.noResults):t.empty}</Text>}/>}
 {tab==='map'&&<View style={{flex:1}}><View style={{padding:22,gap:12}}><Text style={s.screenTitle}>{t.map}</Text><View style={s.topLine}><Text style={u.muted}>{t.auto}</Text><Switch value={auto} onValueChange={v=>{setAuto(v);engine.current.resetCandidate();if(v)enableGps();}} trackColor={{true:C.green}}/></View><Button title={gps?t.gpsOn:t.gps} secondary onPress={()=>{enableGps();if(usablePosition)map.current?.animateToRegion({...usablePosition,latitudeDelta:.015,longitudeDelta:.015});}}/></View>
 {farStatus==='far'&&<View style={[s.notice,{marginHorizontal:16,marginBottom:10}]}><Text accessibilityRole="alert" style={{color:C.red,fontWeight:'700'}}>{locale==='vi'?'Bạn đang ở quá xa Quận 1':'You are too far from District 1'}</Text><Text style={u.muted}>{locale==='vi'?'Cách điểm trung tâm khoảng':'About'} {position?(distance(position,DISTRICT_CENTER)/1000).toFixed(1):''} km. {locale==='vi'?'Bạn vẫn có thể xem địa điểm và nghe thủ công.':'You can still explore and listen manually.'}</Text><Button secondary title={locale==='vi'?'Xem Quận 1':'View District 1'} onPress={()=>map.current?.animateToRegion({...DISTRICT_CENTER,latitudeDelta:.04,longitudeDelta:.04})}/></View>}{farStatus==='unknown'&&<Text style={[u.muted,{paddingHorizontal:22,paddingBottom:10}]}>{locale==='vi'?'Bật GPS và chờ vị trí chính xác để kiểm tra khoảng cách.':'Enable GPS and wait for an accurate location to check distance.'}</Text>}
 <View style={{paddingHorizontal:22,paddingBottom:8}}>{gpsFeedback()}</View><PlaceMap mapRef={map} pois={pois} locale={locale} position={usablePosition} onSelect={setSelected} onList={()=>setTab('explore')}/>
 <View style={{padding:14,backgroundColor:C.paper}}><Text style={u.muted}>{t.autoHint}{position?.accuracy!=null?` · GPS ±${Math.round(position.accuracy)} m`:''}</Text></View></View>}
 {tab==='settings'&&<ScrollView contentContainerStyle={{padding:22,gap:18,paddingBottom:30}} keyboardShouldPersistTaps="handled"><Text style={s.screenTitle}>{t.settings}</Text>
 <View style={u.card}><Text style={u.h2}>{locale==='vi'?'Tài khoản':'Account'}</Text>{account.pending?<ActivityIndicator color={C.green}/>:account.session?<><Text style={u.text}>{account.session.account.name}</Text><Text style={u.muted}>{account.session.account.email} · {account.session.account.role==='admin'?'Admin':locale==='vi'?'Người dùng':'User'}</Text>{account.session.account.role==='admin'&&<Button title={t.admin} onPress={()=>{stop();if(account.session?.account.role==='admin')setAdmin(true);else if(!account.session)setShowAccount(true);else notify(locale==='vi'?'Đăng xuất tài khoản người dùng để đăng nhập admin.':'Sign out of your user account to sign in as admin.');}}/>}<Button secondary title={locale==='vi'?'Đổi mật khẩu':'Change password'} onPress={()=>setShowPassword(true)}/><Button secondary title={locale==='vi'?'Đăng xuất':'Sign out'} onPress={account.logout}/>{!online&&<Button secondary title={locale==='vi'?'Xóa phiên trên máy để đổi kết nối':'Clear local session to change connection'} onPress={()=>Alert.alert(locale==='vi'?'Xóa phiên trên thiết bị?':'Clear local session?',locale==='vi'?'Bạn cần đăng nhập lại. Phiên trên server chưa được thu hồi khi mất kết nối.':'You will need to sign in again. The server session cannot be revoked while disconnected.',[{text:locale==='vi'?'Hủy':'Cancel',style:'cancel'},{text:locale==='vi'?'Xóa phiên':'Clear',onPress:()=>task(account.forget)}])}/>}</>:<Button title={locale==='vi'?'Đăng nhập / Đăng ký':'Sign in / Register'} onPress={()=>{stop();setShowAccount(true);}}/>}</View>
 <View style={u.card}><Text style={u.h2}>{t.language}</Text><View style={{flexDirection:'row',gap:10}}>{(['vi','en'] as Locale[]).map(l=><View key={l} style={{flex:1}}><Button title={l==='vi'?'Tiếng Việt':'English'} secondary={locale!==l} onPress={()=>{stop();setLocale(l);}}/></View>)}</View>{narrationSelector()}<Text style={u.label}>{t.speed}</Text><View style={{flexDirection:'row',gap:8}}>{[.75,.9,1.05].map(v=><View key={v} style={{flex:1}}><Button title={`${v}×`} secondary={speed!==v} onPress={()=>{stop();setSpeed(v);}}/></View>)}</View><Text style={u.muted}>{t.device}</Text></View>
 <View style={u.card}><View style={s.topLine}><Text style={u.text}>{t.auto}</Text><Switch value={auto} onValueChange={v=>{setAuto(v);engine.current.resetCandidate();if(v)enableGps();}} trackColor={{true:C.green}}/></View><Text style={u.muted}>{t.autoHint}</Text>{gpsFeedback()}<Button disabled={gpsStarting} title={gps?t.gpsOn:t.gps} secondary onPress={enableGps}/>{gps&&<Button title={locale==='vi'?'Tắt GPS':'Disable GPS'} secondary onPress={()=>{tracking.disable();fix.current=null;setGps(false);setGpsStarting(false);setGpsProblem(null);setPosition(null);setAuto(false);engine.current.resetCandidate();}}/>}</View>
 <View style={u.card}><Text style={u.h2}>{t.api}</Text><Text style={u.muted}>{API_LOCKED?(locale==='vi'?'Ứng dụng sử dụng máy chủ cố định.':'This app uses a fixed server.'):(locale==='vi'?'Kết nối được tự điền và ghi nhớ trên máy. Đăng xuất trước khi đổi máy chủ.':'Connection is filled in and remembered. Sign out before changing servers.')}</Text>{!API_LOCKED&&<Button secondary title={advancedConnection?(locale==='vi'?'Ẩn cài đặt nâng cao':'Hide advanced settings'):(locale==='vi'?'Cài đặt kết nối nâng cao':'Advanced connection settings')} onPress={()=>setAdvancedConnection(v=>!v)}/>}
 {!API_LOCKED&&advancedConnection&&<><Field label="API URL" editable={!API_LOCKED&&!account.session&&!account.pending} value={apiDraft} onChangeText={setApiDraft} autoCapitalize="none" autoCorrect={false} placeholder="https://api.example.com"/><Button title={t.connect} disabled={API_LOCKED||busy||!!account.session||account.pending} onPress={()=>task(async()=>{const b=normalizeApi(apiDraft);if(b!==base){stop();await vault.remove('adminToken');await vault.remove(SESSION_KEY);setConsent(false);setConsentPending(false);setPois([]);setSelected(null);setOnline(false);engine.current=new GeofenceEngine();loadEpoch.current++;loadBusy.current=false;setBase(b);latest.current.base=b;}else await load();})}/></>}<Text style={[u.muted,{color:online?C.green:C.red}]}>{online?t.online:error||'Chưa kết nối / Not connected'}</Text></View>
 {account.session?.account.role==='user'&&<View style={u.card}><Text style={u.h2}>{locale==='vi'?'Quyền kiểm soát tài khoản':'Account controls'}</Text><Text style={u.muted}>{locale==='vi'?'Bạn có thể xóa hồ sơ, phiên đăng nhập và địa điểm yêu thích khỏi dịch vụ. Bản sao lưu máy chủ (nếu có) có thể lưu dữ liệu đến khi hết hạn theo lịch của đơn vị vận hành.':'You can remove your profile, sessions, and saved places from the service. Server backups, if any, may retain data until they expire under the operator’s retention schedule.'}</Text>{!deleteAccountPrompt?<Button secondary title={locale==='vi'?'Xóa tài khoản':'Delete account'} disabled={account.pending||busy} onPress={()=>setDeleteAccountPrompt(true)}/>:<><Field label={locale==='vi'?'Nhập mật khẩu để xác nhận':'Enter your password to confirm'} value={deleteAccountPassword} onChangeText={setDeleteAccountPassword} secureTextEntry editable={!account.pending&&!busy}/><Button title={locale==='vi'?'Xác nhận xóa tài khoản':'Confirm account deletion'} disabled={!deleteAccountPassword||account.pending||busy} onPress={()=>Alert.alert(locale==='vi'?'Xóa tài khoản?':'Delete account?',locale==='vi'?'Không thể hoàn tác. Hồ sơ, danh sách yêu thích và mọi phiên đăng nhập sẽ bị xóa khỏi dịch vụ.':'This cannot be undone. Your profile, saved places, and all sign-in sessions will be removed from the service.',[{text:locale==='vi'?'Hủy':'Cancel',style:'cancel'},{text:locale==='vi'?'Xóa tài khoản':'Delete account',style:'destructive',onPress:()=>{void (async()=>{if(await account.deleteAccount(deleteAccountPassword)){setDeleteAccountPrompt(false);setDeleteAccountPassword('');}})();}}])}/><Button secondary title={locale==='vi'?'Hủy':'Cancel'} disabled={account.pending||busy} onPress={()=>{setDeleteAccountPrompt(false);setDeleteAccountPassword('');}}/></>}</View>}
 <View style={u.card}><Text style={u.text}>{t.consent}</Text><Text style={u.muted}>{t.consentHint}</Text>{consentPending&&<Text style={{color:C.red}}>{t.consentPending}</Text>}<Switch value={consent} disabled={busy} trackColor={{true:C.green}} onValueChange={value=>task(async()=>{
  const origin=base;
  if(!value){setConsent(false);latest.current.consent=false;setConsentPending(true);}
  const granted=await consents.set(origin,value);setConsent(granted);setConsentPending(false);
 })}/></View>
 <Text style={[u.muted,{textAlign:'center'}]}>QUẬN 1 TOURISM · 1.3.3 · Online\n{t.demo}</Text>
 </ScrollView>}
 {playing&&<View style={s.player}><Pressable style={{flex:1,gap:3}} onPress={()=>setSelected(playing)}><Text style={{fontSize:10,letterSpacing:2,color:C.lime,fontWeight:'700'}}>{t.playing}</Text><Text numberOfLines={1} style={{color:'white',fontSize:15,fontWeight:'700'}}>{name(playing)}</Text></Pressable><Pressable accessibilityLabel={t.stop} onPress={stop} style={s.stop}><Ionicons name="stop" color={C.green} size={20}/></Pressable></View>}
 <View style={s.tabs}>{(['explore','map','saved','settings'] as Tab[]).map(k=><Pressable accessibilityRole="tab" accessibilityState={{selected:tab===k}} key={k} onPress={()=>{setTab(k);if(k==='saved'){setQuery('');setCategory('all');}}} style={s.tab}><Ionicons name={{explore:'compass-outline',map:'map-outline',saved:'heart-outline',settings:'options-outline'}[k] as any} size={22} color={tab===k?C.green:'#94A097'}/><Text style={{fontSize:11,fontWeight:tab===k?'700':'500',color:tab===k?C.green:C.muted}}>{t[k]}</Text>{tab===k&&<View style={s.dot}/>}</Pressable>)}</View>
 </>}
 <Modal visible={!!selected} animationType="slide" presentationStyle="pageSheet" onRequestClose={()=>setSelected(null)}><SafeAreaView style={s.root}>{selected&&<ScrollView contentContainerStyle={{padding:24,gap:20,paddingBottom:40}}><View style={s.topLine}><Text style={s.sectionLabel}>{t.detail}</Text><Pressable accessibilityLabel={t.close} onPress={()=>setSelected(null)} style={s.language}><Ionicons name="close" size={22} color={C.green}/></Pressable></View><View style={[s.detailArt,{backgroundColor:shades[selected.category]}]}>{selected.image_url?<Image source={{uri:selected.image_url}} resizeMode="cover" accessibilityLabel={name(selected)} style={{width:'100%',height:'100%',borderRadius:24}}/>:<><Ionicons name={categoryIcon[selected.category]} size={85} color={C.green}/><Text style={{fontSize:13,fontWeight:'700',color:C.green,letterSpacing:2}}>{t[selected.category].toUpperCase()}</Text></>}</View><Text style={s.screenTitle}>{name(selected)}</Text><Text style={u.muted}>{selected.address} · {meters(selected)}</Text>{!!selected.opening_hours&&<Text style={u.muted}>{locale==='vi'?'Giờ mở cửa':'Opening hours'}: {selected.opening_hours}</Text>}{narrationSelector()}<Button title={playing?.id===selected.id?t.stop:t.listen} icon={playing?.id===selected.id?'stop':'play'} onPress={()=>playing?.id===selected.id?stop():play(selected)}/>{!!selected.content?.[narrationLocale]?.trim()&&<Text style={u.muted}>{locale==='vi'?'Thời lượng đọc ước tính':'Estimated narration'}: {approximateSeconds(selected.content[narrationLocale],narrationLocale)} {locale==='vi'?'giây':'seconds'} · {locale==='vi'?'tùy giọng và tốc độ':'varies by voice and speed'}</Text>}<Text style={{fontSize:17,lineHeight:29,color:C.ink}}>{selected.content?.[narrationLocale]?.trim()||t.missingScript}</Text><Button title={favorites.includes(selected.id)?t.unfavorite:t.favorite} icon={favorites.includes(selected.id)?'heart':'heart-outline'} secondary onPress={()=>toggleFavorite(selected.id)}/><Button title={t.directions} icon="navigate-outline" secondary onPress={()=>task(async()=>{await Linking.openURL(`https://www.google.com/maps/dir/?api=1&destination=${selected.latitude},${selected.longitude}&travelmode=walking`);})}/><View style={u.card}><Text style={u.label}>{t.source}</Text><Text style={u.muted}>{selected.content?.source.type==='demo_original'?t.demo:`${selected.content?.source.license||''} · adapted / đã biên tập`}</Text>{!!(selected.content?.source.revision_url||selected.content?.source.url||selected.source_url)&&<Button title="Wikipedia ↗" secondary onPress={()=>task(async()=>{await Linking.openURL(selected.content?.source.revision_url||selected.content?.source.url||selected.source_url);})}/>}</View></ScrollView>}</SafeAreaView></Modal>
 </SafeAreaView>;
}
const s=StyleSheet.create({root:{flex:1,backgroundColor:C.bg},topLine:{flexDirection:'row',alignItems:'center',justifyContent:'space-between',gap:12},brand:{fontSize:31,letterSpacing:-1.5,fontWeight:'800',color:C.ink},eyebrow:{fontSize:9,letterSpacing:2,color:C.muted,fontWeight:'700',marginTop:4},language:{flexDirection:'row',gap:7,padding:12,borderRadius:30,backgroundColor:'#EAF0E2',alignItems:'center'},hero:{backgroundColor:C.green,borderRadius:26,padding:24,overflow:'hidden',minHeight:225,gap:12},heroTitle:{fontSize:31,lineHeight:37,fontWeight:'700',letterSpacing:-.8,color:'#F8FAF1',zIndex:1},heroSubtitle:{fontSize:13,color:'#D8E3D4',maxWidth:215,lineHeight:20,zIndex:1},heroButton:{alignSelf:'flex-start',flexDirection:'row',alignItems:'center',gap:10,backgroundColor:C.lime,borderRadius:30,paddingHorizontal:15,paddingVertical:10,zIndex:1},orbit:{position:'absolute',width:240,height:240,borderRadius:120,borderWidth:1,borderColor:'#4F7A62',right:-90,top:-50},orbit2:{position:'absolute',width:240,height:240,borderRadius:120,borderWidth:1,borderColor:'#4F7A62',right:-125,top:-25},search:{backgroundColor:C.paper,borderWidth:1,borderColor:C.line,borderRadius:15,flexDirection:'row',alignItems:'center',gap:10,paddingHorizontal:14,minHeight:51},chip:{paddingHorizontal:16,paddingVertical:10,borderRadius:25,borderWidth:1,borderColor:C.line,backgroundColor:C.paper},sectionLabel:{fontSize:10,fontWeight:'700',letterSpacing:1.5,color:C.muted},poiCard:{padding:12,backgroundColor:C.paper,borderRadius:20,borderWidth:1,borderColor:C.line,flexDirection:'row',gap:13,alignItems:'center',minHeight:105},tile:{width:68,height:76,borderRadius:14,alignItems:'center',justifyContent:'center'},poiName:{fontSize:16,fontWeight:'700',color:C.ink},notice:{borderRadius:12,padding:12,backgroundColor:'#EFEBDE',gap:5},screenTitle:{fontSize:30,fontWeight:'700',letterSpacing:-.8,color:C.ink},tabs:{flexDirection:'row',backgroundColor:C.paper,borderTopWidth:1,borderColor:C.line,paddingTop:12,paddingBottom:8},tab:{flex:1,alignItems:'center',gap:5,minHeight:52},dot:{width:4,height:4,borderRadius:2,backgroundColor:C.green},player:{backgroundColor:C.green,marginHorizontal:12,marginBottom:8,padding:13,borderRadius:18,flexDirection:'row',alignItems:'center',gap:12},stop:{backgroundColor:C.lime,width:42,height:42,borderRadius:21,alignItems:'center',justifyContent:'center'},detailArt:{height:175,borderRadius:24,alignItems:'center',justifyContent:'center',gap:12}});
