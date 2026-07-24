#!/usr/bin/env python3
"""Liste sayfalarini tazeler: ana sayfa, arsiv, yil ve ay indeksleri.

Girisler elle yazilmis HTML. Bu script onlari okur, sadece isaret arasindaki
bolgeleri yeniden yazar. Elle yazilan her sey yerinde kalir.

Script olurse site yasar; listeleri elle guncellemek gerekir, o kadar.

Kullanim:  python3 bin/uret.py
"""

import html
import os
import re
import subprocess
import sys

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DILLER = ("tr", "en")

# Script sadece bu isaretlerin arasini yazar.
BAS = "<!-- URETILDI:BAS -->"
SON = "<!-- URETILDI:SON -->"

SOZLUK = {
    "tr": {
        "arsiv_yol": "/tr/arsiv/", "arsiv": "Arşiv", "ana": "Ana sayfa",
        "son": "Son girişler", "tum": "Tüm arşiv", "giris": "giriş",
        "aylar": {"01": "Ocak", "02": "Şubat", "03": "Mart", "04": "Nisan",
                  "05": "Mayıs", "06": "Haziran", "07": "Temmuz", "08": "Ağustos",
                  "09": "Eylül", "10": "Ekim", "11": "Kasım", "12": "Aralık"},
        "yalnizca": "yalnızca İngilizce",
    },
    "en": {
        "arsiv_yol": "/en/archive/", "arsiv": "Archive", "ana": "Home",
        "son": "Recent entries", "tum": "Full archive", "giris": "entries",
        "aylar": {"01": "January", "02": "February", "03": "March", "04": "April",
                  "05": "May", "06": "June", "07": "July", "08": "August",
                  "09": "September", "10": "October", "11": "November", "12": "December"},
        "yalnizca": "only in Turkish",
    },
}


def meta(s, ad):
    m = re.search(r'<meta\s+name="%s"\s+content="([^"]*)"' % ad, s)
    return html.unescape(m.group(1)) if m else ""


def baslik(s):
    m = re.search(r"<title>(.*?)</title>", s, re.S)
    t = html.unescape(m.group(1)) if m else ""
    return re.sub(r"\s*&mdash;.*$|\s*—.*$", "", t).strip()


def git_tarihleri(yol):
    """Ilk ve son commit tarihi. Repo yoksa bos doner."""
    try:
        ilk = subprocess.run(
            ["git", "log", "--diff-filter=A", "--follow", "--format=%ad",
             "--date=short", "--", yol],
            cwd=KOK, capture_output=True, text=True, timeout=15,
        ).stdout.strip().splitlines()
        sonu = subprocess.run(
            ["git", "log", "-1", "--format=%ad", "--date=short", "--", yol],
            cwd=KOK, capture_output=True, text=True, timeout=15,
        ).stdout.strip()
        return (ilk[-1] if ilk else "", sonu)
    except Exception:
        return ("", "")


def girisleri_tara():
    girisler = []
    for dil in DILLER:
        kok = os.path.join(KOK, dil)
        if not os.path.isdir(kok):
            continue
        for yil in sorted(os.listdir(kok)):
            if not re.fullmatch(r"\d{4}", yil):
                continue
            for ay in sorted(os.listdir(os.path.join(kok, yil))):
                if not re.fullmatch(r"\d{2}", ay):
                    continue
                ayyol = os.path.join(kok, yil, ay)
                for slug in sorted(os.listdir(ayyol)):
                    dosya = os.path.join(ayyol, slug, "index.html")
                    if not os.path.isfile(dosya):
                        continue
                    s = open(dosya, encoding="utf-8").read()
                    es = re.search(r'<link rel="alternate" hreflang="(\w+)" href="([^"]+)"', s)
                    ilk, guncel = git_tarihleri(os.path.relpath(dosya, KOK))
                    girisler.append({
                        "dil": dil, "yil": yil, "ay": ay, "slug": slug,
                        "yol": f"/{dil}/{yil}/{ay}/{slug}/",
                        "baslik": baslik(s),
                        "tur": meta(s, "tur"),
                        "ozet": meta(s, "ozet"),
                        "etiket": meta(s, "etiket"),
                        "es": es.group(2) if es else "",
                        "git_ilk": ilk, "git_son": guncel,
                    })
    girisler.sort(key=lambda g: (g["yil"], g["ay"], g["slug"]), reverse=True)
    return girisler


