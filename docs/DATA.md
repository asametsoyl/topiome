# Veri — Topiome perturbasyon yanıtı araştırması

## 1. Aktif veri gereksinimi

İlk model deneyi için tek hücre kontrol ve perturbasyon sayımları gerekir. Dataset düzeyinde en az şu metadata kaydedilmeden örnek analize girmez:

| Alan | Amaç |
|---|---|
| Dataset, makale, kaynak URL ve DOI/erişim numarası | Atıf ve tekrar edinim |
| Kullanım lisansı / veri kullanım koşulu | Ticari ve araştırma kullanım sınırları |
| Ham ve işlenmiş dosya hash'i | İçerik bütünlüğü |
| Perturbasyon kimliği / hedef / tür | Müdahaleyi tanımlamak |
| Kontrol grubu ve kılavuz/compound eşlemesi | Müdahale etkisinin referansı |
| Hücre hattı/donör/başlangıç durumu | Bağlam bazlı dış test |
| Assay, batch, zaman, doz ve perturbasyon verimliliği | Domain kayması ve etki yorumu |
| Gen/feature kimliği ve normalizasyon | Yöntem uyumu |
| Biyolojik tekrar / sample metadata | Doğru istatistik birimi |

Veri hücre başına satırlardan ibaret değildir: gözlem, perturbasyon, kontrol, hücre bağlamı, donör/örnek, teknik batch, assay ve ham sayım bilgisi doğru bağlanmalıdır. Yalnız ortak gen adları eşleşiyor diye farklı çalışmalar doğrudan birleştirilmez.

## 2. İlk veri bileşeni — Arc VCC 2025 / PIE işlenmiş etkiler

- Kaynak deney: Arc Virtual Cell Challenge 2025, H1 hESC CRISPRi Perturb-seq; yaklaşık 300 bin hücre ve 300 hedef içeren challenge bileşeni.
- Kullanılan yerel subset: Arc Institute PIE aynasındaki preprocessed aggregate arrays; 12.286 gen, 190 perturbasyon satırı (146 train / 44 validation), 49.3 MB. Ham hücre düzeyi `.h5ad` dosyaları indirilmedi.
- Lisans: Arc Virtual Cell Atlas sayfası VCC 2025 bileşenini CC0 1.0 olarak listeliyor. Hugging Face aynasının kartında şu an ayrı bir lisans alanı görünmüyor; kullandığımız kaynak/metadata bu farkı kaydediyor. Kaynak ve hash manifesti: `data/perturbation/raw/arc-vcc-2025-pie/manifest.json`.
- Kullanım kapsamı: yalnız aynı H1 bağlamında görülmemiş perturbasyon hedefleri üzerinde aggregate log2 fold-change baseline fizibilitesi. Tek hücre dağılımı, yeni hücre bağlamı veya deney faydası ölçülmedi.
- İşlenmiş ayna notu: [ArcInstitute/PIE_arc_vcc_25](https://huggingface.co/datasets/arcinstitute/PIE_arc_vcc_25); upstream veri ve challenge tanımı [Arc Virtual Cell Atlas](https://arcinstitute.org/tools/virtualcellatlas) ile [Arc VCC 2025 deposunda](https://github.com/ArcInstitute/arc-virtual-cell-atlas/tree/main/virtual-cell-challenge) yer alır.

## 3. Kaynak havuzu ve sonraki adaylar

**Arc Virtual Cell Atlas** açık tek hücre ve perturbasyon koleksiyonları sağlıyor: <https://arcinstitute.org/tools/virtualcellatlas>. Arc sayfası VCC 2025 ile Tahoe-100M verilerini CC0 olarak listeliyor; her bileşen için kayıt, README, alıntı ve lisans ayrı doğrulanmalı. Tüm koleksiyon MVP için indirilmeyecek. Önce küçük ve değerlendirilebilir tek bir görev seçilecek.

Ek kaynaklar (ör. scPerturb, GEO, Figshare, Zenodo) ancak dataset bazında lisans/erişim hakkı, kontrol koşulları ve metadata incelendikten sonra kabul edilir. GEO'da erişilebilir olmak yeniden dağıtım veya ticari eğitim hakkının kanıtı değildir.

## 4. Yerel dizin

```text
data/
  perturbation/
    README.md
    raw/          # yeniden edinilebilir kaynak dosyalar, git dışı
    processed/    # normalize/filtrelenmiş türevler, git dışı
    manifests/    # metadata, split ve checksum kayıtları; hassas olmayan küçük metin
```

`data/` içeriği git'e girmez. Ham verinin kaynağı, lisansı, tarihi, hash'i ve işleme kodu manifestte tutulur. Kullanıcı/proje verisi research benchmark klasörüne alınmaz. Hiçbir gerçek hasta veya kimlik bilgisi repo, demo seed, ekran görüntüsü ya da log içine girmez.

## 5. Önceden var olan veriler

2026-11-07 ürün pivotu sırasında yerel 10x Visium / scRNA spatial ham ve türetilmiş dosyaları temizlendi (yaklaşık 9.2 GB). Bunlar yeni perturbasyon görevine girdi değildir ve public source'lardan yeniden edinilebilir. Eski spatial analiz kodu ile küçük model kartı/raporlar kaynak geçmişinde ve `docs/legacy/spatial/` altında korunuyor.

## 6. Kaynak kaydı şablonu

```yaml
dataset_id: arc-vcc-2025-<task>
source_url: https://arcinstitute.org/tools/virtualcellatlas
publication_doi: null
retrieved_at: null
license: CC0-1.0 # yalnız dataset bileşeninin kaynağı bunu teyit ederse
file_sha256: null
assay: null
species: human
cell_contexts: []
perturbation_types: []
controls: []
processing_version: null
use_status: review_pending
```

`review_pending` durumundaki veriler eğitim, demo veya ürün iddiasında kullanılmaz.
