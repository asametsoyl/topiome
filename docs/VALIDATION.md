# Validasyon — Topiome

> Eski sürümün en büyük sorunu buydu: dekonvolüsyon ve GNN doğrulukları düşüktü, belirsizlik raporlanmıyordu.
> Bu dosya, "doğru görünen" değil **ölçülmüş** sonuç üretme sözleşmesidir.

## 1. Neden düşüktü? (kök neden analizi)

| Olası neden | Belirti | Yeni yaklaşım |
|---|---|---|
| Tek model, tek veri seti | Overfit; başka örnekte çöküş | Çok veri seti + held-out |
| Referans scRNA-seq uyumsuzluğu | Hücre tipi karışması | Referans kalibrasyonu, ortak gen uzayı, batch düzeltme |
| Düşük spot/örnek sayısı | Yüksek varyans | Veri-zengin hastalıklar; örnek başına minimum eşik |
| Validasyonsuz GNN | Güzel görsel, anlamsız kümeler | Baseline + ARI/NMI + marker enrichment |
| Belirsizlik yok | Kullanıcı kesin sanıyor | Spot bazında güven, calibration |
| Değerlendirme metriği yok | "İyi görünüyor" | Önceden tanımlı metrik + eşik |

## 2. Validasyon katmanları

### A. Sentetik pseudospot (bilinen ground truth)
scRNA-seq'den hücreleri karıştırarak sentetik spotlar üret. Kompozisyon bilinir.
- Metrikler: RMSE, Jensen-Shannon divergence (JSD), Pearson/Spearman, hücre tipi F1.
- Amaç: dekonvolüsyon algoritmasının matematiksel doğruluğu.

### B. Held-out gerçek örnek
Aynı çalışmadan değil, **bağımsız çalışmalardan** test örnekleri.
- Annotasyonlu bölgeler varsa: ARI, NMI, adjusted Rand.
- Yoksa: marker enrichment, pathologist spot-check, silüet.
- Amaç: genellenebilirlik.

### C. Pertürbasyon / kararlılık
- Spot downsampling, gürültü ekleme, farklı normalizasyon.
- Sonuçların değişim katsayısı; "stability score".
- Amaç: sonuçların veri kalitesine duyarlılığı.

### D. Kalibrasyon
- Güven skoru ile gerçek doğruluk uyumu: ECE (expected calibration error), reliability diagram.
- Amaç: "0.9 güven" diyorsa gerçekten ~%90 doğru olmalı.

### E. Biyolojik tutarlılık
- Bilinen marker genlerinin beklenen hücre tiplerinde zenginleşmesi.
- Ligand-receptor çiftlerinin beklenen komşuluklarda bulunması (uygulandı: `analysis/communication.py`, uzamsal permütasyon + BH-FDR).
- Pathologist / alan uzmanı spot-check (en az 2 kişi, kör).

### F. Her run'da otomatik güvenilirlik sinyalleri (Glio-Cartography'den, ADR-014)
- **Yöntem uyumu:** NNLS ile marker z-skor softmax arasında spot başına 1−JSD. Ortalama < 0.7 → rapora uyarı. Eski üründe Tangram–NNLS uyumu bağımsız GEO örneklerinde 0.27–0.37 idi; bu yüzden uyum her raporda görünür.
- **Bağımsız atlas kontrolü:** paket `atlas_reference` tanımlıysa (şu an GBM / Ivy GAP), tahmin edilen zonların referans gen ortalamaları atlas yapılarıyla z-skor korelasyonuna sokulur; diagonal ortalama ve top-1 eşleşme raporlanır. Zon marker genleri dışlanır; sentetik veride çalıştırılmaz. Eski üründe dört GSE237183 kesitinde diagonal ort. 0.21, top-1 0.45 idi (bir kesitte −0.09) — olumsuz sonuçlar saklanmaz.

## 3. Metrik eşikleri (Faz 1 önerisi)

Bu eşikler **bilim kurulu onayına** tabidir; hastalık paketi bazında değişebilir.

