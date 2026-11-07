// grod modu: nav'daki grod wordmark'i sayfayi koyu temaya gecirir, tekrar basinca aciga.
// Varsayilan acik. <head>'de senkron yuklenir ki kayitli secim ilk boyamadan once
// uygulansin.
(function () {
  var kok = document.documentElement;
  try {
    if (localStorage.getItem("tema") === "koyu") kok.setAttribute("data-tema", "koyu");
  } catch (e) {}

  function koyuMu() { return kok.getAttribute("data-tema") === "koyu"; }

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

    dugme.addEventListener("click", function () {
      if (koyuMu()) kok.removeAttribute("data-tema");
      else kok.setAttribute("data-tema", "koyu");
      try { localStorage.setItem("tema", koyuMu() ? "koyu" : "acik"); } catch (e) {}
      isaretle();
    });
    nav.appendChild(dugme);
  });
})();
