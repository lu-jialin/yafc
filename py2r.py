#!/bin/env python3
import sys
import yaml as yamllib
import ctypes

import json as jsonlib

stdf = yamllib.safe_load(sys.stdin.read())

def ID(ID):
	return ctypes.cast(id(stdf), ctypes.py_object).value

def _diag(stdf , key=None , insign={} , diag=[]) :
	if not isinstance(stdf,list) and not isinstance(stdf,dict) :
		insign[str(id(stdf))] = str(stdf)
		diag.append(id(stdf))
	elif isinstance(stdf,list) :
		list(map(lambda k:_diag(k,key=None,insign=insign) , stdf))
	elif isinstance(stdf,dict) :
		def skipbool(k) :
			if k not in {True,False} :
				insign[str(id(stdf[k]))] = str(k)
				diag.append(id(stdf[k]))
				#Note that string will use the same id
			_diag(stdf[k],key=k,insign=insign)
		list(map(skipbool , stdf))
	return insign,diag

insign,diag = _diag(stdf)

print(insign)
print(f'''pdg = diag(c({','.join(map(str,diag))}))''')
