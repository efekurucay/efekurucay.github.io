// Ana sayfa ust seridi: suda yuzen 3B logolar, bakir gravur gibi taranmis.
// Tek WebGL2 shader; derleme yok, bagimlilik yok. WebGL2 yoksa serit gorunmez.
(function () {
  var tuval = document.querySelector("canvas.su");
  if (!tuval) return;
  var gl = tuval.getContext("webgl2", { antialias: false });
  if (!gl) { tuval.style.display = "none"; return; }

  // logo.svg'nin kose noktalari (yuvarlatmalar shader'da geri geliyor).
  var KOSELER = [
    [357.5, 6.12], [154.38, 5.25], [143.25, 19.12], [142.75, 77.88], [19.75, 80.25],
    [17.25, 161.62], [142.75, 165.75], [143.25, 216], [19, 219.75], [16.5, 296.62],
    [142.25, 302.38], [149.5, 368.12], [228.38, 368.87], [235.88, 249.75], [352.5, 248.87],
    [365.88, 234.25], [358.88, 165.75], [235.5, 163], [235.37, 90.62], [358.88, 87.62],
    [365.88, 19.88]
  ];
  var POLY = KOSELER.map(function (k) {
    return "vec2(" + ((k[0] - 187.5) / 375).toFixed(4) + "," + (-(k[1] - 187.5) / 375).toFixed(4) + ")";
  }).join(",");

  // Kamera: sudan 1 birim yukarida, hafif asagi bakiyor; ufuk seridin ust ucte birinde.
  var EGIM = -0.09, TAN = 0.22, KAM = [0, 1, 0];
  var ILERI = [0, Math.sin(EGIM), Math.cos(EGIM)], YUKARI = [0, Math.cos(EGIM), -Math.sin(EGIM)];

  // x, z: konum; hiz: yana suruklenme; don: kendi ekseninde donus hizi (0: sadece salinir).
  var LOGOLAR = [
    { x: -2.8, z: 4.4, hiz: 0.07, don: 0, faz: 0.0 },
    { x: 2.4, z: 5.6, hiz: 0.05, don: 0.18, faz: 1.7 },
    { x: 7.0, z: 7.4, hiz: 0.09, don: 0, faz: 3.1 },
    { x: -8.5, z: 9.0, hiz: 0.06, don: -0.12, faz: 4.4 },
    { x: 0.4, z: 12.5, hiz: 0.08, don: 0, faz: 5.2 },
    { x: 12.0, z: 15.0, hiz: 0.05, don: 0.1, faz: 2.3 },
    { x: -15.0, z: 18.0, hiz: 0.07, don: 0, faz: 0.9 }
  ];
  var N = LOGOLAR.length;
  // Ayni anda yasayan en fazla dalga sayisi; eskisi yenisine yer acar.
  var D = 16;

  var KOSE = "#version 300 es\nin vec2 p;void main(){gl_Position=vec4(p,0.,1.);}";
  var PARCA = "#version 300 es\n" +
"precision highp float;\n" +
"out vec4 renk;\n" +
"uniform vec2 coz;\n" +
"uniform float zaman,tanY,oran;\n" +
"uniform vec3 kam,ileri,yukari;\n" +
"uniform vec4 lpos[" + N + "];\n" +
"uniform mat3 lrot[" + N + "];\n" +
"uniform vec4 dalga[" + D + "];\n" +
"const int D=" + D + ";\n" +
"const int N=" + N + ";\n" +
"const vec2 POLY[" + KOSELER.length + "]=vec2[](" + POLY + ");\n" +
"const int V=" + KOSELER.length + ";\n" +
`
const float KAL=.075, YUV=.02;          // yari kalinlik, kenar yuvarlatma
const vec3 KAGIT=vec3(1.), MUREKKEP=vec3(.08,.09,.11);
const vec3 MAVI=vec3(.102,.561,.890), DERIN=vec3(.035,.30,.56);
const vec3 ISIK=vec3(-.55,.62,-.56);

float karma(float n){ return fract(sin(n*127.1)*43758.5453); }
float gurultu(float x){ float i=floor(x),f=fract(x); f=f*f*(3.-2.*f); return mix(karma(i),karma(i+1.),f); }

// Logonun 2B isaretli uzakligi: kenarlara en yakin mesafe, ici negatif.
float sdLogo2(vec2 p){
  float d=1e9,s=1.;
  for(int i=0;i<V;i++){
    vec2 a=POLY[i],b=POLY[i==0?V-1:i-1],e=b-a,w=p-a;
    vec2 q=w-e*clamp(dot(w,e)/dot(e,e),0.,1.);
    d=min(d,dot(q,q));
    bvec3 c=bvec3(p.y>=a.y,p.y<b.y,e.x*w.y>e.y*w.x);
    if(all(c)||all(not(c))) s=-s;
  }
  return s*sqrt(d);
}
// 2B sekli z boyunca kalinlastir, butun kenarlari yuvarlat.
float logo(vec3 q){
  vec2 w=vec2(sdLogo2(q.xy)+YUV,abs(q.z)-KAL+YUV);
  return min(max(w.x,w.y),0.)+length(max(w,0.))-YUV;
}
vec3 normal(vec3 q){
  vec2 e=vec2(.0012,-.0012);
  return normalize(e.xyy*logo(q+e.xyy)+e.yyx*logo(q+e.yyx)+e.yxy*logo(q+e.yxy)+e.xxx*logo(q+e.xxx));
}

// Uc ucuncu dereceden olmayan dalga toplami; JS'teki kabarma() ile ayni.
vec3 kabarma(vec2 w){
  vec2 d0=vec2(.42,.91),d1=vec2(-.75,.66),d2=vec2(.15,.99);
  float a0=dot(w,d0)*1.1-zaman*1.2,a1=dot(w,d1)*1.6-zaman*1.5+1.3,a2=dot(w,d2)*2.7-zaman*2.1+4.;
  float h=.045*sin(a0)+.028*sin(a1)+.014*sin(a2);
  vec2 g=.045*1.1*cos(a0)*d0+.028*1.6*cos(a1)*d1+.014*2.7*cos(a2)*d2;
  return vec3(h,g);
}
// Her logonun etrafinda zayif halkalar: logo suyla temas ediyor hissi.
vec3 halka(vec2 w){
  vec3 r=vec3(0);
  for(int i=0;i<N;i++){
    vec2 v=w-lpos[i].xz; float u=length(v)+1e-4;
    float k=.004*exp(-u*1.4);
    float a=u*16.-zaman*2.4;
    r+=vec3(k*sin(a),k*16.*cos(a)*v/u);
  }
  return r;
}
// Imlec ve tiklamanin dalgalari: merkezden yayilan, sonumlenen halka paketi.
// x: yukseklik, yz: egim, w: tepe cizgisi icin faz.
float dalgaFaz;
vec3 dalgalar(vec2 w){
  vec3 r=vec3(0); float enGuc=0.; dalgaFaz=0.;
  for(int i=0;i<D;i++){
    vec4 d=dalga[i];
    float yas=max(zaman-d.z,0.),on=yas*1.7;
    vec2 v=w-d.xy; float u=length(v)+1e-4,x=u-on;
    float zarf=d.w*.03*exp(-yas*.8)*exp(-x*x*2.)/(1.+u*.5)*step(d.z,zaman);
    // Dalga boyu ~.7: perspektifte basilinca da tepeler piksel araligindan genis kalsin.
    float a=x*9.;
    r+=vec3(zarf*sin(a),zarf*9.*cos(a)*v/u);
    if(zarf>enGuc){ enGuc=zarf; dalgaFaz=a; }
  }
  return r;
}
float yukseklik(vec2 w){ return kabarma(w).x+halka(w).x+dalgalar(w).x; }

struct Vurus{ float t; int i; vec3 q; float enYakin; vec3 enYakinP; };
Vurus izle(vec3 ro,vec3 rd,float tmax){
  Vurus h; h.t=tmax; h.i=-1; h.q=vec3(0); h.enYakin=1e3; h.enYakinP=vec3(0,-1e3,0);
  for(int i=0;i<N;i++){
    mat3 R=lrot[i],Ri=transpose(R);
    vec3 c=lpos[i].xyz,o=Ri*(ro-c),d=Ri*rd;
    // Logonun kutusuyla kesisim: isin sadece kutunun icinde yurur.
    vec3 b=vec3(.53,.53,KAL+.01),inv=1./d,t0=(-b-o)*inv,t1=(b-o)*inv;
    vec3 tk=min(t0,t1),tb=max(t0,t1);
    float ta=max(max(tk.x,tk.y),max(tk.z,0.)),tz=min(min(tb.x,tb.y),min(tb.z,h.t));
    if(ta>tz) continue;
    float t=ta;
    for(int k=0;k<64;k++){
      vec3 p=o+d*t; float s=logo(p);
      if(s<h.enYakin){ h.enYakin=s; h.enYakinP=c+R*p; }
      if(s<.0006){ h.t=t; h.i=i; h.q=p; break; }
      t+=s*.9;
      if(t>tz) break;
    }
  }
  return h;
}

float cizgi(float c,float g,float fw){
  float d=abs(fract(c+.5)-.5);
  return 1.-smoothstep(g-fw*.7,g+fw*.7,d);
}
// Cizgi pikselden sikilasinca titresim yerine ortalama tona dus.
// Genisligi sifir olan cizgi hic iz birakmasin.
float cizgiAA(float c,float g,float fw){ return mix(cizgi(c,g,fw),g*2.,smoothstep(.35,.7,fw))*smoothstep(0.,.03,g); }

// Gravur: on yuzde capraz tarama (mavi), yanlarda kalinlik boyunca cizgiler (siyah),
// golgede ikinci tarama, kenar ve siluet murekkep. x: murekkep, y: maviligi.
vec2 gravur(vec3 nl,vec3 nw,vec3 rd,vec3 c,vec3 fw){
  float aydin=max(dot(nw,normalize(ISIK)),0.);
  float koyu=clamp(1.-aydin*1.2,0.,1.);
  float yuz=smoothstep(.8,.97,abs(nl.z));
  float t1=cizgiAA(c.x,.07+.27*pow(koyu,1.5),fw.x);
  float t2=cizgiAA(c.y,.26*smoothstep(.6,1.,koyu),fw.y);
  float on=max(t1,t2);
  float yan=cizgiAA(c.z,.1+.34*pow(koyu,1.2),fw.z);
  float kenar=smoothstep(.3,.5,abs(nl.z))*(1.-smoothstep(.72,.9,abs(nl.z)));
  float sil=1.-smoothstep(.1,.28,abs(dot(nw,-rd)));
  float m=max(mix(yan,on,yuz),max(kenar,sil));
  float mav=yuz*(1.-max(kenar,sil));
  return vec2(m,mav);
}

void main(){
  vec2 uv=(2.*gl_FragCoord.xy-coz)/coz.y;
  vec3 ro=kam,sag=vec3(1,0,0);
  vec3 rd=normalize(ileri+uv.x*tanY*sag+uv.y*tanY*yukari);
  float pAci=2.*tanY/coz.y;

  float tp=rd.y<-1e-4?-ro.y/rd.y:1e4;
  vec3 wp=ro+rd*tp; vec2 w=wp.xz; float z=max(wp.z,1.);
  vec3 kb=kabarma(w),hl=halka(w)+dalgalar(w);
  float faz=dalgaFaz,dz=abs(hl.x);
  float h=kb.x+hl.x; vec2 g=kb.yz+hl.yz;
  vec3 ns=normalize(vec3(-g.x*1.6,1.,-g.y*1.6));

  Vurus P=izle(ro,rd,tp+3.);
  vec3 bp=ro+rd*P.t;
  float hd=P.i>=0?bp.y-yukseklik(bp.xz):1.;

  // Sakin bir yuzeyden yansima: halkalar titretir, kabarma pek egmez.
  vec3 nr=normalize(vec3(-(kb.y*.3+hl.y*1.2),1.,-(kb.z*.3+hl.z*1.2)));
  vec3 rdY=reflect(rd,nr);
  Vurus Y=izle(wp+nr*.01,rdY,6.);
  vec3 yp=wp+rdY*Y.t;
  float yans=Y.i>=0&&yp.y>yukseklik(yp.xz)?1.:0.;

  // Tarama koordinatlari, turevler butun pikselde ayni akista alinsin diye burada.
  vec3 c=vec3((P.q.x*.75+P.q.y)*46.,(P.q.x-P.q.y*.7)*46.,P.q.z*40.);
  vec3 fw=fwidth(c);
  float fwHd=fwidth(hd);

  // ---- su ----
  float sis=(1.-smoothstep(14.,34.,z))*step(rd.y,-1e-4);
  // Yukseklik seridi oransal kaydirir; uzakta kucuk kalir, ufuk damarlanmaz.
  float serit=-105.*pow(z,-.6)*(1.+h*.6)-hl.x*70.;
  float fwS=fwidth(serit);
  float k=floor(serit+.5),tohum=karma(k*1.37+.31);
  float s=w.x/pow(z,.8)*7.+zaman*(tohum-.5)*.45;
  float n=gurultu(s*.8+tohum*91.)*.65+gurultu(s*2.4+tohum*13.)*.35;
  float esik=mix(.92,.42,sis);
  float kesik=smoothstep(esik-.02,esik+.02,n);
  float serCiz=(1.-smoothstep(.5*oran-.5,.5*oran+.5,abs(fract(serit+.5)-.5)/fwS))*kesik*(1.-smoothstep(.3,.6,fwS))*sis;
  float on=clamp(-ns.z*6.,0.,1.);
  vec3 ton=mix(KAGIT,mix(MAVI,DERIN,on*.7),serCiz*.85);

  // Dalga tepeleri ince halka cizgisi olarak; sadece su hareketliyken.
  float fwF=fwidth(faz/6.2832);
  float tepe=cizgi(faz/6.2832,fwF*.8,fwF)*(1.-smoothstep(.3,.6,fwF))*smoothstep(.0005,.003,dz)*sis;
  ton=mix(ton,DERIN,tepe*.9);

  // Su altinda kalan kisim: soluk mavi, derinlestikce kaybolur.
  if(P.i>=0&&hd<0.){
    mat3 R=lrot[P.i]; vec3 nl=normal(P.q);
    vec2 gv=gravur(nl,R*nl,rd,c,fw);
    ton=mix(ton,MAVI,gv.x*.4*(1.-smoothstep(0.,.3,-hd)));
  }

  // Yansima: logonun tonunu ince, titreyen yatay vuruslarla tasir.
  if(yans>0.){
    mat3 R=lrot[Y.i]; vec3 nl=normal(Y.q),nw=R*nl;
    float koyu=clamp(1.-max(dot(nw,normalize(ISIK)),0.)*1.2,0.,1.);
    float yt=(.25+.75*pow(koyu,1.2))*(1.-smoothstep(.1,1.4,Y.t)*.75);
    float rl=serit*3.;
    float fwr=fwidth(rl);
    float ara=gurultu(w.x*6./sqrt(z)+karma(floor(rl+.5)*.71)*60.+zaman*(karma(floor(rl+.5))-.5)*1.4);
    float v=cizgi(rl,max(.32*yt,fwr*.35),fwr)*smoothstep(.15,.25,ara+yt*.15)*(1.-smoothstep(.35,.7,fwr));
    ton=mix(ton,DERIN,v*.8);
  }

  // Siluet: isin logoya ucundan degip gectiyse murekkep (sadece su ustunde).
  float ustte=P.enYakin<1.?step(yukseklik(P.enYakinP.xz),P.enYakinP.y):0.;
  float pw=length(P.enYakinP-ro)*pAci;
  ton=mix(ton,MUREKKEP,(1.-smoothstep(pw*.35,pw*1.2,P.enYakin))*ustte*step(P.enYakin,1.));

  // ---- logo ----
  if(P.i>=0&&hd>0.){
    mat3 R=lrot[P.i]; vec3 nl=normal(P.q),nw=R*nl;
    vec2 gv=gravur(nl,nw,rd,c,fw);
    // Su cizgisinin hemen ustu islak: biraz daha koyu.
    gv.x=max(gv.x,cizgi(c.x,.3,fw.x)*(1.-smoothstep(0.,.05,hd))*.6);
    vec3 m=mix(MUREKKEP,DERIN,gv.y);
    vec3 l=mix(KAGIT,m,gv.x);
    l=mix(l,MUREKKEP,1.-smoothstep(fwHd*.3,fwHd,abs(hd)));
    ton=mix(l,KAGIT,smoothstep(14.,30.,bp.z)*.6);
  }

  renk=vec4(ton,1.);
}
`;

  function derle(tur, kaynak) {
    var s = gl.createShader(tur);
    gl.shaderSource(s, kaynak);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
    return s;
  }
  var prog = gl.createProgram();
  try {
    gl.attachShader(prog, derle(gl.VERTEX_SHADER, KOSE));
    gl.attachShader(prog, derle(gl.FRAGMENT_SHADER, PARCA));
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(prog));
  } catch (e) {
    console.error(e);
    tuval.style.display = "none";
    return;
  }
  gl.useProgram(prog);

  var tampon = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, tampon);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  var ap = gl.getAttribLocation(prog, "p");
  gl.enableVertexAttribArray(ap);
  gl.vertexAttribPointer(ap, 2, gl.FLOAT, false, 0, 0);

  var U = {};
  ["coz", "zaman", "tanY", "oran", "kam", "ileri", "yukari", "lpos", "lrot", "dalga"].forEach(function (a) {
    U[a] = gl.getUniformLocation(prog, a);
  });
  gl.uniform1f(U.tanY, TAN);
  gl.uniform3fv(U.kam, KAM);
  gl.uniform3fv(U.ileri, ILERI);
  gl.uniform3fv(U.yukari, YUKARI);

  // Shader'daki kabarma()'nin ikizi: logolar ayni dalgaya binsin.
  function kabarma(x, z, t) {
    var a0 = (x * 0.42 + z * 0.91) * 1.1 - t * 1.2;
    var a1 = (x * -0.75 + z * 0.66) * 1.6 - t * 1.5 + 1.3;
    var a2 = (x * 0.15 + z * 0.99) * 2.7 - t * 2.1 + 4;
    var h = 0.045 * Math.sin(a0) + 0.028 * Math.sin(a1) + 0.014 * Math.sin(a2);
    var gx = 0.045 * 1.1 * Math.cos(a0) * 0.42 + 0.028 * 1.6 * Math.cos(a1) * -0.75 + 0.014 * 2.7 * Math.cos(a2) * 0.15;
    var gz = 0.045 * 1.1 * Math.cos(a0) * 0.91 + 0.028 * 1.6 * Math.cos(a1) * 0.66 + 0.014 * 2.7 * Math.cos(a2) * 0.99;
    return [h, gx, gz];
  }

  function carp(A, B) {
    var C = [];
    for (var r = 0; r < 3; r++) for (var c = 0; c < 3; c++) {
      C[r * 3 + c] = A[r * 3] * B[c] + A[r * 3 + 1] * B[3 + c] + A[r * 3 + 2] * B[6 + c];
    }
    return C;
  }
  function donY(a) { var c = Math.cos(a), s = Math.sin(a); return [c, 0, s, 0, 1, 0, -s, 0, c]; }
  function donX(a) { var c = Math.cos(a), s = Math.sin(a); return [1, 0, 0, 0, c, -s, 0, s, c]; }
  function donZ(a) { var c = Math.cos(a), s = Math.sin(a); return [c, -s, 0, s, c, 0, 0, 0, 1]; }

  var pos = new Float32Array(N * 4), rot = new Float32Array(N * 9), en = 1, boy = 1;
  var onceki = null;

  function guncelle(t, dt) {
    var yariEn = TAN * en / boy;
    // Logolar ust uste binmesin: yakinlasan cift birbirini hafifce iter.
    for (var a = 0; a < N; a++) for (var b = a + 1; b < N; b++) {
      var A = LOGOLAR[a], B = LOGOLAR[b], dx = B.x - A.x, dz = B.z - A.z, d = Math.hypot(dx, dz);
      if (d > 1.4 || d < 1e-3) continue;
      var f = (1.4 - d) * 1.5 * dt;
      A.vx = (A.vx || 0) - dx / d * f; A.vz = (A.vz || 0) - dz / d * f;
      B.vx = (B.vx || 0) + dx / d * f; B.vz = (B.vz || 0) + dz / d * f;
    }
    LOGOLAR.forEach(function (L, i) {
      // Gorunen genisligin disina cikan logo obur taraftan girer.
      var sinir = L.z * yariEn + 1.2;
      // Dalga itisi zamanla soner; logo derinlikte seridin icinde kalir.
      var sur = Math.exp(-dt * 0.8);
      L.vx = (L.vx || 0) * sur; L.vz = (L.vz || 0) * sur;
      // Tutulan logo imlecin su ustundeki noktasina yay gibi cekilir; birakinca bu hizla firlar.
      if (L === tutulan && hedef) {
        L.vx = Math.max(-4, Math.min(4, (hedef[0] - L.x) * 10)) - L.hiz;
        L.vz = Math.max(-4, Math.min(4, (hedef[1] - L.z) * 10));
      }
      L.x += (L.hiz + L.vx) * dt;
      L.z = Math.min(Math.max(L.z + L.vz * dt, 3.8), 20);
      if (L !== tutulan && L.x > sinir) L.x -= 2 * sinir;
      if (L !== tutulan && L.x < -sinir) L.x += 2 * sinir;
      // Batma bir yay gibi: asagi itilir, salinarak yerine doner.
      // Tutulan sudan kalkar, ustune gelinen biraz batar.
      var hedefY = L === tutulan ? 0.3 : L === ustteki ? -0.03 : 0;
      L.vy = ((L.vy || 0) + (-14 * ((L.dy || 0) - hedefY) - 3 * (L.vy || 0)) * dt);
      L.dy = (L.dy || 0) + L.vy * dt;
      L.ekDon = (L.ekDon || 0) + (L.donHiz || 0) * dt;
      L.donHiz = (L.donHiz || 0) * Math.exp(-dt * 0.7);
      var k = kabarma(L.x, L.z, t);
      // Yuzey egimini yumusatarak izle: hafif nesne gibi gecikmeli yatar.
      var yumusak = 1 - Math.exp(-dt * 3);
      L.yat = (L.yat || 0) + (Math.atan(k[1]) * 1.6 - (L.yat || 0)) * yumusak;
      L.dik = (L.dik || 0) + (-Math.atan(k[2]) * 1.6 - (L.dik || 0)) * yumusak;
      var yaw = (L.don ? t * L.don + L.faz : 0.45 * Math.sin(t * 0.13 + L.faz)) + (L.ekDon || 0);
      // Tasinirken gidis yonune, ustune gelininca imlecten uzaga yatar.
      var egHedef = L === tutulan ? -(L.vx || 0) * 0.08 : L === ustteki ? ustYon * 0.22 : 0;
      L.egik = (L.egik || 0) + (egHedef - (L.egik || 0)) * (1 - Math.exp(-dt * 6));
      var R = carp(donY(yaw), carp(donX(L.dik), donZ(L.yat + L.egik)));
      pos.set([L.x, k[0] + 0.24 + 0.012 * Math.sin(t * 1.3 + L.faz) + (L.dy || 0), L.z, 0], i * 4);
      rot.set([R[0], R[3], R[6], R[1], R[4], R[7], R[2], R[5], R[8]], i * 9);
    });
  }

  function ciz(t, dt) {
    guncelle(t, dt);
    gl.uniform1f(U.zaman, t);
    gl.uniform4fv(U.lpos, pos);
    gl.uniformMatrix3fv(U.lrot, false, rot);
    gl.uniform4fv(U.dalga, dalgaVeri);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }

  function olc() {
    var oran = Math.min(window.devicePixelRatio || 1, 2), k = tuval.getBoundingClientRect();
    en = Math.round(k.width * oran); boy = Math.round(k.height * oran);
    tuval.width = en; tuval.height = boy;
    gl.viewport(0, 0, en, boy);
    gl.uniform2f(U.coz, en, boy);
    gl.uniform1f(U.oran, oran);
  }

  // Dalga tamponu: x, z, baslangic ani, guc. Bos yuva gucu 0 oldugu icin iz birakmaz.
  var dalgaVeri = new Float32Array(D * 4), dalgaSira = 0, simdi = 20;

  // Imlec konumu, shader'in uv uzayinda (dikey -1..1).
  function ekranUv(e) {
    var k = tuval.getBoundingClientRect(), oran = en / k.width;
    return [(2 * (e.clientX - k.left) * oran - en) / boy, (2 * (k.bottom - e.clientY) * oran - boy) / boy];
  }

  // Ekrandaki noktayi su duzlemine indir; ufkun ustundeyse null.
  function suyaIndir(e) {
    var uv = ekranUv(e), ux = uv[0], uy = uv[1];
    var dx = ux * TAN, dy = ILERI[1] + uy * TAN * YUKARI[1], dz = ILERI[2] + uy * TAN * YUKARI[2];
    if (dy >= -1e-3) return null;
    var t = -KAM[1] / dy;
    return [dx * t, dz * t];
  }

  function dalgaAt(p, guc) {
    dalgaVeri.set([p[0], p[1], simdi, guc], dalgaSira * 4);
    dalgaSira = (dalgaSira + 1) % D;
  }

  // Tiklama: guclu dalga, yakindaki logolari iter, batirir, dondurur.
  function vur(p) {
    dalgaAt(p, 1);
    LOGOLAR.forEach(function (L) {
      var dx = L.x - p[0], dz = L.z - p[1], d = Math.sqrt(dx * dx + dz * dz) + 0.3;
      var f = Math.exp(-d * 0.7);
      L.vx = (L.vx || 0) + dx / d * f * 0.8;
      L.vz = (L.vz || 0) + dz / d * f * 0.8;
      L.vy = (L.vy || 0) - f * 1.2;
      L.donHiz = (L.donHiz || 0) + (dx > 0 ? 1 : -1) * f * 2.5;
    });
  }

  // Imlecin altindaki en yakin logo. Merkezin izdusumu ve yaricapi yeter; isin izlemeye gerek yok.
  function logoBul(e) {
    var uv = ekranUv(e), bulunan = null, enYakin = 1e9;
    LOGOLAR.forEach(function (L, i) {
      var vy = pos[i * 4 + 1] - KAM[1], vz = L.z - KAM[2];
      var derin = vy * ILERI[1] + vz * ILERI[2];
      var sx = (L.x - KAM[0]) / derin / TAN, sy = (vy * YUKARI[1] + vz * YUKARI[2]) / derin / TAN;
      if (Math.hypot(uv[0] - sx, uv[1] - sy) < 0.5 / derin / TAN && derin < enYakin) { bulunan = L; enYakin = derin; }
    });
    return bulunan;
  }

  var sonIz = 0, sonNokta = null, tutulan = null, hedef = null, ustteki = null, ustYon = 0;
  tuval.addEventListener("pointermove", function (e) {
    var p = suyaIndir(e);
    if (tutulan) {
      if (p) hedef = p;
      if (simdi - sonIz > 0.09) { dalgaAt([tutulan.x, tutulan.z], 0.5); sonIz = simdi; }
      return;
    }
    ustteki = logoBul(e);
    if (ustteki) ustYon = p && p[0] > ustteki.x ? -1 : 1;
    tuval.style.cursor = ustteki ? "grab" : "";
    if (!p) return;
    // Imlec yolunda iz: cok sik birakilirsa halkalar ust uste biner.
    var yol = sonNokta ? Math.hypot(p[0] - sonNokta[0], p[1] - sonNokta[1]) : 1;
    if (simdi - sonIz > 0.09 && yol > 0.15) { dalgaAt(p, 0.35); sonIz = simdi; sonNokta = p; }
  });
  tuval.addEventListener("pointerdown", function (e) {
    var L = logoBul(e);
    if (L) {
      tutulan = L; ustteki = null;
      hedef = suyaIndir(e) || [L.x, L.z];
      tuval.setPointerCapture(e.pointerId);
      tuval.style.cursor = "grabbing";
      return;
    }
    var p = suyaIndir(e);
    if (p) vur(p);
  });
  // Birakilan logo suya duser: dustugu yerde dalga.
  function birak() {
    if (!tutulan) return;
    dalgaAt([tutulan.x, tutulan.z], 0.9);
    tutulan = null; hedef = null;
    tuval.style.cursor = "";
  }
  tuval.addEventListener("pointerup", birak);
  tuval.addEventListener("pointercancel", birak);
  tuval.addEventListener("pointerleave", function () { ustteki = null; });

  var sabit = matchMedia("(prefers-reduced-motion: reduce)").matches, gorunur = true, baslangic = null;

  function dongu(an) {
    if (baslangic === null) baslangic = an;
    var t = (an - baslangic) / 1000 + 20;
    simdi = t;
    var dt = onceki === null ? 0 : Math.min((an - onceki) / 1000, 0.1);
    onceki = an;
    if (gorunur && !document.hidden) ciz(t, dt);
    requestAnimationFrame(dongu);
  }

  new ResizeObserver(function () { olc(); if (sabit) ciz(20, 0); }).observe(tuval);
  new IntersectionObserver(function (e) { gorunur = e[0].isIntersecting; }).observe(tuval);
  if (!sabit) requestAnimationFrame(dongu);
})();
