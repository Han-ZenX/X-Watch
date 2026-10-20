import audit,re,collections,json
from pathlib import Path
official=Path(r'F:\KiCad\10.0\share\kicad\footprints\Package_CSP.pretty\ST_WLCSP-208_5.38x5.47mm_Layout26x16_P0.35mm_Stagger.kicad_mod').read_text(encoding='utf-8')
local=(audit.PROJECT/'XWatch_Rev3.0.pretty'/f'{audit.PART}.kicad_mod').read_text(encoding='utf-8')
def pads(text):
 return {re.match(r'\(pad "([^"]+)"',b)[1]:b for _,_,b in audit.children(text) if b.startswith('(pad ')}
op,lp=pads(official),pads(local)
print('OFFICIAL PADS',len(op),'set_equal',set(op)==set(lp))
print('OFFICIAL SAMPLE',[(n,re.search(r'\(at ([^)]+)\)',b)[1],re.search(r'\(size ([^)]+)\)',b)[1]) for n,b in list(op.items())[:6]])
for key in ['solder_mask_margin','solder_paste_margin','solder_paste_margin_ratio']:
 print(key,'local',re.findall(r'\('+key+r' ([^)]+)\)',local),'official',re.findall(r'\('+key+r' ([^)]+)\)',official))
errs=[]
for n,b in op.items():
 oa=list(map(float,re.search(r'\(at ([^)]+)\)',b)[1].split()))
 la=list(map(float,re.search(r'\(at ([^)]+)\)',lp[n])[1].split()))
 if any(abs(a-c)>0.001 for a,c in zip(oa,la)): errs.append((n,la,oa))
print('GEOMETRY DIFFERENCES >1um',len(errs),errs[:5])
