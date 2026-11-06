# STATUS — Topiome

> Bu dosya projenin canlı durum panosudur. Her oturum sonunda güncellenir.
> AI ajanları: işe başlamadan burayı oku, iş bitince işaretle ve oturum kaydı ekle.

**Son güncelleme:** 2026-11-06
**Aşama:** Faz 1 — dikey dilim + gerçek Visium/model + üretim altyapısı
**Genel ilerleme:** ~%45 (ürün akışı, gerçek veri okuyucu, referans/model ve worker/Docker çalışıyor; bilimsel kapılar henüz geçilmedi)

---

## 1. Yapılanlar

### Ürün / strateji
- [x] Eski ürün (Glio-Cartography) ve site incelendi
- [x] Yeni konumlandırma: RUO, çok hastalıklı SaaS
- [x] İlk hastalık seti: veri-zengin 6 tür (meme, akciğer, kolorektal, prostat, melanom, GBM)
- [x] Çalışma markası: **Topiome** (domainler boş; hukuk kontrolü bekliyor)
- [x] Ürün, mimari, validasyon, güvenlik ve iş dokümanları oluşturuldu
- [x] Samsung diskinde yeni repo klasörü: `/Volumes/SAMSUNG/topiome`

### Teknik iskelet
- [x] Monorepo yapısı (`apps/web`, `apps/api`, `packages/analysis`, `packages/disease-packs`)
- [x] Kök script'ler, `.env.example`, `.gitignore`, setup script
- [x] Next.js ürün arayüzü (marketing, auth, dashboard, proje/örnek/run, spatial viewer, rapor, run karşılaştırma)
- [x] FastAPI + veritabanı + auth (Argon2 + httpOnly JWT, org izolasyonu, audit log)
- [x] Alembic migration'ları (0001 başlangıç, 0002 onay + provenance)
- [x] Analiz motoru baseline (QC, NNLS, smoothing, domain, hedef, belirsizlik)
- [x] 6 disease pack YAML + şema + çapraz doğrulama (breast v0.3.0, colorectal/GBM v0.2.0 beta; lung/melanoma/prostate v0.2.0 draft)
- [x] Sentetik demo + seed
- [x] Testler: analiz **33**, API **34**; ruff, ESLint, `tsc --noEmit`, `next build` temiz
- [x] Tarayıcı smoke testi: auth guard → demo login → dashboard → proje → run + canvas → compare → packs → settings → marketing/legal (8/8)
- [x] Üretim Docker stack smoke: 4 konteyner sağlıklı; kayıt → proje → sentetik örnek → queued run → worker → sonuç → HTML rapor

### Gerçek Visium / Space Ranger
- [x] `.h5` (v2/v3) ve `.mtx` + `barcodes` + `features`/`genes` okuyucu
- [x] Headered (`tissue_positions.csv`) ve legacy (`tissue_positions_list.csv`) pozisyonlar
- [x] `scalefactors_json.json` ve `tissue_*_image.png` keşfi; görüntü yolu dataset metadata'sına yazılır
- [x] GEO tarzı iç içe klasörler ve önekli dosya adları (`GSM..._filtered_feature_bc_matrix.h5`)
- [x] Zip/tar(.gz) arşiv çıkarma; path traversal koruması; `._*` / `.DS_Store` filtresi
- [x] `.h5` doğrudan yükleme; API yükleme doğrulaması archive veya parça dosyaları kabul eder
- [x] QC tam matris üzerinde hesaplanır; gen ön seçimi QC veya kütüphane boyutunu değiştirmez
- [x] `n_genes` (ölçülen toplam) ve `n_genes_loaded` (modele yüklenen) ayrı raporlanır
- [x] Testler: 6 IO (h5/mtx eşdeğerliği, sadece doku spotları, QC, koordinat, eksik dosya) + 2 API upload

### Referanslar ve domain modeli
- [x] Wu 2021 meme scRNA referansı (`references/breast_wu2021_v1_signatures.*`): 408 gen, 8 hücre tipi, yalnız eğitim hastaları; test hastaları CID4465/CID4535 hariç
- [x] Wu 2021 Visium + patolog etiketleriyle hasta düzeyinde ayrım: eğitim 4 hasta, test 2 hasta
- [x] 2 katmanlı GraphSAGE (6-NN uzamsal grafik), sıcaklık kalibrasyonu, NumPy çıkarımı (`analysis/gnn.py`)
- [x] Model kartı + ağırlıklar (`models/breast_domain_gnn_v1.*`); pipeline gerçek örnekte modeli uygular, sentetikte atlar, gen kapsamı < %80 ise uyarıyla atlar
- [x] Provenance: paket SHA-256, referans sürümü + SHA-256, domain model sürümü + SHA-256
- [x] Held-out sonuç (pooled, 2.235 spot): GNN Acc 0.770 / Macro-F1 0.446 / ARI 0.260 / ECE 0.098; MLP 0.739 / 0.386 / 0.191 / 0.136; baseline 0.325 / 0.210 / 0.011
- [x] **Kapı geçilmedi:** ARI 0.260 < 0.35 minimum → breast pack **beta** kalır
- [x] Ayrıntı: `docs/validation/breast-wu2021.md`

