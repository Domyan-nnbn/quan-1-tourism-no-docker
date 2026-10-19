import React,{useEffect,useImperativeHandle,useMemo,useRef,useState} from 'react';
import {ActivityIndicator,AppState,Linking,View,Text} from 'react-native';
import {WebView} from 'react-native-webview';
import {Locale,POI,Position} from './types';
import {Button,C,u} from './ui';
import {mapHtml} from './mapHtml';
import {MapHandle,MapRegion,mapState,mapScript,mapMessage} from './mapBridge';

export default function PlaceMap({mapRef,pois,locale,position,onSelect,onList}:{
 mapRef:React.RefObject<MapHandle|null>;pois:POI[];locale:Locale;position:Position|null;
 onSelect:(p:POI)=>void;onList:()=>void;
}){
 const web=useRef<WebView>(null),ready=useRef(false),view=useRef<MapRegion|null>(null);
 const latest=useRef({pois,locale,position});latest.current={pois,locale,position};
 const [attempt,setAttempt]=useState(0),[loaded,setLoaded]=useState(false),[problem,setProblem]=useState(false),[slow,setSlow]=useState(false);
 const [active,setActive]=useState(AppState.currentState==='active');
 const activeRef=useRef(active);
 const source=useMemo(()=>({html:mapHtml()}),[]);
 useImperativeHandle(mapRef,()=>({animateToRegion(region){view.current=region;if(ready.current)web.current?.injectJavaScript(mapScript({type:'view',region}));}}),[]);
 useEffect(()=>{const sub=AppState.addEventListener('change',state=>{const next=state==='active';if(next===activeRef.current)return;activeRef.current=next;ready.current=false;setActive(next);setLoaded(false);setProblem(false);setSlow(false);});return()=>sub.remove();},[]);
 useEffect(()=>{if(!active)return;const timer=setTimeout(()=>setSlow(true),15000);return()=>clearTimeout(timer);},[attempt,active]);
 useEffect(()=>{if(ready.current)web.current?.injectJavaScript(mapScript(mapState(pois,locale,position)));},[pois,locale,position]);
 function retry(){ready.current=false;setLoaded(false);setSlow(false);setProblem(false);setAttempt(n=>n+1);}
 function receive(raw:string){
  const message=mapMessage(raw);if(!message)return;
  if(message.type==='ready'){
   ready.current=true;const s=latest.current;web.current?.injectJavaScript(mapScript(mapState(s.pois,s.locale,s.position)));
   if(view.current)web.current?.injectJavaScript(mapScript({type:'view',region:view.current}));
  }else if(message.type==='tilesLoaded'){setLoaded(true);setProblem(false);}
  else if(message.type==='tileError'||message.type==='fatal')setProblem(true);
  else if(message.type==='select'){const p=latest.current.pois.find(p=>p.id===message.id);if(p)onSelect(p);}
 }
 return <View style={{flex:1,minHeight:180}}>
  {active&&<WebView key={attempt} ref={web} source={source} originWhitelist={['*']} javaScriptEnabled
   style={{flex:1,backgroundColor:C.bg}} applicationNameForUserAgent="Quan1Tourism/1.3.3"
   cacheEnabled geolocationEnabled={false} mixedContentMode="never" setSupportMultipleWindows={false}
   onMessage={event=>receive(event.nativeEvent.data)} onError={()=>setProblem(true)} onHttpError={()=>setProblem(true)}
   onContentProcessDidTerminate={retry} onRenderProcessGone={retry}
   onShouldStartLoadWithRequest={request=>{
    if(request.url==='about:blank'||request.url.startsWith('about:blank#'))return true;
    if(request.url==='https://www.openstreetmap.org/copyright')void Linking.openURL(request.url).catch(()=>{});
    return false;
   }}/>
  }
  {(!loaded||problem)&&active&&<View pointerEvents="none" style={{position:'absolute',top:8,left:12,right:12,backgroundColor:C.paper,padding:12,borderRadius:12,gap:6}}>
   {!problem&&!slow&&<ActivityIndicator color={C.green}/>}
   <Text accessibilityLiveRegion="polite" style={u.muted}>{problem||slow?(locale==='vi'?'Chưa tải được đầy đủ nền bản đồ. Kiểm tra mạng và thử tải lại.':'Map tiles are unavailable or incomplete. Check your connection and reload.'):(locale==='vi'?'Đang tải bản đồ…':'Loading map…')}</Text>
  </View>}
  <View style={{padding:8,backgroundColor:C.paper,flexDirection:'row',gap:8}}>
   <View style={{flex:1}}><Button secondary title={locale==='vi'?'Tải lại bản đồ':'Reload map'} onPress={retry}/></View>
   <View style={{flex:1}}><Button secondary title={locale==='vi'?'Xem danh sách':'Show places'} onPress={onList}/></View>
  </View>
 </View>;
}
