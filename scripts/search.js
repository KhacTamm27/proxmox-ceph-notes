// Bộ tìm kiếm dùng chung: build.py nhúng file này vào docs/index.html, check_search.js chạy nó bằng Node.
// Không phụ thuộc DOM. Dữ liệu từ đồng nghĩa nằm ở data/synonyms.json.
(function(root){
const N=s=>String(s==null?'':s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/đ/g,'d');
const words=s=>N(s).split(/[^a-z0-9]+/).filter(Boolean);
const STOPWORDS=new Set(['bi','la','toi','dang','gap','loi','cua','can','gi','the','nao','lam','sao','cho','voi','mot','nhung','cac','va','tren','duoc','khong','kiem','tra','xem','tim','theo','co','thi','roi','khi','ve','check','checking','is','a','an','for','to','my','it','i','have','got','getting','please','how','of','in','on']);

function createSearch(synGroups){
  const labels=new Map();
  const groups=(synGroups||[]).map(g=>g.map(p=>{const k=words(p).join(' ');if(k&&!labels.has(k))labels.set(k,p);return k}).filter(Boolean));
  const index=new Map();let maxLen=1;
  groups.forEach((g,gi)=>g.forEach(p=>{
    if(!index.has(p))index.set(p,[]);index.get(p).push(gi);
    maxLen=Math.max(maxLen,p.split(' ').length);
  }));
  function term(p){
    const alts=new Set([p]);
    (index.get(p)||[]).forEach(gi=>groups[gi].forEach(a=>alts.add(a)));
    return {raw:p,alts:[...alts]};
  }
  // Tách câu tìm thành các ý; cụm nhiều chữ có trong synonyms.json (ví dụ "khởi động lại") được giữ thành một ý.
  function parse(q){
    const toks=words(q),out=[];
    for(let i=0;i<toks.length;){
      let len=Math.min(maxLen,toks.length-i);
      while(len>=2&&!index.has(toks.slice(i,i+len).join(' ')))len--;
      if(len>=2){out.push(term(toks.slice(i,i+len).join(' ')));i+=len;continue}
      const t=toks[i++];
      if(!STOPWORDS.has(t))out.push(term(t));
    }
    return out;
  }
  // fields: [[văn bản, trọng số], ...], trường quan trọng nhất đặt trước.
  function prepare(fields){
    return fields.map(([text,w])=>({s:' '+words(text).join(' ')+' ',w})).filter(f=>f.s.length>2);
  }
  // Từ 1-2 ký tự (ha, pg, vm, ip) khớp nguyên từ; 3 ký tự khớp đầu từ; dài hơn khớp chuỗi con.
  // Từ đồng nghĩa tự thêm vào (strict) dưới 4 ký tự luôn khớp nguyên từ để tránh kết quả rác ("tat" trong "tất cả").
  function hit(s,alt,strict){
    if(alt.length<=2||strict&&alt.length<=3)return s.includes(' '+alt+' ')||s.includes(' '+alt+'s ');
    if(alt.length===3)return s.includes(' '+alt);
    return s.includes(alt);
  }
  // Trả 0 nếu có ý không khớp; ngược lại cộng điểm theo trường khớp tốt nhất của từng ý.
  function score(doc,terms){
    if(!terms.length)return 0;
    let total=0;
    for(const t of terms){
      let best=0;
      for(const f of doc)for(const a of t.alts){
        if(hit(f.s,a,a!==t.raw)){const v=f.w*(a===t.raw?1:0.8);if(v>best)best=v}
      }
      if(!best)return 0;
      total+=best;
    }
    return total;
  }
  // Triage: đếm số ý khớp nguyên từ (cho phép gõ đảo 2 ký tự liền nhau với từ dài từ 4 ký tự).
  function transposed(a,b){
    if(a.length!==b.length)return false;
    let i=0;while(i<a.length&&a[i]===b[i])i++;
    return i+1<a.length&&a[i]===b[i+1]&&a[i+1]===b[i]&&a.slice(i+2)===b.slice(i+2);
  }
  function triageHits(text,terms){
    const s=' '+words(text).join(' ')+' ',ws=s.trim().split(' ');
    return terms.filter(t=>t.alts.some(a=>s.includes(' '+a+' ')||(a.length>=4&&!a.includes(' ')&&ws.some(w=>transposed(a,w))))).length;
  }
  const label=k=>labels.get(k)||k;
  return {N,words,parse,prepare,score,hit,triageHits,label};
}

// Bài viết Markdown: tách heading ## / ### thành mục lục, anchor theo cách GitHub tạo (để link thẳng tới mục).
function guideOutline(md){
  const toc=[],seen=new Map();
  let fence=false;
  String(md||'').split('\n').forEach(line=>{
    if(/^\s*```/.test(line)){fence=!fence;return}
    const m=!fence&&/^(#{2,3})\s+(.+?)\s*#*\s*$/.exec(line);
    if(!m)return;
    const text=m[2].replace(/\[([^\]]*)\]\([^)]*\)/g,'$1').replace(/[`*]/g,'').trim();
    let anchor=text.toLowerCase().replace(/[^\p{L}\p{N}\s_-]/gu,'').replace(/\s/g,'-');
    const n=seen.get(anchor)||0;seen.set(anchor,n+1);if(n)anchor+='-'+n;
    toc.push({level:m[1].length,text,anchor});
  });
  return toc;
}

// Dựng chỉ mục cho lệnh, case/runbook, script, bài viết và triage; query() trả kết quả đã xếp hạng.
function createIndex(engine,{DATA,CASES,SCRIPTS,TRIAGE,GUIDES=[]}){
  const SIDE={left:'proxmox pve',right:'ceph'};
  const commands=[];
  Object.entries(DATA).forEach(([side,branches])=>branches.forEach(b=>b.subs.forEach(s=>s.items.forEach(it=>{
    commands.push({b,s,it,doc:engine.prepare([[it.c,8],[it.v,5],[it.p,4],[it.k,3],[s.name+' '+b.name,2],[SIDE[side],1]])});
  }))));
  const SCOPE={pve:'proxmox pve',ceph:'ceph'};
  const cases=CASES.map((c,index)=>({c,index,doc:engine.prepare([
    [c.title,8],[c.tags,4],[c.symptoms||c.goal,3],
    [[c.causes,c.prereq,(c.quick_reference||[]).map(x=>x.title+' '+x.text).join(' ')].filter(Boolean).join(' '),1],
    [c.steps.flatMap(st=>st.cmds||[]).join(' '),1],[SCOPE[c.scope]+(c.kind==='runbook'?' runbook':' case'),1]])}));
  const scripts=SCRIPTS.map((s,index)=>({s,index,doc:engine.prepare([
    [s.title,8],[s.tags,4],[s.goal,3],[s.notes+' '+s.usage.map(u=>u.c+' '+u.d).join(' ')+' script',1]])}));
  const guides=GUIDES.map((g,index)=>({g,index,toc:guideOutline(g.md),doc:null}));
  guides.forEach(x=>{x.doc=engine.prepare([[x.g.title,8],[x.g.tags,4],[x.g.summary,3],
    [x.toc.map(t=>t.text).join(' '),2],[(SCOPE[x.g.scope]||'')+' bài viết guide',1],[x.g.md,1]])});
  const rank=(list,terms)=>list.map(x=>({...x,score:engine.score(x.doc,terms)})).filter(x=>x.score>0)
    .sort((a,b)=>b.score-a.score||(a.index||0)-(b.index||0));
  function query(q){
    const terms=engine.parse(q);
    const triage=terms.length<2?[]:TRIAGE.map(item=>({item,score:engine.triageHits(item.title+' '+item.aliases,terms)}))
      .filter(h=>h.score>=2).sort((a,b)=>b.score-a.score);
    return {terms,commands:rank(commands,terms),cases:rank(cases,terms),scripts:rank(scripts,terms),guides:rank(guides,terms),triage};
  }
  return {commands,cases,scripts,guides,query};
}

if(typeof module!=='undefined'&&module.exports)module.exports={createSearch,createIndex,guideOutline,N};
else{root.createSearch=createSearch;root.createIndex=createIndex;root.guideOutline=guideOutline}
})(this);
