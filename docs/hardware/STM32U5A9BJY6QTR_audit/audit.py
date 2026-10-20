from pathlib import Path
import re,json,collections,csv
import pdfplumber
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[2]/'hardware/schematic/v1.0/XWatch_Rev3.0'
PART='STM32U5A9BJY6QTR'
def children(text):
 depth=0; quoted=False; escape=False; start=0
 for i,c in enumerate(text):
  if quoted:
   if escape: escape=False
   elif c=='\\': escape=True
   elif c=='"': quoted=False
  elif c=='"': quoted=True
  elif c=='(':
   if depth==1: start=i
   depth+=1
  elif c==')':
   depth-=1
   if depth==1: yield start,i+1,text[start:i+1]
 assert depth==0 and not quoted
def named(text,kind,name):
 return next(b for _,_,b in children(text) if b.startswith(f'({kind} "{name}"'))
def pins(symbol):
 result=[]
 for _,_,unit in children(symbol):
  if not unit.startswith('(symbol '): continue
  un=re.match(r'\(symbol "([^"]+)"',unit)[1]
  for start,end,pin in children(unit):
   if not pin.startswith('(pin '): continue
   result.append({'ball':re.search(r'\(number "([^"]+)"',pin)[1], 'name':re.search(r'\(name "([^"]+)"',pin)[1], 'type':re.match(r'\(pin (\w+)',pin)[1], 'at':re.search(r'\(at ([^)]+)\)',pin)[1], 'unit':un,'text':pin})
 return result
def canonical(name):
 name=re.sub(r'\s+','',name)
 name=re.sub(r'\(.*?\)','',name)
 name=re.sub(r'\[.*?\]','',name)
 if re.match(r'P[A-K]\d+[-/]',name): return re.match(r'P[A-K]\d+',name)[0]
 return name.replace('_','').replace('-','').replace('+','PLUS')
def official():
 result={}
 with pdfplumber.open(ROOT/'datasheet_lcsc.pdf') as pdf:
  for i in range(113,160):
   for table in pdf.pages[i].extract_tables():
    if not table or len(table[0])!=20: continue
    for row in table:
     ballcell=row[7] or ''; name=row[14] or ''
     if 'Pin name' in name or not name: continue
     balls=re.findall(r'\b[A-HJ-NPRT]\d{1,2}\b',ballcell)
     for ball in balls:
      entry={'name':re.sub(r'\s+','',name),'type':row[15],'page':i+1}
      assert ball not in result or result[ball]['name']==entry['name'],(ball,result.get(ball),entry)
      result[ball]=entry
 (ROOT/'official_pinmap.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 return result
def main():
 ref=official(); print('OFFICIAL',len(ref));
 lib=(PROJECT/'XWatch_Rev3.0.kicad_sym').read_text(encoding='utf-8')
 sym=named(lib,'symbol',PART); pp=pins(sym)
 print('LIBRARY PINS',len(pp),'UNIQUE',len({p['ball'] for p in pp}))
 errors=[{k:v for k,v in p.items() if k!='text'}|{'expected':ref.get(p['ball'])} for p in pp if p['ball'] not in ref or canonical(p['name'])!=canonical(ref[p['ball']]['name'])]
 print('DIFFERENCES',json.dumps(errors,ensure_ascii=False,indent=2))
 print('MISSING',sorted(set(ref)-{p['ball'] for p in pp}))
 for sch in PROJECT.glob('*.kicad_sch'):
  text=sch.read_text(encoding='utf-8'); instances=[]
  for _,_,b in children(text):
   if b.startswith('(symbol') and f'(lib_id "XWatch_Rev3.0:{PART}")' in b:
    instances.append({'reference':re.search(r'\(property "Reference" "([^"]+)"',b)[1],'unit':re.search(r'\(unit (\d+)\)',b)[1],'at':re.search(r'\(at ([^)]+)\)',b)[1]})
  if f'(symbol "XWatch_Rev3.0:{PART}"' in text:
   cache=named(named(text,'lib_symbols','') if False else next(b for _,_,b in children(text) if b.startswith('(lib_symbols')),'symbol','XWatch_Rev3.0:'+PART)
   print('CACHE',sch.name,'equal_library',cache.replace('XWatch_Rev3.0:','',1)==sym,'instances',instances)
 fp=(PROJECT/'XWatch_Rev3.0.pretty'/f'{PART}.kicad_mod').read_text(encoding='utf-8')
 pads=[]
 for _,_,b in children(fp):
  if b.startswith('(pad '):
   pads.append({'ball':re.match(r'\(pad "([^"]+)"',b)[1],'at':re.search(r'\(at ([^)]+)\)',b)[1],'size':re.search(r'\(size ([^)]+)\)',b)[1]})
 print('PADS',len(pads),'UNIQUE',len({p['ball'] for p in pads}),'MISSING',sorted(set(ref)-{p['ball'] for p in pads}),'EXTRA',sorted({p['ball'] for p in pads}-set(ref)))
 print('PAD SAMPLE',pads[:8],pads[-5:])
 (ROOT/'before_audit.json').write_text(json.dumps({'official':ref,'pins':[{k:v for k,v in p.items() if k!='text'} for p in pp],'differences':errors,'pads':pads},ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__': main()
