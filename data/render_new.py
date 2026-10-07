#!/usr/bin/env python3
"""Uso: python3 render_new.py NN | add NN  (secao 31 ou acrescimos a secao NN)
Valida sections/31-NN-*.json (descoberta de tutoriais novos) e gera 31-NN-*.md.
Sai com codigo 1 e lista os erros se algo estiver incompleto."""
import sys, json, glob, os, re
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = B + "/sections"
KIND = {"publicacao", "ultima_atualizacao", "criacao_repo"}
TYPE = {"tutorial", "livro", "curso", "video", "repositorio", "documentacao", "artigo"}
LEVEL = {"iniciante", "intermediario", "avancado"}
LINK = {"vivo", "redirecionado"}
EVID = ("http", "oembed", "api_github", "pagina")
VERD = {"verificado", "parcial"}
MIN, MAX = 5, 12

# uso: render_new.py NN (secao 31)  |  render_new.py add NN (itens novos para a secao NN existente)
prefix, nn = ("31", sys.argv[1].zfill(2)) if len(sys.argv) == 2 else (sys.argv[1], sys.argv[2].zfill(2))
jp = glob.glob(f"{S}/{prefix}-{nn}-*.json")
if not jp:
    sys.exit("json nao encontrado")
jp = jp[0]
d = json.load(open(jp, encoding="utf-8"))
orig = set(re.findall(r"\]\((https?://[^)]+)\)", open(B + "/readme.md", encoding="utf-8").read()))
E = d.get("entries") or []
errs = []
if not (MIN <= len(E) <= MAX):
    errs.append(f"precisa de {MIN} a {MAX} entradas (tem {len(E)})")
if sum(1 for e in E if e.get("verdict") == "verificado") < 3:
    errs.append("precisa de pelo menos 3 entradas 'verificado'")
seen = set()
for i, e in enumerate(E, 1):
    p = f"#{i}"
    u = (e.get("url") or "").strip()
    if not u.startswith("http"): errs.append(f"{p} url invalida")
    if u in seen: errs.append(f"{p} url repetida no arquivo")
    if u in orig: errs.append(f"{p} url ja existe no README original")
    seen.add(u)
    for f in ("title", "author", "language", "summary_pt", "why"):
        if not (e.get(f) or "").strip(): errs.append(f"{p} {f} vazio")
    if e.get("type") not in TYPE: errs.append(f"{p} type invalido (use {sorted(TYPE)})")
    if e.get("level") not in LEVEL: errs.append(f"{p} level invalido")
    if e.get("free") not in (True, False): errs.append(f"{p} free deve ser true/false")
    if e.get("link_status") not in LINK: errs.append(f"{p} link_status deve ser vivo/redirecionado (link morto nao entra)")
    if not any((e.get("link_evidence") or "").startswith(x) for x in EVID): errs.append(f"{p} link_evidence deve comecar com {EVID}")
    if e.get("date"):
        if not re.match(r"^\d{4}(-\d{2}(-\d{2})?)?$", str(e["date"])): errs.append(f"{p} date fora do formato AAAA[-MM[-DD]]")
        if e.get("date_kind") not in KIND: errs.append(f"{p} date_kind invalido")
        if not e.get("date_source") or e["date_source"] == "data nao encontrada": errs.append(f"{p} data sem date_source")
    elif e.get("date_source") != "data nao encontrada":
        errs.append(f"{p} sem data: date_source deve ser 'data nao encontrada'")
    if e.get("verdict") not in VERD: errs.append(f"{p} verdict invalido (verificado|parcial)")
    if re.search(r"\b(Auditor[ií]a|tambi[eé]n|aplicaci[oó]n)\b", (e.get("summary_pt") or "") + (e.get("why") or "")):
        errs.append(f"{p} texto em espanhol")
if errs:
    print("INVALIDO:"); [print(" -", x) for x in errs]; sys.exit(1)

L = [f"# {d['section']} — {d['title']}", "", f"Escopo: {d['scope']}", "",
     "| # | Tutorial | Tipo | Nivel | Data | Gratis | Resumo |", "|---|---|---|---|---|---|---|"]
for i, e in enumerate(E, 1):
    dt = f"{e['date']} ({e['date_kind']}; {e['date_source']})" if e.get("date") else "data nao encontrada"
    row = [str(i), f"[{e['title']}]({e['url']}) — {e['author']} ({e['language']})", e["type"], e["level"],
           dt, "sim" if e["free"] else "nao", f"{e['summary_pt']} Por que: {e['why']} [{e['verdict']}; {e['link_evidence']}]"]
    L.append("| " + " | ".join(c.replace("|", "/").replace("\n", " ") for c in row) + " |")
open(jp[:-5] + ".md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("OK", os.path.basename(jp), len(E), "entradas")
