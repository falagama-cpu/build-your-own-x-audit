#!/usr/bin/env python3
"""Gera o README atualizado do build-your-own-x a partir do README original
(readme.md) + auditorias (sections/NN-*.audit.json).

Uso: python3 build_readme.py [--lang en|pt]
Saída: publish/README.md (+ publish/audit/NN-*.audit.md copiados)

Regras aplicadas em cada tutorial auditado:
  - link morto com alternativa  -> URL trocada pela alternativa; original citado
  - link redirecionado          -> URL trocada pelo destino final (quando legível na evidência)
  - data com fonte              -> anotação com o ano (publicação/atualização)
  - categoria errada            -> anotação com a categoria sugerida (não move o item)
Seções ainda não auditadas ficam como no original.
"""
import argparse, datetime as dt, glob, json, os, re, shutil

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(B, "publish")

L = {
    "en": {
        "banner": "> **Audited & maintained edition.** The [original list]({orig}) has not merged a pull request in months and many links have rotted. "
                  "This edition checks every tutorial: live/dead link (with Wayback or an equivalent replacement for dead ones), "
                  "publication / last-update date with its source, and category. Last audit: **{date}** · {done} audited sections · "
                  "{n} tutorials · {fixed} links replaced. Per-section reports: [`audit/`](audit/).",
        "legend": "> Legend: 📅 year of publication or last update · 🔁 original link was dead, replaced · ↪ moved, URL updated · 🏷 suggested category · 🆕 added by this edition",
        "dead": "🔁 original dead: {u}",
        "moved": "↪",
        "year": "📅 {y}",
        "cat": "🏷 {c}",
    },
    "pt": {
        "banner": "> **Edição auditada e mantida.** A [lista original]({orig}) não aceita pull requests há meses e muitos links morreram. "
                  "Esta edição verifica cada tutorial: link vivo/morto (com Wayback ou substituto equivalente para os mortos), "
                  "data de publicação / última atualização com fonte, e categoria. Última auditoria: **{date}** · {done} seções auditadas · "
                  "{n} tutoriais · {fixed} links substituídos. Relatórios por seção: [`audit/`](audit/).",
        "legend": "> Legenda: 📅 ano de publicação ou última atualização · 🔁 link original morto, substituído · ↪ mudou de endereço, URL atualizada · 🏷 categoria sugerida · 🆕 acrescentado nesta edição",
        "dead": "🔁 original morto: {u}",
        "moved": "↪",
        "year": "📅 {y}",
        "cat": "🏷 {c}",
    },
}

URL_RE = re.compile(r"https?://[^\s)\"'>]+")


def final_url(evidence: str):
    urls = URL_RE.findall(evidence or "")
    return urls[-1].rstrip(".,;") if urls else None


