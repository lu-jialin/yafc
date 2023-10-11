divert(-1)
define(`__code__', _mc_ `$1' _mc_)
define(`__md_code__', changequote([,])[changequote([,])```changequote(`,')]changequote(`,'))
define(`_mc_', `__md_code__')
changecom(`>>', `<<')
define(`__link__', [`$1']($1))
define(`__flink__', [`__code__($1)']($1))
define(`__m4_declaration__',
`
> This document was generated from __flink__($1) by **GNU M4**.
> A client git hook is used, contact *jialinlu@amd.com* if you need it too.'
)
define(`__more_details__',
` More details

> Enter sub directories to get more details for the specific module.'
)
define(`__codeitemlist__', `ifelse(`$#', `0', , `$#', `1', `__code__(`$1')', `__code__(`$1') __codeitemlist__(shift($@))')')
define(`__md_table_title__', `ifelse(`$#', `0', , `$#', `1', ``$1'', ``$1' | __md_table_title__(shift($@))')')
define(`__md_table_spline__', `ifelse(`$#', `0', , `$#', `1', `-', `- | __md_table_spline__(shift($@))')')
define(`__doing__', `⟳')
define(`__fork__', `Build-Build')
define(`__path_title__', ifelse(__path__, `', `', [<code>__path__</code>]()))
define(`__title__', __git__&__fork__ __path_title__)
divert(-0)dnl