### GBM gerçek veri kontrolü
- [x] GEO GSE331374 / GSM9744831 (primer GBM Visium) doğrudan reader ile koşuldu: 2.930 doku spotu, 36.601 gen, 2.727 QC-pass
- [x] Yöntem uyumu 0.656; anlamlı ligand–reseptör 0/10; referans olmadığı için kompozisyon marker-score baseline
- [x] Ivy GAP bağımsız atlas kontrolü: diagonal ort. **−0.179**, top-1 **0.0** (4 zon) — olumsuz sonuç saklandı
- [x] GBM pack **beta**; eğitilmiş GBM referansı/domain modeli yok
- [x] Ayrıntı: `docs/validation/gbm-gse331374.md`

### Üretim / güvenlik
- [x] `QUEUE_MODE=inline` (dev) / `worker` (prod): DB tabanlı kuyruk, atomik `queued → running` sahiplenme, kesinti kurtarma, `RUN_TIMEOUT_HOURS`
- [x] `python -m app.worker` (döngü veya `--once`), SIGTERM/SIGINT ile güvenli çıkış; birden fazla worker güvenli
- [x] Docker: `infra/docker/api.Dockerfile` (API + worker aynı imaj), `web.Dockerfile` (Next standalone), `infra/docker-compose.yml` (db/api/worker/web, healthcheck, volume)
- [x] Non-root kullanıcı + `COPY --chown`; Postgres advisory lock ile eşzamanlı migration koruması
- [x] Compose ve imajlar gerçekten build edildi; dört servis healthy; worker run'ı tamamladı
- [x] Üretim ayar kapıları: zayıf `SECRET_KEY`, SQLite, açık demo login veya geçersiz queue modunda API açılmayı reddeder
- [x] Üretimde demo login kapalı, oturum çerezi `Secure`, origin kontrolü, CORS, güvenlik başlıkları
- [x] Giriş throttling: IP + e-posta 15 dk / 10 deneme; IP başına 50 başarısız deneme; `429` + `Retry-After`
- [x] İki run karşılaştırma (`GET /runs/compare`, `/app/runs/compare`): kayıtlı sonuçtan, org izolasyonu, bitmemiş run 409, aynı run 400
- [x] Docker build sırasında bulunan gerçek hata düzeltildi: exFAT 0700 izinli kaynak dosyaları root'a ait kalıyordu ve `USER topiome` uygulamayı okuyamıyordu

### Ticari
- [ ] Şirket adı / tüzel kişilik
- [ ] Marka tescili başvurusu
- [ ] Domain satın alma (`topiome.com`, `.io`, `.bio`, `.ai`)
- [ ] Fiyatlandırma sayfası ve Stripe test akışı
- [ ] 3 pilot görüşme (akademi / hastane araştırma laboratuvarı)

---

## 2. Şu an üzerinde çalışılan

- [ ] Gerçek bir kamu GBM örneğini (GSE331374) **API/UI upload** üzerinden uçtan uca koşmak (şu an reader doğrudan script ile koşuldu)
- [ ] Kalıcı Playwright E2E paketini repoya eklemek (bu oturumda geçici script ile 8 kontrol + üretim kayıt akışı geçti)
- [ ] Gerçek meme Visium kesitinde referans + GNN'i uçtan uca doğrulamak

---

## 3. Sıradaki (öncelik sırası)

### P0 — Çalışan ürün
1. [x] FastAPI: User/Org/Project/Sample/Run/Report modelleri + Alembic
2. [x] Auth: register, login, logout, me, demo login
3. [x] Upload: Visium klasörü / zip / tar / `.h5`, metadata, dosya doğrulama (zip-slip korumalı)
4. [x] Run pipeline: inline/worker job, durum takibi, hata yönetimi, atomik iptal
5. [x] Analysis baseline: QC, NNLS dekonvolüsyon, spatial smoothing, kümeleme, belirsizlik (+ yöntem uyumu)
6. [x] Results API + spatial viewer
7. [x] HTML rapor + onay kapısı + audit'li dışa aktarma (PDF: tarayıcıdan yazdır)
8. [x] Demo seed + demo hesap
9. [x] E2E smoke test + `npm run build`
10. [x] Git deposu başlatıldı (`main`, ilk commit) — provenance commit hash'ini kaydediyor
11. [x] Gerçek Visium reader + GBM real-data/Ivy GAP kontrolü (sonuç olumsuz, dokümante)
12. [ ] Gerçek kamu örneğini API/UI upload üzerinden uçtan uca koşmak
13. [ ] Kalıcı Playwright E2E + web birim testleri

