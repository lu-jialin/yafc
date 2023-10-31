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

def popbranch(stdf) :
	if not isinstance(stdf,list) and not isinstance(stdf,dict) :
		return stdf
	elif isinstance(stdf,list) :
		for i,s in enumerate(stdf) :
			stdf[i] = popbranch(s)
		return stdf
	elif isinstance(stdf,dict) :
		k,v = stdf.popitem()
		if isinstance(v,list) : #loop
			for i,s in enumerate(v) :
				v[i] = popbranch(s)
			stdf[k] = (v,)
			return stdf
		elif set(v) | {True,False} == {True,False} :
			stdf[k] = [None,None]
			for b in {True,False} :
				if b in set(v) :
					stdf[k][int(b)] = popbranch(v[b])
				else :
					stdf[k][int(b)] = None
			return stdf
		else :
			raise Exception('Format',f'Undefined format : {stdf}')

stdf = flatio(stdf)
stdf = popbranch(stdf)
stdf = ['__start'] + stdf + ['__end']
#stdf = [id(None)] + stdf + [id(None)]

#print(stdf)
print(jsonlib.dumps(stdf))

#def _diag(stdf , key=None , pre=[], insign={} , diag=[] , io={}) :
#	if not isinstance(stdf,list) and not isinstance(stdf,dict) :
#		insign[id(stdf)] = str(stdf)
#		diag.append(id(stdf))
#	elif isinstance(stdf,list) :
#		list(map(lambda k:_diag(k,key=None,pre=pre,insign=insign,diag=diag,io=io) , stdf))
#	elif isinstance(stdf,dict) :
#		if ico := isio(stdf) :
#			insign[id(stdf)] = str(ico[1])
#			diag.append(id(stdf))
#			io[id(stdf)] = (ico[0],ico[2])
#		else :
#			def skipbool(k) :
#				if k not in {True,False} :
#					insign[id(stdf[k])] = str(k)
#					diag.append(id(stdf[k]))
#					#Note that string will use the same id
#				_diag(stdf[k],pre=pre,key=k,insign=insign,diag=diag,io=io)
#			list(map(skipbool , stdf))
#	return insign,diag,io
#insign,diag,IO = _diag(stdf)
#print(f'''insign<-list()''')
#print(f'''io<-list()''')
#for ID in insign : print(f"""insign[['{ID}']]<-'{insign[ID]}'""")
##FIXME : String in step can not contain "'"
#print(f'''pdg<-diag(c({','.join(map(str,diag))}))''')
#for io in IO : print(f'''io[['{str(io)}']]<-c('{str(IO[io][0])}','{str(IO[io][1])}')''')
