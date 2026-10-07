#!/usr/bin/env python3
"""Uso: python3 render_audit.py NN   (ex.: 05)
Valida sections/NN-*.audit.json; se valido, reescreve sections/NN-*.md (tabela) e NN-*.audit.md.
Sai com codigo 1 e lista os erros se algo estiver incompleto."""
import sys, json, glob, os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = B + "/sections"
LINK = {"vivo", "morto", "redirecionado", "bloqueado_bot", "indeterminado"}
EVID = ("http", "wayback", "oembed", "api_github", "pagina")
KIND = {"publicacao", "ultima_atualizacao", "criacao_repo"}
VERD = {"verificado", "parcial", "nao_verificado", "falhou"}
nn = sys.argv[1].zfill(2)
jp = glob.glob(f"{S}/{nn}-*.audit.json")
if not jp:
    sys.exit("json nao encontrado")
jp = jp[0]
d = json.load(open(jp))
errs = []
for e in d["entries"]:
    p = f"#{e['idx']}"
    if e.get("url") is None:
        # entrada sem link no README: so exige veredito
        if e.get("verdict") not in VERD: errs.append(f"{p} sem url: verdict invalido")
        continue
    if e.get("link_status") not in LINK: errs.append(f"{p} link_status invalido: {e.get('link_status')}")
    ev = e.get("link_evidence") or ""
    if not any(ev.startswith(x) for x in EVID): errs.append(f"{p} link_evidence deve comecar com {EVID}: '{ev}'")
    if e.get("date"):
        if e.get("date_kind") not in KIND: errs.append(f"{p} date_kind invalido")
        if not e.get("date_source"): errs.append(f"{p} data sem date_source")
        if e.get("date_kind") == "criacao_repo" and "atualizado" in (e.get("version_note") or "").lower():
            errs.append(f"{p} nao use data de criacao para afirmar que esta atualizado")
    else:
        if (e.get("date_source") or "") != "data nao encontrada": errs.append(f"{p} sem data: date_source deve ser 'data nao encontrada'")
    if not e.get("language"): errs.append(f"{p} language vazio")
    if not e.get("version_note"): errs.append(f"{p} version_note vazio")
    if e.get("category_ok") not in (True, False): errs.append(f"{p} category_ok deve ser true/false")
    if e.get("category_ok") is False and not e.get("category_suggestion"): errs.append(f"{p} categoria incorreta sem category_suggestion")
    if e.get("alternative") is None and not e.get("alternative_reason"): errs.append(f"{p} sem alternativa exige alternative_reason (justificativa)")
    if e.get("link_status") == "morto" and not e.get("alternative"): errs.append(f"{p} link morto: pesquise Wayback/URL nova em 'alternative'")
    if e.get("verdict") not in VERD: errs.append(f"{p} verdict invalido")
if errs:
    print("INVALIDO:"); [print(" -", x) for x in errs]; sys.exit(1)

def cell(e):
    if e.get("url") is None: return "sem link no README"
    dt = f"{e['date']} ({e['date_kind']}; fonte: {e['date_source']})" if e.get("date") else "data nao encontrada"
    alt = e["alternative"] if e.get("alternative") else f"nenhuma ({e['alternative_reason']})"
    cat = "ok" if e["category_ok"] else f"INCORRETA -> {e['category_suggestion']}"
    return f"{e['verdict'].upper()}: link {e['link_status']} [{e['link_evidence']}]; {dt}; {e['language']}; {e['version_note']}; categoria {cat}; alternativa: {alt}".replace("|", "/").replace("\n", " ")
L = [f"# Build your own {d['section']}", "", "| # | Tutorial | URL | HTTP (verificador) | Auditoria |", "|---|---|---|---|---|"]
for e in d["entries"]:
    L.append(f"| {e['idx']} | {e['title'].replace('|','/')} | {e['url'] or ''} | {e['http_prior']} | {cell(e)} |")
open(f"{S}/{d['slug']}.md", "w").write("\n".join(L) + "\n")
cnt = {v: sum(1 for e in d["entries"] if e.get("verdict") == v) for v in VERD}
A = [f"# Auditoria: {d['section']}", "", f"Total: {len(d['entries'])} | " + " | ".join(f"{k}: {v}" for k, v in cnt.items()), ""]
for e in d["entries"]:
    A += [f"## {e['idx']}. {e['title']}", f"- URL: {e['url']}", f"- {cell(e)}", ""]
open(f"{S}/{d['slug']}.audit.md", "w").write("\n".join(A))
print("OK", d["slug"], cnt)
