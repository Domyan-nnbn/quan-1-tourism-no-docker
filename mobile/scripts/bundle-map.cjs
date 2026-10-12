// Rebuild the committed offline library assets; map tiles still require network.
const fs=require('node:fs');
const path=require('node:path');
const root=path.dirname(__dirname);
const leaflet=path.dirname(require.resolve('leaflet/package.json'));
fs.writeFileSync(path.join(root,'src/mapAssets.json'),JSON.stringify({
 js:fs.readFileSync(path.join(leaflet,'dist/leaflet.js'),'utf8'),
 css:fs.readFileSync(path.join(leaflet,'dist/leaflet.css'),'utf8'),
}));
fs.mkdirSync(path.join(root,'licenses'),{recursive:true});
fs.copyFileSync(path.join(leaflet,'LICENSE'),path.join(root,'licenses/Leaflet-LICENSE.txt'));
console.log('Bundled Leaflet library and license.');
