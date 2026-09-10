import re, glob, os, json
SP=os.environ['SP']
BOILER=('국가기술자격','기술사 제','분','야 정보통신','수험','번호','성','명','▶수험자','“채점기준')
res={}
for f in sorted(glob.glob(os.path.join(SP,'txt','*.txt')), key=lambda p:int(os.path.basename(p)[:-4])):
    n=int(os.path.basename(f)[:-4]); t=open(f).read()
    # 1교시: 13문제 안내문 ~ 첫 '6문제 중 4문제' 안내문 직전까지 (페이지 걸침 허용)
    m=re.search(r'13문제\s*중\s*10문제[^\n]*\n(.*?)(?=6문제\s*중\s*4문제|\Z)', t, re.S)
    body=m.group(1) if m else ''
    qs=[]
    for raw in body.split('\n'):
        s=raw.strip()
        if not s: continue
        if s.startswith(BOILER) or re.match(r'^\d\s*[–-]\s*\d$', s): continue   # 헤더/페이지푸터 제거
        mm=re.match(r'^(\d{1,2})\.\s*(.+)$', s)
        if mm and 1<=int(mm.group(1))<=13 and (not qs or int(mm.group(1))==qs[-1][0]+1):
            qs.append([int(mm.group(1)), mm.group(2)])
        elif qs:
            qs[-1][1]+=' '+s
    qs=[[k, re.sub(r'\s+',' ',v).strip()] for k,v in qs]
    res[n]=qs
    flag='' if len(qs)==13 else '  <-- 확인 필요'
    print('=== %d회 : %d문제 %s' % (n, len(qs), flag))
json.dump(res, open(os.path.join(SP,'gisul1.json'),'w'), ensure_ascii=False, indent=1)
