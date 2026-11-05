# Karar Kayıtları (ADR) — Topiome

> Mimariyi etkileyen her karar buraya eklenir. Format: bağlam → karar → sonuçlar.

## ADR-001 — Web SaaS + Python analiz motoru
**Tarih:** 2026-11-06
**Bağlam:** Eski ürün Electron masaüstüydü; lisans dağıtımı ve güncelleme zor. Ticari ürün çok kullanıcılı olmalı.
**Karar:** Next.js web uygulaması + FastAPI/Python analiz servisi. Gerekirse ileride on-prem paket.
**Sonuç:** Uzaktan erişim, kolay güncelleme, abonelik. Dezavantaj: veri yükleme ve gizlilik yönetimi gerekir.

## ADR-002 — Hastalıktan bağımsız çekirdek + YAML disease packs
**Tarih:** 2026-11-06
**Bağlam:** "Her hastalık" ancak ortak çekirdek + konfigürasyonla ölçeklenir.
**Karar:** Pipeline kodu hastalıktan bağımsız; marker, zone, hedef, rapor şablonu YAML'da.
**Sonuç:** Yeni hastalık = veri + validasyon işi. Şema ve sürümleme zorunlu.

## ADR-003 — RUO konumlandırma
**Tarih:** 2026-11-06
**Bağlam:** Klinik ürün regülasyonu (IVDR/ISO 13485) ağır; ekip ve kanıt henüz hazır değil.
**Karar:** Ürün Research Use Only. Klinik iddia yok; klinik yol ayrı faz/ürün.
**Sonuç:** Hızlı lansman, düşük regülasyon yükü. Ticari sınır: hastane klinik kullanımı kapsam dışı.

## ADR-004 — Next.js ve FastAPI ayrımı
**Tarih:** 2026-11-06
**Bağlam:** UI/SEO için JS ekosistemi; analiz için Python ekosistemi.
**Karar:** İki uygulama, tek repo; `/api/*` Next.js rewrite ile FastAPI'ye proxy.
**Sonuç:** Doğru araçlar, bağımsız ölçekleme. Dezavantaj: iki deploy, tip paylaşımı için OpenAPI.

## ADR-005 — Faz 1'de NNLS baseline
**Tarih:** 2026-11-06
**Bağlam:** Ağır modeller (Cell2location/Tangram/GraphST) kurulumu zorlaştırır; önce ölçülebilir bir baseline gerek.
**Karar:** Faz 1'de NumPy/SciPy NNLS + grafik smoothing + KMeans/Leiden. Ağır modeller opsiyonel adaptör.
**Sonuç:** Hızlı, şeffaf, test edilebilir. Doğruluk sınırlı; benchmark ile ölçülür.

## ADR-006 — SQLite (dev) / PostgreSQL (prod)
**Tarih:** 2026-11-06
**Bağlam:** Yerel kurulum sürtünmesini azaltmak; prod'da eşzamanlılık ve JSONB.
**Karar:** SQLAlchemy ile her ikisi; Alembic migration.
**Sonuç:** Tek komutla dev. Prod'da Postgres zorunlu.

## ADR-007 — exFAT diskte geliştirme
**Tarih:** 2026-11-06
**Bağlam:** Kullanıcı projeyi Samsung exFAT diskte istiyor.
**Karar:** Repo diskte; symlink çalışıyor. Performans sorun olursa `node_modules`/`.venv` APFS'e taşınıp symlink verilecek.
**Sonuç:** Taşınabilirlik. Risk: yavaş I/O, bazı araçlarda sert bağlantı sorunu.

## ADR-008 — Marka: Topiome (çalışma adı)
**Tarih:** 2026-11-06
**Bağlam:** Glio adı tek hastalığa bağlı; yeni çatı marka gerek.
**Karar:** Topiome. Domainler boş; tescil kontrolü bekliyor.
**Sonuç:** Hastalıktan bağımsız marka. Yedek: Mappiome, Cartiome, Tissiome.

## ADR-009 — Auth: kendi JWT cookie + Argon2
**Tarih:** 2026-11-06
**Bağlam:** Dış auth servisi maliyet/bağımlılık; ihtiyaç basit.
**Karar:** FastAPI içinde Argon2id + httpOnly JWT cookie; ileride MFA/SSO.
**Sonuç:** Tam kontrol, düşük maliyet. Güvenlik testleri kritik.

## ADR-010 — Hastalık önceliği: veri zenginliği
**Tarih:** 2026-11-06
**Bağlam:** Eski model doğruluğu düşüktü; az veri ana neden.
**Karar:** İlk 6 paket: breast, colorectal, lung, melanoma, prostate, GBM. Veri zenginliği düşük hastalık açılmaz.
**Sonuç:** Daha güvenilir benchmark; kapsam daha yavaş büyür.

