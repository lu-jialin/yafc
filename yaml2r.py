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
if not args.d :
	def R(*__p , end=';') : _pyprint(*__p,end=end)
else :
	def R(*__p) : pass


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

diag = [None]
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
#R(f'pdg=diag({len(diag)})') #include end
R(f'pdg=matrix(0,{len(diag)},{len(diag)})') #include end
for i,d in enumerate(diag[1:]) :
	if not isinstance(d,tuple) :
		R(f'''insign[{i+1}]="{d}"''')
	else :
		R(f'''pdginput[{i+1}]="{d[0]}"''')
		R(f'''insign[{i+1}]="{d[1]}"''')
		R(f'''pdgoutput[{i+1}]="{d[2]}"''')
	#FIXME : string in `diag` cannot contain `"`

def assignjmp(stdf , branch=[] , delay=[]) :
#`R` <- pdg[] index order will change row-major or column-major
#XXX column-major Now :
	#None zero value in column means the destination
	#None zero value in row means the source
	if stdf is None :
		#print('delay')
		return [branch.pop()]
	elif not isinstance(stdf,list) and not isinstance(stdf,dict) :
		#print('atom')
		if branch :
			c,b = branch.pop()
			R(f'pdg[{stdf},{c}]={1 if b else -1}')
			#print(f'{diag[stdf]} <- {diag[c]} : {b}')
		if delay :
			while(delay) :
				c,b = delay.pop()
				R(f'pdg[{stdf},{c}]={1 if b else -1}')
				#print(f'{diag[stdf]} <- {diag[c]} : {b}')
		return delay
	elif isinstance(stdf,list) :
		for i,s in enumerate(stdf) :
			delay = assignjmp(
				stdf[i] ,
				branch=branch ,
				delay=delay
			)
		return delay
	elif isinstance(stdf,dict) and len(stdf)==1 :
		cond,stdf = stdf.copy().popitem()
		if branch :
			c,b = branch.pop()
			R(f'pdg[{cond},{c}]={1 if b else -1}')
			#print(f'{diag[cond]} <- {diag[c]} : {b}')
		if delay :
			while(delay) :
				c,b = delay.pop()
				R(f'pdg[{cond},{c}]={1 if b else -1}')
				#print(f'{diag[cond]} <- {diag[c]} : {b}')
		if None : pass
		elif isinstance(stdf,tuple) and len(stdf)==1 :
			#print('loop')
			delayif = assignjmp(
				stdf:=stdf[0] ,
				branch=branch+[(cond,True)] ,
				delay=delay
			)
			return [(cond,False)] + delayif
		elif isinstance(stdf,list) and len(stdf)==2 :
			#To distinguish branch and sequence, don't invoke stdf directly
			#print('branch')
			delayif = []
			for i,s in enumerate(stdf) :
				delayif += assignjmp(
					stdf[i] ,
					branch=branch+[(cond,bool(i))] ,
					delay=delay
				)
			return delayif
		else :
			raise Exception('Format',f'Undefined format : {stdf}')
	else :
		raise Exception('Format',f'Undefined format : {stdf}')
delay = assignjmp(stdf)
if delay :
	while(delay) :
		c,b = delay.pop()
		R(f'pdg[{len(diag)},{c}]={1 if b else -1}')
		#print(f'{diag[stdf]} <- {diag[c]} : {b}')

#TODO :
def assignloop(stdf , loop=None , index=-1 , length=0) :
	if stdf is None :
		pass
		#TODO : Move delay to the loop
	elif not isinstance(stdf,list) and not isinstance(stdf,dict) :
		#print('atom')
		if loop is not None and (index==length-1) :
			pass
			#print(f'{diag[loop]} <- {diag[stdf]}')
	elif isinstance(stdf,list) :
		for i,s in enumerate(stdf) :
			assignloop(stdf[i] , loop=loop , index=i , length=len(stdf))
	elif isinstance(stdf,dict) and len(stdf)==1 :
		cond,stdf = stdf.copy().popitem()
		if loop is not None and (index==length-1) :
			#print(f'{diag[loop]} <- {diag[cond]}')
			loop = None
		if None : pass
		elif isinstance(stdf,tuple) and len(stdf)==1 :
			#print('loop')
			assignloop(stdf:=stdf[0] , loop=cond , index=index , length=length)
		elif isinstance(stdf,list) and len(stdf)==2 :
			#To distinguish branch and sequence, don't invoke stdf directly
			#print('branch')
			for i,s in enumerate(stdf) :
				assignloop(stdf[i] , loop=loop , index=index , length=length)
		else :
			raise Exception('Format',f'Undefined format : {stdf}')
	else :
		raise Exception('Format',f'Undefined format : {stdf}')
assignloop(stdf)
