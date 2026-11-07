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

## 2b. İkinci veri bileşeni — PIE Replogle-Nadig essential Perturb-seq

- Kaynak: [arcinstitute/PIE_replogle_nadig_essential](https://huggingface.co/datasets/arcinstitute/PIE_replogle_nadig_essential); canonical split'ler [arcinstitute/PIE_splits](https://huggingface.co/datasets/arcinstitute/PIE_splits).
- Deneyler: Replogle et al. 2022 (K562, RPE1) ve Nadig et al. 2025 (HepG2, Jurkat) CRISPRi essential-gene Perturb-seq ekranları.
- Yerel subset: `data/perturbation/raw/pie-replogle-nadig-essential/preprocessed/`; `lfc_true.npy`, `tested.npy`, `ctrl_means.npy`, `ctx_ids.npy`, `pert_ids.npy`, `meta.json`, `contexts.yaml`; yaklaşık 327 MB. 5.459 (bağlam, perturbasyon) satırı, 6.642 gen, 4 hücre hattı, 1.857 perturbasyon.
- Split'ler: `data/perturbation/raw/pie-splits/`; 36 JSON dosyası ve bir README (4 fold × 3 setting × 3 part). `unseen_ctx` bir hücre hattını tümüyle dışarıda tutar, `unseen_pert` perturbasyonları dışarıda tutar, `unseen_ctx_pert` ikisini birlikte test eder. Kullanılan fold'larda split satırları, bağlam izolasyonu ve test perturbasyon kapsaması doğrulandı.
- Lisans: Hugging Face veri kartında lisans alanı yok. Orijinal çalışmalar kamuya açık, ancak türev setin ticari kullanım koşulları doğrulanmadı. Kaynak/hash kaydı: `data/perturbation/raw/pie-replogle-nadig-essential/preprocessed/manifest.json`. Yalnız araştırma amaçlıdır; ticari iddia veya ürün eğitimi için kullanılmaz.
- Kullanım: `unseen_ctx` ön kayıtlı transfer kapısı (onaylayıcı fold'lar HepG2/Jurkat/RPE1, keşifsel K562); `unseen_pert` keşifsel negatif kontrol. Ayrıntı `docs/VALIDATION.md` bölüm 11–12.
- Sınır: aggregate log2 fold-change; tek hücre dağılımı, doz/zaman, perturbasyon verimliliği ve bağımsız biyolojik tekrar yok. Dört hücre hattı da aynı assay ailesindedir; başka platform/assay dış testi değildir.

### 2b.1 PIE knowledge sources — yalnız keşifsel

- `arcinstitute/PIE_sources` ESM2 (1.280 boyut), STRING (512) ve DepMap (1.186) embedding'leri `data/perturbation/raw/pie-sources/` altında tutulur.
- 1.857 perturbasyonun sırasıyla 47/22/53'ünde kapsam eksiktir; eksikler eğitim perturbasyon sütun ortalamasıyla doldurulur.
- Veri kartlarında lisans alanı yok. DepMap zaten perturbasyon yanıtı/essentiality verisi olduğu için olası sızıntı riski taşır. Bu kaynaklar onaylayıcı bağlam kapısına sokulmadı; yalnız `unseen_pert` keşifsel kontrolünde kullanıldı ve ticari kullanım için uygun sayılmaz.

## 2d. Dördüncü veri bileşeni — PIE Tahoe-100M

- Kaynak: `arcinstitute/PIE_tahoe100m`, commit `0d5089a2b4f13239383f135ef8e2db2462a00808`, `preprocessed/` (yalnız `lfc_true.npy`, `tested.npy`, `ctx_ids.npy`, `pert_ids.npy`, `meta.json`, `contexts.yaml`; `fdr`, `fold_changes`, `delta_p` indirilmedi).
- Özgün çalışma: Zhang et al. 2025, Tahoe-100M; 379 bileşik × 3 doz = 1.137 koşul, 50 kanser hücre hattı, DMSO kontrolü. 56.827 satır, 18.151 gen.
- SHA-256 (meta.json `array_sha256` ile eşleşti): `lfc_true.npy` `2deab02282e67c812daef3e3836ccd2b11c5eb2deb522f062de1d3ff63cf87ad`, `tested.npy` `b52a8e7934eacab61d7a651e0f09875612df8c6e6f9d6e95c3eeb0021aaf6a81`, `ctx_ids.npy` `d6fe20bb…`, `pert_ids.npy` `39b3dcb0…`.
- Lisans: upstream `tahoebio/Tahoe-100M` CC0 1.0; PIE aynasının kartında lisans alanı yok. Yalnız araştırma amaçlı kullanıldı.
- Yerel: `data/perturbation/raw/pie-tahoe100m/preprocessed/` (~9,3 GB, git dışında). Etiket dosyaları ön kayıt commit'i `9a9c118`'den sonra indirildi.
- Sınır: aggregate log2 fold-change; tek hücre dağılımı ve doz-yanıt eğrisi kullanılmadı; hücre hatları kanser hatlarıdır.

## 2c. Üçüncü veri bileşeni — PIE X-Atlas/Orion

- Kaynak: [arcinstitute/PIE_x_atlas_orion](https://huggingface.co/datasets/arcinstitute/PIE_x_atlas_orion), commit `abfa3da0f3bb98c9df9c90082386ed0c7c9282d3`, `preprocessed/` array'leri.
- Özgün çalışma: Huang et al. 2025, X-Atlas/Orion genome-wide CRISPRi Perturb-seq; HCT116 ve HEK293T.
- Yerel subset: `data/perturbation/raw/pie-x-atlas-orion/preprocessed/`; `lfc_true.npy` (2,36 GB), `tested.npy` (295 MB), `meta.json`, `contexts.yaml`, `ctx_ids.npy`, `pert_ids.npy`, `ctrl_means.npy`; toplam yaklaşık 2,65 GB. `de/` parquet dosyaları indirilmedi.
- Boyut: 13.284 (bağlam, perturbasyon) satırı; 22.182 gen; 2 bağlam; 10.007 perturbasyon. İki bağlamda ortak 3.277 perturbasyon. HCT116 8.987 satır, HEK293T 4.297 satır.
- Lisans: **CC BY-NC-SA 4.0**; ticari kullanım yok. Kaynak/hash kaydı: `data/perturbation/raw/pie-x-atlas-orion/preprocessed/manifest.json`. `lfc_true.npy` SHA-256 `078cb346a4e3a025edc3d4ca1e9ba6c8717ee7b54d73941591838b4d21b64ec8`; `tested.npy` `fcb837692e06e1e712c6b3d6cc3602497e2fdc1211598ce73fcafa0eedd79e57`.
- Kullanım: bağımsız görülmemiş-bağlam transferi tekrarı; iki simetrik fold (`hct116_to_hek293t`, `hek293t_to_hct116`), 3.277 ortak perturbasyon, beta=0,25 önceden sabit. Sonuç negatif; ayrıntı `docs/VALIDATION.md` bölüm 13. Bu veri seti ticari ürün/eğitim için kullanılmaz.
- Sınır: aggregate log2 fold-change; tek hücre dağılımı, doz/zaman, perturbasyon verimliliği ve bağımsız biyolojik tekrar yok. Orion ve Replogle-Nadig aynı CRISPRi Perturb-seq ailesindendir; assay platformu bağımsızlığı yoktur.

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
