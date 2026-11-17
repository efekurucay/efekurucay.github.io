// Ada gorununce karsilar; balona dokunulunca kayit daveti acilir.
(function () {
  var ada = document.querySelector(".akdenizos-ada");
  if (!ada) return;
  var balon = ada.querySelector(".ada-balon");
  var kayit = ada.querySelector(".ada-kayit");
  var mesaj = balon.dataset.mesaj;
  var harf = balon.dataset.selam.length;
  var azalt = matchMedia("(prefers-reduced-motion: reduce)");
  var durum = "karsilama", basladi = false, zamanlayici = null;

  function davetiAc() {
    zamanlayici = null;
    if (!document.hidden) kayit.hidden = false;
  }
  function tamamla() {
    clearTimeout(zamanlayici);
    zamanlayici = null;
    harf = mesaj.length;
    balon.textContent = mesaj;
    if (durum === "davet") kayit.hidden = false;
  }
  function yaz() {
    zamanlayici = null;
    if (document.hidden) return;
    if (azalt.matches) { tamamla(); return; }
    if (harf >= mesaj.length) {
      if (durum === "davet" && kayit.hidden) zamanlayici = setTimeout(davetiAc, 1200);
      return;
    }
    harf++;
    balon.textContent = mesaj.slice(0, harf);
    zamanlayici = setTimeout(yaz, /[!?]/.test(mesaj[harf - 1]) ? 350 : 55);
  }
  function baslat() {
    if (basladi) return;
    basladi = true;
    if (azalt.matches) tamamla();
    else zamanlayici = setTimeout(yaz, 1000);
  }
  balon.addEventListener("click", function () {
    if (durum === "davet") return;
    clearTimeout(zamanlayici);
    basladi = true;
    durum = "davet";
    mesaj = balon.dataset.davet;
    harf = 0;
    balon.setAttribute("aria-label", mesaj);
    balon.setAttribute("aria-expanded", "true");
    balon.textContent = "";
    yaz();
  });
  if ("IntersectionObserver" in window) {
    var gozlem = new IntersectionObserver(function (kayitlar) {
      if (!kayitlar.some(function (kayit) { return kayit.isIntersecting; })) return;
      gozlem.disconnect();
      baslat();
    }, { threshold: 0.4 });
    gozlem.observe(ada);
  } else baslat();
  document.addEventListener("visibilitychange", function () {
    if (document.hidden) { clearTimeout(zamanlayici); zamanlayici = null; }
    else if (basladi && zamanlayici === null) yaz();
  });
  azalt.addEventListener("change", function () { if (azalt.matches && basladi) tamamla(); });
  window.addEventListener("pagehide", tamamla);
})();
