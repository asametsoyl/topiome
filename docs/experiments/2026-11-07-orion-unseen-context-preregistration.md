# Ön kayıt — X-Atlas/Orion görülmemiş bağlam transferi (bağımsız tekrar)

**Tarih:** 2026-11-07  
**Durum:** Bu belge ve aynı commit'teki benchmark kodu, Orion `lfc_true.npy` indirilmeden ve hiçbir Orion test metriği hesaplanmadan önce sabitlendi. Beta Orion test etiketlerinden seçilmez.  
**Kod commit'i:** Bu belge ile aynı commit'teki `scripts/perturbation/benchmark_orion_transfer.py` ve `packages/analysis/analysis/perturbation.py` değişiklikleri.

## 1. Soru ve kapsam

Replogle-Nadig verisinde görülen dar görülmemiş-bağlam transfer sinyali, bağımsız bir public CRISPRi Perturb-seq veri setinde ve farklı hücre hatlarında tekrarlanıyor mu?

Bu, “sanal hücre”, görülmemiş perturbasyon veya yeni assay teknolojisi iddiası değildir. Yalnız **daha önce ölçülmüş perturbasyon etkilerinin, görülmemiş bir hücre hattına basit ölçekli transferi** sınanır. Orion da Replogle-Nadig gibi CRISPRi Perturb-seq ailesindendir; bağımsızlık veri seti, laboratuvar ve hücre hatları düzeyindedir, assay platformu düzeyinde değildir.

## 2. Veri ve lisans

- Kaynak: `arcinstitute/PIE_x_atlas_orion`, commit `abfa3da0f3bb98c9df9c90082386ed0c7c9282d3`, `preprocessed/` array'leri.
- Özgün çalışma: Huang et al. 2025, X-Atlas/Orion genome-wide CRISPRi Perturb-seq; HCT116 ve HEK293T.
- Boyut: 13.284 (bağlam, perturbasyon) satırı; 22.182 gen; 2 bağlam; 10.007 perturbasyon. HCT116 8.987 satır, HEK293T 4.297 satır. İki bağlamda ortak 3.277 perturbasyon vardır.
- Kullanılan dosyalar ve SHA-256:
  - `lfc_true.npy`: `078cb346a4e3a025edc3d4ca1e9ba6c8717ee7b54d73941591838b4d21b64ec8`
  - `tested.npy`: `fcb837692e06e1e712c6b3d6cc3602497e2fdc1211598ce73fcafa0eedd79e57`
  - `ctx_ids.npy`: `90ad5397492619cac657be7a916de3c95c0b51628c3e5d91cbbd281280a2f88a`
  - `pert_ids.npy`: `c6b28cf5551da18d25f83225c55037c08d586a2856aacf37b5a68c50a8246ee6`
  - `meta.json`: `16b83a176823c2e87b5ccdfb6fd2cc8283e60f860e1797acdc9d01e6aa77398c`
  - `contexts.yaml`: `13b724c3de36980ddc200f34fbd424acbd1e4ac55bfa89177ee395927d40bbc3`
  - `ctrl_means.npy`: `08aa13a9cbbd2012936123914c948b662c263d5a7844fe4c41d0c8d3f37c77b3`
- Lisans: CC BY-NC-SA 4.0. Ticari kullanım yok; bu koşu yalnız araştırma amaçlıdır ve ticari ürün iddiasına temel yapılmaz.
- Yerel kayıt: `data/perturbation/raw/pie-x-atlas-orion/preprocessed/`; indirme ve hash doğrulaması manifestte tutulur.

## 3. Split tasarımı

Ortak perturbasyon kümesi `P`, HCT116 ve HEK293T perturbasyon adlarının kesişimidir. `|P| = 3.277`. Sıralı `P` adlarının SHA-256 değeri:

`af2997b213db7ff95bfc6da6744e017d6a4e4305472fa1fba7d5d1ce9a1603dd`

İki simetrik fold:

| Fold | Eğitim bağlamı | Test bağlamı | Eğitim satırı | Test satırı |
|---|---|---|---:|---:|
| `hct116_to_hek293t` | HCT116 | HEK293T | 3.277 | 3.277 |
| `hek293t_to_hct116` | HEK293T | HCT116 | 3.277 | 3.277 |

- Her fold'da eğitim, eğitim bağlamındaki `P` perturbasyonlarının tüm satırlarıdır; test, test bağlamındaki aynı `P` perturbasyonlarının tüm satırlarıdır.
- **Doğrulama seti yoktur.** Beta, Orion verisine bakılmadan 0,25 olarak sabitlenmiştir. Gerekçe: Replogle-Nadig ön kayıtlı kapısında doğrulama ile seçilen beta HepG2/Jurkat/K562'de 0,25, RPE1'de 0,30 idi; 0,25 medyan/çoğunluk değeridir.
- Test perturbasyon kapsaması tasarım gereği 1,0'dır. Test bağlamı eğitimde yoktur; eğitim ve test satırları çakışmaz.
- İki fold aynı perturbasyon kümesini paylaşır ve birbirinin simetriğidir; bağımsız biyolojik tekrar sayılmaz. Veri seti düzeyinde iddia için iki fold'un birlikte sonucu gerekir.

## 4. Aday ve baseline'lar

Tüm tahminler log2 fold-change uzayındadır. Yalnız test satırında test edilmiş ve sonlu gen değerleri ölçülür.

- `g`: eğitim satırlarının gen başına ortalama LFC'si (global mean).
- `m_p`: `p` perturbasyonunun eğitim bağlamındaki gen başına ortalama LFC'si. Eğitim bağlamında her perturbasyon için tek satır olduğundan, `p` satırında test edilmemiş genler `g` ile doldurulur. Böylece bilgi olmayan genlerde aday, global mean'e döner.
- **Aday (beta=0,25):** `g + 0,25 × (m_p − g)`.

