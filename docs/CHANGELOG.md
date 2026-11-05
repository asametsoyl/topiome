# Changelog — Topiome

Tüm önemli değişiklikler burada. Format: [Keep a Changelog](https://keepachangelog.com/), sürümleme: SemVer.

## [Unreleased]

### Added
- Faz 1 iskeleti: monorepo, dokümantasyon, ajan hafızası (`AGENTS.md`, `docs/STATUS.md`)
- Marka çalışma adı: Topiome
- Ürün, mimari, validasyon, güvenlik, iş modeli, marka, yol haritası dokümanları
- 6 hastalık paketi planı (breast, colorectal, lung, melanoma, prostate, glioblastoma)
- Next.js 16 + Tailwind 4 web uygulaması iskeleti
- FastAPI + SQLAlchemy API iskeleti
- Analiz motoru baseline (NNLS + spatial smoothing + clustering + uncertainty)
- Sentetik demo verisi ve demo hesap
- Marketing landing page, auth, dashboard, proje/örnek/run akışı, spatial viewer, rapor

- Rapor onayı: taslak bandı, RUO onay kutusu, onaylayan/not kaydı; yalnızca onaylı rapor dışa aktarılır ve her dışa aktarma audit log'a yazılır
- Run provenance: paket SHA-256, referans sürümü, girdi dosyası hash'leri, parametreler, yazılım sürümleri ve commit; raporda "Methods & versions" altında
- Glio-Cartography'den: yöntemler arası uyum (belirsizliğe dahil), uzamsal ligand–reseptör analizi (yeni "Communication" sekmesi), Ivy GAP bağımsız atlas kontrolü (GBM, gerçek örneklerde), "Not assessed" sınırları (tüm paketler)
- Paketler v0.2.0: her pakete küratörlü ligand–reseptör çiftleri ve "not_assessed" listesi; GBM'ye Ivy GAP referansı
- Alembic migration'ları; mevcut dev veritabanı açılışta otomatik yükseltilir
- API test paketi (20 test) ve yeni analiz testleri (toplam 21)

### Changed
- Glio-Cartography adı ve GBM-only kapsamı terk edildi; hastalıktan bağımsız platforma geçildi.
- Viewer rolü artık salt okunur (proje/örnek/run oluşturamaz, rapor onaylayamaz)
- GBM paketinde IDH1/MGMT açıklamaları: RNA düzeyinin mutasyon/metilasyonu göstermediği açıkça yazıldı
- Pipeline sürümü 0.2.0-baseline

### Fixed
- `next build` exFAT'ta Turbopack önbelleği yüzünden düşüyordu
- ESLint yapılandırması (Next 16 flat config) ve 15 React hooks hatası
- İptal edilen run, arka plan işi bitince "succeeded" olarak üzerine yazılabiliyordu
- Depolama kökü sembolik bağlantı üzerindeyse tüm dosya yolları reddediliyordu
- API tarihleri saat dilimi olmadan dönüyordu; arayüzde 3 saat kayma vardı

### Security
- httpOnly cookie auth, Argon2id, org bazlı izolasyon, audit log planı
