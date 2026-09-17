# efekurucay.com

Elle yazılmış statik site. Framework yok, derleme adımı yok, veritabanı yok.
Tarayıcı dosyaları olduğu gibi açar.

## Yapı

```
index.html            dil seçimi (tarayıcı diline göre yönlendirir, tercih hatırlanır)
stil.css              tüm stil (max-width + print)
dil.js                dil tercihini hatırlar
asistan.js            her sayfaya iletişim panelini ekler
robots.txt            her şey serbest, sitemap'i gösterir
sitemap.xml           üretilir (lastmod git'ten)
CNAME .nojekyll       GitHub Pages
tr/  en/              iki dil, simetrik
  <yıl>/<ay>/<slug>/  her giriş bir klasör + index.html
  arsiv|archive/      tam liste + arama
  hakkinda|about/     
  cv/                 
bin/uret.py           liste sayfalarını, geçmiş sayfalarını ve sitemap'i üretir
```

## Yeni giriş

1. `tr/<yıl>/<ay>/<slug>/index.html` yaz (varsa `en/...` karşılığı).
   `<meta name="tur">`, `<meta name="ozet">`, `<meta name="etiket">` doldur.
   İki dil birbirine `<link rel="alternate" hreflang>` ile bağlanır.
2. `python3 bin/uret.py` çalıştır — ana sayfa, arşiv, yıl/ay indekslerini ve
   `sitemap.xml`'i tazeler.
   Script sadece `<!-- URETILDI:BAS -->` ile `<!-- URETILDI:SON -->` arasını değiştirir;
   elle yazılan her şey yerinde kalır. Script silinse site yaşar.

## Türler

`yazı` · `proje` · `not` · `terk` · `müzik`

İngilizce girişlerde: `writing` · `project` · `note` · `abandoned` · `music`

Listede olmayan bir tür arşivde "Diğer" başlığı altına düşer, kaybolmaz.

## Yerelde bakmak

```
python3 -m http.server 8000
```