### P1 — Ticari ürün
14. [ ] Organizasyon davetleri (roller mevcut; davet akışı yok)
15. [ ] Audit log ekranı
16. [ ] Stripe abonelik + kullanım kotaları
17. [ ] API anahtarları + dış API
18. [ ] S3 storage + signed URL
19. [x] Worker kuyruğu + Docker Compose (DB tabanlı); [ ] yeniden deneme/backoff ve Redis/RQ seçeneği
20. [ ] E-posta bildirimleri
21. [ ] KVKK/GDPR metinleri, DPA, veri saklama politikası
22. [ ] Dokümantasyon sitesi (veri formatları, metodoloji, validasyon)

### P2 — Bilimsel derinleşme
23. [x] Gerçek kamu veri setlerinden Wu 2021 ve GSE331374 kullanıldı; lisans kaydı `docs/DATA.md`'de
24. [x] Benchmark harness: pseudospot, held-out sample, ARI/NMI/JSD/ECE (`analysis/benchmark.py`)
25. [ ] Cell2location / Tangram adaptörleri
26. [ ] GraphST / STAGATE adaptörleri
27. [x] Ligand-receptor ve komşuluk analizi (uzamsal permütasyon + BH-FDR)
28. [x] İlaç hedefi skorlama + hedef veritabanı (paket bazlı, kanıt düzeyi)
29. [x] Meme model card + sürüm kaydı; [ ] GBM ve diğer paketler için model card
30. [ ] Her hastalık için bağımsız held-out doğrulama raporu

### P3 — Ölçek / klinik yol
31. [ ] Visium HD, Xenium, CosMx desteği
32. [ ] Çok örnekli / çok hastalıklı karşılaştırma (iki run karşılaştırma var)
33. [ ] On-prem / VPC kurulum
34. [ ] ISO 13485 / IVDR fizibilite
35. [ ] Klinik validasyon çalışması (RUO dışı, ayrı ürün hattı)

---

## 4. Kararlar bekliyor

| # | Konu | Seçenekler | Sahibi | Durum |
|---|---|---|---|---|
| D1 | Marka tescili | Topiome / alternatif | kurucular + vekil | Bekliyor |
| D2 | Şirket türü | Ltd. Şti. / A.Ş. / yurt dışı | kurucular + mali müşavir | Bekliyor |
| D3 | İlk pilot kurum | 3 üniversite laboratuvarı | ekip | Bekliyor |
| D4 | Bulut sağlayıcı | AWS Frankfurt / Hetzner / Fly.io | teknik | Bekliyor |
| D5 | Açık veri lisansları | kullanım koşulları kontrolü — **Ivy GAP (Allen) ticari kullanım dahil** | bilim ekibi | Bekliyor |

---

## 5. Oturum kaydı

### 2026-11-06 — Faz 1 başlangıcı
- Eski repo/site analiz edildi; ürün yönü netleştirildi.
- Marka adayları elendi; **Topiome** çalışma adı seçildi.
- `/Volumes/SAMSUNG/topiome` oluşturuldu.
- `AGENTS.md`, `README.md`, `docs/*` yazıldı.
- Next.js + FastAPI + analysis iskeleti kuruluyor.

### 2026-11-06 — P0 kapanışı + Glio-Cartography'den taşıma
- Önceki oturum kodu büyük ölçüde yazmış ama STATUS güncellenmemişti; durum doğrulandı.
- `next build` exFAT/Turbopack önbelleği yüzünden düşüyordu → önbellek kapatıldı (ADR-015). ESLint Next 16 flat config'e geçti; 15 hooks hatası düzeltildi.
- Alembic eklendi (ADR-011); mevcut `apps/api/topiome.db` açılışta 0002'ye yükseltildi (yedek oturum scratchpad'inde alındı).
- Run iptali atomik yapıldı; provenance kaydı (ADR-013); rapor onay kapısı + audit'li export (ADR-012); viewer salt okunur.
- Glio-Cartography incelendi ve 4 parça taşındı (ADR-014). GNN/knockout/TCGA risk/sağkalım bilinçli olarak alınmadı.
- Testlerin yakaladığı hatalar: symlink'li depolama kökü, saat dilimi eksik tarihler (UI'da 3 saat kayma).
- Doğrulandı: analiz 21/21, API 20/20, ruff, ESLint, tsc, `next build`, curl smoke (demo → run → onay → export), tarayıcıda Communication/Validation/Report sekmeleri.
- Not: port 8000'de önceki oturumdan kalma, eski kodla çalışan bir uvicorn süreci vardı; dokunulmadı.
- Ayrıca `breast.yaml` v0.3.0'a yükseltildi: referans imzaları ve domain modeli bağlandı. **Kapı geçilmedi** (held-out ARI 0.260 < 0.35); paket beta kaldı.

