#!/bin/env python3
import sys
import yaml as yamllib

yafc = sys.stdin.read()
yafc = yamllib.safe_load(yafc)

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

#def showtype(yafc:list) :
#	for seq in yafc :
#		t = typeof(seq)
#		if t == 'branch' :
#			print(t)
#			for cond in seq :
#				if True in seq[cond] : showtype(seq[cond][True])
#				if False in seq[cond] : showtype(seq[cond][False])
#		elif t == 'loop' :
#			print(t)
#			for cond in seq : showtype(seq[cond])
#		else : print(t)
#showtype(yafc)
#exit(0)

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

def uniform(yafc:list , struct:list=[] , ref:dict={}) :
	if yafc is None : return [],{}
	for seq in yafc :
		t = typeof(seq)
		if t == 'trivial' :
			struct.append(id(seq))
			ref[id(seq)] = {'label' : str(seq)}
		elif t == 'io' :
			o,call = seq.popitem()
			i,call = call.popitem()
			struct.append(id(call))
			ref[id(call)] = {
				'label' : str(call) ,
				'i'     : str(i)    ,
				'o'     : str(o)    ,
			}
		elif t == 'branch' :
			cond,branch = seq.popitem()
			struct.append(id(cond))
			ref[id(cond)] = {'label' : str(cond)}
			s,r = uniform(branch[True])
			struct.append(s)
			ref.update(r)
			ref[id(cond)][True] = s[0] if len(s) > 0 else None
			s,r = uniform(branch[False])
			struct.append(s)
			ref.update(r)
			ref[id(cond)][False] = s[0] if len(s) > 0 else None
		elif t == 'loop' :
			cond,loop = seq.popitem()
			struct.append(id(cond))
			ref[id(cond)] = {'label' : str(cond)}
			s,r = uniform(loop)
			struct.append(s)
			ref.update(r)
			ref[id(cond)][True] = s[0] if len(s) > 0 else None
			struct.append([])
			ref[id(cond)]['b'] = True
	return struct,ref

yafc = complete(yafc)
yafc,ref = uniform(yafc)

print(yamllib.dump(ref))
