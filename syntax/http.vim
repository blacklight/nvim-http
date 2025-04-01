" Syntax for HTTP request files
" Language: HTTP
" Maintainer: Fabio Manganiello <fabio@manganiello.tech>

" Quit when a syntax file was already loaded
if exists('b:current_syntax')
  finish
endif

syn case ignore
syn include @JSON syntax/json.vim
syn include @HTML syntax/html.vim
syn include @XML syntax/xml.vim

syn region HttpResponse start=/^HTTP\/\d\+\.\d\+\s\+/ end='skip' contains=HttpHead,HttpComment
syn region HttpRequest start=/^\(###\)\|\(GET\)\|\(POST\)\|\(PUT\)\|\(PATCH\)\|\(DELETE\)\|\(HEAD\)\|\(CONNECT\)/
            \ end=/^\(###\)\|$/ matchgroup=Comment contains=HttpHead,HttpComment

syn region HttpHead
            \ start=/^\(\(GET\)\|\(POST\)\|\(PUT\)\|\(PATCH\)\|\(DELETE\)\|\(HEAD\)\|\(CONNECT\)\|\(HTTP\/\d\+\.\d\+\)\)\s\+/
            \ end=/^\n/
            \ contained keepend
            \ contains=HttpMethod,HttpURL,HttpVersion,HttpHeader,HttpResponseLine,HttpVariable
            \ nextgroup=HttpPayload

syn region HttpComment start=/#/ end=/$/ contained
syn region HttpHeader start=/^[A-Za-z0-9_\-{}]\+:/ end=/$/ contained contains=HttpHeaderName,HttpVariable
syn region HttpResponseLine start=/^HTTP\/\d\+\.\d\+\s\+/ end=/$/ contained contains=HttpVersion,HttpResponseStatus
syn region HttpPayload start='.' end=/^\(\n\|###.*\|$\)/ keepend contained contains=HttpJsonPayload,HttpHtmlPayload,HttpXmlPayload
syn region HttpJsonPayload start=/^\s*\({\|\[\)/ end=/^\s*\(}\|\]\)\s*$/ contained contains=@JSON
syn region HttpHtmlPayload start=/^\s*\(\(<html\s*\)\|\(<?doctype\s\+\)\).*>/ end=/^\s*<\/\s*html\s*>/ keepend contained contains=@HTML
syn region HttpXmlPayload start=/^\s*<?xml\s\+/ end=/^(\n\|###)/ keepend contained contains=@XML

syn match  HttpMethod /^\(\(GET\)\|\(POST\)\|\(PUT\)\|\(PATCH\)\|\(DELETE\)\|\(HEAD\)\|\(CONNECT\)\)\s\+/
            \ contained nextgroup=HttpURL
syn match  HttpURL /http[s]\?:\/\/[A-Za-z0-9\/\-._:?%&{}()\]\[]\+/ contained contains=HttpVariable
syn match  HttpVersion /HTTP\/\d\+\.\d\+/ contained
syn match  HttpResponseStatus /\s\+\d\+\s\+[A-Za-z ]\+$/ contained
syn match  HttpHeaderName /^[^:]\+/ contained contains=HttpVariable
syn match  HttpVariable /{{.\+}}/ contained

hi def link HttpComment         Comment
hi def link HttpMethod          Function
hi def link HttpHeader          Normal
hi def link HttpURL             Type
hi def link HttpVersion         Number
hi def link HttpHeaderName      Identifier
hi def link HttpVariable        PreProc
hi def link HttpPayload         String
hi def link HttpResponseStatus  String

let b:current_syntax = 'http'

