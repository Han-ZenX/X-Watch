import audit,re,json,collections
lib=__import__('pathlib').Path(r'F:\KiCad\10.0\share\kicad\symbols\MCU_ST_STM32U5.kicad_sym').read_text(encoding='utf-8')
s=audit.named(lib,'symbol','STM32U5A9BJYxQ'); pp=audit.pins(s)
ref=json.loads((audit.ROOT/'official_pinmap.json').read_text(encoding='utf-8'))
print('KiCad official symbol pins',len(pp),len({p['ball'] for p in pp}),'types',collections.Counter(p['type'] for p in pp))
print('DIFFERENCES',[(p['ball'],p['name'],ref.get(p['ball'])) for p in pp if p['ball'] not in ref or audit.canonical(p['name'])!=audit.canonical(ref[p['ball']]['name'])])
print('POWER TYPES',[(p['ball'],p['name'],p['type']) for p in pp if not re.match(r'P[A-K]\d+',p['name'])])
print('FOOTPRINT',re.search(r'\(property "Footprint" "([^"]+)"',s)[1])
(audit.ROOT/'kicad_official_reference.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "audit")\n'+s+'\n)',encoding='utf-8')
print('SCHEMATIC CONNECTIONS OF TARGETS')
net=(audit.ROOT/'before.net').read_text(encoding='utf-8')
for _,_,b in audit.children(net):
 if b.startswith('(nets'):
  for _,_,n in audit.children(b):
   if any(f'(pin "{ball}")' in n and '(ref "U15")' in n for ball in ['N24','N26','M23','M25']): print(n)
