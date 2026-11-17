(function(g){
const roots=[1.875104068711961,4.694091132974174,7.854757438237612];
function raw(n,x){let b=roots[n-1],s=(Math.cosh(b)+Math.cos(b))/(Math.sinh(b)+Math.sin(b));return Math.cosh(b*x)-Math.cos(b*x)-s*(Math.sinh(b*x)-Math.sin(b*x))}
function shape(n,x){return raw(n,x)/raw(n,1)}
function nodes(n){let r=[],a=.00001,fa=shape(n,a);for(let i=1;i<=2000;i++){let b=i/2000,fb=shape(n,b);if(fa*fb<0){let lo=a,hi=b;for(let j=0;j<40;j++){let m=(lo+hi)/2;if(shape(n,lo)*shape(n,m)<=0)hi=m;else lo=m}r.push((lo+hi)/2)}a=b;fa=fb}return r}
const api={roots,shape,nodes,frequency:(k,m)=>Math.sqrt(k/m)/(2*Math.PI),response:(r,z)=>1/Math.sqrt((1-r*r)**2+(2*z*r)**2)};
g.ModalMath=api;if(typeof module!=='undefined')module.exports=api;
})(typeof globalThis!=='undefined'?globalThis:this);