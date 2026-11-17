"""Rebuild the AI-curated Wiki, traceable teaching deck and observed workflow records."""
from pathlib import Path
from datetime import datetime, timezone
from html import escape as E
from collections import Counter
import json, hashlib, shutil, sys, re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist'
def load(name): return json.loads((ROOT/'input'/name).read_text(encoding='utf-8'))
sources=load('sources.json'); claims=load('claims.json'); notes=load('notes.json'); slides=load('slides.json')
S={s['id']:s for s in sources}; C={c['id']:c for c in claims}; W={w['id']:w for w in notes}
def stamp(): return datetime.now(timezone.utc).isoformat()
def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def event(stage,status,detail):
    p=ROOT/'records'/'events.jsonl'
    with p.open('a',encoding='utf-8') as f:f.write(json.dumps(dict(time=stamp(),stage=stage,status=status,detail=detail),ensure_ascii=False)+'\n')
def validate_slides(items):
    errors=[]
    for s in items:
        if s.get('type')=='references':continue
        if not s.get('wiki') or not s.get('claims'):
            errors.append(dict(slide=s['id'],category='missing_wiki_claim_mapping',message='教學初稿尚未建立 Wiki／知識句對照'));continue
        for w in s['wiki']:
            if w not in W:errors.append(dict(slide=s['id'],category='unknown_wiki',value=w))
        known=set(c for w in s['wiki'] if w in W for c in W[w]['claims'])
        for c in s['claims']:
            if c not in C or c not in known:errors.append(dict(slide=s['id'],category='uncovered_claim',value=c))
    return errors
def ingest():
    assert len(sources)>=5 and len({s['url'] for s in sources})==len(sources)
    manifest=[]
    for s in sources:
        text='# '+s['title']+'\n\n作者：'+s['author']+'\n版本：'+s['version']+'\n來源：'+s['url']+'\n位置：'+s['locator']+'\n\n## AI 查讀整理\n'+s['note']+'\n\n## 支援範圍\n'+s['scope']+'\n'
        p=ROOT/'sources'/(s['id']+'.md');p.parent.mkdir(exist_ok=True);p.write_text(text,encoding='utf-8')
        manifest.append(dict(source_id=s['id'],url=s['url'],path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(text.encode()).hexdigest(),ingested_at=stamp(),mode='AI-authored source notes after web read; original full text not mirrored',location=s['locator']))
    for c in claims:assert all(s in S for s in c['sources']) and c['scope']
    for w in notes:
        assert all(c in C for c in w['claims']) and all(l in W for l in w['links'])
        text='# '+w['title']+'\n\n'+w['summary']+'\n\n'+''.join('## '+c+'\n'+C[c]['text']+'\n\n適用範圍：'+C[c]['scope']+'\n來源：'+', '.join(C[c]['sources'])+'\n\n' for c in w['claims'])
        text+='## 補充與教學推導\n'+w['extra']+'\n\n相關條目：'+', '.join('[['+l+']]' for l in w['links'])+'\n'
        p=ROOT/'wiki'/(w['id']+'.md');p.parent.mkdir(exist_ok=True);p.write_text(text,encoding='utf-8')
    dump(ROOT/'records'/'ingest-manifest.json',manifest)
    dump(ROOT/'wiki'/'index.json',notes)
    event('ingest','pass',dict(independent_sources=len(sources),wiki_notes=len(notes),claims=len(claims),note='匯入的是查讀後的來源筆記與 AI 整理結果；非原文鏡像。'))
def query(text):
    terms=text.lower().split()
    ranked=[]
    for w in notes:
        hay=' '.join([w['title'],w['summary'],*w['tags'],*[C[c]['text'] for c in w['claims']]]).lower()
        score=sum((3 if t in ' '.join(w['tags']).lower() else 1) for t in terms if t in hay)
        if score:ranked.append(dict(wiki=w['id'],score=score,claims=w['claims'],sources=sorted({s for c in w['claims'] for s in C[c]['sources']})))
    return sorted(ranked,key=lambda x:(-x['score'],x['wiki']))
