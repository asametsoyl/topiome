# Veri — Topiome

## 1. İlkeler

- Gerçek hasta verisi yalnızca kullanıcının org'unda, şifreli olarak saklanır.
- Repo'ya, demo'ya, log'a, prompt'a hasta verisi girmez.
- Her veri seti için kaynak, lisans, tarih, hash ve kullanım amacı kaydedilir.
- Veri silme talebi 30 gün içinde uygulanır; yedeklerden de temizlenir.

## 2. Desteklenen formatlar (Faz 1)

### 10x Visium
```
sample/
├── matrix.mtx.gz
├── barcodes.tsv.gz
├── features.tsv.gz
├── tissue_positions.csv
├── scalefactors_json.json
└── (opsiyonel) tissue_hires_image.png
```

### scRNA-seq referansı
- `.h5ad` (AnnData), gözlemlerde `cell_type` kolonu.
- Alternatif: `.rds` (Seurat) → Faz 2.

### Metadata (`sample.json`)
```json
{
  "sample_id": "S001",
  "disease": "breast",
  "tissue": "breast",
  "platform": "visium",
  "species": "human",
  "condition": "tumor",
  "sex": "female",
  "age_group": "50-59",
  "batch": "run-2026-01",
  "notes": ""
}
```

## 3. Yükleme kuralları

- Maksimum boyut: 2 GB (yapılandırılabilir).
- Zip veya klasör (tarayıcıda çoklu dosya).
- Zorunlu dosyalar eksikse anlaşılır hata; kısmi run başlatılmaz.
- Barcode'lar tissue_positions ile eşleşmeli; eşleşmeyenler raporlanır.
- Spot sayısı < 500 ise uyarı; < 100 ise run reddedilir (paket eşiği değişebilir).

## 4. Depolama düzeni

```
orgs/{org_id}/
  projects/{project_id}/
    samples/{sample_id}/
      raw/            # kullanıcı dosyaları (değişmez)
      derived/        # pipeline çıktıları
      report/         # HTML/PDF
      sample.json
```

- Ham dosyalar salt okunur; pipeline yeni klasöre yazar.
- Her çıktı `manifest.json` ile sürümlenir.
- Signed URL süresi: 15 dakika (indirme), 60 dakika (yükleme).

## 5. Kamuya açık veri kaynakları

| Kaynak | Kullanım | Lisans notu |
|---|---|---|
| 10x Genomics public datasets | Visium örnekleri | 10x kullanım koşulları |
| HTAN Data Portal | Tümör atlasları | Veri seti bazında |
| GEO | Visium/scRNA-seq | Veri seti bazında |
| Human Cell Atlas | Referans | HCA kullanım koşulları |
| Tabula Sapiens | Referans | CC BY 4.0 (doğrulanacak) |
| TCGA | Bulk referans | TCGA veri kullanım politikası |
| Wu et al. 2021 meme kanseri scRNA atlası (GEO GSE176078) | Meme referans imzaları (`references/breast_wu2021_v1_signatures.*`); test hastaları CID4465 ve CID4535 hariç | GEO kamu verisi; yayına atıf zorunlu |
| Wu et al. 2021 Visium + patolog anotasyonları (Zenodo 10.5281/zenodo.4739739) | GNN eğitimi/testi (hasta düzeyinde ayrım) | CC BY 4.0 |
| GEO GSE331374 (GSM9744831, GBM primer tümör Visium) | GBM gerçek veri kontrolü + Ivy GAP | GEO kamu verisi; atıf |
| Ivy GAP (Allen Institute) | GBM atlas kontrolü — `packages/disease-packs/references/ivygap_gbm_ish.json` (28 gen × 5 yapı, türetilmiş ortalamalar; Glio-Cartography'den) | Allen Institute Terms of Use — **ticari kullanım teyidi bekliyor** (`license_status: review_pending`, STATUS D5) |

> Her veri seti indirilmeden önce lisansı `references.yaml`'a yazılır; lisanssız veri kullanılmaz.

## 6. Sentetik demo verisi

- `scripts/generate_demo_data.py` ile üretilir.
- 1.200 spot, 6 hücre tipi, 5 domain, bilinen ground truth.
- Amaç: UI ve pipeline smoke test'i; bilimsel iddia değil.
- Demo verisi `data/demo/` altında; git'e girmez (üretim script'i girer).

## 7. Veri kalitesi kontrolleri

- Toplam UMI, gen sayısı, mitokondriyal oran.
- Spot–doku örtüşmesi (görüntü varsa).
- Barcode tekilliği.
- Referans gen kapsaması (ortak gen sayısı).
- Batch metadata zorunluluğu (mümkünse).

## 8. Gizlilik sınıfları

| Sınıf | Örnek | Saklama |
|---|---|---|
| Public | Yayınlanmış veri seti | Süresiz |
| Internal | Yayınlanmamış araştırma | 24 ay (varsayılan) |
| Sensitive | Hasta kimliğiyle eşleşebilir | 12 ay, org politikası |
| Restricted | Klinik veri | Faz 3; ayrı ortam |

## 9. Veri silme

- Kullanıcı sample/project siler → soft delete + 30 gün geri alma.
- 30 gün sonra hard delete; S3 versiyonları ve yedekler dahil.
- Audit log silme işlemini kaydeder (kim, ne zaman, ne).
