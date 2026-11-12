(function(){var q=new URLSearchParams(location.search),c=q.get('code');
if(c){document.getElementById('c').textContent=c;document.getElementById('ok').hidden=false;
var b=document.getElementById('cp');b.addEventListener('click',function(){navigator.clipboard.writeText(c).then(function(){b.textContent='Code copié'},function(){var r=document.createRange();r.selectNodeContents(document.getElementById('c'));var s=getSelection();s.removeAllRanges();s.addRange(r)})})}
else{document.getElementById('ko').hidden=false}})();
