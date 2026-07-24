// Dil secildiginde hatirla. Kok sayfa bir daha tahmin etmesin.
document.addEventListener("click", function (e) {
  var a = e.target.closest("a[data-dil]");
  if (a) localStorage.setItem("dil", a.getAttribute("data-dil"));
});
