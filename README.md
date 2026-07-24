# efekurucay.com

Elle yazılmış statik site. Framework yok, derleme adımı yok, veritabanı yok.
Tarayıcı dosyaları olduğu gibi açar.

## Yapı

```
index.html            dil seçimi (JS cihaza göre yönlendirir)
stil.css              tüm stil (max-width + print)
dil.js                dil tercihini hatırlar
CNAME .nojekyll       GitHub Pages
tr/  en/              iki dil, simetrik
  <yıl>/<ay>/<slug>/  her giriş bir klasör + index.html
  arsiv|archive/      tam liste + arama
  hakkinda|about/     
  cv/                 
bin/uret.py           liste sayfalarını üretir
```

## Yeni giriş

1. `tr/<yıl>/<ay>/<slug>/index.html` yaz (varsa `en/...` karşılığı).
   `<meta name="tur">`, `<meta name="ozet">`, `<meta name="etiket">` doldur.
   İki dil birbirine `<link rel="alternate" hreflang>` ile bağlanır.
2. `python3 bin/uret.py` çalıştır — ana sayfa, arşiv, yıl/ay indekslerini tazeler.
   Script sadece `<!-- URETILDI:BAS -->` ile `<!-- URETILDI:SON -->` arasını değiştirir;
   elle yazılan her şey yerinde kalır. Script silinse site yaşar.

## Türler

`yazı` · `proje` · `not` · `terk` · `müzik`

## Yerelde bakmak

```
python3 -m http.server 8000
```
