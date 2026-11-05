# Yol Haritası — Topiome

> "Tam ürün" hedefi uzun soluklu. Aşağıdaki aşamalar birbirine bağımlı; her aşama çalışan ve test edilmiş bir dilimle kapanır.

## Faz 0 — Karar ve iskelet ✅ (2026-11-06)
- Marka/konumlandırma, mimari, validasyon stratejisi
- Repo, dokümantasyon, ajan hafızası
- Samsung diskinde çalışma ortamı

## Faz 1 — Çalışan dikey dilim (2–4 hafta)
**Hedef:** Demo hesabıyla uçtan uca: kayıt → proje → örnek → analiz → harita → rapor.

- [ ] FastAPI veri modeli + Alembic
- [ ] Auth (register/login/logout/me/demo)
- [ ] Organizasyon + roller
- [ ] Proje/örnek CRUD
- [ ] Visium klasörü/zip yükleme + doğrulama
- [ ] Sentetik demo verisi
- [ ] Analysis baseline: QC, NNLS, smoothing, KMeans/Leiden, uncertainty
- [ ] Run durum makinesi + hata yönetimi
- [ ] Spatial viewer (canvas, katmanlar, tooltip)
- [ ] HTML rapor + yazdırma
- [ ] Marketing landing page
- [ ] Build + smoke test + demo seed

**Çıkış kriteri:** `npm run dev` ile tek komutta çalışıyor; demo verisiyle sonuç ve rapor alınıyor; build hatasız.

## Faz 2 — Ürünleşme (4–8 hafta)
- [ ] 6 disease pack (beta) + şema + doğrulama
- [ ] Gerçek kamu veri setleriyle benchmark harness
- [ ] Cell2location/Tangram adaptörleri
- [ ] GraphST/STAGATE adaptörleri
- [ ] Belirsizlik kalibrasyonu + reliability diagram
- [ ] Çok örnekli karşılaştırma
- [ ] Ekip davetleri, audit log, API anahtarları
- [ ] Stripe abonelik + kotalar
- [ ] S3 storage + signed URL
- [ ] Redis/RQ worker + retry
- [ ] Dokümantasyon sitesi
- [ ] KVKK/GDPR metinleri + DPA
- [ ] 3 pilot kurum

**Çıkış kriteri:** En az 2 hastalık paketi beta; ödeme test modu; 3 pilot kullanıcı geri bildirimi.

## Faz 3 — Ölçek ve gelir (3–6 ay)
- [ ] Visium HD, Xenium, CosMx
- [ ] Ligand-receptor + komşuluk analizi
- [ ] İlaç hedefi veritabanı + kanıt düzeyleri
- [ ] On-prem/VPC kurulum
- [ ] SSO/SAML, gelişmiş audit
- [ ] Model sürümleme + model card UI
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