Baseline'lar:

1. **Zero:** tüm genlerde 0.
2. **Global mean:** `g`.
3. **Unscaled perturbation mean:** `m_p`.
4. **Centered perturbation mean:** `m_p − g`.
5. **Duyarlılık beta'ları:** 0,10; 0,15; 0,20; 0,30; 0,35; 0,40; 0,50; 0,75; 1,00. Bunlar yalnız tanımlayıcıdır; birincil aday 0,25'tir ve başarısız birincil sonucu kurtaramaz.

İkincil tanımlayıcı analizler (birincil karara girmez):

- eğitim etkisi büyüklüğüne göre üst çeyrekteki perturbasyonlar (seçim yalnız eğitim verisinden);
- eğitim ve test satırında birlikte test edilmiş genlerde (ortak destek) skor;
- 20 etiket permütasyonu (eğitim perturbasyon etiketleri karıştırılır; sabit seed 20261107) ile negatif kontrol.

## 5. Ölçümler

Birincil ölçüt: **eşit-ağırlıklı ortalama satır RMSE'si** (her bağlam–perturbasyon satırı eşit).

İkincil ölçütler:

- havuzlanmış RMSE;
- satır başına Pearson korelasyonunun medyanı;
- mutlak etkide top-50 örtüşmesi (zero ve global mean'e göre);
- işaret doğruluğu (yalnız `|true log2FC| > 0,1` girişlerde);
- satır RMSE'sinin çeyrekleri ve adayın zero/global mean'i yendiği satır oranı;
- test satırları üzerinde 2.000 yeniden örneklemeli paired bootstrap ile RMSE farkı için %95 aralık (birim: bağlam–perturbasyon satırı, seed 20261107);
- fold bazında ve iki fold birleşik tanımlayıcı özet.

## 6. Başarı kuralı

### A. Sayısal transfer kapısı

Her iki fold'da aşağıdakilerin **tümü** sağlanırsa sayısal transfer tekrarlanmış sayılır:

1. Zero baseline'ına göre eşit-ağırlıklı satır RMSE'sinde en az **%3 göreli iyileşme**;
2. Paired bootstrap ile `zero − aday` RMSE farkının %95 aralığının tamamı sıfırın üstünde;
3. Medyan satır korelasyonu **> 0,20**;
4. Adayın ortalama satır RMSE'si global mean'den **kötü değil**;
5. Adayın medyan satır korelasyonu global mean'inkinden **küçük değil**;
6. Beta 0,25 olarak sabit ve 0'dan büyük.

### B. Sıralama kapısı

Her iki fold'da aşağıdakilerin **tümü** sağlanırsa sıralama da tekrarlanmış sayılır:

7. Adayın ortalama top-50 örtüşmesi global mean'inkinden **küçük değil**;
8. Adayın ortalama top-50 örtüşmesi zero'ya göre en az **+0,02**.

### C. Genel karar

- **Tam tekrar:** A ve B birlikte 2/2 fold'da geçerse.
- **Yalnız sayısal tekrar:** A 2/2 geçer, B geçmezse. Bu durumda gen sıralaması iddiası kurulmaz.
- **Kısmi sonuç:** A yalnız bir fold'da geçerse. Genel tekrar iddiası kurulmaz; sonuç fold bazında raporlanır.
- **Başarısız:** A iki fold'da da geçmezse. Bu veri ve görevle görülmemiş-bağlam hattı durdurulur; beta veya metrik değiştirilerek aynı test setinde yeniden denenmez.
- Duyarlılık beta'ları, permütasyon kontrolü veya ikincil alt kümeler birincil kararı değiştiremez.

## 7. Yorum sınırı

Bu kapı geçse bile:

- görülmemiş perturbasyon tahmini kanıtlanmış olmaz;
- tek hücre dağılımı, doz/zaman, başka assay platformu veya başka hücre tipi kapsanmaz;
- prospektif deney, klinik fayda veya ticari kullanım gösterilmez;
- Orion ve Replogle-Nadig aynı CRISPRi Perturb-seq ailesindendir; assay teknolojisi bağımsızlığı yoktur;
- top-50 sıralaması zayıf bir metriktir; asıl kontrol global mean'e göre sıralamadır;
- ortak küme birçok zayıf/sıfıra yakın etki içerir; negatif sonuç, güçlü etkili perturbasyonlarda sinyal yokluğu anlamına gelmez. Üst çeyrek analizi yalnız tanımlayıcıdır;
- iki hücre hattı da kanser hücresi hattıdır; primer hücre, donör veya doku iddiası yoktur;
- CC BY-NC-SA 4.0 lisansı nedeniyle ticari kullanım yoktur.

## 8. Çıktı ve tekrar

- Kod: `scripts/perturbation/benchmark_orion_transfer.py`
- Analiz yardımcıları: `packages/analysis/analysis/perturbation.py`
- Çıktı: `data/perturbation/processed/orion-unseen-ctx-gate.json`
- Hesaplama: CPU, NumPy; beta ve split Orion test etiketlerinden bağımsız.
- Rapor: `docs/VALIDATION.md`, `docs/STATUS.md`, `docs/DATA.md`, `docs/PRODUCT.md`, `docs/CHANGELOG.md` ve `README.md` içine sonuç eklenecek.
- Yeniden üretim:

```bash
PYTHONPATH=packages/analysis apps/api/.venv/bin/python scripts/perturbation/benchmark_orion_transfer.py --commit "$(git rev-parse --short HEAD)"
```