def retrieve():
    qs=['模態 自由振動 用途','固有頻率 週期 彈簧 質量 剛性','振型 節點 懸臂樑','拘束 近零頻率 剛體','正規化 振幅 顯示倍率','共振 阻尼 激振','特徵值 矩陣 角頻率','Workbench 網格 收斂 結果']
    records=[dict(time=stamp(),query=q,method='tag-weighted keyword retrieval; no vector database or live LLM API',results=query(q)) for q in qs]
    assert all(r['results'] for r in records)
    covered={r['wiki'] for q in records for r in q['results']}
    assert set(W)<=covered
    dump(ROOT/'records'/'queries.json',records)
    event('wiki_retrieval','pass',dict(queries=len(records),covered_notes=len(covered),note='LLM 在本次對話整理；這裡實際執行關鍵詞檢索與來源覆蓋檢查。'))
def shell(title,body,prefix='',deck=False):
    scripts='<script defer src="'+prefix+'assets/math.js"></script><script defer src="'+prefix+'assets/app.js"></script>'
    return '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="模態分析觀念入門：可追溯來源的 LLM Wiki 與互動教學 HTML 簡報。"><title>'+E(title)+'｜Modal Wiki</title><link rel="stylesheet" href="'+prefix+'assets/style.css">'+scripts+'</head><body'+(' data-deck' if deck else '')+'><a class="skip" href="#main">跳到內容</a><header class="top"><a class="brand" href="'+prefix+'index.html">∿ MODAL / LEARNING NOTES</a><nav aria-label="主要導覽"><a href="'+prefix+'index.html">教學簡報</a><a href="'+prefix+'wiki/index.html">LLM Wiki</a><a href="'+prefix+'workflow.html">流程與紀錄</a></nav></header>'+body+'</body></html>'
def save(name,body,title,prefix='',deck=False):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(shell(title,body,prefix,deck),encoding='utf-8')
def source_links(ids,prefix=''):
    return ' '.join('<a href="'+prefix+'sources.html#'+s+'">'+s+'</a>' for s in ids)
def wiki_refs(s):
    return ' '.join('<a href="wiki/'+w+'.html">'+E(W[w]['title'])+'</a>' for w in s['wiki'])
def chart(kind,caption,**attrs):
    attributes=' '.join('data-'+k+'="'+E(str(v),quote=True)+'"' for k,v in attrs.items())
    return '<figure class="chart" data-chart="'+kind+'" '+attributes+'><svg viewBox="0 0 640 330" role="img" aria-label="'+E(caption)+'"></svg><figcaption>'+E(caption)+'</figcaption></figure>'
def slider(key,label,lo,hi,step,val,unit=''):
    return '<label>'+label+'<input type="range" data-input="'+key+'" min="'+str(lo)+'" max="'+str(hi)+'" step="'+str(step)+'" value="'+str(val)+'" aria-label="'+label+'"><output data-output="'+key+'">'+str(val)+' '+unit+'</output></label>'
