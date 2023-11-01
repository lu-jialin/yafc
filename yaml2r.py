#!/bin/env python3
import sys,argparse
from functools import reduce
import yaml as yamllib
#XXX :
	#Note that pyyaml will load "the same content dicts at different palces in list"
	#in different address.
	#But not for string
import ctypes
def ID(ID): return ctypes.cast(ID, ctypes.py_object).value

import json as jsonlib

parser = argparse.ArgumentParser()
parser.add_argument('-d' , action="store_true" , help='''Output variables but not R. This option should be used with editing source code.''')
args,_ = parser.parse_known_args()

stdf = yamllib.safe_load(sys.stdin.read())

_pyprint = print
#def print(*__p , end='' if not args.d else '\n') : _pyprint(*__p,end=end)
def print(*__p , end='\n' if not args.d else '\n') : _pyprint(*__p,end=end)
def R(*__p , end=';' if not args.d else '\n') : _pyprint(*__p,end=end)


def isio(stdf) -> bool :
	child = stdf
	if isinstance(child,dict) and len(child) == 1 :
		i,child = child.copy().popitem()
		if isinstance(child,dict) and len(child) == 1 :
			c,child = child.copy().popitem()
			if not isinstance(child,dict) and not isinstance(child,list) :
				return (i,c,o:=child)
	return None
def flatio(stdf) :
	if ico := isio(stdf) :
		return ico
	elif not isinstance(stdf,list) and not isinstance(stdf,dict) :
		return stdf
	elif isinstance(stdf,list) :
		for i,s in enumerate(stdf) :
			stdf[i] = flatio(s)
		return stdf
	elif isinstance(stdf,dict) :
		for k in stdf :
			stdf[k] = flatio(stdf[k])
		return stdf
#Now all dict is branch or loop

def stripbool(stdf) :
	if not isinstance(stdf,list) and not isinstance(stdf,dict) :
		return stdf
	elif isinstance(stdf,list) :
		for i,s in enumerate(stdf) :
			stdf[i] = stripbool(s)
		return stdf
	elif isinstance(stdf,dict) :
		k,v = stdf.popitem()
		if isinstance(v,list) : #loop
			for i,s in enumerate(v) :
				v[i] = stripbool(s)
			stdf[k] = (v,)
			return stdf
		elif set(v) | {True,False} == {True,False} :
			stdf[k] = [None,None]
			for b in {True,False} :
				if b in set(v) :
					stdf[k][int(b)] = stripbool(v[b])
				else :
					stdf[k][int(b)] = None
			return stdf
		else :
			raise Exception('Format',f'Undefined format : {stdf}')
#cond:len(list)==1 : loop
#cond:len(list)==2 : branch / 0:False , 1:True
#len(tuple)==3 : io / (input , procedure , output)

diag   = [None]
def numbering(stdf) :
	if stdf is None : return None
	elif not isinstance(stdf,list) and not isinstance(stdf,dict) :
		#print('atom')
		diag.append(stdf)
		return len(diag)-1
	elif isinstance(stdf,list) :
		#for i,s in enumerate(stdf) : numbering(stdf[i])
		return [numbering(s) for s in stdf]
	elif isinstance(stdf,dict) and len(stdf)==1 :
		cond,stdf = stdf.popitem()
		diag.append(cond)
		if None : pass
		elif isinstance(stdf,tuple) and len(stdf)==1 :
			return {len(diag)-1 : (numbering(stdf:=stdf[0]),)}
		elif isinstance(stdf,list) and len(stdf)==2 :
			return {len(diag)-1 : numbering(stdf)}
		else :
			raise Exception('Format',f'Undefined format : {stdf}')
	else :
		raise Exception('Format',f'Undefined format : {stdf}')

stdf = flatio(stdf)
stdf = stripbool(stdf)
stdf = numbering(stdf)

R('insign=c()')
R('pdginput=c()')
R('pdgoutput=c()')
R(f'pdg=diag({len(diag[1:])})')
for i,d in enumerate(diag[1:]) :
	if not isinstance(d,tuple) :
		R(f'''insign[{i+1}]="{d}"''')
	else :
		R(f'''pdginput[{i+1}]="{d[0]}"''')
		R(f'''insign[{i+1}]="{d[1]}"''')
		R(f'''pdgoutput[{i+1}]="{d[2]}"''')
	#FIXME : string in `diag` cannot contain `"`

def jmp(stdf , branch=[] , delay=[]) :
	if stdf is None :
		#print('delay')
		return [branch.pop()]
	elif not isinstance(stdf,list) and not isinstance(stdf,dict) :
		#print('atom')
		if branch :
			cond,b = branch.pop()
			R(f'pdg[{stdf},{cond}]={1 if b else -1}')
			#print(f'{diag[stdf]} <- {diag[cond]} : {b}')
		if delay :
			while(delay) :
				cond,b = delay.pop()
				R(f'pdg[{stdf},{cond}]={1 if b else -1}')
				#print(f'{diag[stdf]} <- {diag[cond]} : {b}')
		return delay
	elif isinstance(stdf,list) :
		for i,s in enumerate(stdf) :
			delay = jmp(stdf[i] , branch=branch , delay=delay)
		return delay
	elif isinstance(stdf,dict) and len(stdf)==1 :
		cond,stdf = stdf.popitem()
		if delay :
			while(delay) :
				d,b = delay.pop()
				R(f'pdg[{cond},{d}]={1 if b else -1}')
				#print(f'{diag[cond]} <- {diag[d]} : {b}')
		if None : pass
		elif isinstance(stdf,tuple) and len(stdf)==1 :
			#print('loop')
			jmp(stdf:=stdf[0] , branch=branch+[(cond,True)] , delay=delay)
			return [(cond,False)]
		elif isinstance(stdf,list) and len(stdf)==2 :
			#To distinguish branch and sequence, don't invoke stdf directly
			#print('branch')
			delayif = []
			for i,s in enumerate(stdf) :
				delayif += jmp(stdf[i] , branch=branch+[(cond,bool(i))] , delay=delay)
			return delayif
		else :
			raise Exception('Format',f'Undefined format : {stdf}')
	else :
		raise Exception('Format',f'Undefined format : {stdf}')
jmp(stdf)

#print(stdf)
#print()
#print(list(enumerate(diag)))
