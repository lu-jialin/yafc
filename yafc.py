#!/bin/env python3
import sys
import yaml as yamllib
from functools import reduce

yafc = sys.stdin.read()
yafc = yamllib.safe_load(yafc)

def p(a) : print(a)

def typeof(seq , maybe:str='trivial') :
	if None : pass
	elif not isinstance(seq,dict) and not isinstance(seq,list) :
		return maybe
	elif isinstance(seq,list) :
		return 'loop'
	elif set(seq) == {True} or set(seq) == {False} or set(seq) == {True,False} :
		return 'branch'
	elif isinstance(seq,dict) :
		return typeof(seq[list(seq)[0]] , maybe='io')
	else :
		raise Exception('Format',f'Undefined structure {seq}')

def complete(yafc:list) :
	if yafc is None : return None
	for seq in yafc :
		t = typeof(seq)
		if None : pass
		elif t == 'loop' :
			for cond in seq : complete(seq[cond])
		elif t == 'branch' :
			tocomplete = {False , True}
			for cond in seq :
				tocomplete -= set(seq[cond])
				for b in tocomplete : seq[cond][b] = None
				complete(seq[cond][True])
				complete(seq[cond][False])
	return yafc

def uniform(yafc:list , level=0 , struct:list=[] , ref:dict={} , last:list=[]) :
	level = level + 1
	if yafc is None : return [],{},last
	for seq in yafc :
		t = typeof(seq)
		if t == 'trivial' :
			ID = id(seq)
			for k,v in [(k,v) for k,v in last if ref[k][v] is None] : ref[k][v] = ID
			struct.append(ID)
			ref[ID] = {
				'dot' : {
					'node' : {
						'label' : str(seq) ,
						'shape' : 'box' ,
					} ,
				} ,
				'l' : level ,
			}
		elif t == 'io' :
			o,call = seq.popitem()
			call,i = call.popitem()
			ID = id(call)
			for k,v in [(k,v) for k,v in last if ref[k][v] is None] : ref[k][v] = ID
			struct.append(ID)
			ref[ID] = {
				'dot' : {
					'node' : {
						'label' : str(call)       ,
						'shape' : 'parallelogram' ,
					} ,
				} ,
				'l' : level , 'i' : str(i) , 'o' : str(o) ,
			}
		elif t == 'branch' :
			cond,branch = seq.popitem()
			ID = id(cond)
			for k,v in [(k,v) for k,v in last if ref[k][v] is None] : ref[k][v] = ID
			struct.append(ID)
			ref[ID] = {
				'dot' : {
					'node' : {
						'label' : str(cond) ,
						'shape' : 'diamond' ,
					} ,
				} ,
				'l'   : level ,
				True  : None  ,
				False : None  ,
			}
			for boolean in [True,False] :
				s,r,b = uniform(branch[boolean] , level=level , struct=[] , ref=ref , last=[(ID,boolean)])
				last += b
				if s == [] : last += [(ID,boolean)]
				struct+=(s)
				ref.update(r)
		elif t == 'loop' :
			cond,loop = seq.popitem()
			ID = id(cond)
			for k,v in [(k,v) for k,v in last if ref[k][v] is None] : ref[k][v] = ID
			struct.append(ID)
			ref[ID] = {
				'dot' : {
					'node' : {
						'label' : str(cond) ,
						'shape' : 'diamond' ,
					} ,
				} ,
				'l' : level , True : None , False : None , 'b' : True ,
			}
			s,r,l = uniform(loop , level=level , struct=[] , ref=ref , last=[(ID,True)])
			last += l
			if s == [] : last += [(ID,True)]
			else : struct+=(s)
			ref.update(r)
			#struct+=([])
			ref[ID]['b'] = False
			last += [(ID,False)]
	return struct,ref,last

flat = uniform

yafc = complete(yafc)
yafc,ref,_ = flat(yafc)

level = reduce(max , map(lambda ID : ref[ID]['l'] , yafc))

start = {
	'dot' : {
		'node' : {
			'label'  : ''      ,
			'shape'  : 'point' ,
			'width'  : 0       ,
			'height' : 0       ,
		} ,
	} ,
	'l' : 0 ,
}
end = {
	'dot' : {
		'node' : {
			'label'  : ''      ,
			'shape'  : 'point' ,
			'width'  : 0       ,
			'height' : 0       ,
		} ,
	} ,
	'l' : 0 ,
}

