from pathlib import Path
import audit,re,json,hashlib,zipfile,datetime,csv
P=audit.PROJECT; A=audit.ROOT; PART=audit.PART
ref=json.loads((A/'official_pinmap.json').read_text(encoding='utf-8'))
stocklib=Path(r'F:\KiCad\10.0\share\kicad\symbols\MCU_ST_STM32U5.kicad_sym').read_text(encoding='utf-8')
stock=audit.named(stocklib,'symbol','STM32U5A9BJYxQ')
sp={p['ball']:p for p in audit.pins(stock)}
assert len(ref)==len(sp)==208
assert all(audit.canonical(sp[n]['name'])==audit.canonical(r['name']) for n,r in ref.items())
fpstock=Path(r'F:\KiCad\10.0\share\kicad\footprints\Package_CSP.pretty\ST_WLCSP-208_5.38x5.47mm_Layout26x16_P0.35mm_Stagger.kicad_mod').read_text(encoding='utf-8')
fpref={re.match(r'\(pad "([^"]+)"',b)[1]:b for _,_,b in audit.children(fpstock) if b.startswith('(pad ')}
assert set(fpref)==set(ref)
targets=[P/'XWatch_Rev3.0.kicad_sym',P/'MCU_IO.kicad_sch',P/'MCU_PWR.kicad_sch',P/'XWatch_Rev3.0.pretty'/f'{PART}.kicad_mod']
original={p:p.read_bytes() for p in targets}
backup=A/('before_fix_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.zip')
with zipfile.ZipFile(backup,'w',zipfile.ZIP_DEFLATED) as z:
 for p,b in original.items(): z.writestr(str(p.relative_to(P)),b)
def update_symbol(sym):
 edits=[]
 for us,ue,unit in audit.children(sym):
  if not unit.startswith('(symbol '): continue
  pe=[]
  for ps,pend,pin in audit.children(unit):
   if not pin.startswith('(pin '): continue
   ball=re.search(r'\(number "([^"]+)"',pin)[1]
   new=re.sub(r'^\(pin \w+', '(pin '+sp[ball]['type'],pin,count=1)
   if ball in ['N24','N26']:
    new=re.sub(r'\(name "[^"]+"','(name "'+ref[ball]['name']+'"',new,count=1)
   pe.append((ps,pend,new))
  newunit=unit
  for ps,pend,new in reversed(pe): newunit=newunit[:ps]+new+newunit[pend:]
  edits.append((us,ue,newunit))
 for us,ue,b in reversed(edits): sym=sym[:us]+b+sym[ue:]
 return sym
newfiles={}
for p in targets[:3]:
 text=original[p].decode('utf-8')
 if p.suffix=='.kicad_sym': old=audit.named(text,'symbol',PART)
 else: old=audit.named(next(b for _,_,b in audit.children(text) if b.startswith('(lib_symbols')),'symbol','XWatch_Rev3.0:'+PART)
 new=update_symbol(old)
 before={q['ball']:q for q in audit.pins(old)}; after={q['ball']:q for q in audit.pins(new)}
 assert len(after)==208 and set(after)==set(ref)
 for n,q in after.items():
  assert audit.canonical(q['name'])==audit.canonical(ref[n]['name'])
  assert q['type']==sp[n]['type']
  assert q['at']==before[n]['at'] and q['unit']==before[n]['unit']
 newfiles[p]=text.replace(old,new,1).encode('utf-8')
fp=original[targets[3]].decode('utf-8'); edits=[]
for start,end,b in audit.children(fp):
 if not b.startswith('(pad '): continue
 n=re.match(r'\(pad "([^"]+)"',b)[1]
 expected=fpref[n]
 new=re.sub(r'\(pad "[^"]+" smd \w+',f'(pad "{n}" smd circle',b,count=1)
 for field in ['at','size']:
  term=re.search(r'\('+field+r' [^)]+\)',expected)[0]
  new=re.sub(r'\('+field+r' [^)]+\)',term,new,count=1)
 edits.append((start,end,new))
assert len(edits)==208
for s,e,b in reversed(edits): fp=fp[:s]+b+fp[e:]
fp=fp.replace('\t(attr smd)','\t(solder_mask_margin 0.0325)\n\t(solder_paste_margin 0.0125)\n\t(attr smd)',1)
newfiles[targets[3]]=fp.encode('utf-8')
for p,b in newfiles.items():
 assert p.read_bytes()==original[p],f'{p} changed during audit; refusing to overwrite'
 list(audit.children(b.decode('utf-8')))
for p,b in newfiles.items(): p.write_bytes(b)
oldpins={p['ball']:p for p in audit.pins(audit.named(original[targets[0]].decode('utf-8'),'symbol',PART))}
newpins={p['ball']:p for p in audit.pins(audit.named(newfiles[targets[0]].decode('utf-8'),'symbol',PART))}
oldpads={p['ball']:p for p in json.loads((A/'before_audit.json').read_text(encoding='utf-8'))['pads']}
with (A/'208球位核对明细.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f); w.writerow(['球位','官方引脚名','数据手册页码','修改前名称','修改后名称','修改前类型','修改后类型','封装编号','X毫米','Y毫米','铜焊盘直径毫米','阻焊开口直径毫米','锡膏开口直径毫米','核对结果'])
 for ball in sorted(ref,key=lambda n:('ABCDEFGHJKLMNPRT'.index(n[0]),int(n[1:]))):
  xy=re.search(r'\(at ([^)]+)\)',fpref[ball])[1].split()
  w.writerow([ball,ref[ball]['name'],ref[ball]['page'],oldpins[ball]['name'],newpins[ball]['name'],oldpins[ball]['type'],newpins[ball]['type'],ball,*xy,'0.210','0.275','0.235','通过'])
report={'part':PART,'source':'ST DS13543 Rev 3 May 2025; Table 27, Figure 19, Tables 169 and 170','official_symbol':'MCU_ST_STM32U5:STM32U5A9BJYxQ (installed KiCad 10)','pin_count':208,'pad_count':208,'name_fixes':{'N24':['PH0-OSC_IN','VREF-'],'N26':['PH1-OSC_OUT','VSSA']},'types_changed':sum(oldpins[n]['type']!=newpins[n]['type'] for n in ref),'geometry':'Numbering and top-view orientation correct; coordinates aligned to KiCad official footprint (original deviations below 1um).','pad_diameter':['0.192','0.210'],'mask_diameter':'0.275','paste_diameter':'0.235','backup':str(backup),'files':[{'path':str(p.relative_to(P)),'before_sha256':hashlib.sha256(original[p]).hexdigest(),'after_sha256':hashlib.sha256(newfiles[p]).hexdigest()} for p in targets]}
(A/'fix_summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