def visual(s):
    t=s['type']
    if t=='cover':
        return '<div class="two-col"><div><p class="big">振多快？<br>怎麼振？</p><p class="note-text">從一支懸臂樑，讀懂結構振動。</p><p class="fine">15 頁 · 初學者 · 可用方向鍵切換</p></div><div>'+chart('cover','均勻細長懸臂樑的三個彎曲形狀；以自由端位移正規化，不是 ANSYS 結果。')+'</div></div>'
    if t=='contrast':
        return '<div class="flat-pair"><div><p class="big">固有頻率</p><p class="lead">振動的特徵頻率</p><p>以 Hz 表示</p></div><div><p class="big">振型</p><p class="lead">各位置的相對運動</p><p>每個模態有對應形狀</p></div></div><p class="hint">想知道特定外力下「振多大」，還需要響應分析。</p>'
    if t=='frequency':
        return '<div class="two-col"><div><div class="formula">f<sub>n</sub> = (1 / 2π) √(k/m)</div><p class="note-text">k：剛性（N/m）<br>m：質量（kg）<br>f<sub>n</sub>：固有頻率（Hz）</p><p class="hint">模型假設：線性、無阻尼、單自由度。</p></div><div data-lab="frequency">'+chart('frequency','解析位移 x/A 隨時間變化；橫軸 s，縱軸正規化位移。')+'<p class="readout" data-readout></p><div class="controls">'+slider('k','剛性 k',25,400,25,100,'N/m')+slider('mass','質量 m',.5,4,.5,1,'kg')+'</div></div></div>'
    if t=='factors':
        return '<div class="two-col"><div><div class="formula">f<sub>n</sub> ∝ √k / √m</div><p class="hint">真實結構改尺寸，質量與剛性可能同時改變，需回到完整模型。</p></div><div><p class="fine">相對頻率 f / f₀（由公式自行計算）</p><div class="bar-row"><span>基準</span><i style="--w:50%"></i><b>1.0</b></div><div class="bar-row"><span>k × 4</span><i style="--w:100%"></i><b>2.0</b></div><div class="bar-row"><span>m × 4</span><i style="--w:25%"></i><b>0.5</b></div></div></div>'
    if t=='shapes':
        return '<div class="shape-grid">'+''.join('<div><h3>第 '+str(n)+' 個同方向彎曲</h3>'+chart('shape','內部位移節點：'+str(n-1)+' 個；x/L 為長度座標。',mode=n)+'</div>' for n in [1,2,3])+'</div><p class="hint">三維模型也可能有側彎與扭轉；這裡不指定它們在三維結果中的排序。</p>'
    if t=='nodes':
        return '<div data-lab="nodes">'+chart('nodes','Euler–Bernoulli 解析振型；圓點是內部位移節點，虛線是未變形中心線。')+'<p class="readout" data-readout></p><div class="controls"><label>彎曲形狀<select data-input="mode" aria-label="彎曲形狀"><option value="1">第一個同方向彎曲</option><option value="2">第二個同方向彎曲</option><option value="3">第三個同方向彎曲</option></select></label><button data-play aria-pressed="false">▶ 播放示意</button>'+slider('phase','相位',0,360,1,90,'°')+'</div><p class="fine">各振型以共同展示速度慢放。瞬間整條樑通過零位移，不代表每個位置都是節點。</p></div>'
    if t=='supports':
        return '<div class="flat-pair"><div><h3>剛體平移</h3>'+chart('rigid','整條中心線同量位移；幾何不彎曲，位置為概念展示。')+'</div><div><h3>彈性彎曲</h3>'+chart('shape','固定端位移為零，沿樑長出現彎曲。',mode=1)+'</div></div><p class="hint">判讀順序：預期自由還是固定？ → 看振型 → 查支撐、連接與單位。</p>'
    if t=='scale':
        return '<div class="two-col"><div><div class="formula">φ → aφ</div><p class="note-text">同一個振型，改變的是畫面尺度。</p><p class="hint">要算真實受迫位移，需加入外力與阻尼等條件。</p></div><div data-lab="scale">'+chart('scale','虛線為 1 倍基準；實線為選定顯示倍率。相對形狀不變，沒有真實 mm 單位。')+'<div class="controls">'+slider('scale','顯示倍率',.5,2.5,.1,1,'×')+'</div><p class="readout" data-readout></p></div></div>'
    if t=='resonance':
        return '<div class="two-col"><div><div class="formula" style="font-size:25px">D = 1 / √[(1−r²)² + (2ζr)²]</div><p class="note-text">D：位移放大因子<br>ζ：阻尼比</p><p class="hint">有阻尼單自由度、諧波力、穩態響應；D 不是真實 mm，峰值也不一定恰在 r = 1。</p></div><div data-lab="resonance">'+chart('resonance','解析受迫響應：橫軸 r，縱軸 D = X / (F₀/k)。')+'<p class="readout" data-readout></p><div class="controls">'+slider('zeta','阻尼比 ζ',.05,.5,.05,.2)+slider('ratio','頻率比 r',.25,1.75,.05,1)+'</div></div></div>'
    if t=='math':
        return '<div class="formula">(K − ω²M) φ = 0</div><div class="flat-pair"><div><h3>M 與 K</h3><p class="lead">質量矩陣與剛性矩陣</p></div><div><h3>φ 與 ω</h3><p class="lead">振型與固有角頻率</p></div></div><p class="lead">f = ω / (2π)，把 rad/s 換成 Hz。</p><p class="hint">適用於這裡介紹的線性無阻尼自由振動模型。</p>'
    if t=='workbench':
        return '<ol class="step-list"><li>Modal（模態分析）：確定分析問題</li><li>Engineering Data（工程材料資料）：核對密度與彈性</li><li>Mechanical（分析環境）：核對網格、支撐與連接</li><li>Solution（求解與結果）：一起讀頻率和振型</li></ol><p class="hint">這是觀念對照，不是假造的軟體介面，也不是已完成的實機操作紀錄。</p>'
    if t=='mesh':
        return '<div class="two-col"><ol class="step-list"><li>保持幾何、材料、拘束一致</li><li>細化網格，追蹤相同物理振型</li><li>比較頻率變化，記錄研究容許範圍</li></ol><div><div class="formula" style="font-size:25px">Δf = |f<sub>fine</sub> − f<sub>coarse</sub>| / |f<sub>fine</sub>| × 100%</div><p class="hint">階次可能交換；接近零頻率時相對誤差也可能失去判讀價值。沒有所有模型通用的百分比。</p></div></div>'
    if t=='practice':
        pairs=[('看到 0.01 Hz，可以直接判定錯誤嗎？','不能。先確認模型是否本來就自由，再看該模態是整體剛體運動還是變形；若預期固定，再查支撐與連通性。'),('動畫放大 2 倍，固有頻率也變 2 倍嗎？','不會。顯示倍率只改變圖形尺度，不改質量、剛性或拘束。'),('細網格的第三階，能直接和粗網格第三階比較嗎？','先比形狀。模態可能交換排序，應追蹤同一物理振型；複雜簡併情況需要進一步方法。')]
        return ''.join('<details><summary>'+q+'</summary><p>'+a+'</p></details>' for q,a in pairs)
    if t=='takeaways':
        return '<ol class="step-list"><li>模型合理嗎？材料、單位、拘束、連接</li><li>振多快？固有頻率與單位</li><li>怎麼振？相對形狀與節點</li><li>可以相信哪些數值？正規化與網格敏感度</li></ol><p class="hint">模態分析建立動態分析的基礎；真實受迫振幅仍要看外力、阻尼與響應。</p>'
    return '<div class="reference-links">'+''.join('<p><a href="sources.html#'+s['id']+'">'+s['id']+' · '+E(s['title'])+'</a><br><span class="fine">'+E(s['version'])+'</span></p>' for s in sources)+'</div><p><a href="wiki/index.html">瀏覽 Wiki →</a>　<a href="workflow.html">流程與實際紀錄 →</a></p>'
