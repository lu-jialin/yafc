#!/bin/env python3
import sys
import yaml as yamllib

yafc = sys.stdin.read()
yafc = yamllib.safe_load(yafc)

All = {}
Alll = []

def typeof(seq , maybe:str='trivial') :
	if None : pass
	elif not isinstance(seq,dict) and not isinstance(seq,list) :
		return maybe
	elif isinstance(seq,dict) :
		if set(seq) == {True} or set(seq) == {False} or set(seq) == {True,False} :
			return 'branch'
		elif len(seq) == 1 :
			return typeof(seq[list(seq)[0]] , maybe='io')
	elif isinstance(seq,list) :
		return 'loop'
	else :
		raise Exception('Format',f'Undefined structure {seq}')

def complete(yafc:list) :
	for seq in yafc :
		if None : pass
		elif typeof(seq) == 'loop' :
			for cond in seq : complete(seq[cond])
		elif typeof(seq) == 'branch' :
			tocomplete = {False , True}
			for cond in seq :
				complete(seq[cond])
				tocomplete -= set(seq[cond])
				for b in tocomplete : seq[cond][b] = None
	return yafc

def uniform(yafc:list) :
	for i,seq in enumerate(yafc) :
		t = typeof(seq)
		if t == 'trivial' :
			yafc[i] = {'label' : str(seq)}
		elif t == 'io' :
			pass
		elif t == 'branch' :
			pass
		elif t == 'loop' :
			pass
	return yafc

yafc = complete(yafc)
yafc = uniform(yafc)

print(yamllib.dump(yafc))
