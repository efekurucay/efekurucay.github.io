// grod modu: nav'daki grod ikonu sayfayi koyu temaya gecirir, tekrar basinca aciga.
// <head>'de senkron yuklenir ki kayitli tema ilk boyamadan once uygulansin; secim
// yoksa tema isletim sistemini izler (stil.css).
(function () {
  var kok = document.documentElement;
  var kayitli = null;
  try { kayitli = localStorage.getItem("tema"); } catch (e) {}
  if (kayitli === "acik" || kayitli === "koyu") kok.setAttribute("data-tema", kayitli);

  var sistemKoyu = matchMedia("(prefers-color-scheme: dark)");
  function koyuMu() {
    var t = kok.getAttribute("data-tema");
    return t ? t === "koyu" : sistemKoyu.matches;
  }

  document.addEventListener("DOMContentLoaded", function () {
    var nav = document.querySelector("nav");
    if (!nav) return;
    var dugme = document.createElement("button");
    dugme.type = "button";
    dugme.className = "tema";
    var ad = kok.lang === "tr" ? "grod modu" : "grod mode";
    dugme.setAttribute("aria-label", ad);
    dugme.title = ad;
    // grod/brand/grod-wordmark.svg. Dar ekranda stil.css genisligi daraltir,
    // slice kalanini keser, yalnizca "g" (logonun kendisi) gorunur.
    dugme.innerHTML = '<svg viewBox="0 -4 54 26" preserveAspectRatio="xMinYMid slice" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true">'
      + '<circle cx="7" cy="9" r="5"/><path d="M12 4v11.5a5 5 0 0 1-5 5H4"/>'
      + '<path d="M17.5 14V9a5 5 0 0 1 5-5"/>'
      + '<circle cx="31.5" cy="9" r="5"/>'
      + '<circle cx="47" cy="9" r="5"/><path d="M52 -2.5V14"/>'
      + '</svg>';

    function isaretle() { dugme.setAttribute("aria-pressed", String(koyuMu())); }
    isaretle();
    sistemKoyu.addEventListener("change", isaretle);

    dugme.addEventListener("click", function () {
      var yeni = koyuMu() ? "acik" : "koyu";
      kok.setAttribute("data-tema", yeni);
      try { localStorage.setItem("tema", yeni); } catch (e) {}
      isaretle();
    });
    nav.appendChild(dugme);
  });
})();
