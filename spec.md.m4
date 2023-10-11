include(__root__/README/md.m4)dnl
divert(-1)dnl
define(`___',`YAFC')
divert(0)dnl
# ___ specification

___ use YAML to describe standard control flow and base IO,
*i.e.* {sequence , branch , loop , IO} .

---

<style>ul{list-style-type:none}</style>
<div style="font-family:CMU Typewriter Text,monospace;">

- :___ :: [{:sequence}]
	- :sequence :: :atom | :branch | :loop
		- :atom :: :trivial | :IO
			- :trivial :: "description of this step"
			- :IO :: "description of output" / :call
				- :call :: "what get input and do output" / :input
					- :input :: "description of input" / :
- :loop :: :condition / :___
- :branch :: :condition / :ifelse
	- :ifelse :: true / :___ | false / :___ | {:bool} / :___
		- :bool :: true | false

</div>

---