def build():
    assert not validate_slides(slides), 'Final slide mapping incomplete'
    OUT.mkdir(exist_ok=True);shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
    chunks=[]
    for i,s in enumerate(slides):
        tag='h1' if i==0 else 'h2'
        srcs=sorted({sid for c in s['claims'] for sid in C[c]['sources']})
        refs='<div class="source-line">Wiki 依據：'+wiki_refs(s)+'<br>知識句：'+', '.join(s['claims'])+' · 原始來源：'+source_links(srcs)+'</div>' if s['wiki'] else ''
        chunks.append('<section class="slide" id="'+s['id']+'" aria-labelledby="title-'+s['id']+'"><p class="kicker">'+str(i+1).zfill(2)+' / '+E(s['eyebrow'])+'</p><'+tag+' id="title-'+s['id']+'">'+E(s['title'])+'</'+tag+'><p class="lead">'+E(s['text'])+'</p>'+visual(s)+refs+'</section>')
    options=''.join('<option value="'+s['id']+'">'+str(i+1).zfill(2)+' '+E(s['title'])+'</option>' for i,s in enumerate(slides))
    bar='<nav class="deck-bar" aria-label="簡報換頁"><button id="prev" aria-label="上一頁">←</button><span id="counter" aria-live="polite">1 / 15</span><select id="slide-picker" aria-label="選擇投影片">'+options+'</select><button id="next" aria-label="下一頁">→</button><button id="print" aria-label="列印簡報">列印</button></nav><div class="progress" aria-hidden="true"><span id="progress-fill"></span></div>'
    save(Path('index.html'),'<noscript><p>未啟用 JavaScript：以下以連續講義顯示；互動圖表需啟用 JavaScript。</p></noscript><main id="main" class="deck">'+''.join(chunks)+'</main>'+bar,'模態分析觀念入門',deck=True)
    intro='<main id="main" class="wiki-main"><p class="kicker">LLM WIKI / MODAL ANALYSIS</p><h1>模態分析知識 Wiki</h1><p>由本次 ChatGPT 查讀整理的 8 篇來源筆記，編成 8 個互相連結的條目。每條知識句都有來源與適用範圍。</p><p class="hint">這是 AI 整理、可查詢的主題 Wiki，不是維基百科，也不是即時聊天機器人。網頁搜尋採關鍵詞，無需 API。</p><label for="wiki-search">查詢 Wiki</label><input class="search" id="wiki-search" type="search" placeholder="例如：節點、阻尼、顯示倍率"><p id="wiki-status" aria-live="polite">8 個條目</p><div class="wiki-list">'
    intro+=''.join('<article data-wiki-search="'+E(' '.join([w['title'],w['summary'],*w['tags'],*[C[c]['text'] for c in w['claims']]]),quote=True)+'"><a href="'+w['id']+'.html"><span class="tag">'+E(' / '.join(w['tags']))+'</span><h2>'+E(w['title'])+'</h2><p>'+E(w['summary'])+'</p></a></article>' for w in notes)
    save(Path('wiki/index.html'),intro+'</div><p><a href="../sources.html">來源與 ingest 紀錄 →</a></p></main>','LLM Wiki','../')
    for w in notes:
        body='<main id="main" class="wiki-main"><a href="index.html">← Wiki 目錄</a><p class="kicker">'+w['id']+'</p><h1>'+E(w['title'])+'</h1><p class="lead">'+E(w['summary'])+'</p>'
        for cid in w['claims']:
            c=C[cid];body+='<section class="claim" id="'+cid+'"><h2>'+cid+' · 知識句</h2><p>'+E(c['text'])+'</p><p class="fine">適用範圍：'+E(c['scope'])+'</p><p>依據：'+source_links(c['sources'],'../')+'</p></section>'
        body+='<h2>補充與教學推導</h2><p>'+E(w['extra'])+'</p><h2>相關條目</h2><ul>'+''.join('<li><a href="'+wid+'.html">'+E(W[wid]['title'])+'</a></li>' for wid in w['links'])+'</ul>'
        backlinks=[x for x in notes if w['id'] in x['links']]
        body+='<h2>連入此頁的條目</h2><ul>'+''.join('<li><a href="'+x['id']+'.html">'+E(x['title'])+'</a></li>' for x in backlinks)+'</ul><h2>使用此條目的投影片</h2><ul>'+''.join('<li><a href="../index.html#'+s['id']+'">'+E(s['title'])+'</a></li>' for s in slides if w['id'] in s['wiki'])+'</ul></main>'
        save(Path('wiki')/(w['id']+'.html'),body,w['title'],'../')
    manifest=json.loads((ROOT/'records/ingest-manifest.json').read_text(encoding='utf-8'))
    body='<main id="main" class="wiki-main"><h1>資料來源與 ingest</h1><p>8 篇獨立文件已匯入。匯入內容為閱讀後的 AI 來源筆記，非原文全文；保留 URL、章節、支援範圍與筆記 SHA-256。雜湊只用來核對本地筆記，不證明內容正確。</p><p>ANSYS 官方文件可能依存取環境要求登入；基礎理論不以軟體版本限制。</p>'
    for s,m in zip(sources,manifest):
        body+='<article id="'+s['id']+'"><p class="kicker">'+s['id']+'</p><h2>'+E(s['title'])+'</h2><p>'+E(s['author'])+' · '+E(s['version'])+'</p><p><a target="_blank" rel="noopener noreferrer" href="'+E(s['url'],quote=True)+'">閱讀原始文件 ↗</a>　<a href="source-notes/'+s['id']+'.md">本次匯入筆記</a></p><p>查讀位置：'+E(s['locator'])+'</p><p>'+E(s['note'])+'</p><p class="fine">支援：'+E(s['scope'])+'<br>匯入時間：'+m['ingested_at']+'<br>筆記 SHA-256：<code>'+m['sha256']+'</code></p></article>'
    save(Path('sources.html'),body+'<p class="fine">OpenStax 作者：William Moebs、Samuel J. Ling、Jeff Sanny。Access for free at <a href="https://openstax.org/books/university-physics-volume-1/pages/1-introduction">OpenStax University Physics Volume 1</a>。本專案以自撰說明與通用物理公式教學，未複製其圖片。</p></main>','來源與匯入紀錄')
    shutil.copytree(ROOT/'sources',OUT/'source-notes',dirs_exist_ok=True)
    workflow_page()
    (OUT/'.nojekyll').touch()
    (ROOT/'index.html').write_text('<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=dist/index.html"><title>開啟教學簡報</title><a href="dist/index.html">開啟模態分析教學簡報</a></html>',encoding='utf-8')
    event('html_build','pass',dict(slides=len(slides),wiki_pages=len(notes)+1,source_pages=1))
    print('Built 15-slide deck, 8 Wiki articles, Wiki index, sources and workflow.')
