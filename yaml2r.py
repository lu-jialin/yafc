#!/bin/env python3
import sys,argparse,textwrap
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
args,Rmatrixnames = parser.parse_known_args()

stdf = yamllib.safe_load(sys.stdin.read())

_pyprint = print
#def print(*__p , end='' if not args.d else '\n') : _pyprint(*__p,end=end)
def print(*__p , end='\n' if not args.d else '\n') : _pyprint(*__p,end=end)
if not args.d :
	def Rdebug(*__p) : pass
	def R(*__p , end=';') : _pyprint(*__p,end=end)
else :
	def Rdebug(*__p , end='\n') : _pyprint(*__p,end=end)
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

if not Rmatrixnames : Rmatrixname = 'pdg'
else : Rmatrixname = Rmatrixnames[0]

R('insign<-c()')
R('pdginput<-c()')
R('pdgoutput<-c()')
#R(f'{Rmatrixname}<-diag({len(diag)})') #include end
R(f'{Rmatrixname}<-matrix(0,{len(diag)},{len(diag)})') #include end
for i,d in enumerate(diag[1:]) :
	if not isinstance(d,tuple) :
		R(f'''insign[{i+1}]<-"{d}"''')
	else :
		R(f'''pdginput[{i+1}]<-"{d[0]}"''')
		R(f'''insign[{i+1}]<-"{d[1]}"''')
		R(f'''pdgoutput[{i+1}]<-"{d[2]}"''')
	#FIXME : string in `diag` cannot contain `"`

def assignjmp(stdf , branch=[] , delay=[] , last=False) :
#`R` <- {Rmatrixname}[] index order will change row-major or column-major
#XXX column-major Now :
	#None zero value in column means the destination
	#None zero value in row means the source
	if stdf is None :
		#print('delay')
		return [branch.pop()],stdf
	elif not isinstance(stdf,list) and not isinstance(stdf,dict) :
		#print('atom')
		if branch :
			c,b = branch.pop()
			R(f'{Rmatrixname}[{stdf},{c}]<-{1 if b else -1}')
			Rdebug(f'{diag[stdf]} <- {diag[c]} : {b}')
		if delay :
			while(delay) :
				c,b = delay.pop()
				R(f'{Rmatrixname}[{stdf},{c}]<-{1 if b else -1}')
				Rdebug(f'{diag[stdf]} <- {diag[c]} : {b}')
		return delay,stdf
	elif isinstance(stdf,list) :
		for i,s in enumerate(stdf) :
			delay,toloop = assignjmp(
				stdf[i] ,
				branch=branch ,
				delay=delay ,
				last=last ,
			)
		return delay,toloop
	elif isinstance(stdf,dict) and len(stdf)==1 :
		cond,stdf = stdf.copy().popitem()
		if branch :
			c,b = branch.pop()
			R(f'{Rmatrixname}[{cond},{c}]<-{1 if b else -1}')
			Rdebug(f'{diag[cond]} <- {diag[c]} : {b}')
		if delay :
			while(delay) :
				c,b = delay.pop()
				R(f'{Rmatrixname}[{cond},{c}]<-{1 if b else -1}')
				Rdebug(f'{diag[cond]} <- {diag[c]} : {b}')
		if None : pass
		elif isinstance(stdf,tuple) and len(stdf)==1 :
			#print('loop')
			delayif,toloop = assignjmp(
				stdf:=stdf[0] ,
				branch=branch+[(cond,True)] ,
				delay=delay ,
				last=last ,
			)
			if delayif :
				while(delayif) :
					c,b = delayif.pop()
					R(f'{Rmatrixname}[{cond},{c}]<-{1 if b else -1}')
					Rdebug(f'{diag[cond]} <- {diag[c]} : {b}')
			if toloop is not None :
				R(f'{Rmatrixname}[{cond},{toloop}]<-1')
				Rdebug(f'{diag[cond]} <- {diag[toloop]}')
			return ([(cond,False)]+delayif),None
			#Only atom node can go back to loop
			#Branch/Loop go back to loop is similar to `goto or empty block or `do-while
			#Structure above is not supported
			#Loop must be back from only 1 Atom or multiple implict branch(with nested).
		elif isinstance(stdf,list) and len(stdf)==2 :
			#To distinguish branch and sequence, don't invoke stdf directly
			#print('branch')
			delayif = []
			for i,s in enumerate(stdf) :
				delaybool,toloop = assignjmp(
					stdf[i] ,
					branch=branch+[(cond,bool(i))] ,
					delay=delay ,
					last=last ,
				)
				delayif += delaybool
			return delayif,toloop
		else :
			raise Exception('Format',f'Undefined format : {stdf}')
	else :
		raise Exception('Format',f'Undefined format : {stdf}')
delay,_ = assignjmp(stdf)
if delay :
	while(delay) :
		c,b = delay.pop()
		R(f'{Rmatrixname}[{len(diag)},{c}]<-{1 if b else -1}')
		Rdebug(f' <- {diag[c]} : {b}')
R(f'{Rmatrixname}[{len(diag)},{len(diag)}]<-1') #Mark the end point by self repeat
R(f'{Rmatrixname}<-rbind(rep(0,ncol({Rmatrixname})),{Rmatrixname})')
R(f'{Rmatrixname}<-cbind(rep(0,nrow({Rmatrixname})),{Rmatrixname})')
