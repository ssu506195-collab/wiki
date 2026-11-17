(function(){
'use strict';
const M=window.ModalMath;
const NS='http://www.w3.org/2000/svg';
function node(s,name,attrs,text){let e=document.createElementNS(NS,name);for(let k in attrs)e.setAttribute(k,attrs[k]);if(text!==undefined)e.textContent=text;s.append(e);return e}
function label(s,x,y,t,anchor='start',color='#63766b'){return node(s,'text',{x,y,'text-anchor':anchor,fill:color,'font-size':15,'font-family':'Microsoft JhengHei,system-ui,sans-serif'},t)}
function line(s,x1,y1,x2,y2,color='#c7d3c0',dash=''){return node(s,'line',{x1,y1,x2,y2,stroke:color,'stroke-width':1.5,'stroke-dasharray':dash})}
function curve(s,points,color='#3b6b55',dash=''){return node(s,'polyline',{points:points.map(p=>p.join(',')).join(' '),fill:'none',stroke:color,'stroke-width':3,'stroke-dasharray':dash,'stroke-linejoin':'round'})}
function point(s,x,y,color='#c1854a'){node(s,'circle',{cx:x,cy:y,r:5,fill:color})}
function clear(s){s.replaceChildren()}
function axes(s,{ymin=-1.2,ymax=1.2,xmax=1,xlabel='x/L',ylabel='相對位移 φ',ticks=4}={}){
 clear(s);const tx=x=>65+535*x/xmax,ty=y=>270-225*(y-ymin)/(ymax-ymin);
 line(s,65,45,65,270);line(s,65,270,600,270);
 for(let i=0;i<=ticks;i++){let x=i*xmax/ticks;line(s,tx(x),45,tx(x),270,'#e1e7d9');label(s,tx(x),294,Number(x.toFixed(2)).toString(),'middle')}
 for(let y of [ymin,(ymin+ymax)/2,ymax]){line(s,65,ty(y),600,ty(y),'#e1e7d9');label(s,54,ty(y)+5,Number(y.toFixed(2)).toString(),'end')}
 label(s,600,323,xlabel,'end');label(s,65,24,ylabel);return{tx,ty}
}
function beam(s,n=1,amp=1,phase=1,mark=false,compare=false){
 const a=axes(s,{ymin:compare?-2.7:-1.2,ymax:compare?2.7:1.2});
 line(s,a.tx(0),a.ty(0),a.tx(1),a.ty(0),'#a1ae9b','5 5');
 if(compare)curve(s,Array.from({length:201},(_,i)=>[a.tx(i/200),a.ty(M.shape(n,i/200))]),'#aebfac','5 5');
 curve(s,Array.from({length:201},(_,i)=>[a.tx(i/200),a.ty(amp*phase*M.shape(n,i/200))]));
 line(s,a.tx(0)-5,a.ty(-.55),a.tx(0)-5,a.ty(.55),'#a4774b');
 if(mark)for(let x of M.nodes(n)){point(s,a.tx(x),a.ty(0));label(s,a.tx(x),a.ty(0)+27,x.toFixed(3),'middle','#9b602b')}
}
document.querySelectorAll('[data-chart]').forEach(fig=>{
 const s=fig.querySelector('svg'),kind=fig.dataset.chart;
 if(kind==='shape')beam(s,Number(fig.dataset.mode));
 if(kind==='rigid'){const a=axes(s);line(s,a.tx(0),a.ty(0),a.tx(1),a.ty(0),'#b4c0ac','5 5');curve(s,[[a.tx(0),a.ty(.6)],[a.tx(1),a.ty(.6)]],'#538eab')}
 if(kind==='cover'){let a=axes(s);[1,2,3].forEach((n,i)=>curve(s,Array.from({length:201},(_,j)=>[a.tx(j/200),a.ty(M.shape(n,j/200))]),['#3b6b55','#538eab','#c1854a'][i]));label(s,595,36,'同方向彎曲 1 / 2 / 3','end')}
});
const labs=[];
document.querySelectorAll('[data-lab]').forEach(root=>{
 const kind=root.dataset.lab,s=root.querySelector('svg'),controls={};root.querySelectorAll('[data-input]').forEach(e=>controls[e.dataset.input]=e);
 let playing=false,raf=0,last=0;
 function value(k){return Number(controls[k].value)}
 function output(k,v){let e=root.querySelector('[data-output="'+k+'"]');if(e)e.textContent=v}
 function render(){
 if(kind==='frequency'){
 const k=value('k'),m=value('mass'),f=M.frequency(k,m),a=axes(s,{xmax:2,xlabel:'時間 t（s）',ylabel:'正規化位移 x/A'});
 curve(s,Array.from({length:501},(_,i)=>{let t=i*2/500;return[a.tx(t),a.ty(Math.cos(2*Math.PI*f*t))]}),'#538eab');
 root.querySelector('[data-readout]').textContent='fn = '+f.toFixed(3)+' Hz　T = '+(1/f).toFixed(3)+' s';output('k',k+' N/m');output('mass',m.toFixed(1)+' kg');
 }else if(kind==='nodes'){
 let n=value('mode'),phase=Math.sin(value('phase')*Math.PI/180);beam(s,n,1,phase,true);
 let ns=M.nodes(n);root.querySelector('[data-readout]').textContent=ns.length+' 個內部位移節點'+(ns.length?'：x/L ≈ '+ns.map(x=>x.toFixed(3)).join('、'):'');output('phase',value('phase')+'°');
 }else if(kind==='scale'){
 beam(s,1,value('scale'),1,false,true);output('scale',value('scale').toFixed(1)+'×');root.querySelector('[data-readout]').textContent='顯示倍率 '+value('scale').toFixed(1)+'×；模型的 fn 不變';
 }else if(kind==='resonance'){
 const z=value('zeta'),r=value('ratio'),a=axes(s,{ymin:0,ymax:11,xmax:2,xlabel:'頻率比 r = fexc / fn',ylabel:'放大因子 D',ticks:4});
 line(s,a.tx(1),45,a.tx(1),270,'#b9a181','5 5');
 curve(s,Array.from({length:501},(_,i)=>{let x=i*2/500;return[a.tx(x),a.ty(M.response(x,z))]}),'#c1854a');
 point(s,a.tx(r),a.ty(M.response(r,z)));
 root.querySelector('[data-readout]').textContent='r = '+r.toFixed(2)+'　D = '+M.response(r,z).toFixed(3);
 output('zeta',z.toFixed(2));output('ratio',r.toFixed(2));
 }
 }
 function stop(){playing=false;cancelAnimationFrame(raf);last=0;const b=root.querySelector('[data-play]');if(b){b.textContent='▶ 播放示意';b.setAttribute('aria-pressed','false')}}
 function tick(now){if(!playing)return;let dt=last?Math.min(now-last,80):0;last=now;controls.phase.value=String((value('phase')+dt*.09)%360);render();raf=requestAnimationFrame(tick)}
 Object.values(controls).forEach(e=>e.addEventListener('input',()=>{stop();render()}));
 root.querySelector('[data-play]')?.addEventListener('click',function(){if(playing)stop();else{playing=true;last=0;this.textContent='Ⅱ 暫停示意';this.setAttribute('aria-pressed','true');raf=requestAnimationFrame(tick)}});
 labs.push({root,stop});render();
});
const deck=document.querySelector('[data-deck]');
if(deck){
 const slides=[...document.querySelectorAll('.slide')],picker=document.querySelector('#slide-picker');let current=0;
 function show(index,hash=true){
 current=Math.max(0,Math.min(slides.length-1,index));
 slides.forEach((s,i)=>{s.classList.toggle('active',i===current);if(i===current)s.removeAttribute('inert');else s.setAttribute('inert','')});
 labs.forEach(l=>l.stop());
 picker.value=slides[current].id;
 document.querySelector('#counter').textContent=(current+1)+' / '+slides.length;
 document.querySelector('#progress-fill').style.width=((current+1)/slides.length*100)+'%';
 document.querySelector('#prev').disabled=current===0;document.querySelector('#next').disabled=current===slides.length-1;
 if(hash)history.replaceState(null,'','#'+slides[current].id);
 window.scrollTo({top:0,behavior:'instant'});
 }
 function fromHash(){let i=slides.findIndex(s=>s.id===location.hash.slice(1));show(i<0?0:i,false)}
 document.body.classList.add('enhanced');
 document.querySelector('#prev').addEventListener('click',()=>show(current-1));
 document.querySelector('#next').addEventListener('click',()=>show(current+1));
 picker.addEventListener('change',()=>show(slides.findIndex(s=>s.id===picker.value)));
 document.querySelector('#print').addEventListener('click',()=>{slides.forEach(s=>s.removeAttribute('inert'));window.print()});
 document.addEventListener('keydown',e=>{if(/INPUT|SELECT|TEXTAREA|BUTTON|SUMMARY/.test(e.target.tagName)||e.altKey||e.ctrlKey||e.metaKey)return;if(e.key==='ArrowRight'||e.key==='PageDown'){e.preventDefault();show(current+1)}if(e.key==='ArrowLeft'||e.key==='PageUp'){e.preventDefault();show(current-1)}if(e.key==='Home'){e.preventDefault();show(0)}if(e.key==='End'){e.preventDefault();show(slides.length-1)}});
 window.addEventListener('hashchange',fromHash);window.addEventListener('afterprint',()=>show(current,false));fromHash();
}
document.addEventListener('visibilitychange',()=>{if(document.hidden)labs.forEach(l=>l.stop())});
window.addEventListener('beforeprint',()=>labs.forEach(l=>l.stop()));
let reduced=matchMedia('(prefers-reduced-motion: reduce)');reduced.addEventListener?.('change',e=>{if(e.matches)labs.forEach(l=>l.stop())});
const search=document.querySelector('#wiki-search');
if(search)search.addEventListener('input',()=>{let terms=search.value.toLowerCase().trim().split(/\s+/).filter(Boolean),n=0;document.querySelectorAll('[data-wiki-search]').forEach(e=>{e.hidden=!terms.every(t=>e.dataset.wikiSearch.toLowerCase().includes(t));if(!e.hidden)n++});document.querySelector('#wiki-status').textContent='顯示 '+n+' / 8 個條目';});
})();