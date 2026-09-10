import re, glob, os, json
SP=os.environ['SP']
BOILER=('국가기술자격','기술사 제','분','야 정보통신','수험','번호','성','명','▶수험자','“채점기준','※','<표>')
HEAD=re.compile(r'(?:13\s*문제\s*중\s*10\s*문제|다음\s*문제\s*중\s*10\s*문제)[^\n]*\n(.*?)(?=(?:6\s*문제|다음\s*문제)\s*중\s*4\s*문제|\Z)', re.S)

def collect(body):
    qs=[]
    for raw in body.split('\n'):
        s=raw.strip()
        if not s or s.startswith(BOILER) or re.match(r'^\d\s*[–-]\s*\d$', s): continue
        mm=re.match(r'^(\d{1,2})\.\s*(.+)$', s)
        if mm and 1<=int(mm.group(1))<=13 and (not qs or int(mm.group(1))==qs[-1][0]+1):
            qs.append([int(mm.group(1)), mm.group(2)])
        elif qs:
            qs[-1][1]+=' '+s
        if len(qs)==13 and qs[-1][0]==13 and s.startswith('13.'): pass
    return [[k, re.sub(r'\s*※\s*총.*$','', re.sub(r'\s+',' ',v)).strip()] for k,v in qs]

res={}; issues=[]
for f in sorted(glob.glob(os.path.join(SP,'txt','*.txt')), key=lambda p:int(os.path.basename(p)[:-4])):
    n=int(os.path.basename(f)[:-4]); t=open(f).read()
    m=HEAD.search(t)
    body = m.group(1) if m else t.split('1 - 1')[0]   # 116회 등 안내문 없는 형식: 첫 페이지까지
    qs=collect(body)
    res[n]=qs
    if len(qs)!=13: issues.append((n, '%d문제'%len(qs)))
json.dump(res, open(os.path.join(SP,'all1.json'),'w'), ensure_ascii=False, indent=1)
print('회차 %d개 / 총 %d문항' % (len(res), sum(len(v) for v in res.values())))
print('점검 필요:', issues if issues else '없음')
print('\n[116회 검증]')
for k,v in res[116]: print(' %2d. %s' % (k,v))