## ADR-011 — Alembic migration'ları + exFAT uyumlu çalıştırıcı
**Tarih:** 2026-11-06
**Bağlam:** Şema `create_all` ile kuruluyordu; yeni kolonlar (rapor onayı, run provenance) mevcut veritabanlarına eklenemiyordu. Ayrıca exFAT diskte macOS her dosyanın yanına `._*.py` yazıyor ve stok Alembic bunları migration sanıp çöküyor.
**Karar:** `apps/api/migrations` (0001 başlangıç şeması, 0002 onay+provenance). Uygulama açılışında `upgrade_db()` çalışır; Alembic'ten önce oluşturulmuş DB'ler 0001'e damgalanıp yükseltilir. CLI her zaman `uv run python -m app.migrate …` ile çağrılır (`._*` dosyalarını atlayan yama burada).
**Sonuç:** Şema değişiklikleri izlenebilir ve geri alınabilir. Bare `alembic` komutu bu diskte kullanılmamalı.

## ADR-012 — Rapor onay kapısı (kural #6)
**Tarih:** 2026-11-06
**Karar:** Rapor `draft` doğar; önizlemede görünür "Draft — not approved" bandı vardır. `POST /runs/{id}/report/approve` (analyst+) RUO onay kutusu ister, onaylayanı/zamanı/notu kaydeder ve raporu yeniden üretir. `GET /runs/{id}/report/export` yalnızca onaylı raporu indirir; her onay ve dışa aktarma audit log'a yazılır. Viewer rolü okuyabilir ve onaylı raporu indirebilir, veri değiştiremez/onaylayamaz.
**Sonuç:** İnsan onayı olmadan rapor dışarı çıkmaz. İleride "dört göz" (onaylayan ≠ run sahibi) eklenebilir.

## ADR-013 — Run provenance kaydı (kural #5)
**Tarih:** 2026-11-06
**Karar:** Her run `runs.provenance` JSON'unda pipeline sürümü, paket id/sürüm/SHA-256 parmak izi, referans sürümü, parametreler, girdi dosyası SHA-256'ları, sentetik seed ve yazılım sürümleri (commit, Python, NumPy, SciPy, scikit-learn, pandas) tutar. Commit sırası: `TOPIOME_GIT_COMMIT` → `git rev-parse` (+`-dirty`) → `unversioned`.
**Sonuç:** Repo henüz git deposu olmadığı için commit şu an `unversioned`; `git init` sonrası otomatik dolar.

## ADR-014 — Glio-Cartography'den taşınanlar ve bilinçli olarak taşınmayanlar
**Tarih:** 2026-11-06
**Bağlam:** Eski ürünün (v3.2.9, `~/Downloads/glio-cartography-main`) bağımsız validasyon raporları (GSE237183, GSE331374) ve kod denetimi incelendi.
**Taşınanlar:**
1. *Yöntemler arası uyum* (Tangram–NNLS kontrolünün karşılığı): NNLS + marker z-skor softmax; spot başına 1−JSD uyumu belirsizliğe %25 ağırlıkla girer, ortalama < 0.7 ise uyarı.
2. *Uzamsal ligand–reseptör skoru* (otokrin + satır-normalize parakrin). **Değişiklik:** eski sıfır model (hücre tipi oranlarını karıştırmak) liberaldi — ifade edilen hemen her çift anlamlı çıkıyordu (sentetik GBM'de 10/10). Yeni sıfır model alıcı sinyalini spotlar arasında karıştırır (sentetik GBM'de 3/10) ve BH-FDR uygulanır.
3. *Bağımsız Ivy GAP atlas kontrolü* (GBM; 28 gen × 5 yapı). **Değişiklik:** zon etiketlemede kullanılan marker genleri karşılaştırmadan otomatik dışlanır (eski uygulamada döngüsellik vardı). Sentetik veride çalıştırılmaz.
4. *"Not assessed" sınırları* (IDH/MGMT/WHO derecesi vb.) her pakette ve raporda.
**Taşınmayanlar:** GNN zon modeli (hedefi dekonvolüsyon çıktısı → döngüsel), knockout simülasyonu, TCGA risk / sağkalım, eğitilmemiş ilaç yanıtı başlıkları, lisans/makine kimliği, Electron güncelleyici. RUO ve bilimsel geçerlilik gerekçesiyle.
**Not:** GBM paketine Ivy GAP "cellular tumor" zonu eklemek sentetik domain ARI'yi 0.60 → 0.48'e düşürdü (kapı 0.55); geri alındı, atlas kontrolü 4 eşleşen yapıyla yapılır.

## ADR-015 — Turbopack dosya önbelleği kapalı (exFAT)
**Tarih:** 2026-11-06
**Bağlam:** `next build` "Failed to open database / invalid digit found in string" ile düşüyordu; sebep `.next/cache/turbopack` içindeki `._v16…` AppleDouble dosyaları.
**Karar:** `turbopackFileSystemCacheForDev/Build` varsayılan kapalı; `TOPIOME_TURBOPACK_FS_CACHE=1` ile açılabilir (APFS'te).
**Sonuç:** Derleme biraz daha yavaş ama güvenilir.
