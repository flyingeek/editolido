!function(t,e){"object"==typeof exports&&"object"==typeof module?module.exports=e():"function"==typeof define&&define.amd?define([],e):"object"==typeof exports?exports.editolido=e():t.editolido=e()}(window,function(){return function(t){var e={};function n(i){if(e[i])return e[i].exports;var r=e[i]={i:i,l:!1,exports:{}};return t[i].call(r.exports,r,r.exports,n),r.l=!0,r.exports}return n.m=t,n.c=e,n.d=function(t,e,i){n.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:i})},n.r=function(t){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},n.t=function(t,e){if(1&e&&(t=n(t)),8&e)return t;if(4&e&&"object"==typeof t&&t&&t.__esModule)return t;var i=Object.create(null);if(n.r(i),Object.defineProperty(i,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var r in t)n.d(i,r,function(e){return t[e]}.bind(null,r));return i},n.n=function(t){var e=t&&t.__esModule?function(){return t.default}:function(){return t};return n.d(e,"a",e),e},n.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},n.p="",n(n.s=0)}([function(t,e,n){t.exports=n(1)},function(t,e,n){"use strict";n.r(e);class i{constructor(t,e){this.latitude=t,this.longitude=e}get[Symbol.toStringTag](){return"LatLng"}get asDM(){const t=function(t,e="NS"){let n=Math.abs(t),i=Math.floor(n),r=60*(n-i),o=Math.floor(r),s=Math.round(10*(r-o));s>=10&&(s=0,o+=1),o>=60&&(o=0,i+=1);let l="",a=2;return"NS"===e?l=t>=0?e[0]:e[1]:(l=t>0?e[0]:e[1],a=3),[l,i.toFixed(0).padStart(a,"0"),o.toFixed(0).padStart(2,"0"),"."+s.toFixed(0)].join("")};return t(this.latitude)+t(this.longitude,"EW")}get asLatPhi(){const[t,e]=[this.latitude,this.longitude].map(t=>t*Math.PI/180);return new r(t,e)}}class r{constructor(t,e){this.rlat=t,this.phi=e}get[Symbol.toStringTag](){return"LatPhi"}get asLatLng(){const[t,e]=[this.rlat,this.phi].map(t=>180*t/Math.PI);return new i(t,e)}}const o=6371e3,s=t=>t*o/1852,l=t=>1852*t/o;function a(t){return t&&t.length?new i(...t):new i([0,0])}class c{constructor(t,{name:e="",description:n="",normalizer:r=a}={}){t instanceof c?(this.latlng=t.latlng,e=e||t.name||"",n=n||t.description||""):t instanceof i?this.latlng=t:t&&Reflect.has(t,"longitude")&&Reflect.has(t,"latitude")?(this.latlng=new i(parseFloat(t.latitude),parseFloat(t.longitude)),e=e||t.name||"",n=n||t.description||""):this.latlng=r?r(t):t,this.name=e.trim(),this.description=n,this.latphi_cache=null,this.dm_cache=null}get[Symbol.toStringTag](){return"GeoPoint"}get latitude(){return this.latlng.latitude}get longitude(){return this.latlng.longitude}get latphi(){return null===this.latphi_cache&&(this.latphi_cache=this.latlng.asLatPhi),this.latphi_cache}get dm(){return null===this.dm_cache&&(this.dm_cache=this.latlng.asDM),this.dm_cache}static distance(t,e,n=null){return t.distanceTo(e,n)}static getCenter(t,e){let n=t.length,i=0,o=0,s=0,l=0,a=0;for(let e of t){o=e.latphi.rlat,i=e.latphi.phi;let t=Math.cos(o);s+=t*Math.cos(i),l+=t*Math.sin(i),a+=Math.sin(o)}return s/=n,l/=n,a/=n,o=Math.atan2(a,Math.sqrt(Math.pow(s,2)+Math.pow(l,2))),i=Math.atan2(l,s),new c(new r(o,i).asLatLng,e||{})}distanceTo(t,e=null){const n=this.latphi.rlat,i=this.latphi.phi,r=t.latphi.rlat,o=t.latphi.phi,s=Math.acos(Math.sin(n)*Math.sin(r)+Math.cos(n)*Math.cos(r)*Math.cos(o-i));return null!==e?e(s):s}atFraction(t,e=.5,n=null){const i=null===n?this.distanceTo(t):n,o=this.latphi.rlat,s=this.latphi.phi,l=t.latphi.rlat,a=t.latphi.phi,d=Math.sin((1-e)*i)/Math.sin(i),h=Math.sin(e*i)/Math.sin(i),p=d*Math.cos(o)*Math.cos(s)+h*Math.cos(l)*Math.cos(a),u=d*Math.cos(o)*Math.sin(s)+h*Math.cos(l)*Math.sin(a),m=d*Math.sin(o)+h*Math.sin(l),f=Math.atan2(m,Math.sqrt(Math.pow(p,2)+Math.pow(u,2))),g=Math.atan2(u,p);return new c(new r(f,g).asLatLng)}equals(t){return this.latitude.toFixed(6)===t.latitude.toFixed(6)&&this.longitude.toFixed(6)===t.longitude.toFixed(6)}toJSON(){return{__geopoint__:!0,latitude:this.latitude.toFixed(6),longitude:this.longitude.toFixed(6),name:this.name,description:this.description}}}const d=0,h=["#placemark-none","#placemark-blue","#placemark-yellow","#placemark-brown","#placemark-orange","#placemark-pink","#placemark-red","#placemark-green","#placemark-purple"],p=["FFFFFF","6699FF","FFFF00","CC9966","FF9922","DD5599","FF0000","22DD44","BB11EE"].map(t=>`http://chart.googleapis.com/chart?chst=d_map_pin_letter&chld=|${t}`),u=["null","blue","yellow","red","orange","red","red","green","purple"].map(t=>`http://download.avenza.com/images/pdfmaps_icons/pin-${t}-inground.png`);class m{constructor(t,{name:e="",description:n=""}={}){this.points=t||[],this.name=e,this.description=n}get[Symbol.toStringTag](){return"Route"}get[Symbol.iterator](){return this.points[Symbol.iterator]}equals(t){if(this.points.length!==t.points.length)return!1;for(let[e,n]of((t,e)=>t.map((t,n)=>[t,e[n]]))(this.points,t.points))if(!e.equals(n))return!1;return!0}get segments(){let t=[];return this.points.length>0&&this.points.reduce((e,n)=>(t.push([e,n]),n)),t}distance(t=s){const e=this.segments.map(([t,e])=>t.distanceTo(e)).reduce((t,e)=>t+e,0);return null===t?e:t(e)}split(t,e){let{converter:n=l,preserve:i=!1}=e||{},r=[],o=0,s=!0,a=n?n(t):t,c=null,d=null;for([c,d]of this.segments){s&&(s=!1,r.push(c));let t=c.distanceTo(d),e=o;for(;e<=t-a;)e+=a,r.push(c.atFraction(d,e/t,t));o=parseFloat((e-t).toFixed(10)),i&&o&&(r.push(d),o=0)}return o&&r.push(d),new m(r,e)}}class f extends m{constructor(t,e){let{isMine:n=!1,isComplete:i=!0}=e||{};super(t,e),this.isMine=n,this.isComplete=i}get[Symbol.toStringTag](){return"Track"}}const g=({point:t,style:e})=>`\n     <Placemark>\n      <name><![CDATA[${t.name||t.dm}]]></name>\n      <styleUrl>${e}</styleUrl>\n      <description><![CDATA[${t.description||""}]]></description>\n      <Point>\n        <coordinates>${t.longitude.toFixed(6)},${t.latitude.toFixed(6)}</coordinates>\n      </Point>\n    </Placemark>\n`,y=({coordinates:t,name:e,style:n,description:i})=>`\n<Placemark>\n  <name><![CDATA[${e}]]></name>\n  <styleUrl>${n}</styleUrl>\n  <description><![CDATA[${i}]]></description>\n  <LineString>\n    <tessellate>1</tessellate>\n    <coordinates>${t}</coordinates>\n  </LineString>\n</Placemark>\n`,T=({coordinates:t,name:e,style:n})=>`\n<Placemark>\n  <name><![CDATA[${e}]]></name>\n  <styleUrl>${n}</styleUrl>\n  <LineString>\n    <coordinates>${t}</coordinates>\n  </LineString>\n</Placemark>\n`,F=({name:t,content:e,open:n=1})=>`\n<Folder>\n    <name>${t}</name>\n    <open>${n}</open>\n    ${e}\n</Folder>\n`,M=({name:t,styles:e,folders:n})=>`<?xml version='1.0' encoding='UTF-8'?>\n<kml xmlns='http://www.opengis.net/kml/2.2'>\n  <Document>\n    <name><![CDATA[${t}]]></name>\n        ${e}\n        ${n}\n  </Document>\n</kml>\n`,S=({name:t,styles:e,folders:n})=>`<?xml version='1.0' encoding='UTF-8'?>\n<kml xmlns='http://www.opengis.net/kml/2.2'>\n  <Document>\n    <name><![CDATA[${t}]]></name>\n        ${e}\n        <Folder><name><![CDATA[${t}]]></name>\n        ${n}\n        </Folder>\n  </Document>\n</kml>\n`,P=({id:t,color:e,width:n=6})=>`\n    <Style id="${t}">\n        <LineStyle>\n            <width>${n}</width>\n            <color>${e}</color>\n        </LineStyle>\n    </Style>\n`,_=({id:t,color:e,width:n=2})=>P({id:t,color:e,width:n}),x=({id:t,href:e,x:n="0.5",y:i="0.0"})=>`\n    <Style id="${t}">\n        <IconStyle>\n            <Icon>\n                <href><![CDATA[${e}]]></href>\n            </Icon>\n            <hotSpot x="${n}"  y="${i}" xunits="fraction" yunits="fraction"/>\n        </IconStyle>\n    </Style>\n`,$=({id:t,href:e,x:n="0.5",y:i="0.5"})=>x({id:t,href:e,x:n,y:i}),b=Symbol("pin private property");class w{constructor(t,e={}){this.name=t,this.options=e,this.linestrings=[],this.placemarks=[],this.lineStyle={},this[b]=void 0===e.pinId?d:e.pinId,this.enabled=void 0===e.enabled||e.enabled}get pin(){return this[b]}empty(){this.linestrings=[],this.placemarks=[]}set pin(t){const e=h[this[b]];this[b]=t;const n=h[t];this.placemarks=this.placemarks.map(t=>(t.style===e&&(t.style=n),t))}}class k{constructor(t={}){this.folders=new Map,this.template=t.template||M,this.pointTemplate=t.pointTemplate||g,this.lineTemplate=t.lineTemplate||y,this.folderTemplate=t.folderTemplate||F,this.styleTemplate=t.styleTemplate||P,this.iconTemplate=t.iconTemplate||x,this.segmentTemplate=t.segmentTemplate||T,this.icons=t.icons||p}static escape(t){return t.replace("&","&amp;").replace("<","&lt;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")}computeOptions(t,e={},n=!1){if(e={...e},n&&void 0===e.style){let{style:n=this.folders.get(t).pin}=e;e.style=n}return void 0===e.style?e.style="#"+t:isNaN(e.style)||(e.style=h[e.style]),e}addFolder(t,e={}){let n=new w(t,e);this.folders.set(t,n);let i={id:t,color:t+"_color"};n.lineStyle={...i,...e}}addFolders(...t){for(let e of t)if("string"==typeof e||e instanceof String)this.addFolder(e);else{let t={...e};Reflect.deleteProperty(t,"name"),this.addFolder(e.name,t)}}addLine(t,e,n={}){let i={name:(n=this.computeOptions(t,n)).name||e.name,style:n.style,description:n.description||e.description};this.folders.get(t).linestrings.push(this.renderLine(e.points,{...i,...n}))}addPoints(t,e,n={}){const i=n.excluded||[];n=this.computeOptions(t,n,!0);for(let r of e.points)i.indexOf(r)>=0&&(n.style=d),this.addPoint(t,r,n)}addPoint(t,e,n={}){n=this.computeOptions(t,n,!0),this.folders.get(t).placemarks.push({point:e,...n})}addSegments(t,e,n={}){n=this.computeOptions(t,n);for(let[i,r]of e.segments){const o={name:`${e.name||t}: ${i.name||i.dm}->${r.name||r.dm}`};this.folders.get(t).linestrings.push(this.renderLine([i,r],{...o,...n},!0))}}render(t={}){let e="";h.forEach((n,i)=>{0!==i&&(n={id:h[i].slice(1),href:this.icons[i]},e+=this.iconTemplate({...n,...t}))});for(let[,t]of this.folders)t.enabled&&(e+=this.styleTemplate(t.lineStyle));return this.template({...t,styles:e,folders:this.renderFolders()})}renderFolder(t,e=this.folderTemplate){if(("string"==typeof t||t instanceof String)&&(t=this.folders.get(t)),!t.enabled)return"";let n=[];return n=t.pin===d||void 0===t.pin?t.placemarks.filter(t=>t.style!==h[d]&&void 0!==t.style):t.placemarks.filter(t=>t.style!==h[d]),e({...{name:t.name,content:t.linestrings.concat(n.map(t=>this.pointTemplate(t,t.style))).join("\n")},...t.options})}renderFolders(){let t=[];for(let[,e]of this.folders)t.push(this.renderFolder(e));return t.join("\n")}renderLine(t,e={},n=!1){const i={...e,coordinates:t.map(t=>(t=>`${t.longitude.toFixed(6)},${t.latitude.toFixed(6)}`)(t)).join(" ")};return n?this.segmentTemplate(i):this.lineTemplate(i)}changeFolderColor(t,e,n={}){const i={id:t,color:e};this.folders.get(t).lineStyle=this.styleTemplate({...i,...n})}changeFolderPin(t,e){this.folders.get(t).pin=e}changeFolderState(t,e){this.folders.get(t).enabled=e}reset(){for(let[,t]of this.folders)t.empty()}}n.d(e,"GeoPoint",function(){return c}),n.d(e,"KMLGenerator",function(){return k}),n.d(e,"Route",function(){return m}),n.d(e,"Track",function(){return f}),n.d(e,"rad_to_nm",function(){return s}),n.d(e,"nm_to_rad",function(){return l}),n.d(e,"PIN_BROWN",function(){return 3}),n.d(e,"PIN_BLUE",function(){return 1}),n.d(e,"PIN_PINK",function(){return 5}),n.d(e,"PIN_PURPLE",function(){return 8}),n.d(e,"PIN_YELLOW",function(){return 2}),n.d(e,"PIN_RED",function(){return 6}),n.d(e,"PIN_ORANGE",function(){return 4}),n.d(e,"PIN_GREEN",function(){return 7}),n.d(e,"PIN_NONE",function(){return d}),n.d(e,"NAT_POSITION_ENTRY",function(){return 0}),n.d(e,"NAT_POSITION_EXIT",function(){return 1}),n.d(e,"template",function(){return M}),n.d(e,"styleTemplate",function(){return P}),n.d(e,"iconTemplate",function(){return x}),n.d(e,"avenzaTemplate",function(){return S}),n.d(e,"avenzaStyleTemplate",function(){return _}),n.d(e,"avenzaIconTemplate",function(){return $}),n.d(e,"PINS",function(){return h}),n.d(e,"AVENZAICONS",function(){return u}),n.d(e,"GOOGLEICONS",function(){return p})}])});