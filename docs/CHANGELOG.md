# Changelog — Topiome

Tüm önemli değişiklikler burada. Format: [Keep a Changelog](https://keepachangelog.com/), sürümleme: SemVer.

## [Unreleased] — 2026-11-06

### Added

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
- GEO tarzı önekli/iç içe klasörler; `.zip` / `.tar.gz` / `.tgz` / `.tar` çıkarma (path traversal korumalı)
- `.h5` doğrudan yükleme; yükleme doğrulaması arşiv veya parça dosyaları kabul eder
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

### Changed
- Glio-Cartography adı ve GBM-only kapsamı terk edildi; hastalıktan bağımsız platforma geçildi
- Viewer rolü salt okunur (proje/örnek/run oluşturamaz, rapor onaylayamaz)
- GBM paketinde IDH1/MGMT açıklamaları: RNA düzeyinin mutasyon/metilasyonu göstermediği açıkça yazıldı
- Pipeline sürümü `0.3.0-baseline` (Visium reader + referans/GNN entegrasyonu)
- `docs/ARCHITECTURE.md`, `docs/DEPLOY.md`, `README.md` kuyruk ve dağıtım gerçeklerine göre güncellendi

### Fixed
- `next build` exFAT'ta Turbopack önbelleği yüzünden düşüyordu
- ESLint yapılandırması (Next 16 flat config) ve 15 React hooks hatası
- İptal edilen run, arka plan işi bitince "succeeded" olarak üzerine yazılabiliyordu
- Depolama kökü sembolik bağlantı üzerindeyse tüm dosya yolları reddediliyordu
- API tarihleri saat dilimi olmadan dönüyordu; arayüzde 3 saat kayma vardı
- Docker API imajında exFAT 0700 izinleri nedeniyle `USER topiome` uygulamayı okuyamıyordu; `COPY --chown` ile düzeltildi
- Docker BuildKit exFAT `._*` dosyalarında xattr hatası veriyordu; temiz build bağlamı ve `.dockerignore` ile giderildi

### Security
- httpOnly cookie auth, Argon2id, org bazlı izolasyon, audit log
- Üretimde demo login kapalı; zayıf ayarlarla API başlamaz
- Login throttling ve origin kontrolü
- Rapor onay kapısı ve audit'li dışa aktarma
- Bilinen sınırlar: register throttling yok, MFA/SSO yok, queue retry yok, throttle süreç başına

### Known limitations
- **Breast pack beta:** held-out ARI 0.260 < 0.35; tek çalışma/tek merkez (Wu 2021), 6 hasta
- **GBM pack beta:** Ivy GAP ile uyum negatif; eğitilmiş GBM referansı/domain modeli yok
- Diğer paketler draft; bağımsız held-out doğrulama yok
- Gerçek kamu örneği API/UI upload üzerinden henüz uçtan uca koşulmadı (reader script ile koşuldu)
- PDF rapor yok (tarayıcıdan yazdır); Stripe/S3/SMTP entegrasyonları yok