def satir(g, sz, tarih_goster=True):
    tarih = f"{int(g['ay'])}" if False else sz["aylar"][g["ay"]]
    ust = f'  <dt><a href="{g["yol"]}">{html.escape(g["baslik"])}</a></dt>'
    parcalar = []
    if tarih_goster:
        parcalar.append(f"{tarih} {g['yil']}")
    if g["tur"]:
        parcalar.append(html.escape(g["tur"]))
    if g["ozet"]:
        parcalar.append(html.escape(g["ozet"]))
    return ust + "\n  <dd>" + " &middot; ".join(parcalar) + "</dd>"


def yaz(dosya, icerik):
    if not os.path.isfile(dosya):
        return False
    s = open(dosya, encoding="utf-8").read()
    if BAS not in s or SON not in s:
        print(f"  atlandi (isaret yok): {os.path.relpath(dosya, KOK)}")
        return False
    yeni = re.sub(
        re.escape(BAS) + r".*?" + re.escape(SON),
        BAS + "\n" + icerik + "\n" + SON,
        s, flags=re.S,
    )
    if yeni != s:
        open(dosya, "w", encoding="utf-8").write(yeni)
        print(f"  yazildi: {os.path.relpath(dosya, KOK)}")
    return True


def main():
    girisler = girisleri_tara()
    print(f"{len(girisler)} giris bulundu")

    for dil in DILLER:
        sz = SOZLUK[dil]
        kendi = [g for g in girisler if g["dil"] == dil]

        # Ana sayfa: son bes giris. Muzik ayri tutulur, akisa girmez.
        akis = [g for g in kendi if g["tur"] not in ("müzik", "music")]
        blok = "<dl>\n" + "\n\n".join(satir(g, sz) for g in akis[:5]) + "\n</dl>"
        blok += f'\n\n<p><a href="{sz["arsiv_yol"]}">&rarr; {sz["tum"]}</a></p>'
        yaz(os.path.join(KOK, dil, "index.html"), blok)

        # Arsiv: yila gore gruplanmis tam liste.
        parcalar = []
        for yil in sorted({g["yil"] for g in kendi}, reverse=True):
            oyil = [g for g in kendi if g["yil"] == yil]
            parcalar.append(f"<h2>{yil}</h2>\n\n<dl>\n"
                            + "\n\n".join(satir(g, sz) for g in oyil) + "\n</dl>")
            aylar = sorted({g["ay"] for g in oyil}, reverse=True)
            baglar = " &middot; ".join(
                f'<a href="/{dil}/{yil}/{a}/">{sz["aylar"][a]}</a>' for a in aylar)
            parcalar.append(f"<p><small>{baglar}</small></p>")
        arsiv_dosya = os.path.join(KOK, dil, "arsiv" if dil == "tr" else "archive", "index.html")
        yaz(arsiv_dosya, "\n\n".join(parcalar))

        # Yil ve ay indeksleri.
        for yil in sorted({g["yil"] for g in kendi}):
            oyil = [g for g in kendi if g["yil"] == yil]
            aylar = sorted({g["ay"] for g in oyil}, reverse=True)
            govde = "\n\n".join(
                f'<h2><a href="/{dil}/{yil}/{a}/">{sz["aylar"][a]}</a></h2>\n\n<dl>\n'
                + "\n\n".join(satir(g, sz, tarih_goster=False)
                              for g in oyil if g["ay"] == a) + "\n</dl>"
                for a in aylar)
            sayfa_yaz(os.path.join(KOK, dil, yil, "index.html"), dil, sz, yil, govde)

            for a in aylar:
                oay = [g for g in oyil if g["ay"] == a]
                govde = "<dl>\n" + "\n\n".join(
                    satir(g, sz, tarih_goster=False) for g in oay) + "\n</dl>"
                sayfa_yaz(os.path.join(KOK, dil, yil, a, "index.html"), dil, sz,
                          f"{sz['aylar'][a]} {yil}", govde)

    for g in girisler:
        gecmis_yaz(g)

    eksik = [g for g in girisler if not g["es"]]
    if eksik:
        print(f"\ncevirisi olmayan {len(eksik)} giris:")
        for g in eksik:
            print(f"  {g['yol']}")


