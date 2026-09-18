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
import shutil
import subprocess
import sys

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DILLER = ("tr", "en")

SITE = "https://efekurucay.com"

# Script sadece bu isaretlerin arasini yazar.
BAS = "<!-- URETILDI:BAS -->"
SON = "<!-- URETILDI:SON -->"

SOZLUK = {
    "tr": {
        "arsiv_yol": "/tr/arsiv/", "arsiv": "Arşiv", "ana": "Ana sayfa",
        "about_yol": "/tr/hakkinda/", "ventures_yol": "/tr/ventures/",
        "contact_yol": "/tr/contact/",
        "son": "Son girişler", "tum": "Tüm arşiv", "giris": "giriş",
        "aylar": {"01": "Ocak", "02": "Şubat", "03": "Mart", "04": "Nisan",
                  "05": "Mayıs", "06": "Haziran", "07": "Temmuz", "08": "Ağustos",
                  "09": "Eylül", "10": "Ekim", "11": "Kasım", "12": "Aralık"},
        "yalnizca": "yalnızca İngilizce",
        "ozet": "{ad} girişleri.", "locale": "tr_TR", "diger": "Diğer",
    },
    "en": {
        "arsiv_yol": "/en/archive/", "arsiv": "Archive", "ana": "Home",
        "about_yol": "/en/about/", "ventures_yol": "/en/ventures/",
        "contact_yol": "/en/contact/",
        "son": "Recent entries", "tum": "Full archive", "giris": "entries",
        "aylar": {"01": "January", "02": "February", "03": "March", "04": "April",
                  "05": "May", "06": "June", "07": "July", "08": "August",
                  "09": "September", "10": "October", "11": "November", "12": "December"},
        "yalnizca": "only in Turkish",
        "ozet": "Entries from {ad}.", "locale": "en_US", "diger": "Other",
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
    # Iki dilde ayni sira icin ortak anahtar: es (karsilik) yolundaki slug.
    # TR girisin es'i EN yolu, EN girisin es'i TR yolu; ikisini de EN slug'a
    # gore siralamak icin EN olani sec.
    def ortak(g):
        yol = g["yol"] if g["dil"] == "en" else g["es"]
        m = re.search(r"/\d{4}/\d{2}/([^/]+)/", yol or g["yol"])
        return m.group(1) if m else g["slug"]

    girisler.sort(key=lambda g: (g["yil"], g["ay"], ortak(g)), reverse=True)
    return girisler


_KALEM = '<svg viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34a.996.996 0 00-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>'
_KOD = '<svg viewBox="0 0 24 24" width="14" height="14"><path fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" d="M8 6l-5 6 5 6M16 6l5 6-5 6"/></svg>'
_NOTA = '<svg viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M12 3v10.55A4 4 0 1014 17V7h4V3h-6z"/></svg>'
_LISTE = '<svg viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M4 6h16v2H4zm0 5h16v2H4zm0 5h10v2H4z"/></svg>'
_DURDUR = '<svg viewBox="0 0 24 24" width="14" height="14"><path fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" d="M12 3.5a8.5 8.5 0 100 17 8.5 8.5 0 000-17zM6 6l12 12"/></svg>'

# Tur -> ikon. tr ve en turleri.
TUR_IKON = {
    "yazı": ("yazı", _KALEM), "writing": ("writing", _KALEM),
    "proje": ("proje", _KOD), "project": ("project", _KOD),
    "müzik": ("müzik", _NOTA), "music": ("music", _NOTA),
    "not": ("not", _LISTE), "note": ("note", _LISTE),
    "terk": ("terk", _DURDUR), "abandoned": ("abandoned", _DURDUR),
}


def satir(g, sz, tarih_goster=True):
    tarih = sz["aylar"][g["ay"]]
    ik = TUR_IKON.get(g["tur"])
    ikon = f'<span class="tur-ikon" title="{ik[0]}">{ik[1]}</span>' if ik else ""
    ust = f'  <dt><a href="{g["yol"]}">{html.escape(g["baslik"])}</a>{ikon}</dt>'
    parcalar = []
    if tarih_goster:
        parcalar.append(f"{tarih} {g['yil']}")
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

    # Hangi dil/yil/ay kombinasyonlarinda giris var: hreflang ve dil secici
    # yalnizca gercekten dolu olan kardes sayfaya baglanir.
    dolu = {(g["dil"], g["yil"], g["ay"]) for g in girisler}

    for dil in DILLER:
        sz = SOZLUK[dil]
        kendi = [g for g in girisler if g["dil"] == dil]

        # Arsiv: ture gore bolunmus, her grup icinde tarih sirasi.
        gruplar = ([("proje", "Projeler"), ("yazı", "Yazılar"), ("müzik", "Müzik"),
                    ("not", "Notlar"), ("terk", "Terk edilenler")]
                   if dil == "tr" else
                   [("project", "Projects"), ("writing", "Writing"), ("music", "Music"),
                    ("note", "Notes"), ("abandoned", "Abandoned")])
        # Tanimsiz tur arsivden dusmesin; son grup her seyi toplar.
        gruplar.append((None, sz["diger"]))
        bilinen = {t for t, _ in gruplar}
        parcalar = []
        for tur, grup_adi in gruplar:
            grup = [g for g in kendi
                    if g["tur"] == tur or (tur is None and g["tur"] not in bilinen)]
            if not grup:
                continue
            parcalar.append(f"<h2>{grup_adi}</h2>\n\n<dl>\n"
                            + "\n\n".join(satir(g, sz) for g in grup) + "\n</dl>")
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
            obur = "en" if dil == "tr" else "tr"
            es = (f"/{obur}/{yil}/"
                  if any(d == obur and y == yil for d, y, _ in dolu) else "")
            sayfa_yaz(os.path.join(KOK, dil, yil, "index.html"), dil, sz, yil,
                      govde, es)

            for a in aylar:
                oay = [g for g in oyil if g["ay"] == a]
                govde = "<dl>\n" + "\n\n".join(
                    satir(g, sz, tarih_goster=False) for g in oay) + "\n</dl>"
                es = f"/{obur}/{yil}/{a}/" if (obur, yil, a) in dolu else ""
                sayfa_yaz(os.path.join(KOK, dil, yil, a, "index.html"), dil, sz,
                          f"{sz['aylar'][a]} {yil}", govde, es)

    for g in girisler:
        gecmis_yaz(g)

    sitemap_yaz(girisler)

    eksik = [g for g in girisler if not g["es"]]
    if eksik:
        print(f"\ncevirisi olmayan {len(eksik)} giris:")
        for g in eksik:
            print(f"  {g['yol']}")


def sitemap_yaz(girisler):
    """Tum sayfalari sitemap.xml'e yazar. Sabit sayfalar + tum girisler.

    lastmod git'ten gelir. Hesaplanamayan sayfada alan hic yazilmaz; yanlis
    tarih, tarih yoklugundan kotudur.
    """
    sabit = ["/", "/tr/", "/en/", "/tr/arsiv/", "/en/archive/",
             "/tr/hakkinda/", "/en/about/", "/tr/cv/", "/en/cv/",
             "/tr/ventures/", "/en/ventures/", "/tr/contact/", "/en/contact/",
             "/tr/bilmok/", "/en/bilmok/", "/tr/hsd/", "/en/hsd/",
             "/tr/giraffe/", "/en/giraffe/"]
    tarih = {}
    for y in sabit:
        tarih[y] = git_tarihleri(y.lstrip("/") + ("index.html" if y.endswith("/") else ""))[1]
    for g in girisler:
        tarih[g["yol"]] = g["git_son"]
        # Yil ve ay indeksleri uretilir; listeledikleri en yeni giris kadar tazedir.
        for y in (f"/{g['dil']}/{g['yil']}/", f"/{g['dil']}/{g['yil']}/{g['ay']}/"):
            tarih[y] = max(tarih.get(y, ""), g["git_son"])
    satirlar = "\n".join(
        f"  <url><loc>{SITE}{y}</loc>"
        + (f"<lastmod>{tarih[y]}</lastmod>" if tarih[y] else "")
        + "</url>" for y in sorted(tarih))
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + satirlar + "\n</urlset>\n")
    open(os.path.join(KOK, "sitemap.xml"), "w", encoding="utf-8").write(xml)
    print(f"  sitemap.xml: {len(tarih)} url")


def _govde(sayfa):
    """Girisin okunur kismi: nav ile kapanis script'leri arasi."""
    if "</nav>" not in sayfa or "<script" not in sayfa:
        return ""
    bas = sayfa.index("</nav>") + len("</nav>")
    son = sayfa.index("<script", bas)
    return sayfa[bas:son].strip()


def _metin(govde):
    """Karsilastirma anahtari: yalniz metin. Etiket degisikligi surum sayilmaz."""
    return " ".join(re.sub(r"<[^>]+>", " ", govde).split())


def _gorselleri_tazele(govde, klasor):
    """Eski govdedeki gorsel yollarini bugun diskte olanla esler.

    Bir zamanlar .png olan gorseller .webp'e cevrildi; eski surum sayfasi
    kirik gorsel gostermesin. Karsiligi da yoksa gorsel tamamen dusuruluyor.
    """
    def degistir(m):
        yol = m.group(1)
        if os.path.isfile(os.path.join(KOK, yol.lstrip("/"))):
            return m.group(0)
        webp = re.sub(r"\.(png|jpg|jpeg)$", ".webp", yol)
        if os.path.isfile(os.path.join(KOK, webp.lstrip("/"))):
            return m.group(0).replace(yol, webp)
        return ""
    govde = re.sub(r'<img[^>]+src="([^"]+)"[^>]*>', degistir, govde)
    return re.sub(r"<p>\s*</p>", "", govde)


def _surumler(ipath):
    """Metni gercekten degismis commit'ler, eskiden yeniye.

    Site geneli degisiklikler (nav, head, gorsel bicimi) surum sayilmaz;
    okuyucu icin yeni bir sey yok.
    """
    try:
        cikti = subprocess.run(
            ["git", "log", "--follow", "--date=format:%Y-%m-%d %H:%M",
             "--format=%ad\t%h", "--", ipath],
            cwd=KOK, capture_output=True, text=True, timeout=30,
        ).stdout.strip()
    except Exception:
        return []
    if not cikti:
        return []
    cikti = list(reversed(cikti.splitlines()))
    surumler, onceki = [], None
    for satir in cikti:
        damga, kisa = satir.split("\t")
        tarih = damga.split(" ")[0]
        try:
            icerik = subprocess.run(
                ["git", "show", f"{kisa}:{ipath}"],
                cwd=KOK, capture_output=True, text=True, timeout=15,
            ).stdout
        except Exception:
            continue
        govde = _govde(icerik)
        if not govde:
            continue
        anahtar = _metin(govde)
        if anahtar != onceki:
            surumler.append({"tarih": tarih, "damga": damga,
                             "kisa": kisa, "govde": govde})
            onceki = anahtar
    return surumler


def _surum_sayfasi(g, s, tr):
    """Bir surumun kendi sayfasi: o gunku metin, bugunku sablonda."""
    yol = g["yol"]
    govde = _gorselleri_tazele(s["govde"], os.path.dirname(yol))
    baslik = html.escape(g["baslik"])
    return f"""<!DOCTYPE html>
<html lang="{g['dil']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{baslik} &mdash; {s['tarih']}</title>
<meta name="robots" content="noindex">
<link rel="stylesheet" href="/stil.css">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
</head>
<body>

<nav>
<a href="{yol}gecmis.html">&larr; {'geçmiş' if tr else 'history'}</a> &middot;
<a href="{yol}">{'güncel hâli' if tr else 'current version'}</a>
</nav>

<p><small>{'Bu, yazının' if tr else 'This is how the entry read on'} <b>{s['damga']}</b>
{'tarihli hâli. Güncel sürüm' if tr else '. The current version is'}
<a href="{yol}">{'burada' if tr else 'here'}</a>.</small></p>

<hr>

{govde}

</body>
</html>
"""


def gecmis_yaz(g):
    """Girisin surum listesi ve her eski surumun kendi sayfasi.

    Listede commit mesaji yok: okuyucuyu ilgilendiren sey metnin o gunku
    hali, onu degistiren isin adi degil.
    """
    ipath = os.path.join(g["dil"], g["yil"], g["ay"], g["slug"], "index.html")
    klasor = os.path.join(KOK, os.path.dirname(ipath))
    surumler = _surumler(ipath)
    if not surumler:
        return

    tr = g["dil"] == "tr"
    baslik = html.escape(g["baslik"])
    yol = g["yol"]
    gecmis_klasor = os.path.join(klasor, "gecmis")

    # Eski surumler diske: en yenisi zaten girisin kendisi.
    eskiler = surumler[:-1]
    if os.path.isdir(gecmis_klasor):
        shutil.rmtree(gecmis_klasor)
    if eskiler:
        os.makedirs(gecmis_klasor, exist_ok=True)
    for s in eskiler:
        ad = f"{s['tarih']}-{s['kisa']}.html"
        open(os.path.join(gecmis_klasor, ad), "w", encoding="utf-8").write(
            _surum_sayfasi(g, s, tr))

    if len(surumler) == 1:
        govde = (f"<p>{'Bu yazı yayımlandığından beri değişmedi.' if tr else 'This entry has not changed since it was published.'} "
                 f"{'Yayım tarihi' if tr else 'Published'} {surumler[0]['tarih']}.</p>")
    else:
        gunler = [x["tarih"] for x in surumler]
        alan = "damga" if len(set(gunler)) != len(gunler) else "tarih"
        satirlar = [f'  <dt>{surumler[-1][alan]}</dt>\n'
                    f'  <dd><a href="{yol}">{"güncel hâli" if tr else "current version"}</a></dd>']
        for s in reversed(eskiler):
            ad = f"{s['tarih']}-{s['kisa']}.html"
            satirlar.append(f'  <dt>{s[alan]}</dt>\n'
                            f'  <dd><a href="{yol}gecmis/{ad}">{"o zamanki hâli" if tr else "as it read then"}</a></dd>')
        govde = "<dl>\n" + "\n\n".join(satirlar) + "\n</dl>"

    sayfa = f"""<!DOCTYPE html>
<html lang="{g['dil']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{baslik} &mdash; {'geçmiş' if tr else 'history'}</title>
<meta name="robots" content="noindex">
<link rel="stylesheet" href="/stil.css">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
</head>
<body>

<nav>
<a href="{yol}">&larr; {baslik}</a> &middot;
<a href="/{g['dil']}/">{'Ana sayfa' if tr else 'Home'}</a>
</nav>

<h1>{baslik} &mdash; {'geçmiş' if tr else 'history'}</h1>

{govde}

</body>
</html>
"""
    open(os.path.join(klasor, "gecmis.html"), "w", encoding="utf-8").write(sayfa)


SAYFA = """<!DOCTYPE html>
<html lang="{dil}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{ad} &mdash; Yahya Efe Kuruçay</title>
<meta name="ozet" content="{ozet}">
<meta name="description" content="{ozet}">
<meta property="og:type" content="website">
<meta property="og:title" content="{ad}">
<meta property="og:description" content="{ozet}">
<meta property="og:url" content="{site}{yol}">
<meta property="og:locale" content="{locale}">
{locale_alt}<meta property="og:site_name" content="Yahya Efe Kuruçay">
{gorsel}<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@efekurucay24">
<meta name="twitter:creator" content="@efekurucay24">
<link rel="canonical" href="{site}{yol}">
<link rel="stylesheet" href="/stil.css">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{alternate}</head>
<body>

<nav>
<a href="/{dil}/" class="logo" aria-label="{ana}"><img src="/logo.svg" alt="" width="22" height="22"></a>
<a href="{ventures_yol}">ventures</a>
<a href="{arsiv_yol}">log</a>
<a href="{about_yol}">about</a>
<a href="{contact_yol}">contact</a>
<span class="dil"><a href="{tr_yol}" data-dil="tr">TR</a> · <a href="{en_yol}" data-dil="en">EN</a></span>
</nav>

<h1>{ad}</h1>

{BAS}
{govde}
{SON}

<script src="/dil.js"></script>
</body>
</html>
"""


def sayfa_yaz(dosya, dil, sz, ad, govde, es):
    """Yil/ay indeksleri tamamen uretilir; elle yazilmis icerikleri yok.

    es: obur dildeki ayni yil/ay sayfasi. Karsilik yoksa bos gelir; o zaman
    dil secici yalnizca dil kokune bakar, hreflang hic yazilmaz.
    """
    os.makedirs(os.path.dirname(dosya), exist_ok=True)
    if os.path.isfile(dosya):
        yaz(dosya, govde)
        return
    yol = "/" + os.path.dirname(os.path.relpath(dosya, KOK)).replace(os.sep, "/") + "/"
    obur = "en" if dil == "tr" else "tr"
    # og:image yalnizca gorsel gercekten varsa; kirik onizleme yazmayalim.
    gorsel = (f'<meta property="og:image" content="{SITE}/assets/og.png">\n'
              '<meta property="og:image:width" content="1200">\n'
              '<meta property="og:image:height" content="630">\n'
              if os.path.isfile(os.path.join(KOK, "assets", "og.png")) else "")
    locale_alt = (f'<meta property="og:locale:alternate" content="{SOZLUK[obur]["locale"]}">\n'
                  if es else "")
    alternate = (f'<link rel="alternate" hreflang="{obur}" href="{es}">\n'
                 if es else "")
    oteki = es or f"/{obur}/"
    open(dosya, "w", encoding="utf-8").write(SAYFA.format(
        dil=dil, ad=ad, ana=sz["ana"], arsiv=sz["arsiv"],
        arsiv_yol=sz["arsiv_yol"], ventures_yol=sz["ventures_yol"],
        about_yol=sz["about_yol"], contact_yol=sz["contact_yol"],
        ozet=html.escape(sz["ozet"].format(ad=ad), quote=True),
        site=SITE, yol=yol, locale=sz["locale"], locale_alt=locale_alt, gorsel=gorsel,
        alternate=alternate,
        tr_yol=yol if dil == "tr" else oteki,
        en_yol=yol if dil == "en" else oteki,
        govde=govde, BAS=BAS, SON=SON))
    print(f"  olusturuldu: {os.path.relpath(dosya, KOK)}")


if __name__ == "__main__":
    sys.exit(main())
