# STATUS — Topiome

> Bu dosya projenin canlı durum panosudur. Her oturum sonunda güncellenir.
> AI ajanları: işe başlamadan burayı oku, iş bitince işaretle ve oturum kaydı ekle.

**Son güncelleme:** 2026-11-06
**Aşama:** Faz 1 — Ürün iskeleti + çalışan dikey dilim
**Genel ilerleme:** ~%30 (dikey dilim çalışıyor; P0'ın çoğu tamam)

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
- [x] Next.js ürün arayüzü (marketing, auth, dashboard, proje/örnek/run, spatial viewer, rapor)
- [x] FastAPI + veritabanı + auth (Argon2 + httpOnly JWT, org izolasyonu, audit log)
- [x] Alembic migration'ları (0001 başlangıç, 0002 onay + provenance)
- [x] Analiz motoru baseline (QC, NNLS, smoothing, domain, hedef, belirsizlik)
- [x] 6 disease pack YAML (v0.2.0) + şema + çapraz doğrulama
- [x] Sentetik demo + seed
- [x] Testler: analiz 21, API 20; `npm run build`, ESLint, ruff temiz; canlı smoke test (curl + tarayıcı)

### Glio-Cartography'den taşınanlar (ADR-014)
- [x] Yöntemler arası uyum → spot belirsizliği
- [x] Uzamsal ligand–reseptör analizi (daha sıkı sıfır model + BH-FDR) + "Communication" sekmesi
- [x] Ivy GAP bağımsız atlas kontrolü (GBM, gerçek örneklerde; zon marker'ları dışlanır)
- [x] "Not assessed" sınırları (her paket, rapor, UI)
- [ ] İki örnek yan yana karşılaştırma (eski "multi-patient comparison")
- [ ] PDF rapor (eski reportlab hattı) — şimdilik tarayıcıdan yazdır
- [ ] Bağımsız GEO validasyonunu (GSE237183, GSE331374) Topiome'da yeniden koşmak

### Ticari
- [ ] Şirket adı / tüzel kişilik
- [ ] Marka tescili başvurusu
- [ ] Domain satın alma (`topiome.com`, `.io`, `.bio`, `.ai`)
- [ ] Fiyatlandırma sayfası ve Stripe test akışı
- [ ] 3 pilot görüşme (akademi / hastane araştırma laboratuvarı)

---

## 2. Şu an üzerinde çalışılan

- [x] **Dikey dilim:** kayıt → proje → örnek → analiz → spatial viewer → rapor → onay → dışa aktarma
- [ ] Gerçek Visium örneğiyle uçtan uca test (şu ana kadar yalnız sentetik demo)

---

## 3. Sıradaki (öncelik sırası)

### P0 — Çalışan ürün
1. [x] FastAPI: User/Org/Project/Sample/Run/Report modelleri + Alembic
2. [x] Auth: register, login, logout, me, demo login
3. [x] Upload: Visium klasörü / zip, metadata, dosya doğrulama (zip-slip korumalı)
4. [x] Run pipeline: inline job, durum takibi, hata yönetimi, atomik iptal
5. [x] Analysis baseline: QC, NNLS dekonvolüsyon, spatial smoothing, kümeleme, belirsizlik (+ yöntem uyumu)
6. [x] Results API + spatial viewer
7. [x] HTML rapor + onay kapısı + audit'li dışa aktarma (PDF: tarayıcıdan yazdır)
8. [x] Demo seed + demo hesap
9. [x] E2E smoke test + `npm run build`
10. [x] Git deposu başlatıldı (`main`, ilk commit) — provenance artık commit hash'ini kaydediyor
11. [ ] Gerçek Visium örneği (ör. 10x public GBM / GSE331374) ile uçtan uca koşu + Ivy GAP kontrolünün gerçek veride sonucu
12. [ ] Playwright E2E (kayıt → run → onay → dışa aktarma) ve web birim testleri

### P1 — Ticari ürün
10. [ ] Organizasyon davetleri, roller (owner/admin/analyst/viewer)
11. [ ] Audit log ekranı
12. [ ] Stripe abonelik + kullanım kotaları
13. [ ] API anahtarları + dış API
14. [ ] S3 storage + signed URL
15. [ ] Redis/RQ worker + yeniden deneme
16. [ ] E-posta bildirimleri
17. [ ] KVKK/GDPR metinleri, DPA, veri saklama politikası
18. [ ] Dokümantasyon sitesi (veri formatları, metodoloji, validasyon)

### P2 — Bilimsel derinleşme
19. [ ] Gerçek kamu veri setlerini indirme + lisans kaydı
20. [ ] Benchmark harness: pseudospot, held-out sample, ARI/NMI/JSD/ECE
21. [ ] Cell2location / Tangram adaptörleri
22. [ ] GraphST / STAGATE adaptörleri
23. [ ] Ligand-receptor ve komşuluk analizi
24. [ ] İlaç hedefi skorlama + hedef veritabanı
25. [ ] Model card + sürüm kaydı
26. [ ] Her hastalık için doğrulama raporu

### P3 — Ölçek / klinik yol
27. [ ] Visium HD, Xenium, CosMx desteği
28. [ ] Çok örnekli / çok hastalıklı karşılaştırma
29. [ ] On-prem / VPC kurulum
30. [ ] ISO 13485 / IVDR fizibilite
31. [ ] Klinik validasyon çalışması (RUO dışı, ayrı ürün hattı)

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

---

### 2026-11-06 — P0 kapanışı + Glio-Cartography'den taşıma
- Önceki oturum kodu büyük ölçüde yazmış ama STATUS güncellenmemişti; durum doğrulandı.
- `next build` exFAT/Turbopack önbelleği yüzünden düşüyordu → önbellek kapatıldı (ADR-015). ESLint Next 16 flat config'e geçti; 15 hooks hatası düzeltildi.
- Alembic eklendi (ADR-011); mevcut `apps/api/topiome.db` açılışta 0002'ye yükseltildi (yedek oturum scratchpad'inde alındı).
- Run iptali atomik yapıldı; provenance kaydı (ADR-013); rapor onay kapısı + audit'li export (ADR-012); viewer salt okunur.
- Glio-Cartography incelendi ve 4 parça taşındı (ADR-014). GNN/knockout/TCGA risk/sağkalım bilinçli olarak alınmadı.
- Testlerin yakaladığı hatalar: symlink'li depolama kökü, saat dilimi eksik tarihler (UI'da 3 saat kayma).
- Doğrulandı: analiz 21/21, API 20/20, ruff, ESLint, tsc, `next build`, curl smoke (demo → run → onay → export), tarayıcıda Communication/Validation/Report sekmeleri.
- Not: port 8000'de önceki oturumdan kalma, eski kodla çalışan bir uvicorn süreci vardı; dokunulmadı.
- Kullanıcı onayıyla `git init -b main` + ilk commit; `.gitignore`'a yerel DB'ler, `/data/`, `.claude/`, `*.tsbuildinfo` eklendi. Push yapılmadı (remote yok).

## 6. Bilinen riskler

| Risk | Etki | Azaltma |
|---|---|---|
| Dekonvolüsyon/GNN doğruluğu düşük | Ürün güvenilirliği | Benchmark kapısı, ensemble, belirsizlik, held-out test |
| Hastalık başına veri yetersizliği | Kapsam | Veri-zengin 6 türle başla; veri skoru < eşik olan paketi yayına alma |
| RUO sınırının ihlali | Hukuki | UI/rapor/pazarlamada zorunlu uyarı; klinik iddia yasağı |
| exFAT performansı | Geliştirme hızı | Gerekirse node_modules/.venv'i APFS'e taşı, symlink |
| exFAT `._*` dosyaları | Araçlar çöküyor (Turbopack, Alembic, ruff) | Turbopack önbelleği kapalı; `python -m app.migrate`; ruff `extend-exclude` |
| Next `rewrites` derleme anında sabitlenir | Yanlış API'ye proxy | `API_URL`'i `next build` sırasında ver |
| Tek kişiye bağımlılık | Operasyon | Dokümantasyon, ADR, test, otomasyon |
| Marka tescili çakışması | Marka | Vekil kontrolü; yedek isim listesi |
