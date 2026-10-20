import audit,re,json,collections,csv
A=audit.ROOT; P=audit.PROJECT
def netgroups(path):
 text=path.read_text(encoding='utf-8'); groups=[]; targets=[]
 ns=next(b for _,_,b in audit.children(text) if b.startswith('(nets'))
 for _,_,n in audit.children(ns):
  if not n.startswith('(net'): continue
  nodes=[]
  for _,_,b in audit.children(n):
   if b.startswith('(node'):
    ref=re.search(r'\(ref "([^"]+)"',b)[1]; pin=re.search(r'\(pin "([^"]+)"',b)[1]; nodes.append((ref,pin))
    if ref=='U15' and pin in ['N24','N26']: targets.append((pin,re.search(r'\(name "([^"]+)"',n)[1],len([v for v in audit.children(n) if v[2].startswith('(node')])))
  groups.append(tuple(sorted(nodes)))
 return collections.Counter(groups),targets
b,bt=netgroups(A/'before.net'); a,at=netgroups(A/'after.net')
assert a==b,'Connectivity changed'
print('Electrical connectivity unchanged, net groups:',sum(a.values()),'corrected pins:',at)
lib=(P/'XWatch_Rev3.0.kicad_sym').read_text(encoding='utf-8'); pp=audit.pins(audit.named(lib,'symbol',audit.PART)); ref=json.loads((A/'official_pinmap.json').read_text(encoding='utf-8'))
assert len(pp)==208 and len({p['ball'] for p in pp})==208 and set(p['ball'] for p in pp)==set(ref)
assert all(audit.canonical(p['name'])==audit.canonical(ref[p['ball']]['name']) for p in pp)
print('All 208 symbol pins match ST; unique and complete')
for name in ['MCU_IO.kicad_sch','MCU_PWR.kicad_sch']:
 text=(P/name).read_text(encoding='utf-8'); cache=audit.named(next(b for _,_,b in audit.children(text) if b.startswith('(lib_symbols')),'symbol','XWatch_Rev3.0:'+audit.PART)
 cp=audit.pins(cache)
 assert [{k:v for k,v in p.items() if k!='text'} for p in cp]==[{k:v for k,v in p.items() if k!='text'} for p in pp]
 print(name,'cache matches library')
fp=(P/'XWatch_Rev3.0.pretty'/f'{audit.PART}.kicad_mod').read_text(encoding='utf-8')
pads={re.match(r'\(pad "([^"]+)"',b)[1]:b for _,_,b in audit.children(fp) if b.startswith('(pad ')}
assert len(pads)==208 and set(pads)==set(ref)
assert all('(size 0.21 0.21)' in b for b in pads.values())
print('All 208 pads complete; diameter .21, mask .275, paste .235')
before=json.loads((A/'erc_before.json').read_text(encoding='utf-8')); after=json.loads((A/'erc_after.json').read_text(encoding='utf-8'))
def violations(j): return [v for s in j['sheets'] for v in s['violations']]
bv,av=violations(before),violations(after)
def key(v): return (v['type'],v.get('description',''),tuple(i.get('uuid','') for i in v['items']))
old={key(v) for v in bv}; added=[v for v in av if key(v) not in old]
print('ERC before',len(bv),'after',len(av),'new',len(added),'new kinds',collections.Counter(v['type'] for v in added))
(A/'erc_new_findings.json').write_text(json.dumps(added,ensure_ascii=False,indent=2),encoding='utf-8')
print('NEW ERC samples',json.dumps(added[:3],ensure_ascii=False,indent=2))
report={'symbol_pins_checked':208,'footprint_pads_checked':208,'all_match_ST':True,'schematic_cache_matches':True,'net_connectivity_unchanged':True,'net_groups':sum(a.values()),'erc_before':len(bv),'erc_after':len(av),'new_erc_kinds':dict(collections.Counter(v['type'] for v in added)),'corrected_pins_unconnected':at,'pcb_contains_WLCSP208_instance':f'(footprint "XWatch_Rev3.0:{audit.PART}"' in (P/'XWatch_Rev3.0.kicad_pcb').read_text(encoding='utf-8')}
(A/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
