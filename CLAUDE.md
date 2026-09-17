# efekurucay.com

Elle yazılmış statik site. Framework yok, derleme adımı yok, bağımlılık yok.
Tarayıcı dosyaları olduğu gibi açar. GitHub Pages'ten yayınlanır.

Yapı için `README.md`, giriş eklemek için `yeni-giris` skill'i.

## Değişmezler

**Derleme yok.** Node, npm, bundler, şablon motoru ekleme. `bin/uret.py`
dışında araç yok; o da sadece liste sayfalarını tazeler, site onsuz da yaşar.

**İki dil simetrik.** `tr/` altındaki her sayfanın `en/` karşılığı var
(tek istisna: `tr/2023/05/muzik/`). İkisi birbirine `hreflang` ile **çift
yönlü** bağlanır — tek yönlü bağ sıralamayı bozar.

**Üretilen bölgeye elle dokunma.** `<!-- URETILDI:BAS -->` ile
`<!-- URETILDI:SON -->` arası `bin/uret.py`'nin. Oraya yazdığın şey ilk
koşuda silinir. Yıl/ay indeks sayfaları ve `gecmis.html`'ler bütünüyle
üretilir; elle düzenlenmez.

**Giriş ekledikten sonra `python3 bin/uret.py`.** Ana sayfa, arşiv, yıl/ay
indeksleri, `sitemap.xml` ve `gecmis.html`'ler bu koşuda tazelenir.

**Her sayfanın `<head>`'i tam.** `description`, `canonical`, og, twitter
card, favicon — hiçbiri opsiyonel değil. Mevcut bir sayfayı örnek alırken
kopyaladığın şeyin eksiksiz olduğunu doğrula.

**Görsel WebP.** Ekran görüntüleri `cwebp -q 80 -m 6`. Her `<img>`
gerçek `width`/`height` taşır; sayfanın ilki dışındakiler `loading="lazy"`.

## Yazım

Kod yorumları ve docstring'ler Türkçe, **diakritiksiz**:
`# Liste sayfalarini tazeler`. Kullanıcının gördüğü HTML metni Türkçe,
**tam diakritikli**: `Geçmiş`. İkisi karışmaz.

HTML'de tipografik varlıklar: `&mdash;` `&middot;` `&ldquo;` `&rdquo;`.
Kesme işareti eğik: `’` (U+2019), karakterin kendisi — düz `'` değil,
`&#39;` değil. `Claude’un`, `2026’da`.

## Sınırlar

`stil.css` tek dosya ve kısa kalır — yeni bir görünüm için önce mevcut
sınıfları (`.kart`, `.mozaik`, `.buton`, `.etiket`, `.sosyal`) kullan.

Girdi klasörleri kendi içinde kapalı: görseli girdinin kendi klasöründe
durur, `/assets/` yalnızca siteye ait ortak görseller içindir.
