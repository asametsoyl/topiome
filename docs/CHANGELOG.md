# Changelog — Topiome

Tüm önemli değişiklikler burada. Format: [Keep a Changelog](https://keepachangelog.com/), sürümleme: SemVer.

## [Unreleased] — 2026-11-07

### 2026-11-07 — Ürün yönü araştırma önizlemesine çevrildi

- Topiome adı korunarak araştırma odağı single-cell perturbation-response tahmini fizibilitesine çevrildi; yeni yönde henüz model veya sonuç bulunmadığı sayfada açık.
- Landing, docs, RUO, pricing ve kayıt akışları araştırma önizlemesi oldu; kayıt/fiyat/ürün erişimi iddiaları durduruldu. Eski workspace legacy uyarısı gösteriyor.
- Eski spatial public/processed yerel verisinden yaklaşık 9.2 GB temizlendi; küçük tarihsel validasyon raporları `docs/legacy/spatial/validation/` altında korundu.
- İlk veri seçimi öncesi lisans, metadata ve split kontrolü yapıldı; güncel deneme ve kısıtları aşağıdaki baseline kaydı açıklıyor.
- Eski spatial yönün mimari/validasyon belgeleri yeni araştırma planından ayrıştırıldı; çalışma kaydı ve ADR-029 eklendi.
- Arc VCC 2025 / PIE'dan 49.3 MB ön işlenmiş aggregate etki verisi alındı ve kaynak hash'leri doğrulandı; 146/44 unseen-target split'te zero ve gen-ortalaması baseline'ları çalıştırıldı. Ham 15.5 GB hücre matrisi alınmadı.
- İlk baseline raporu ve tekrarlanabilir runner eklendi; yalnız tek H1 bağlamındaki population-level etkileri değerlendirir, model veya single-cell validation iddiası içermez.

### 2026-11-07 — Replogle-Nadig görülmemiş-bağlam kapısı ve negatif perturbasyon kontrolü

- PIE Replogle-Nadig essential Perturb-seq preprocessed array'leri ve PIE canonical split'leri indirildi; 5.459 satır, 6.642 gen, 4 hücre hattı, 1.857 perturbasyon. Split satırları, bağlam izolasyonu ve test perturbasyon kapsaması doğrulandı.
- Ön kayıtlı görülmemiş-bağlam transfer kapısı HepG2/Jurkat/RPE1 fold'larında 3/3 geçti; beta 0,25/0,25/0,30, RMSE iyileşmesi %4,34/%5,84/%4,56, medyan korelasyon 0,357/0,441/0,386. Bootstrap aralıkları zero ve global mean'e göre sıfırın üstünde. K562 keşifsel fold da geçti.
- `analysis.perturbation` benchmark modülü, 9 test ve `scripts/perturbation/benchmark_replogle_transfer.py` eklendi; sonuç `data/perturbation/processed/replogle-unseen-ctx-gate.json`.
- Görülmemiş-perturbasyon keşifsel kontrolü negatif: ESM2/STRING/DepMap ridge ve kNN, bağlam ortalamasını RMSE+korelasyon+top-50 birlikte geçmedi; bu veri/görevde model karmaşıklığını artırma durduruldu. Çıktı `data/perturbation/processed/replogle-unseen-pert-exploratory.json`.
- Sınır: basit ölçekli transfer bir Topiome modeli değil; görülmemiş perturbasyon, tek hücre dağılımı, prospektif deney veya ticari kullanım kanıtı yok. PIE/PIE_sources lisans alanları boş; yalnız araştırma.

### Added

- Wu 2021 GNN hasta split'i için alias dahil sızıntı/eksik katılımcı koruması ve hedefli testler. Zenodo 10.5281/zenodo.18917100 kaydının AnnData + patolog anotasyonu içeren 33 kesit / 32 kişi dış meme kohortu olduğu doğrulandı; lisansı/atıfı boş olduğundan kullanım beklemeye alındı.
- Hazır GNN incelemesi: Novae ağırlıklarının spot-tabanlı Visium için hazır olmadığı netleştirildi; GraphST/STAGATE/Novae yöntemleri yalnızca adil benchmark baseline'ı olarak değerlendirilecek.
- Kamuya açık Visium envanterinde MTX ve H5 matrislerini birlikte okuyabilme.
- Resmî ürün sayfalarına dayalı rakip analizi ve Topiome viewer/bilimsel güven öncelikleri (`docs/COMPETITIVE_ANALYSIS.md`).
- Henüz geçilmemiş validasyon kapıları nedeniyle ürün tanımındaki “validated atlas” iddiası kaldırılıp “transparent, reproducible atlas” olarak düzeltildi.
- Spatial viewer: gerçek Visium dosyasından barkodla eşleşen tek-gen log1p(CP10K) katmanı; serbest ROI seçimi, QC/belirsizlik/domain özeti ve rapor onayı + audit log arkasında CSV dışa aktarımı.
- İki run karşılaştırmasında assay/tür/koşul uyumsuzluğu uyarıları ve yan yana doku haritaları; onaylı rapor sonrası audit'li PNG harita export'u.
- İki-run spatial kıyasında bir haritada seçilen genin diğerine de yüklenmesi; iki log1p(CP10K) haritası ortak renk ölçeğini kullanır ve görsel kıyasın istatistiksel test olmadığı açıklanır (ADR-027).
- ROI içi/dışı genleri normalize ortalama ve algılanma farkıyla sıralayan betimleyici analiz; spotlar bağımsız tekrar sayılmadığı için p-değeri/FDR üretilmiyor.
- Gen ekspresyon katmanında eşik slider'ı ve eşiği geçen ifade-pozitif spotları tek tıkla ROI seçimine alma.
- ROI ile arka plan arasındaki QC-pass hücre kompozisyonu yüzdelik farklarını gösterme.
- İlk Visium HD okuyucu dilimi: `square_016um` H5 + Parquet tissue positions eşlemesi, 12.000 spot bellek sınırı ve 2/8 µm binleri için anlaşılır ret (ADR-026). Tiled/tam ölçek HD analizi henüz yok.

#### Ürünleşme
- Workspace davetleri ve davet kabul ekranı; üye rolü değiştirme/çıkarma ve pending davetleri iptal etme
- TOTP MFA kurulum, recovery code ve giriş akışı
- Organization API key yönetim uçları ve analyst-seviyesi API key erişimi
- Plan kullanım kotaları, Stripe Checkout/webhook ve settings ekranında kullanım durumu
- S3 uyumlu storage, süreli signed URL, run retry/backoff, Redis tabanlı paylaşımlı rate limit
- SMTP davet ve analiz tamamlanma/başarısızlık bildirimleri
- KVKK/GDPR/DPA, saklama politikası, alt işleyici ve veri sınıflandırma taslakları

#### Ürün ve analiz
- Faz 1 iskeleti: monorepo, dokümantasyon, ajan hafızası (`AGENTS.md`, `docs/STATUS.md`)
- Marka çalışma adı: Topiome
- Ürün, mimari, validasyon, güvenlik, iş modeli, marka, yol haritası dokümanları
- 6 hastalık paketi (breast, colorectal, lung, melanoma, prostate, glioblastoma)
- Next.js 16 + Tailwind 4 web uygulaması: marketing, auth, dashboard, proje/örnek/run, spatial viewer, rapor
- FastAPI + SQLAlchemy API: auth, org izolasyonu, projeler, örnekler, run'lar, raporlar
- Analiz motoru baseline: QC, NNLS + marker-score dekonvolüsyon, spatial smoothing, domain clustering, hedef skorlama, belirsizlik
- Sentetik demo verisi ve demo hesap
- Rapor onayı: taslak bandı, RUO onay kutusu, onaylayan/not kaydı; yalnızca onaylı rapor dışa aktarılır ve her dışa aktarma audit log'a yazılır
- Run provenance: paket SHA-256, referans/domain model sürümü + SHA-256, girdi dosyası hash'leri, parametreler, yazılım sürümleri ve commit
- Glio-Cartography'den: yöntemler arası uyum, uzamsal ligand–reseptör analizi (BH-FDR), Ivy GAP atlas kontrolü, "Not assessed" sınırları
- Paketler: breast v0.3.0; colorectal/GBM v0.2.0 beta; lung/melanoma/prostate v0.2.0 draft
- Alembic migration'ları; mevcut dev veritabanı açılışta otomatik yükseltilir
- İki run karşılaştırma: `/app/runs/compare` ve `GET /api/v1/runs/compare?a=&b=`

#### Gerçek Visium / Space Ranger
- `.h5` (v2/v3) ve `.mtx` + `barcodes` + `features`/`genes` okuyucu
- Headered ve legacy `tissue_positions`; `scalefactors_json.json` ve doku görüntüsü keşfi
- Run haritasında H&E hires görüntü üstü spot katmanı; same-org korumalı görüntü endpoint'i, ölçek başlığı ve aç/kapat kontrolü
- Sıkıştırılmış `.csv.gz` pozisyon, `.json.gz` scale-factor ve `.png.gz` tissue image keşfi
- GEO tarzı önekli/iç içe klasörler; `.zip` / `.tar.gz` / `.tgz` / `.tar` çıkarma (path traversal korumalı)
- `.h5` doğrudan yükleme; yükleme doğrulaması arşiv veya parça dosyaları kabul eder
- Next.js → FastAPI catch-all proxy istek/yanıt gövdelerini akışlı taşır; 10 MB rewrite kesilmesi kaldırıldı (ADR-020)
- QC tam matris üzerinde; gen ön seçimi QC ve kütüphane boyutunu değiştirmez
- `n_genes` (ölçülen toplam) ve `n_genes_loaded` (modele yüklenen) ayrımı
- exFAT `._*` / `.DS_Store` filtresi ve arşiv güvenlik kontrolleri

#### Referanslar ve domain modeli
- Wu et al. 2021 meme scRNA referansı (`breast_wu2021_v1`): 408 gen, 8 hücre tipi, yalnız eğitim hastaları; CID4465/CID4535 hariç
- Wu 2021 Visium + patolog etiketleriyle hasta düzeyi split (4 eğitim / 2 test)
- 2 katmanlı GraphSAGE domain modeli (`breast_domain_gnn_v1`), sıcaklık kalibrasyonu, NumPy çıkarımı
- Model kartı, ağırlıklar ve doğrulama raporu (`docs/validation/breast-wu2021.md`)
- Pipeline gerçek örnekte modeli uygular; sentetik veride ve gen kapsamı < %80'de uyarıyla atlar
- GBM gerçek veri kontrolü (`docs/validation/gbm-gse331374.md`): GSE331374, 2.930 spot, 2.727 QC-pass, Ivy GAP diagonal −0.179 / top-1 0.0 (olumsuz)

#### Üretim / güvenlik
- DB tabanlı run kuyruğu: `QUEUE_MODE=inline` (dev) / `worker` (prod), atomik sahiplenme, kesinti kurtarma, `RUN_TIMEOUT_HOURS`
- `python -m app.worker` döngü/`--once`, SIGTERM/SIGINT ile güvenli çıkış; çoklu worker güvenli
- Docker: API + worker aynı imaj, Next.js standalone web imajı, compose (db/api/worker/web), healthcheck ve volume'lar
- Postgres advisory lock ile eşzamanlı migration koruması
- Üretim ayar kapıları (zayıf secret, SQLite, açık demo login, geçersiz queue modu → açılmayı reddet)
- Giriş throttling (IP + e-posta 15 dk / 10; IP başına 50 başarısız), `429` + `Retry-After`
- Origin kontrolü, CORS, güvenlik başlıkları, üretimde `Secure` httpOnly cookie
- Tarayıcı smoke testi (8 kontrol) ve üretim compose E2E (kayıt → run → worker → sonuç → rapor)
- Kalıcı Playwright E2E: sentetik run ve isteğe bağlı gerçek GEO örneği UI upload/run kontrolü

### Changed
- GNN planı: beş kanserde otomatik ayrı model eğitimi yerine etiket/harici kohort kapısı ve grafsız baseline ablation (ADR-021)
- Gerçek GBM haritasında marker grupları artık daha ayrışan renklerle eşzamanlı gösteriliyor; varsayılan katman “baskın marker grubu” ve açıkça kalibre hücre oranı/ince hücre alt tipi olmadığı belirtiliyor.
- Ligand–reseptör görselinde seçilen çiftin BH düzeltilmiş q-değeri ve anlamlılık sonucu gösteriliyor.
- Dokümantasyon validasyon ve hastalık paketi tablolarındaki sentetik başarı metrikleri, gerçek held-out meme sonuçları ve paketlerin mevcut kanıt durumuyla değiştirildi.
- Pricing/docs'taki kullanıcı `.h5ad` yüklemesinin hazır olduğunu söyleyen metin düzeltildi; bu özellik bugün UI/API akışında yok ve tek hücre referansı yükleme sonraki ürün dilimi olarak kaydedildi.
- Arayüz beyaz/paper tasarım sistemine geçirildi; marketing atlas kartı sentetik harita yerine kamu GBM örneğinin gerçek özetini, yöntem kısıtını ve beta durumunu gösteriyor.
- Demo login ve sentetik örnek oluşturma UI akışı kaldırıldı. Var olan sentetik demo projeleri/örnekleri geri alınabilir şekilde arşivlendi; audit ve eski raporlar korunuyor.
- Marketing/dashboard breast metrikleri sentetik başarı örneği yerine held-out Wu 2021 sonuçlarını ve geçilmeyen ARI/Macro-F1 kapılarını gösteriyor.
- Glio-Cartography adı ve GBM-only kapsamı terk edildi; hastalıktan bağımsız platforma geçildi
- Viewer rolü salt okunur (proje/örnek/run oluşturamaz, rapor onaylayamaz)
- GBM paketinde IDH1/MGMT açıklamaları: RNA düzeyinin mutasyon/metilasyonu göstermediği açıkça yazıldı
- Pipeline sürümü `0.3.0-baseline` (Visium reader + referans/GNN entegrasyonu)
- Gerçek örneklerde sentetik benchmark metrik kartı gösterilmez; boş `metrics` nesnesinin SpatialMap'i çökertmesi düzeltildi
- `docs/ARCHITECTURE.md`, `docs/DEPLOY.md`, `README.md` kuyruk ve dağıtım gerçeklerine göre güncellendi

### Fixed
- Gerçek Visium haritasında spot koordinatlarına `tissue_hires_scalef` ikinci kez uygulanıyordu; ölçek çarpanı kaldırıldı ve y-up analiz koordinatı görselin y-down eksenine doğru çevrildi. GBM kamu örneğinde spotlar H&E dokusuna tarayıcıda hizalandı.
- Marker-group katmanında eskiden tek renkli, birbirine yakın renkli grup seçimi yerine legend'i olan çok renkli baskın grup haritası varsayılan hale getirildi; marker-score'ların gerçek dekonvolüsyon/hücre oranı gibi okunması engellendi.
- Gerçek run doğrulama görünümünde boş `{}` metrics nesnesi benchmark varmış gibi ele alınıp hata veriyordu; artık bağımsız etiket yoksa “No benchmark available” görünür.
- `next build` exFAT'ta Turbopack önbelleği yüzünden düşüyordu
- ESLint yapılandırması (Next 16 flat config) ve 15 React hooks hatası
- İptal edilen run, arka plan işi bitince "succeeded" olarak üzerine yazılabiliyordu
- Depolama kökü sembolik bağlantı üzerindeyse tüm dosya yolları reddediliyordu
- API tarihleri saat dilimi olmadan dönüyordu; arayüzde 3 saat kayma vardı
- Docker API imajında exFAT 0700 izinleri nedeniyle `USER topiome` uygulamayı okuyamıyordu; `COPY --chown` ile düzeltildi
- Docker BuildKit exFAT `._*` dosyalarında xattr hatası veriyordu; temiz build bağlamı ve `.dockerignore` ile giderildi
- Rewrite proxy 10 MB üstü upload gövdesini kesiyordu; 13 MB kamu Visium örneği akışlı Route Handler ile başarıyla yüklendi ve analiz edildi

### Security
- httpOnly cookie auth, Argon2id, org bazlı izolasyon, audit log
- Üretimde demo login kapalı; zayıf ayarlarla API başlamaz
- Login throttling ve origin kontrolü
- Rapor onay kapısı ve audit'li dışa aktarma
- API anahtarları analyst rolüyle sınırlandırıldı; owner/admin/billing/MFA ayarları interaktif oturum gerektirir
- MFA TOTP secret'ı şu an DB'de şifrelenmeden tutulur; üretim öncesi at-rest uygulama şifrelemesi gereklidir
- Bilinen sınırlar: register throttling yok, MFA/SSO yok, queue retry yok, throttle süreç başına

### Known limitations
- **Breast pack beta:** held-out ARI 0.260 < 0.35; tek çalışma/tek merkez (Wu 2021), 6 hasta
- **GBM pack beta:** Ivy GAP ile uyum negatif; eğitilmiş GBM referansı/domain modeli yok
- Diğer paketler draft; bağımsız held-out doğrulama yok
- PDF rapor yok (tarayıcıdan yazdır); Stripe/S3/SMTP entegrasyonları yok

### 2026-11-06 — Kamu Visium kohort envanteri
- Envanter, GEO seri düzeyinde ortak MTX feature/barcode dosyalarını, ayrı spatial klasörlerini ve flat H5 + `spatial.tar` çiftlerini destekliyor.
- `._*` AppleDouble dosyaları sidecar keşfinden dışlandı; geçici arşiv çıkarımı güvenli filtre ile yapılıyor. Manifestte matris/pozisyon ve mevcut sidecar SHA-256 değerleri yazılıyor.
- Gerçek okuyucu envanteri: 78 kesit ve 196.880 doku spotu; 1 bozuk melanom H5 hariç. Beş ana hastalıkta 77 kesit: meme 6, CRC 12, akciğer 40, prostat 5/52, melanom 14/15.
- Veri örneği testi eklendi: exFAT sidecar'ı seçilmez; tekil GEO seri düzeyi sidecar ile MTX örneği yüklenir.
