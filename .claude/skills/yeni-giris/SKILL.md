---
name: yeni-giris
description: Use when adding, translating or editing an entry on this site — a blog post, project page, note, abandoned project or music page. Triggers include "siteye yazı ekle", "yeni blog yazısı", "bunu siteye koy", "projeyi yayınla", "new post", "publish this project", or any request to write site content under tr/<yıl>/<ay>/ or en/<year>/<month>/. Not for the static pages (about, cv, ventures, contact) and not for changing bin/uret.py.
---

# Yeni giriş

Bu sitede bir giriş = bir klasör + `index.html`. Klasör iki dilde açılır,
`bin/uret.py` listeleri üretir. İçerik elle yazılır; hiçbir şey derlenmez.

**İskeleti gerçek girdiden al.** Ayrı şablon dosyası yok: aynı türden en son
eklenen girdiyi kopyala, aşağıdaki alanları değiştir. Şablon tutmuyoruz çünkü
tek bir kopya bayatlar, girdiler bayatlamaz.

## Doldurulacaklar

| Alan | Nereden gelir |
|---|---|
| `tur` | aşağıdaki türler tablosu, TR ve EN değeri farklı |
| `ozet` | listelerde görünen tek cümle, arşivde ve `description`'da aynen kullanılır |
| `etiket` | virgüllü, küçük harf. Hiçbir yerde render edilmiyor, yine de doldurulur |
| `description` | `ozet` ile **birebir aynı** metin |
| `og:title` | başlık, `— Yahya Efe Kuruçay` eki **olmadan** |
| `canonical` / `og:url` | `https://efekurucay.com/<dil>/<yıl>/<ay>/<slug>/` |
| `article:published_time` | görünen tarih satırıyla **aynı gün**: `YYYY-AA-GG` |
| `hreflang` | karşı dildeki girdi, **iki dosyada da** |

## Türler

| TR | EN | Arşiv başlığı |
|---|---|---|
| `yazı` | `writing` | Yazılar / Writing |
| `proje` | `project` | Projeler / Projects |
| `not` | `note` | Notlar / Notes |
| `terk` | `abandoned` | Terk edilenler / Abandoned |
| `müzik` | `music` | Müzik / Music |

Tablodaki değerlerden birini yaz. Başka bir şey yazarsan giriş "Diğer"
grubuna düşer ve ikon almaz — sessizce kaybolmaz ama yanlış yerde durur.

## Slug

Yazılarda her dil kendi dilinde slug alır
(`bes-yilda-uc-site` ↔ `three-sites-five-years`).
Projelerde iki dil **aynı** slug'ı paylaşır (`keyseed`, `docentic`) — ürün
adı çevrilmez.

## Tarih satırı

Başlığın hemen altında, tek `<p><small>`:

```
gün Ay yıl &middot; tur &middot; <a href=".../gecmis.html">geçmiş</a>
```

Projede tür ile geçmişin arasına dil adı ve kaynak kod linki girer:

```
5 Nisan 2026 &middot; proje &middot; Swift &middot;
<a target="_blank" rel="noopener" href="https://github.com/...">kaynak kod</a> &middot;
<a href="/tr/2026/04/rleon/gecmis.html">geçmiş</a>
```

Gün her zaman yazılır. Sitede günsüz birkaç eski girdi var; onları örnek alma.

## Görsel

Girdinin kendi klasörüne, `g1`, `g2`… diye. `/assets/` ortak görseller içindir.

```
cwebp -q 80 -m 6 ekran.png -o g1.webp   # saydamlık yoksa: -noalpha
```

PNG/JPEG bırakma. Her `<img>` gerçek piksel boyutunu taşır; `g1` sayfanın
ilk görseli olduğu için `decoding="async"`, gerisi `loading="lazy"` de alır:

`src` **mutlak** yazılır — sitedeki her görsel öyle:

```html
<p><img src="/tr/YIL/AY/SLUG/g1.webp" alt="" width="1024" height="538" decoding="async"></p>
<p><img src="/tr/YIL/AY/SLUG/g2.webp" alt="" width="1024" height="612" loading="lazy" decoding="async"></p>
```

Girdiye dışarıdan gelen kaynak dosya (repo köküne bırakılmış bir PNG gibi)
çevrildikten sonra silinir; kökte kopya bırakma.

## Sıra

1. `tr/<yıl>/<ay>/<slug>/index.html` yaz — en son eklenen aynı türden girdiden.
2. `en/<year>/<month>/<slug>/index.html` yaz. **Tek dilli girdi bırakma.**
   İkisinin `hreflang`'i birbirini göstersin.
3. Görselleri WebP'e çevir, boyutları oku, `<img>`'leri yaz.
4. `python3 bin/uret.py` — listeler, `sitemap.xml`, `gecmis.html`.
5. Commit et.
6. `python3 bin/uret.py` **tekrar** — `gecmis.html` git log'dan üretiliyor,
   ilk koşuda girdi henüz commit'lenmemiş olduğu için o sayfa boş kalır.
   Bu koşu `sitemap.xml`'deki `lastmod` değerlerini de tazeler; ikisini
   birlikte commit et.

Koşu çıktısındaki `cevirisi olmayan N giris` satırını oku. Orada senin yeni
girdin görünüyorsa ikinci dili yazmayı unutmuşsundur — tek beklenen satır
`/tr/2023/05/muzik/`.

## Doğrulama

`python3 -m http.server 8000`, sonra şunları gerçekten aç:
girdinin kendisi, `/tr/arsiv/` (doğru grupta mı, ikon geldi mi), ay indeksi,
ve dil seçicideki karşı dil linki.

## Sık yapılan hatalar

| Hata | Neden oluyor |
|---|---|
| `<head>`'de sadece `tur`/`ozet` var, SEO bloğu yok | Eski bir girdi örnek alınmış. En yenisini al |
| `og:title`'a `— Yahya Efe Kuruçay` eklenmiş | O ek `<title>`'a ait, `og:site_name` zaten adı taşıyor |
| `hreflang` tek yönlü | İki dosyaya da yazılmalı |
| Ekran görüntüsü PNG bırakılmış | Site 24 MB'tan 2.4 MB'a indi, tek girdi bunu geri alır |
| `<img>`'de boyut yok | `width`/`height` olmadan sayfa yüklenirken zıplar |
| `src` göreli yazılmış | Sitedeki 103 görselin hepsi mutlak yol kullanır |
| `uret.py` çalıştırılmamış | Girdi hiçbir listede görünmez |
| `uret.py` commit'ten önce bir kez çalıştırılmış | `gecmis.html` boş kalır, link 404 |
| Üretilen bölgeye elle yazılmış | İlk koşuda silinir |

## Dur ve baştan bak

- "Türkçesi yeter, İngilizcesini sonra eklerim" → simetri bozulur, `uret.py`
  uyarı verir
- "Görseli şimdilik PNG koyayım" → kalır
- "Arşive elle eklerim" → `URETILDI` bölgesi, ilk koşuda silinir
- "`description` yerine `ozet` zaten var" → `ozet` siteye özgü, arama motoru
  okumaz