ref[id(start)] = start
ref[id(end)]   = end
yafc = [id(start)] + yafc + [id(end)]
anchor = {
	'label'  : ''      ,
	'shape'  : 'point' ,
	'width'  : 0       ,
	'height' : 0       ,
}

for ID in yafc :
	node = [f'{k}="{ref[ID]["dot"]["node"][k]}"' for k in ref[ID]['dot']['node']]
	p(f'{ID}[{" ".join(node)}]')
	p('{node[label=""shape=point width=0 height=0]')
	p(f'"{ID} i"')
	p(f'"{ID} o"')
	p('}')
	p(f'{{edge[style=invis dir=none]"{ID} i"->"{ID}"->"{ID} o"}}')
def grid(id1 , id2) :
	#pivot = f',{id2}'
	#ref[pivot] = {}
	ref[id1][id2] = {
		'dot' : {
			'node' : {
				'label'  : ''      ,
				'shape'  : 'point' ,
				'width'  : 0       ,
				'height' : 0       ,
			}
		}
	}
	node = [f'{k}="{ref[id1]["dot"]["node"][k]}"' for k in ref[id1]['dot']['node']]
	p(f'{id1}[{" ".join(node)}]')
	node = [f'{k}="{ref[id1][id2]["dot"]["node"][k]}"' for k in ref[id1][id2]['dot']['node']]

	p('{rank=same')
	if True not in ref[id1] and False not in ref[id1] :
		pass
	else :
		p('edge[style=invis dir=none]')
	p(f'{id1}->{id2}')
	p('}')
	p(f'{{rank=same edge[style=invis dir=none]"{id1} i"->"{id2} i"}}')
	p(f'{{rank=same edge[style=invis dir=none]"{id1} o"->"{id2} o"}}')

	return id2

reduce(grid , yafc)
for ID in yafc :
	p('{edge[style=invis dir=none] node[label=""shape=point width=0 height=0]')
	for l in range(1,level) :
		p(f'"{ID} -{l}"->"{ID} -{l+1}"')
	p(f'"{ID} -{level}"->"{ID} i"->{ID}')
	p('}')
for ID in yafc :
	p('{edge[style=invis dir=none] node[label=""shape=point width=0 height=0]')
	for l in range(1,level) :
		p(f'"{ID} {l+1}"->"{ID} {l}"')
	p(f'"{ID}"->"{ID} o"->"{ID} {level}"')
	p('}')

#def trunk(yafc , append=[]) -> list :
#	for i,seq in enumerate(yafc[:-1]) :
#		append.append(seq)
#		pivot = f',{yafc[i+1]}'
#		append.append(pivot)
#	append.append(yafc[-1])
#	return append
#yafc = trunk(yafc)

for i,ID in enumerate(yafc) :
	if 'b' in ref[ID] : pass
		#src = yafc[-1]
		#des = f',{str(ref[ID][ref[ID]["b"]])}'
		#p(f'"{src}"->"{des}"[]')
	if True in ref[ID] :
		src = ID
		des = ref[ID][True]
		level = ref[des]['l']
		p(f'"{src}"->"{src} {level}"[label="T" dir=none]')
		p(f'{{rank=same"{src} {level}"->"{des} {level}"[dir=none]}}')
		p(f'"{des}"->"{des} {level}"[dir=back]')
	if False in ref[ID] :
		src = ID
		des = ref[ID][False]
		level = ref[des]['l']
		p(f'"{src} -{level}"->"{src}"[label="F" dir=none]')
		p(f'{{rank=same"{src} -{level}"->"{des} -{level}"[dir=none]}}')
		p(f'"{des} -{level}"->"{des}"')

#for l in range(level + 1) :
#	for ID in yafc :
#		node = [f'{k}="{anchor[k]}"' for k in io]
#		p(f'"{ID} {l}"[{" ".join([])}]')
#		node = [f'{k}="{anchor[k]}"' for k in io]
#		p(f'"{ID} -{l}"[{" ".join([])}]')

#for l in range(1,level+1) :
#	p('{rank=same edge[style=dotted]')
#	for i in range(len(yafc)-1) :
#		p(f'"{yafc[i]} -{l}"->"{yafc[i+1]} -{l}"')
#	p('}')
#	p('{rank=same edge[style=dotted]')
#	for i in range(len(yafc)-1) :
#		p(f'"{yafc[i]} {l}"->"{yafc[i+1]} {l}"')
#	p('}')