### 2026-11-06 — İki run yan yana karşılaştırma
- `GET /api/v1/runs/compare?a=&b=` (`routers/compare.py` + `services/compare.py`): yalnızca `Result.payload` okunur, analiz yeniden koşmaz. Run özeti (paket, spot, yöntem uyumu, anlamlı L–R), `composition_mean` farkları (B − A), domain payı (% spot), L–R q-değerleri yan yana; paket/paket sürümü/pipeline sürümü farkı, aynı örnek ve sentetik veri için `warnings`.
- Paketler farklıysa yalnız iki pakette de tanımlı hücre tipi/domain/çift hizalanır; diğerleri karşı tarafta `null` ("not in pack"). Aynı pakette hiç spotu olmayan domain 0 sayılır.
- Router, `runs` router'ından **önce** eklenir; yoksa `/runs/{run_id}` "compare"ı yutar (`main.py`'de yorum var).
- Web: Runs sayfasında "Compare" modu (`?compare=1` ile de açılır; ilk seçim A, ikinci B; yalnız tamamlanmış run seçilebilir) ve `/app/runs/compare` (iki sütun özet, kompozisyon fark çubukları, domain tablosu, L–R tablosu, RUO + Not assessed, "Swap A / B").
- Dil: "better/worse" yok; "higher in A/B" ve q-değerlerinin run'lar arası fark testi olmadığı notu.
- Doğrulandı: `npm test` (analiz 21 + API 27, yeni 7 test: org dışı → 404, bitmemiş → 409, aynı run → 400, paket ve sürüm uyumsuzluğu uyarısı), `npm run lint`, `npm run build`; 8010/3010 portlarında geçici DB ile curl + tarayıcı smoke testi (masaüstü ve 375 px).
- Kullanıcı onayıyla `git init -b main` + ilk commit; `.gitignore`'a yerel DB'ler, `/data/`, `.claude/`, `*.tsbuildinfo` eklendi. Push yapılmadı (remote yok).

### 2026-11-06 — Gerçek Visium reader + Wu 2021 referansı + GNN
- `analysis/io.py`: Space Ranger `.h5` v2/v3, `.mtx(.gz)`, headered/legacy pozisyonlar, scalefactors/görüntü keşfi, GEO önekleri, iç içe klasörler, zip/tar çıkarma (path traversal korumalı), `._*` filtresi.
- QC tam matris üzerinde; `total_counts` gen seçiminden önce hesaplanır. `n_genes` (ölçülen) ve `n_genes_loaded` (yüklenen) ayrıldı.
- Wu 2021 scRNA referansı (GSE176078) yalnız eğitim hastalarından üretildi; `breast_wu2021_v1_signatures.csv.gz` + card. Test hastaları CID4465/CID4535 referansta yok.
- `analysis/gnn.py`: 2 katman GraphSAGE, 6-NN grafik, sıcaklık kalibrasyonu, NumPy çıkarım; eğitim `scripts/validation/train_domain_gnn.py` (PyTorch, offline).
- Hasta düzeyi split: eğitim 4 / test 2. Test pooled: GNN Acc 0.770, Macro-F1 0.446, ARI 0.260, ECE 0.098; MLP 0.739/0.386/0.191/0.136; baseline 0.325/0.210/0.011. **Breast beta** (ARI kapısı).
- Model gerçek örnekte uygulanır; sentetik demo ve düşük gen kapsamı (< %80) atlanır, provenance'a SHA-256 yazılır.
- Doğrulandı: analiz 33/33 (6 GNN + 6 IO testi dahil), ruff temiz.

