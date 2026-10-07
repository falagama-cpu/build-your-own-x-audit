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
                  "publication / last-update date with its source, and category. Last audit: **{date}** · {done}/30 sections · "
                  "{n} tutorials · {fixed} links replaced. Per-section reports: [`audit/`](audit/).",
        "legend": "> Legend: 📅 year of publication or last update · 🔁 original link was dead, replaced · ↪ moved, URL updated · 🏷 suggested category",
        "dead": "🔁 original dead: {u}",
        "moved": "↪",
        "year": "📅 {y}",
        "cat": "🏷 {c}",
    },
    "pt": {
        "banner": "> **Edição auditada e mantida.** A [lista original]({orig}) não aceita pull requests há meses e muitos links morreram. "
                  "Esta edição verifica cada tutorial: link vivo/morto (com Wayback ou substituto equivalente para os mortos), "
                  "data de publicação / última atualização com fonte, e categoria. Última auditoria: **{date}** · {done}/30 seções · "
                  "{n} tutoriais · {fixed} links substituídos. Relatórios por seção: [`audit/`](audit/).",
        "legend": "> Legenda: 📅 ano de publicação ou última atualização · 🔁 link original morto, substituído · ↪ mudou de endereço, URL atualizada · 🏷 categoria sugerida",
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="en", choices=L)
    t = L[ap.parse_args().lang]

    audits = {}
    for p in sorted(glob.glob(os.path.join(B, "sections", "*.audit.json"))):
        d = json.load(open(p, encoding="utf-8"))
        if d["entries"] and all(e.get("verdict") for e in d["entries"]):  # só seções completas
            audits[d["section"]] = d

    out, cur, idx = [], None, 0
    n = fixed = 0
    for line in open(os.path.join(B, "readme.md"), encoding="utf-8").read().splitlines():
        m = re.match(r"#### Build your own `?(.+?)`?\s*$", line)
        if m:
            cur, idx = m.group(1), 0
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
            notes = []
            if e.get("link_status") == "morto" and e.get("alternative"):
                notes.append(t["dead"].format(u=url))
                url = e["alternative"]
                fixed += 1
            elif e.get("link_status") == "redirecionado":
                fu = final_url(e.get("link_evidence"))
                if fu and fu.startswith("https://") and fu != url:
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
    print(f"OK publish/README.md: {len(audits)}/30 seções, {n} tutoriais anotados, {fixed} links substituídos")


if __name__ == "__main__":
    main()