| Metrik | Minimum | Hedef | Not |
|---|---|---|---|
| Pseudospot JSD (ortalama) | < 0.20 | < 0.12 | Düşük daha iyi |
| Pseudospot Pearson (baskın tip) | > 0.75 | > 0.85 | |
| Hücre tipi F1 (makro) | > 0.65 | > 0.80 | |
| Held-out ARI | > 0.35 | > 0.55 | Annotasyon varsa |
| Marker enrichment AUROC | > 0.70 | > 0.85 | |
| Kalibrasyon ECE | < 0.15 | < 0.08 | |
| Stability (CV) | < 0.30 | < 0.15 | |
| Örnek başına spot | ≥ 500 | ≥ 1.500 | Kalite eşiği |
| Bağımsız çalışma | ≥ 3 | ≥ 5 | Paket kapsamı |

**Kapı kuralı:** Bir hastalık paketi, tüm "minimum"ları geçmeden `status: validated` olamaz. UI'da `beta` etiketiyle ve belirgin uyarıyla gösterilir.

## 4. Benchmark veri setleri (aday havuz)

> Lisans ve erişim koşulları her veri seti için ayrıca kaydedilecek. Aşağıdakiler **aday**dır; indirme/doğrulama yapılmadan "kullanıldı" denmez.

| Hastalık | Spatial adayları | scRNA-seq referansı | Not |
|---|---|---|---|
| Meme | 10x Visium breast cancer; HTAN breast | Tabula Sapiens, HCA, TCGA-derived | En olgun veri |
| Akciğer | 10x Visium lung cancer; HTAN lung | Human Lung Cell Atlas | |
| Kolorektal | 10x Visium colorectal; HTAN colon | Tabula Sapiens, HCA | |
| Prostat | Visium prostate çalışmaları; HTAN prostate | Tabula Sapiens, HCA | Veri daha sınırlı |
| Melanom | HTAN melanoma; GEO Visium | HCA, melanoma scRNA-seq | |
| GBM | 10x Visium GBM; GSE237183/GSE331374 (eski repodan) | GBM scRNA-seq atlasları | Eski ürünle kıyaslanabilir |

Ek kaynaklar: GEO, ArrayExpress, HTAN Data Portal, 10x Genomics public datasets, Human Cell Atlas, Tabula Sapiens.

## 5. Referans veri yönetimi

- Her referans için: kaynak URL, lisans, indirme tarihi, dosya hash'i, örnek sayısı, gen sayısı, hücre tipi etiketleri.
- `packages/disease-packs/references.yaml` (planlanan) içinde sürüm lenir.
- Aynı gen sembolü uzayına projeksiyon; eksik genler raporlanır.
- Batch etkisi: hastalık/çalışma bazında ayrı değerlendirme; harmonizasyon yöntemi belgelenir.

## 6. Model kartı şablonu

Her model/paket sürümü için:

```yaml
model: topiome-deconv-nnls
version: 0.1.0
trained_on: []            # eğitim yoksa boş
validated_on: []          # veri setleri + sürüm
metrics:
  jsd: null
  pearson: null
  f1: null
intended_use: "RUO; hücre kompozisyonu keşfi"
limitations:
  - "Düşük hücreli spotlarda güvenilmez"
  - "Referans atlas kapsamı dışındaki tipleri ayırt edemez"
  - "Klinik kullanım için değildir"
```

## 7. Benchmark çalıştırma

```bash
cd apps/api
uv run python -m analysis.benchmark --pack breast --dataset synthetic --out ../../data/benchmarks/breast
```

Çıktı: `metrics.json`, `report.html`, `run.log`, `manifest.json` (commit, sürüm, parametre).

## 8. Yayın öncesi kontrol listesi

- [ ] Veri lisansı kontrol edildi
- [ ] En az 3 bağımsız çalışma
- [ ] Pseudospot + held-out metrikleri eşik üstü
- [ ] Kalibrasyon raporlandı
- [ ] Marker enrichment doğrulandı
- [ ] Uzman spot-check yapıldı
- [ ] Model card yazıldı
- [ ] Sınırlamalar UI ve raporda görünüyor
- [ ] RUO uyarısı her yerde
- [ ] Versiyonlar (pack, pipeline, referans, commit) kaydedildi
- [ ] Bilim kurulu onayı

## 9. Açık bilim ve tekrarlanabilirlik

- Benchmark kodu ve sentetik veri üretimi açık; gerçek hasta verisi açık değil.
- Yayınlarda kullanılan parametreler ve sürümler ek olarak paylaşılır.
- "Topiome ile üretildi" ifadesi için sürüm numarası zorunlu.
