import audit,re,collections,json
P=audit.PROJECT
text=(P/'XWatch_Rev3.0.kicad_sym').read_text(encoding='utf-8')
sym=audit.named(text,'symbol',audit.PART)
pp=audit.pins(sym)
print('Types',collections.Counter(p['type'] for p in pp))
print('POWER',[(p['ball'],p['name'],p['at'],p['unit']) for p in pp if not re.match(r'P[A-K][0-9]',p['name'])])
for schname in ['MCU_IO.kicad_sch','MCU_PWR.kicad_sch']:
 sch=(P/schname).read_text(encoding='utf-8')
 cache=audit.named(next(b for _,_,b in audit.children(sch) if b.startswith('(lib_symbols')),'symbol','XWatch_Rev3.0:'+audit.PART)
 cp=audit.pins(cache)
 print('CACHE DIFFERENCES',schname,[(p['ball'],p['name'],p['type'],p['at']) for p in cp if {k:v for k,v in p.items() if k!='text'} not in [{k:v for k,v in q.items() if k!='text'} for q in pp]])
 for _,_,b in audit.children(sch):
  if b.startswith('(symbol') and f'(lib_id "XWatch_Rev3.0:{audit.PART}")' in b: print('INSTANCE',schname,b[:450])
 points={(106.68,110.49),(106.68,115.57),(106.68,107.95),(106.68,113.03)}
 for _,_,b in audit.children(sch):
  if b.startswith(('(wire','(label','(junction','(no_connect','(hierarchical_label')):
   xy=[tuple(map(float,m)) for m in re.findall(r'\((?:xy|at) ([-.\d]+) ([-.\d]+)',b)]
   if any(v in points for v in xy): print('NEAR',b)
pcb=(P/'XWatch_Rev3.0.kicad_pcb').read_text(encoding='utf-8')
for _,_,b in audit.children(pcb):
 if b.startswith('(footprint') and 'STM32U5' in b[:150]: print('PCB MCU',b[:450])
fp=(P/'XWatch_Rev3.0.pretty'/f'{audit.PART}.kicad_mod').read_text(encoding='utf-8')
print('FOOTPRINT PADS EXAMPLE')
for _,_,b in audit.children(fp):
 if b.startswith(('(pad "A2"','(pad "B1"','(pad "T25"')): print(b)
