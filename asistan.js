// Her sayfaya iletisim yan panelini ekler. Asistan sadece ana sayfada
// (orada elle kurulu). Ana sayfa panelini elle tasidigi icin (id zaten var)
// orada atlar. dil.js gibi her sayfada yuklenir.
(function () {
  if (document.querySelector('#asistan-chat, #assistant-chat')) return; // ana sayfa: elle kurulu
  var ENDPOINT = 'https://docentic.efekurucay.com';
  var tr = (document.documentElement.lang || 'tr').slice(0, 2) === 'tr';
  var body = document.body;
  var nav = body.querySelector('nav');

  // Mevcut icerigi (.nav ve <script> haric) .icerik'e sar.
  var icerik = document.createElement('div');
  icerik.className = 'icerik';
  Array.prototype.slice.call(body.childNodes).forEach(function (n) {
    if (n === nav) return;
    if (n.nodeType === 1 && n.tagName === 'SCRIPT') return;
    icerik.appendChild(n);
  });

  var yan = document.createElement('div');
  yan.className = 'yan';
  yan.innerHTML =
    '<hr>' +
    '<h2 id="iletisim">' + (tr ? 'İletişim' : 'Contact') + '</h2>' +
    '<div id="iletisim-form"></div>';

  // nav'dan hemen sonra: once yan, sonra icerik (insertBefore ters sira ile dogru yerlesir).
  var ref = nav ? nav.nextSibling : body.firstChild;
  body.insertBefore(yan, ref);
  body.insertBefore(icerik, yan);
  body.classList.add('home');

  var w = document.createElement('script');
  w.src = ENDPOINT + '/widget.js';
  w.onload = function () {
    window.docentic({
      endpoint: ENDPOINT, key: 'efekurucay', mode: 'contact', mount: '#iletisim-form',
      nameLabel: tr ? 'Adın' : 'Your name',
      emailLabel: tr ? 'E-posta' : 'Email',
      messageLabel: tr ? 'Mesajın…' : 'Your message…',
      sendLabel: tr ? 'gönder →' : 'send →',
      emptyLabel: tr ? 'Mesaj boş.' : 'Message is empty.',
      thanksLabel: tr ? 'İletildi, teşekkürler.' : 'Sent, thank you.',
    });
  };
  document.head.appendChild(w);
})();