def looks_generic(orig: str, final: str) -> bool:
    """Redirecionamento para raiz/categoria (soft 404): não troca o link."""
    from urllib.parse import urlparse
    so = [x for x in urlparse(orig).path.split("/") if x]
    sf = [x for x in urlparse(final).path.split("/") if x]
    return (so and not sf) or len(sf) < len(so) - 1 or (len(sf) >= 1 and sf[0] in ("c", "category", "tag", "topics"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="en", choices=L)
    t = L[ap.parse_args().lang]

    audits = {}
    for p in sorted(glob.glob(os.path.join(B, "sections", "*.audit.json"))):
        d = json.load(open(p, encoding="utf-8"))
        if d["entries"] and all(e.get("verdict") for e in d["entries"]):  # só seções completas
            audits[d["section"]] = d

    out, cur, idx, label = [], None, 0, None
    removed = []
    n = fixed = 0
    for line in open(os.path.join(B, "readme.md"), encoding="utf-8").read().splitlines():
        if line.startswith("#### Uncategorized"):
            cur, idx, label = "Uncategorized", 0, "Uncategorized"
            out.append(line)
            continue
        if line.startswith("## "):
            cur = None   # fim das listas (Contribute, License...)
        m = re.match(r"#### Build your own `?(.+?)`?\s*$", line)
        if m:
            cur, idx = m.group(1), 0
            label = cur
            out.append(line)
            continue
        if cur and line.startswith("* "):
            idx += 1
            d = audits.get(cur)
            mm = re.match(r"\* \[(.+?)\]\((https?://[^)]+)\)(.*)$", line)
            if not d or not mm or idx > len(d["entries"]):
                out.append(line)
                continue
            e = d["entries"][idx - 1]
            if e.get("url") != mm.group(2):  # desalinhado: não arrisca
                out.append(line)
                continue
            n += 1
            title, url, rest = mm.groups()
            if e.get("exclude"):
                removed.append((label, title, url, e.get("exclude_reason") or ""))
                n -= 1
                continue
            notes = []
            if e.get("link_status") == "morto" and e.get("alternative"):
                notes.append(t["dead"].format(u=url))
                url = e["alternative"]
                fixed += 1
            elif e.get("link_status") == "redirecionado":
                fu = final_url(e.get("link_evidence"))
                if fu and fu.startswith("https://") and fu != url and not looks_generic(url, fu):
                    url = fu
                    notes.append(t["moved"])
            if e.get("date") and e.get("date_source") and e["date_source"] != "data nao encontrada":
                notes.append(t["year"].format(y=str(e["date"])[:4]))
            if e.get("category_ok") is False and e.get("category_suggestion"):
                notes.append(t["cat"].format(c=e["category_suggestion"]))
            suffix = f" <sub>{' · '.join(notes)}</sub>" if notes else ""
            out.append(f"* [{title}]({url}){rest}{suffix}")
            continue
        out.append(line)

    # acréscimos validados (add-NN-*.json): entram no fim da seção existente, com 🆕
    adds = {}
    for p in sorted(glob.glob(os.path.join(B, "sections", "add-*.json"))):
        d = json.load(open(p, encoding="utf-8"))
        E = d.get("entries") or []
        if len(E) >= 5 and all(e.get("verdict") for e in E):
            adds[d["section"]] = E
    if adds:
        last, sec = {}, None
        for i, l in enumerate(out):
            m = re.match(r"#### Build your own `?(.+?)`?\s*$", l)
            if m:
                sec = m.group(1)
            elif l.startswith("## ") or l.startswith("#### Uncategorized"):
                sec = None
            elif sec and l.startswith("* ["):
                last[sec] = i
        known = set(re.findall(r"\]\((https?://[^)]+)\)", "\n".join(out)))
        for sec_name, i in sorted(last.items(), key=lambda kv: -kv[1]):
            new = []
            for e in adds.get(sec_name, []):
                if e["url"] in known:
                    continue
                known.add(e["url"])
                notes = ["🆕"]
                if e.get("date") and e.get("date_source") != "data nao encontrada":
                    notes.append(t["year"].format(y=str(e["date"])[:4]))
                new.append(f"* [**{e['language']}**: _{e['title']}_]({e['url']}) <sub>{' · '.join(notes)}</sub>")
            out[i + 1:i + 1] = new
            n += len(new)

    # seção nova 31 (descoberta): entra em ordem alfabética, antes de Command-Line Tool
    subs = []
    for p in sorted(glob.glob(os.path.join(B, "sections", "31-*.json"))):
        d = json.load(open(p, encoding="utf-8"))
        E = d.get("entries") or []
        if 5 <= len(E) and all(e.get("verdict") for e in E):
            subs.append(d)
    if subs:
        name = subs[0]["section"]
        block, seen = [f"#### Build your own `{name}`", ""], set()
        for d in subs:
            block += [f"##### {d['title']}", ""]
            for e in d["entries"]:
                if e["url"] in seen:
                    continue
                seen.add(e["url"])
                notes = ["🆕"]
                if e.get("date") and e.get("date_source") != "data nao encontrada":
                    notes.append(t["year"].format(y=str(e["date"])[:4]))
                block.append(f"* [**{e['language']}**: _{e['title']}_]({e['url']}) <sub>{' · '.join(notes)}</sub>")
            block.append("")
        anchor = "build-your-own-" + re.sub(r"[^a-z0-9 -]", "", name.lower()).replace(" ", "-")
        i = next(i for i, l in enumerate(out) if l.startswith("* [Command-Line Tool]"))
        out.insert(i, f"* [{name}](#{anchor}) 🆕")
        j = next(i for i, l in enumerate(out) if l.startswith("#### Build your own `Command-Line Tool`"))
        out[j:j] = block
        n += len(seen)

    # itens removidos: listados antes de "## Contribute", com o motivo
    if removed:
        k = next(i for i, l in enumerate(out) if l.startswith("## Contribute"))
        blk = ["## Removed in this edition", "",
               "Tutorials from the original list that were dropped because they are dead and/or no longer runnable "
               "with current tools. Kept here for reference.", ""]
        blk += [f"* {sec} — [{title}]({url}): {why}" for sec, title, url, why in removed]
        out[k:k] = blk + [""]

    # banner logo depois do título principal
    banner = [
        "",
        t["banner"].format(orig="https://github.com/codecrafters-io/build-your-own-x",
                           date=dt.date.today().isoformat(), done=len(audits), n=n, fixed=fixed),
        ">",
        t["legend"],
        "",
    ]
    pos = next(i for i, l in enumerate(out) if l.startswith("## Build your own"))
    out[pos + 1:pos + 1] = banner

    os.makedirs(os.path.join(OUT, "audit"), exist_ok=True)
    open(os.path.join(OUT, "README.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    for d in audits.values():
        src = os.path.join(B, "sections", f"{d['slug']}.audit.md")
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(OUT, "audit", os.path.basename(src)))
    print(f"OK publish/README.md: {len(audits)} seções, {n} tutoriais anotados, {fixed} links substituídos")


if __name__ == "__main__":
    main()
