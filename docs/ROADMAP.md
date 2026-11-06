# Yol Haritası — Topiome

> "Tam ürün" hedefi uzun soluklu. Aşağıdaki aşamalar birbirine bağımlı; her aşama çalışan ve test edilmiş bir dilimle kapanır.

## Faz 0 — Karar ve iskelet ✅ (2026-11-06)
- Marka/konumlandırma, mimari, validasyon stratejisi
- Repo, dokümantasyon, ajan hafızası
- Samsung diskinde çalışma ortamı

## Faz 1 — Çalışan dikey dilim (2–4 hafta)
**Hedef:** Demo hesabıyla uçtan uca: kayıt → proje → örnek → analiz → harita → rapor.

- [x] FastAPI veri modeli + Alembic
- [x] Auth (register/login/logout/me/demo)
- [x] Organizasyon + roller
- [x] Proje/örnek CRUD
- [x] Visium `.h5` / `.mtx` / klasör / zip-tar yükleme + doğrulama
- [x] Sentetik demo verisi
- [x] Analysis baseline: QC, NNLS, smoothing, KMeans/Leiden, uncertainty
- [x] Run durum makinesi + hata yönetimi (inline + DB worker)
- [x] Spatial viewer (canvas, katmanlar, tooltip)
- [x] HTML rapor + yazdırma + onay kapısı
- [x] Marketing landing page
- [x] Build + smoke test + demo seed
- [x] Wu 2021 referans imzaları + hasta düzeyi GNN domain modeli (breast beta)
- [x] İki run karşılaştırma

**Çıkış kriteri:** `npm run dev` ile tek komutta çalışıyor; demo verisiyle sonuç ve rapor alınıyor; build hatasız.

## Faz 2 — Ürünleşme (4–8 hafta)
- [x] 6 disease pack + şema + doğrulama (3 beta, 3 draft)
- [x] Gerçek kamu verileriyle benchmark/held-out (Wu 2021, GSE331374) — kapılar geçilmedi
- [ ] Cell2location/Tangram adaptörleri
- [ ] GraphST/STAGATE adaptörleri
- [x] Belirsizlik kalibrasyonu + ECE (breast modeli); [ ] reliability diagram UI
- [x] İki run karşılaştırma; [ ] çok örnekli kohort analizi
- [x] Audit log altyapısı; [ ] ekip davetleri, audit ekranı, API anahtarları
- [ ] Stripe abonelik + kotalar
- [ ] S3 storage + signed URL
- [x] DB tabanlı worker + Docker Compose; [ ] Redis/RQ + otomatik retry
- [ ] Dokümantasyon sitesi
- [ ] KVKK/GDPR metinleri + DPA
- [ ] 3 pilot kurum

**Çıkış kriteri:** En az 2 hastalık paketi beta; ödeme test modu; 3 pilot kullanıcı geri bildirimi.

## Faz 3 — Ölçek ve gelir (3–6 ay)
- [ ] Visium HD, Xenium, CosMx
- [x] Ligand-receptor + komşuluk analizi
- [x] İlaç hedefi veritabanı + kanıt düzeyleri (paket bazlı)
- [ ] On-prem/VPC kurulum
- [ ] SSO/SAML, gelişmiş audit
- [ ] Model sürümleme + model card UI (meme model card dosyası var)
- [ ] 20+ ödeyen müşteri
- [ ] Vaka çalışmaları, yayınlar
- [ ] Yatırım/fon başvuruları

## Faz 4 — Klinik yol (12+ ay, ayrı ürün hattı)
- [ ] ISO 13485 QMS
- [ ] IVDR sınıflandırma ve klinik validasyon
- [ ] Patolog iş akışı, LIS entegrasyonu
- [ ] Regülasyon danışmanı, etik kurul
- [ ] Klinik ortam için ayrı marka/ürün

> Faz 4, RUO ürünün bir parçası değildir. Ayrı ekip, ayrı kalite sistemi, ayrı validasyon gerektirir.

## Teknik borç / sonra
- [ ] SSE ile canlı run durumu
- [ ] WebSocket işbirliği
- [ ] Görüntü (H&E) üzerine spot overlay
- [ ] 3D/çok kesit atlas
- [ ] R/Seurat köprüsü
- [ ] On-prem lisans anahtarı
- [ ] Çoklu dil (TR/EN) UI
- [ ] Erişilebilirlik (WCAG 2.1 AA)
- [ ] Performans: büyük örneklerde streaming

## Ölçülebilir hedefler

| Metrik | Faz 1 | Faz 2 | Faz 3 |
|---|---|---|---|
| Analiz süresi (1.500 spot) | < 2 dk | < 5 dk (gerçek model) | < 3 dk |
| Desteklenen hastalık | 1 (demo) | 6 beta | 10+ |
| Aktif kullanıcı | 10 | 50 | 250 |
| Ödeyen müşteri | 0 | 5 | 20 |
| Benchmark eşiğini geçen paket | 0 | 2 | 6 |
