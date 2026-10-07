# Auditoria: Docker

Total: 6 | parcial: 0 | verificado: 6 | falhou: 0 | nao_verificado: 0

## 1. **C**: _Linux containers in 500 lines of code_
- URL: https://blog.lizzie.io/linux-containers-in-500-loc.html
- VERIFICADO: link vivo [http 200 https://blog.lizzie.io/linux-containers-in-500-loc.html (curl -sIL); pagina lida via web_extract: artigo de Lizzie Dixon sobre contained.c, namespaces, capabilities, seccomp]; 2016-10-17 (publicacao; fonte: RSS do blog (https://blog.lizzie.io/rss.xml), pubDate Mon, 17 Oct 2016); inglês; C puro (contained.c, ~570 linhas apos revisao; Linux syscalls namespaces/capabilities/seccomp/cgroups); versao de kernel nao verificada; categoria ok; alternativa: nenhuma (Artigo original vivo e acessivel; cobre implementacao de containers Linux em C, exatamente o escopo da secao Docker)

## 2. **Go**: _Build Your Own Container Using Less than 100 Lines of Go_
- URL: https://www.infoq.com/articles/build-a-container-golang
- VERIFICADO: link redirecionado [http 200 https://www.infoq.com/articles/build-a-container-golang/ (curl -sIL; URL final com barra final); pagina lida via web_extract: artigo de Julian Friedman sobre namespaces, cgroups e filesystems em Go]; 2016-04-22 (publicacao; fonte: pagina InfoQ (cabecalho Apr 22, 2016 e meta Published: 2016-04-22)); inglês; Go (codigo de exemplo em Go puro usando syscall); versao de Go nao especificada no artigo; versao nao verificada; categoria ok; alternativa: nenhuma (Artigo original vivo (so redireciona para URL com barra final); tutorial direto sobre construir container em Go, dentro do escopo da secao)

## 3. **Go**: _Building a container from scratch in Go_
- URL: https://www.youtube.com/watch?v=8fi7uSYlOdc
- VERIFICADO: link vivo [oembed https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=8fi7uSYlOdc&format=json retornou 200 com titulo 'Containers From Scratch • Liz Rice • GOTO 2018']; 2018-06-29 (publicacao; fonte: pagina do YouTube (meta uploadDate/publishDate 2018-06-29T02:00:30-07:00)); inglês; Go (palestra escreve um runtime de container em Go ao vivo); versao de Go nao verificada; categoria ok; alternativa: nenhuma (Video oficial GOTO 2018 disponivel no YouTube (oEmbed 200); palestra duplicada como repositorio github.com/lizrice/containers-from-scratch, mas o link original esta vivo)

## 4. **Python**: _A workshop on Linux containers: Rebuild Docker from Scratch_
- URL: https://github.com/Fewbytes/rubber-docker
- VERIFICADO: link vivo [http 200 https://github.com/Fewbytes/rubber-docker (curl -sIL); api_github repos/Fewbytes/rubber-docker retornou 200]; 2024-07-28 (ultima_atualizacao; fonte: api_github pushed_at); inglês; Python 2/3 com modulo nativo em C (linux.c expoe syscalls); workshop por niveis (levels); ultima alteracao 2024; versao de Python nao verificada; categoria ok; alternativa: nenhuma (Repositorio oficial do workshop, vivo e acessivel; conteudo em Python, dentro do escopo da secao Docker)

## 5. **Python**: _A proof-of-concept imitation of Docker, written in 100% Python_
- URL: https://github.com/tonybaloney/mocker
- VERIFICADO: link vivo [http 200 https://github.com/tonybaloney/mocker (curl -sIL); api_github repos/tonybaloney/mocker retornou 200]; 2021-07-01 (ultima_atualizacao; fonte: api_github pushed_at); inglês; Python (README cita teste em CentOS 7 e Ubuntu 14; usa namespaces/cgroups/iproute2); versao de Python nao verificada; categoria ok; alternativa: nenhuma (Repositorio vivo do projeto mocker; proof-of-concept em Python puro, exatamente o tema da entrada)

## 6. **Shell**: _Docker implemented in around 100 lines of bash_
- URL: https://github.com/p8952/bocker
- VERIFICADO: link vivo [http 200 https://github.com/p8952/bocker (curl -sIL); api_github repos/p8952/bocker retornou 200]; 2017-12-09 (ultima_atualizacao; fonte: api_github pushed_at); inglês; Bash puro (~100 linhas); requisitos: btrfs-progs, iproute2, iptables, libcgroup-tools, util-linux >= 2.25.2, coreutils >= 7.5; repo sem atividade desde 2017; categoria ok; alternativa: nenhuma (Repositorio original vivo e acessivel; implementacao classica em bash referenciada pela comunidade, dentro do escopo da secao)
