import assets from './mapAssets.json';
export function mapHtml():string {
 return `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
 <style>${assets.css} html,body,#map{height:100%;width:100%;margin:0;background:#eef0e9} .leaflet-tooltip{font-family:sans-serif;color:#182e28} .leaflet-control-attribution{font-size:10px;max-width:85vw}</style></head>
 <body><div id="map" aria-label="OpenStreetMap"></div><script>${assets.js.replace(/<\/script/gi,'<\\/script')}</script><script>
 (function(){
  function send(type,id){window.ReactNativeWebView&&window.ReactNativeWebView.postMessage(JSON.stringify({type:type,id:id}));}
  try{
   var map=L.map('map',{zoomControl:true}).setView([10.777,106.700],14);
   var places=L.layerGroup().addTo(map),user=L.layerGroup().addTo(map),lastPois='';
   var tiles=L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{
    minZoom:3,maxZoom:19,keepBuffer:1,updateWhenIdle:true,
    attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
   });
   var tileFailures=0;
   tiles.on('loading',function(){tileFailures=0;});
   tiles.on('tileerror',function(){tileFailures++;send('tileError');});
   tiles.on('load',function(){send(tileFailures?'tileError':'tilesLoaded');});tiles.addTo(map);
   function valid(p){return p&&Number.isFinite(p.latitude)&&Math.abs(p.latitude)<=90&&Number.isFinite(p.longitude)&&Math.abs(p.longitude)<=180;}
   window.quan1Map={map:map,receive:function(command){
    if(!command)return;
    if(command.type==='view'&&valid(command.region)){
     var r=command.region,lat=Math.max(.001,Math.min(120,Math.abs(r.latitudeDelta)||.03)),lon=Math.max(.001,Math.min(360,Math.abs(r.longitudeDelta)||.03));
     map.fitBounds([[Math.max(-85,r.latitude-lat/2),r.longitude-lon/2],[Math.min(85,r.latitude+lat/2),r.longitude+lon/2]],{animate:false});return;
    }
    if(command.type!=='state'||!Array.isArray(command.pois))return;
    var signature=JSON.stringify(command.pois);
    if(signature!==lastPois){lastPois=signature;places.clearLayers();command.pois.forEach(function(p){
     if(!valid(p)||typeof p.id!=='string')return;
     if(p.radius>0)L.circle([p.latitude,p.longitude],{radius:p.radius,color:'#235c48',weight:1,fillOpacity:.12,interactive:false}).addTo(places);
     var title=document.createElement('span');title.textContent=p.name;
     L.circleMarker([p.latitude,p.longitude],{radius:8,color:'#fff',weight:2,fillColor:'#235c48',fillOpacity:1}).bindTooltip(title).on('click',function(){send('select',p.id);}).addTo(places);
    });}
    user.clearLayers();if(valid(command.position)){
     var p=command.position;
     if(p.accuracy>0)L.circle([p.latitude,p.longitude],{radius:p.accuracy,color:'#3879ba',weight:1,fillOpacity:.12,interactive:false}).addTo(user);
     L.circleMarker([p.latitude,p.longitude],{radius:6,color:'#fff',weight:2,fillColor:'#3879ba',fillOpacity:1,interactive:false}).addTo(user);
    }
   }};
   if(window.ResizeObserver)new ResizeObserver(function(){map.invalidateSize();}).observe(document.getElementById('map'));
   else window.addEventListener('resize',function(){map.invalidateSize();});
   send('ready');
  }catch(error){send('fatal');}
 })();</script></body></html>`;
}
