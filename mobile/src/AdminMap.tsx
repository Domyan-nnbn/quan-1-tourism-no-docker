import React,{useEffect,useMemo,useRef,useState} from 'react';
import {Text,View} from 'react-native';
import {WebView} from 'react-native-webview';
import {POI} from './types';
import {mapHtml} from './mapHtml';
import {mapScript,mapState} from './mapBridge';
import {C,u} from './ui';

export default function AdminMap({pois}:{pois:POI[]}){
 const web=useRef<WebView>(null),ready=useRef(false);
 const source=useMemo(()=>({html:mapHtml()}),[]);
 useEffect(()=>{if(ready.current)web.current?.injectJavaScript(mapScript(mapState(pois,'vi',null)));},[pois]);
 return <View style={[u.card,{padding:0,overflow:'hidden',gap:0}]}>
  <Text style={[u.label,{padding:14}]}>Bản đồ địa điểm và vùng kích hoạt</Text>
  <WebView ref={web} source={source} originWhitelist={['*']} javaScriptEnabled style={{height:240,backgroundColor:C.bg}}
   onMessage={event=>{try{const message=JSON.parse(event.nativeEvent.data);if(message.type==='ready'){ready.current=true;web.current?.injectJavaScript(mapScript(mapState(pois,'vi',null)));}}catch{}}}
   onShouldStartLoadWithRequest={request=>request.url==='about:blank'||request.url.startsWith('about:blank#')}/>
 </View>;
}