def gecmis_yaz(g):
    """Her giris icin gecmis.html: git log'dan surumler. Repo yoksa atlar."""
    ipath = os.path.join(g["dil"], g["yil"], g["ay"], g["slug"], "index.html")
    try:
        cikti = subprocess.run(
            ["git", "log", "--follow", "--date=short",
             "--format=%ad\t%h\t%s", "--", ipath],
            cwd=KOK, capture_output=True, text=True, timeout=15,
        ).stdout.strip()
    except Exception:
        return
    if not cikti:
        return

    tr = g["dil"] == "tr"
    surumler = [x.split("\t", 2) for x in cikti.splitlines()]
    satirlar = []
    for i, (tarih, kisa, konu) in enumerate(surumler):
        etiket = ("yayımlandı" if tr else "published") if i == len(surumler) - 1 \
            else (konu or ("düzenlendi" if tr else "edited"))
        satirlar.append(f"  <dt>{tarih} &middot; <code>{kisa}</code></dt>\n"
                        f"  <dd>{html.escape(etiket)}</dd>")

    yol = g["yol"]
    sayfa = f"""<!DOCTYPE html>
<html lang="{g['dil']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(g['baslik'])} &mdash; {'geçmiş' if tr else 'history'}</title>
<meta name="robots" content="noindex">
<link rel="stylesheet" href="/stil.css">
</head>
<body>

<nav>
<a href="{yol}">&larr; {html.escape(g['baslik'])}</a> &middot;
<a href="/{g['dil']}/">{'Ana sayfa' if tr else 'Home'}</a>
</nav>

<h1>{html.escape(g['baslik'])} &mdash; {'geçmiş' if tr else 'history'}</h1>

<dl>
{chr(10).join(satirlar)}
</dl>

<p><small>{'Bu sayfa git geçmişinden üretildi.' if tr else 'Generated from git history.'}</small></p>

</body>
</html>
"""
    open(os.path.join(KOK, os.path.dirname(ipath), "gecmis.html"), "w",
         encoding="utf-8").write(sayfa)


SAYFA = """<!DOCTYPE html>
<html lang="{dil}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{ad} &mdash; Yahya Efe Kuruçay</title>
<link rel="stylesheet" href="/stil.css">
</head>
<body>

<nav>
<a href="/{dil}/">{ana}</a> &middot; <a href="{arsiv_yol}">{arsiv}</a>
</nav>

<h1>{ad}</h1>

{BAS}
{govde}
{SON}

<script src="/dil.js"></script>
</body>
</html>
"""


def sayfa_yaz(dosya, dil, sz, ad, govde):
    """Yil/ay indeksleri tamamen uretilir; elle yazilmis icerikleri yok."""
    os.makedirs(os.path.dirname(dosya), exist_ok=True)
    if os.path.isfile(dosya):
        yaz(dosya, govde)
        return
    open(dosya, "w", encoding="utf-8").write(SAYFA.format(
        dil=dil, ad=ad, ana=sz["ana"], arsiv=sz["arsiv"],
        arsiv_yol=sz["arsiv_yol"], govde=govde, BAS=BAS, SON=SON))
    print(f"  olusturuldu: {os.path.relpath(dosya, KOK)}")


if __name__ == "__main__":
    sys.exit(main())
