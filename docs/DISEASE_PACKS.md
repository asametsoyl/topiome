# Hastalık Paketleri — Topiome

## 1. Amaç

Hastalığa özgü bilgiyi koddan ayırmak. Yeni bir hastalık eklemek; YAML + referans veri + benchmark + uzman onayı işidir. Kod değişmez.

## 2. Klasör yapısı

```
packages/disease-packs/
├── schema.json
├── references.yaml
├── breast.yaml
├── lung.yaml
├── colorectal.yaml
├── prostate.yaml
├── melanoma.yaml
├── glioblastoma.yaml
└── README.md
```

## 3. Şema (özet)

```yaml
id: breast
version: 0.1.0
status: draft            # draft | beta | validated | deprecated
name: Breast Cancer
short_name: Breast
tissue: breast
data_richness: high      # high | medium | low
description: >
  ...
aliases: [BRCA, mammary carcinoma]
reference:
  scrna_sources: []
  spatial_sources: []
  minimum_samples: 3
cell_types:
  - id: epithelial
    name: Epithelial
    markers: [EPCAM, KRT8, KRT18]
    color: "#E8B4B8"
  - id: immune
    ...
zones:
  - id: tumor_core
    name: Tumor core
    markers: [EPCAM, KRT8]
    color: "#FF6B6B"
  - id: stroma
    ...
targets:
  - gene: ERBB2
    name: HER2
    rationale: "..."
    evidence_level: established | emerging | exploratory
report:
  title: Breast Cancer Spatial Atlas
  sections: [summary, qc, composition, domains, targets, limitations]
validation:
  metrics: {}
  last_run: null
  approved_by: null
```

Tam şema: `packages/disease-packs/schema.json` (oluşturulacak).

## 4. Durumlar

| Durum | Anlam | UI |
|---|---|---|
| `draft` | Geliştiriliyor; sonuç üretilebilir ama uyarılı | "Draft — not validated" |
| `beta` | Baseline çalışıyor; validasyon eksik | "Beta — research preview" |
| `validated` | Minimum metrikler + uzman onayı | "Validated for research use" |
| `deprecated` | Yeni sürüm var | Arşiv |

**Kural:** `validated` olmayan paket, pazarlamada doğruluk iddiasıyla kullanılamaz.

## 5. İlk 6 paket

| Paket | Veri zenginliği | Öncelik | Gerekçe |
|---|---|---|---|
| Breast | Yüksek | P0 | En çok Visium + scRNA-seq; iyi başlangıç |
| Colorectal | Yüksek | P0 | HTAN + 10x; net epitel/stroma/immün yapı |
| Lung | Yüksek | P1 | Human Lung Cell Atlas; tümör heterojenliği |
| Melanoma | Orta-Yüksek | P1 | İmmünoterapi bağlamı; HTAN |
| Prostate | Orta | P2 | Veri daha sınırlı; benign/tümör ayrımı zor |
| Glioblastoma | Orta | P2 | Eski ürünle kıyas; GNN/zone geçmişi |

## 6. Ortak hücre tipleri (başlangıç sözlüğü)

| ID | Ad | Örnek markerlar |
|---|---|---|
| epithelial | Epithelial | EPCAM, KRT8, KRT18, KRT19 |
| tumor | Tumor cells | hastalığa özgü (aşağıda) |
| fibroblast | Fibroblast | COL1A1, COL1A2, DCN, PDGFRB |
| endothelial | Endothelial | PECAM1, VWF, CDH5 |
| t_cell | T cell | CD3D, CD3E, CD2, CD8A |
| b_cell | B cell | CD79A, MS4A1, CD19 |
| macrophage | Macrophage | CD68, CD163, CSF1R |
| dendritic | Dendritic | CD1C, LAMP3, ITGAX |
| neutrophil | Neutrophil | FCGR3B, S100A8, S100A9 |
| mast | Mast | TPSAB1, CPA3, MS4A2 |
| adipocyte | Adipocyte | ADIPOQ, PLIN1, FABP4 |
| smooth_muscle | Smooth muscle | ACTA2, MYH11, DES |
| neuron | Neuron | RBFOX3, SYT1, SNAP25 |
| oligodendrocyte | Oligodendrocyte | MBP, PLP1, MOG |
| astrocyte | Astrocyte | GFAP, AQP4, ALDH1L1 |

Hastalık paketleri bu sözlüğü genişletir; çakışan ID'ler `schema.json` ile doğrulanır.

## 7. Bölge (zone) tanımları

Bölgeler hastalığa özgüdür ve **patolojik olarak yorumlanabilir** olmalıdır. Örnek:

- **Breast:** tumor core, invasive margin, stroma, immune aggregate, normal gland, necrosis.
- **Colorectal:** tumor core, invasive front, lymphoid aggregate, normal mucosa, stroma, necrosis.
- **Lung:** tumor, stroma, immune, necrosis, alveolar, airway.
- **Prostate:** tumor, benign gland, stroma, immune, perineural.
- **Melanoma:** tumor, invasive margin, immune, stroma, necrosis.
- **GBM:** pseudopalisading necrosis, microvascular proliferation, leading edge, infiltrative tumor, normal brain.

> Not: Bu etiketler **araştırma amaçlı mekânsal domain**'lerdir; patolojik tanı değildir.

## 8. İlaç hedefi skorlama

- Hedef listesi hastalık paketinde; her hedef için gen, yolak, kanıt düzeyi, hücre tipi/bölge ilişkisi.
- Skor = hedefin ilgili hücre tipi/bölgede ifade ağırlığı × kapsam × belirsizlik cezası.
- Çıktı: "research prioritization score", tedavi önerisi değil.
- Kanıt düzeyi `exploratory` olan hedefler ayrı gösterilir.

## 9. Paket ekleme süreci

1. Literatür + veri taraması; `data_richness` değerlendirmesi.
2. `references.yaml`'a kaynak ekle; lisans/URL/tarih.
3. YAML paketi yaz; `python scripts/validate_packs.py`.
4. Marker/zone setini uzmanla gözden geçir.
5. Benchmark çalıştır; metrikleri `validation.metrics`'e yaz.
6. `status: beta` ile UI'a al; geri bildirim topla.
7. Eşikler + uzman onayı → `validated`.
8. Model card + changelog.

## 10. Sürümleme

- SemVer: `major.minor.patch`.
- Marker/zone değişikliği = minor; metrik/validate = minor; hata düzeltme = patch.
- Eski run'lar, çalıştıkları paket sürümünü korur; yeniden üretim için sürüm pinlenir.
