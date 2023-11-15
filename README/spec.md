# ___ specification

YAFC use YAML to describe standard control flow and base IO,
*i.e.* {sequence , branch , loop , IO} .

---

<style>ul{list-style-type:none}</style>
<div style="font-family:CMU Typewriter Text,monospace;">

- :YAFC :: [:sequence]
	- :sequence :: :atom | :branch | :loop
		- :atom :: :trivial | :IO
			- :trivial :: "description of this step"
			- :IO :: "description of output" / :call
				- :call :: "what get input and do output" / :input
					- :input :: "description of input" / :
- :loop :: :atom / :YAFC
- :branch :: :atom / :ifelse
	- :ifelse {:bool} / :YAFC
		- :bool :: true | false

</div>

---
