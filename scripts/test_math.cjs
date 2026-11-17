const assert=require('node:assert/strict'),M=require('../assets/math.js');
function near(a,b,t=1e-8){assert.ok(Math.abs(a-b)<t,String(a)+' != '+b)}
near(M.frequency(100,1),1.5915494309189535);near(M.frequency(400,1),2*M.frequency(100,1));near(M.frequency(100,4),M.frequency(100,1)/2);
for(let n=1;n<=3;n++){let b=M.roots[n-1];near(Math.cosh(b)*Math.cos(b)+1,0,1e-7);near(M.shape(n,0),0);near(M.shape(n,1),1);assert.equal(M.nodes(n).length,n-1);near((M.shape(n,.00001)-M.shape(n,0))/.00001,0,0.001);for(let x of M.nodes(n))near(M.shape(n,x),0,1e-9)}
near(M.nodes(2)[0],.78344455,1e-6);near(M.nodes(3)[0],.50354787,1e-6);near(M.nodes(3)[1],.86767759,1e-6);
near(M.response(0,.2),1);near(M.response(1,.2),2.5);assert.ok(M.response(1,.05)>M.response(1,.5));
console.log('PASS: Hz conversion and mass/stiffness scaling; 3 beam roots and 0/1/2 internal nodes; normalized end and clamped slope; damped steady-state response.');
