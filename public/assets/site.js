(function(){
  var fa=document.documentElement.lang==='fa';

  document.querySelectorAll('.copy').forEach(function(b){
    b.addEventListener('click',function(){
      var el=document.getElementById(b.dataset.copy), t=el.textContent.trim(), label=b.textContent;
      var done=function(){b.textContent=fa?'کپی شد':'Copied';setTimeout(function(){b.textContent=label},1400)};
      var sel=function(){var r=document.createRange();r.selectNodeContents(el);var s=getSelection();s.removeAllRanges();s.addRange(r)};
      if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t).then(done,sel)}else sel();
    });
  });

  /* Home hero: depth contours around islands, with a market graph drifting over them */
  var c=document.getElementById('chart'); if(!c) return;
  var ctx=c.getContext('2d'), reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  var W,H,nodes=[],col={};
  function readColors(){var s=getComputedStyle(document.documentElement);['sea','soil','contour'].forEach(function(k){col[k]=s.getPropertyValue('--'+k).trim()})}
  function rand(a,b){return a+Math.random()*(b-a)}
  function resize(){
    var dpr=Math.min(devicePixelRatio||1,2); W=c.clientWidth; H=c.clientHeight;
    c.width=W*dpr; c.height=H*dpr; ctx.setTransform(dpr,0,0,dpr,0,0);
    var n=Math.round(Math.min(46,Math.max(18,W*H/26000)));
    nodes=[]; for(var i=0;i<n;i++) nodes.push({x:rand(0,W),y:rand(0,H),vx:rand(-.18,.18),vy:rand(-.12,.12),r:rand(1.6,3.2),hot:Math.random()<.12});
  }
  var islands=[{x:.18,y:.78,R:.15,p:1.3},{x:.86,y:.22,R:.11,p:4.1},{x:.62,y:.92,R:.09,p:2.2}];
  function contours(){
    ctx.lineWidth=1; ctx.strokeStyle=col.contour; var S=Math.max(W,H);
    islands.forEach(function(is){
      for(var k=1;k<=7;k++){
        ctx.beginPath();
        for(var a=0;a<=Math.PI*2+0.01;a+=0.05){
          var r=is.R*S*(.35+k*.32)*(1+.13*Math.sin(3*a+is.p+k*.3)+.07*Math.sin(5*a-is.p)+.04*Math.sin(9*a+k));
          var x=is.x*W+Math.cos(a)*r, y=is.y*H+Math.sin(a)*r*.82;
          a===0?ctx.moveTo(x,y):ctx.lineTo(x,y);
        }
        ctx.stroke();
      }
    });
  }
  function frame(){
    ctx.clearRect(0,0,W,H); contours();
    var D=Math.min(170,W/5);
    for(var i=0;i<nodes.length;i++){var a=nodes[i];
      for(var j=i+1;j<nodes.length;j++){var b=nodes[j],dx=a.x-b.x,dy=a.y-b.y,d=Math.sqrt(dx*dx+dy*dy);
        if(d<D){ctx.globalAlpha=(1-d/D)*((a.hot||b.hot)?.55:.28);ctx.strokeStyle=(a.hot&&b.hot)?col.soil:col.sea;ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();}}}
    nodes.forEach(function(n){ctx.fillStyle=n.hot?col.soil:col.sea;ctx.globalAlpha=n.hot?.9:.55;ctx.beginPath();ctx.arc(n.x,n.y,n.hot?n.r+1.2:n.r,0,Math.PI*2);ctx.fill();
      if(!reduce){n.x+=n.vx;n.y+=n.vy;if(n.x<-10)n.x=W+10;if(n.x>W+10)n.x=-10;if(n.y<-10)n.y=H+10;if(n.y>H+10)n.y=-10;}});
    ctx.globalAlpha=1;
    if(!reduce&&!document.hidden) requestAnimationFrame(frame);
  }
  readColors(); resize(); frame();
  addEventListener('resize',function(){resize();if(reduce)frame()});
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change',function(){readColors();if(reduce)frame()});
  new MutationObserver(function(){readColors();if(reduce)frame()}).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});
  document.addEventListener('visibilitychange',function(){if(!document.hidden&&!reduce)requestAnimationFrame(frame)});
})();