def workflow_page():
    first=json.loads((ROOT/'records/outline-check-first.json').read_text(encoding='utf-8')) if (ROOT/'records/outline-check-first.json').exists() else {}
    final=validate_slides(slides)
    flow=[
    ('取得與查讀資料','LLM／本次 ChatGPT','查讀原始來源，記錄版本與支援範圍。'),
    ('ingest 與建立 Wiki','LLM 整理＋Python 匯入','來源筆記 → 知識句 → 互連條目；至少五篇來源。'),
    ('查詢 Wiki','Python 關鍵詞檢索＋LLM 選材','實際執行 8 個教學問題查詢，輸出條目、分數、知識句與來源。'),
    ('引用覆蓋檢查','Python 結構檢查','每頁技術內容須綁定 Wiki ID 與 claim ID；缺漏時回到 Wiki。'),
    ('整理大綱與內容審查','LLM／本次 ChatGPT','把依據改寫成初學者可懂的教學；人工式語義審查不能由連結檢查取代。'),
    ('產生 HTML 與圖表','Python＋瀏覽器 JavaScript','以共用版型產生頁面，解析模型提供互動圖表。'),
    ('測試與修正','程式檢查＋瀏覽器 QA','檢查來源關聯、連結、公式、換頁與版面；有問題回到對應節點。')]
    body='<main id="main" class="wiki-main"><p class="kicker">WORKFLOW / EVIDENCE / REFLECTION</p><h1>從 Wiki 到教學簡報</h1><p>LLM 是本次對話中的 ChatGPT。這不是自動呼叫外部模型的系統；Python 負責可重跑的 ingest、檢索、引用檢查與 HTML 生成。</p><h2>本次 graph</h2><ol class="workflow">'
    body+=''.join('<li><h3>'+a+'</h3><p><strong>'+b+'</strong><br>'+c+'</p></li>' for a,b,c in flow)+'</ol><h2>哪些地方會 loop？</h2><div class="table-wrap"><table><tr><th>檢查結果</th><th>回到哪裡</th><th>原因</th></tr><tr><td>來源不足或版本不合</td><td>取得資料／ingest</td><td>先補知識，再寫投影片</td></tr><tr><td>檢索缺少主張</td><td>查詢 Wiki；必要時補條目</td><td>避免生成無依據內容</td></tr><tr><td>引用或條件漏掉</td><td>引用覆蓋與內容整理</td><td>讓每頁可追溯</td></tr><tr><td>公式或圖形錯誤</td><td>解析模型與資料來源</td><td>先驗算，再畫圖</td></tr><tr><td>換頁、連結、版面有問題</td><td>HTML 與瀏覽器 QA</td><td>修正後重測受影響功能</td></tr></table></div>'
    body+='<h2>一次實際執行</h2><p>第一份大綱只有教學內容，尚未填 Wiki／知識句對照。實際引用檢查發現 '+str(first.get('error_count','待執行'))+' 頁缺對照；補上後重新檢查，最終剩 '+str(len(final))+' 項引用結構錯誤。這是初稿的關聯缺漏，不是同樣數量的物理錯誤。</p>'
    body+='<p><a href="records/outline-check-first.json">第一次檢查</a> · <a href="records/outline-check-final.json">修正後檢查</a> · <a href="records/queries.json">8 次 Wiki 查詢</a> · <a href="records/ingest-manifest.json">ingest 紀錄</a> · <a href="records/validation.json">檔案檢查</a> · <a href="records/browser-review.json">瀏覽器檢查</a> · <a href="records/events.jsonl">實際事件紀錄</a></p>'
    body+='<h2>反思</h2><p><strong>本次最集中的缺漏：</strong>大綱整理後的引用關聯。第一份大綱沒有把技術內容逐頁連回 Wiki。這一次的紀錄不能推論長期錯誤率，也不能證明沒有語義錯誤。</p><p><strong>把檢查往前移：</strong>原本若只在 HTML 完成後才看引用，會連版面一起返工；現在先檢查大綱的 Wiki／claim 覆蓋，再允許渲染。</p><p><strong>workflow 調整：</strong>在「查詢 Wiki」與「產生 HTML」之間加入必要的引用 gate，並保留獨立的語義與數學審查。程式只能驗證 ID 與覆蓋，不能自動判斷來源是否真的支持敘述。</p><p><strong>實際限制：</strong>未執行 ANSYS；沒有外部 LLM API 重跑紀錄。重新執行腳本會重建本次整理內容，不會重新閱讀網路或自動生成新知識。</p>'
    mapping='<h2>Wiki 與投影片對照</h2><div class="table-wrap"><table><tr><th>投影片</th><th>Wiki 條目</th><th>知識句</th><th>來源</th></tr>'
    for s in slides:
        mapping+='<tr><td><a href="index.html#'+s['id']+'">'+E(s['title'])+'</a></td><td>'+wiki_refs(s)+'</td><td>'+', '.join(s['claims'])+'</td><td>'+source_links(sorted({sid for c in s['claims'] for sid in C[c]['sources']}))+'</td></tr>'
    body+=mapping+'</table></div></main>'
    save(Path('workflow.html'),body,'流程與實際紀錄')
    dest=OUT/'records';dest.mkdir(exist_ok=True)
    for f in (ROOT/'records').glob('*'):
        if f.is_file():shutil.copy2(f,dest/f.name)
def run():
    cmd=sys.argv[1] if len(sys.argv)>1 else 'build'
    if cmd=='query':
        print(json.dumps(query(' '.join(sys.argv[2:])),ensure_ascii=False,indent=2));return
    if cmd=='first-check':
        errors=validate_slides(load('outline-first-pass.json'))
        dump(ROOT/'records/outline-check-first.json',dict(time=stamp(),input='input/outline-first-pass.json',error_count=len(errors),errors=errors,status='needs_mapping',purpose='實際檢查初稿，未刻意加入錯誤物理敘述'))
        event('outline_citation_check','needs_revision',dict(errors=len(errors),category='missing_wiki_claim_mapping'))
        print('Initial outline mapping gaps:',len(errors));return
    if cmd=='ingest':ingest();retrieve();return
    if cmd=='build':
        assert (ROOT/'records/ingest-manifest.json').exists(),'Run ingest before build'
        errors=validate_slides(slides);dump(ROOT/'records/outline-check-final.json',dict(time=stamp(),error_count=len(errors),errors=errors,status='pass' if not errors else 'fail'))
        event('outline_citation_check','pass' if not errors else 'fail',dict(errors=len(errors)))
        build()
if __name__=='__main__':run()
