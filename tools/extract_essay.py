import re, glob, os, json
SP=os.environ['SP']
BOILER=('국가기술자격','기술사 제','분','야 정보통신','수험','번호','성','명','▶수험자','“채점기준','<표>')
HEAD=re.compile(r'(?:6\s*문제|다음\s*문제)\s*중\s*4\s*문제[^\n]*')
FOOT=re.compile(r'^\s*\d\s*[–-]\s*\d\s*$')

def clean(s):
    s=re.sub(r'\s+',' ',s).strip()
    return re.sub(r'\s*\d\s*[–-]\s*\d\s*$','',s).strip()

def parse_block(body):
    """논술형 6문항 + 소문항(가/나/다/라) 추출"""
    items=[]
    for raw in body.split('\n'):
        s=raw.strip()
        if not s or s.startswith(BOILER) or FOOT.match(s): continue
        m=re.match(r'^(\d)\.\s*(.+)$', s)
        sub=re.match(r'^([가-라])\.\s*(.+)$', s)
        if m and 1<=int(m.group(1))<=6 and (not items or int(m.group(1))==items[-1]['no']+1):
            items.append({'no':int(m.group(1)), 'stem':m.group(2), 'subs':[]})
        elif sub and items:
            items[-1]['subs'].append([sub.group(1), sub.group(2)])
        elif items:
            if items[-1]['subs']: items[-1]['subs'][-1][1] += ' '+s
            else: items[-1]['stem'] += ' '+s
    for it in items:
        it['stem']=clean(it['stem'])
        it['subs']=[[k, clean(v)] for k,v in it['subs']]
    return items

res={}; issues=[]
for f in sorted(glob.glob(os.path.join(SP,'txt','*.txt')), key=lambda p:int(os.path.basename(p)[:-4])):
    n=int(os.path.basename(f)[:-4]); t=open(f).read()
    marks=re.findall(r'제\s*([1-4])\s*교시', t)
    labeled = bool(marks)                       # 헤더에 교시 표기가 있는 회차
    starts=[m.end() for m in HEAD.finditer(t)]
    if not starts:
        # 안내문 없는 형식: 1교시 블록 이후를 문항번호 리셋 기준으로 교시 분리
        after = t.split('1 - 1', 1)[1] if '1 - 1' in t else t
        groups=[]; cur=[]
        for raw in after.split('\n'):
            ss=raw.strip()
            if not ss or ss.startswith(BOILER) or FOOT.match(ss): continue
            mm=re.match(r'^(\d)\.\s*(.+)$', ss)
            if mm and int(mm.group(1))==1 and cur:
                groups.append(cur); cur=[ss]
            else:
                cur.append(ss)
        if cur: groups.append(cur)
        blocks=[{'gyosi':i+2,'items':parse_block('\n'.join(g))} for i,g in enumerate(groups[:3])]
        res[n]={'labeled':bool(marks),'blocks':blocks}
        bad=[b['gyosi'] for b in blocks if len(b['items'])!=6]
        if len(blocks)!=3 or bad: issues.append((n,'블록%d개, 6문항아닌교시%s'%(len(blocks),bad)))
        continue
    ends=starts[1:]+[len(t)]
    blocks=[]
    for i,(s,e) in enumerate(zip(starts,ends)):
        # 다음 블록 안내문 앞의 헤더 반복부를 제거하기 위해 그대로 넘기고 파서에서 걸러냄
        items=parse_block(t[s:e])
        blocks.append({'gyosi': i+2, 'items': items})
    res[n]={'labeled':labeled, 'blocks':blocks}
    bad=[b['gyosi'] for b in blocks if len(b['items'])!=6]
    if len(blocks)!=3 or bad: issues.append((n,'블록%d개, 6문항아닌교시%s'%(len(blocks),bad)))
json.dump(res, open(os.path.join(SP,'essay.json'),'w'), ensure_ascii=False, indent=1)
tot=sum(len(b['items']) for v in res.values() for b in v['blocks'])
print('회차 %d개 / 논술형 %d문항' % (len(res), tot))
print('교시 표기 확인된 회차: %d개' % sum(1 for v in res.values() if v['labeled']))
print('점검 필요:', issues if issues else '없음')