### 2026-11-06 — GBM gerçek veri + Ivy GAP (olumsuz sonuç)
- GSE331374 / GSM9744831 doğrudan `load_visium` ile okundu: 2.930 doku spotu, 36.601 gen, 2.727 QC-pass, adaptif mito eşiği %45.
- Referans/domain modeli olmadığı için marker-score baseline; yöntem uyumu 0.656, anlamlı L–R 0/10.
- Ivy GAP: diagonal ort. −0.179, top-1 0.0 (4 zon, 21 gen; marker genleri hariç). Tahmin edilen zonlar atlas yapılarıyla eşleşmiyor.
- **GBM beta**; eğitilmiş GBM referansı/domain modeli olmadan zon etiketleri güvenilir değil. Rapor: `docs/validation/gbm-gse331374.md`.

### 2026-11-06 — Üretim worker/Docker + güvenlik + E2E
- DB tabanlı kuyruk: `services/queue.py` + `app/worker.py`; atomik `queued → running`, kesinti kurtarma, `RUN_TIMEOUT_HOURS`, çoklu worker güvenli.
- `infra/docker-compose.yml` + iki Dockerfile: Postgres, API (2 uvicorn worker), worker, Next standalone web; healthcheck'ler ve volume'lar. Compose config doğrulandı.
- Build'de gerçek hata: exFAT 0700 dosyaları `COPY` sonrası root'a ait kalıyordu → `COPY --chown=topiome:topiome` ve kullanıcı oluşturma sırası düzeltildi. Ayrıca exFAT `._*` dosyaları BuildKit xattr taramasını kırıyor; temiz bağlam gerekir.
- Üretim güvenliği: prod ayar kapıları, demo login kapalı, `Secure` cookie, Origin kontrolü, CORS, güvenlik başlıkları, giriş throttling.
- Doğrulandı: 4 konteyner healthy; web proxy `/api/v1/health`; üretimde demo login 404; kayıt → proje → sentetik örnek → queued run → worker → succeeded → sonuç → HTML rapor (RUO + synthetic). Tarayıcıda üretim kayıt akışı da geçti.
- Web smoke (geçici Playwright): auth guard, demo login, dashboard, proje, run + canvas, compare, packs, settings, marketing/legal — 8/8.

### 2026-11-06 — Kapanış doğrulaması ve commit
- Son doğrulama: analiz **33/33**, API **34/34**; `ruff`, ESLint, `tsc --noEmit`, `next build` temiz.
- Sentetik benchmark kanıtı `docs/validation/benchmarks/` altına alındı (küçük JSON; `data/` kuralı gereği ham veri git'e girmez).
- Üretim Docker stack'i doğrulama sonrası durduruldu (`docker compose down --volumes`); imajlar yerelde kaldı.
- Tüm çalışma `main` dalına commit'lendi; remote yok, push yapılmadı.

## 6. Bilinen riskler

| Risk | Etki | Azaltma |
|---|---|---|
| Dekonvolüsyon/GNN doğruluğu düşük | Ürün güvenilirliği | Benchmark kapısı, ensemble, belirsizlik, held-out test; breast beta |
| GBM zonları Ivy GAP ile uyuşmuyor | GBM paketi güvenilmez | GBM beta; bağımsız etiketli referans + domain modeli gelene kadar zon iddiası yok |
| Tek çalışma / tek merkez (Wu 2021) | Genellenebilirlik bilinmiyor | Yeni held-out kohort; Visium HD ve farklı protokoller |
| Hastalık başına veri yetersizliği | Kapsam | Veri-zengin 6 türle başla; veri skoru < eşik olan paketi yayına alma |
| RUO sınırının ihlali | Hukuki | UI/rapor/pazarlamada zorunlu uyarı; klinik iddia yasağı |
| exFAT performansı | Geliştirme hızı | Gerekirse node_modules/.venv'i APFS'e taşı, symlink |
| exFAT `._*` dosyaları | Araçlar çöküyor (Turbopack, Alembic, ruff, Docker BuildKit) | Turbopack önbelleği kapalı; `python -m app.migrate`; ruff exclude; Docker build öncesi temiz bağlam |
| Docker build exFAT'te yavaş/kırılgan | Dağıtım | Temiz kopya veya `._*` temizliği; CI'da APFS/Linux checkout |
| Queue'da otomatik retry yok | Geçici hata run'ı düşürür | Kullanıcı "Re-run"; ileride backoff/retry |
| Giriş throttling süreç başına | Çok worker'da sınır esner | Ters proxy/WAF; ileride Redis tabanlı sayaç |
| Next `rewrites` derleme anında sabitlenir | Yanlış API'ye proxy | `API_URL`'i `next build` sırasında ver |
| Tek kişiye bağımlılık | Operasyon | Dokümantasyon, ADR, test, otomasyon |
| Marka tescili çakışması | Marka | Vekil kontrolü; yedek isim listesi |
