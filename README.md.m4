include(__root__/README/md.m4)
# yafc

Y*aml* A*s* F*low* C*hart*

Generate a flowchart from a YAML file.

## Usage

### Flow char YAML specification

- A flow chart is supposed to be a **list**
	- Every node is the list element
	- The flow order is the list order

#### Atom, IO, branch, and loop

- Atom nodes
	- A atom node is supposed to be a element of the list with yaml atomic type

		> In most cases it should be a string to describe what this step do.
		> Other atomic will be convert to string still.

- IO nodes
	- A IO node is supposed to be a element of the list with yaml associative array type
		- The top level must contain only a key, the key describe *what to output*
			- *what to ouput* contains another associative array.
				Its key describe *what to do*.
				And its value is supposed to be yaml atomic type,
				describing *what to input*

	> *i.e.* _mc_ what to output : {what to call : what to input}_mc_

- Branch nodes
	- A branch node is supposed to be a element of the list with yaml associative array type
	- The top level must contain only a key, the key describe the branch *condition*
		- Another associative array will be under the *condition*.
			Only yaml/_mc_ true _mc_ or yaml/_mc_ false _mc_ and at least 1 of them
			can be in its keys.
			- yaml/_mc_ true _mc_ or yaml/_mc_ false _mc_ contains its sub flow list

	> *i.e.* _mc_`{ condition : {{true:[...]} , {false:[...]}} }'_mc_

- Loop nodes
	- A branch node is supposed to be a element of the list with yaml associative array type
	- The top level must contain only a key, the key describe the branch *condition*
		- _mc_ condition _mc_ contains its sub flow list

	> *i.e.* _mc_`{ condition : [...] }'_mc_

#### Limit

- Delay condition loop *aka* _mc_ do-while _mc_ is not allowed
- Empy branch or loop is not allowed

	> Note that **yafc** cannot distinguish infinite loop,
	> any loop contain any step(but at least 1).
	> Of cause we can write 'doing nothing' in node or 'TRUE'/'infinite' in condition.

### Invoke

_mc_
./yaml2py < .yaml | R -s --no-save > .rds && ./r2dot.r .rds
_mc_
where _mc_ .yaml _mc_ is the flow chart yaml file and
_mc_ .rds _mc_ could be any filename,
just note that the file _mc_ .rds _mc_ will be covered
if existing.
will generate a dot file _mc_ .dot _mc_,
use [graphviz](https://graphviz.org/)
to convert it to pdf/svg/png/*etc*.

__flink__(sample.ninja) show a example from __flink__(stdf.yaml)

Or use [R](https://r-project.org/)
to process the core data to generate any other readable filetipe. Refer to [#Development](#Development).

### E.g.

From __flink__(stdf.yaml)
![](__relative_root__/README/pdg.svg)

## Development

### Standard Flow Matrix -- The MOST IMPORTANT data structure

This concept comes from yafc,
*aka* from trying convert yaml to flow chart.
But it is independent from YAML or chart.

As the name suggests, Standard Flow Matrix(STM) is a matrix.
Actually it is similar to a adjacency matrix of control flow in
Program Dependency Graph(PDG).

STM([**S**]) specification :

- Numbering flow nodes in a flow by the matrix row/column number

	> so it is supposed to be a square matrix.

define(`Sii',`[**S**]<sub><i>i</i>,<i>i</i></sub>')dnl
define(`Sij',`[**S**]<sub><i>i</i>,<i>j</i></sub>')dnl
- For a value Sij in the **S** located at *i* row and *j* column :
	- Sij is **1**
		- If *j* is a branch node and the *true* branch path is from *i* to *j*
	- Sij is **-1**
		- If *j* is a branch node and the *false* branch path is from *i* to *j*
	- Sij ∉ **{-1 , 0 , 1}**
		- If *j* is a trival node and there is a path from *j* to *i*

		> __flink__(yaml2r.py) use 2 here

divert(-1)dnl
	- Sii is **1**
		- If *i* is the end node
divert(0)dnl
	- Sij is **0**
		- Others

Some properties in a STM([**S**]) of correct standard control flow :

- Count of none 0 value in a column **S**<sub><i>i</i></sub> should be in **{0 , 1 , 2}** and :
	- Only the last column is 0 and it should be always 0 as a result STM
	- Only branch or loop condition node is 2
	- Sii is always 0
	- Sij is trival value(∉ **{-1 , 0 , 1}**) and *j* < *i* + 1 means a loop back

*e.g.* STM of __flink__(stdf.yaml) is :
![](__relative_root__/README/plot.svg)

__flink__(yaml2r.py) generate R statements to generate a R list data contain :

- STM of control flow described by the yaml file in _mc_ $M _mc_ field
- Node description in _mc_ $I _mc_ field
- Node input description in _mc_ $i _mc_ field
- Node input description in _mc_ $o _mc_ field

as _mc_ .rds _mc_ format to the standard output.

So _mc_ yaml2r.py < .yaml | R -s --no-save > .rds _mc_
will save informations above to _mc_ .rds _mc_

And __flink__(r2dot.r) just generate dot statements according to the STM _mc_ .rds _mc_

divert(-1)dnl
#### Program Dependency Graph & Standard Flow Matrix

### Human readable relative

divert(0)dnl

### Why more

#### Why YAML

- YAML may be the readable, structured text contain most data type
- YAML can show more "pure" content of the flow chart
	- YAML use as less as possible none whitespace character to define list
	
		> Especially list element can be without suffix. Such as _mc_ , _mc_ in TOML or JSON
	
	- YAML use as less as possible none whitespace character to define string
- Pyyaml is a part of python standard

#### Why Python

- Pyyaml is a part of python standard
- Python has stricter atom data type to distinguish them

	> Especially for that it was hard to distinguish character vector and "string vector" in R

#### Why R

As said above, Standard Flow Matrix(STM) is the most important concept and structure,
and it is a matrix.

- R support native matrix and it can index matrix element or matrix area in lots of ways easily
- All information include STM can be saved into RDS without any other additional definition out of R itself
