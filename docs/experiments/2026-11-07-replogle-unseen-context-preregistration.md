# Ön kayıt — Replogle-Nadig görülmemiş bağlam transferi

**Tarih:** 2026-11-07  
**Durum:** Test setleri açılmadan önce sabitlendi. K562 fold'u bu ön kayıttan önce keşifsel sinyal kontrolünde kullanıldığı için onaylayıcı kapıya dahil değildir.  
**Kod commit'i:** Bu belge ile aynı commit'teki `scripts/perturbation/benchmark_replogle_transfer.py`.

## 1. Soru

Ölçülmüş perturbasyon etkileri, daha önce görülmemiş bir hücre hattına basit bir doğrusal ölçekleme ile taşınabilir mi; bu transfer, “değişiklik yok” ve gen-ortalaması baseline'larından daha iyi mi?

Bu, “sanal hücre” veya görülmemiş perturbasyon iddiası değildir. Yalnız **görülmemiş bağlam + daha önce ölçülmüş perturbasyon** görevini sınar.

## 2. Veri

- Kaynak: `arcinstitute/PIE_replogle_nadig_essential` preprocessed array'leri; Replogle et al. 2022 (K562, RPE1) ve Nadig et al. 2025 (HepG2, Jurkat) CRISPRi essential-gene Perturb-seq ekranları.
- Boyut: 5.459 (bağlam, perturbasyon) satırı; 6.642 gen; 4 hücre hattı; 1.857 perturbasyon.
- Kullanılan dosyalar: `lfc_true.npy`, `tested.npy`, `ctrl_means.npy`, `meta.json`, `ctx_ids.npy`, `pert_ids.npy`.
- Split kaynağı: `arcinstitute/PIE_splits`, `replogle_wdataset/unseen_ctx/<fold>/{train,val,test}.json`.
- Lisans: Hugging Face veri kartında lisans alanı yok. Orijinal çalışmalar kamuya açık; türev setin ticari kullanım koşulları doğrulanmadı. Bu koşu yalnız araştırma amaçlıdır ve ticari ürün iddiasına temel yapılmaz. Kayıt: `data/perturbation/raw/pie-replogle-nadig-essential/preprocessed/manifest.json`.

## 3. Split tasarımı

Her fold için:

- **Eğitim:** diğer üç hücre hattındaki perturbasyonlar (`train.json`).
- **Doğrulama:** aynı üç hücre hattından ayrılmış perturbasyonlar (`val.json`). Yalnız beta seçimi için kullanılır.
- **Test:** tamamen dışarıda tutulan hücre hattı (`test.json`).

Onaylayıcı fold'lar: **RPE1, HepG2, Jurkat**. Bu üç test seti bu belge yazılırken açılmadı. K562 fold'u keşifsel analizde kullanıldı; sonuçları ayrı raporlanır ve başarı kapısına sayılmaz.

Sızıntı kontrolleri:

- Test hücre hattı eğitimde veya doğrulamada bulunamaz.
- Test satırları eğitim/doğrulama satırlarıyla çakışamaz.
- Beta yalnız doğrulama satırlarından seçilir; test etiketleri beta, özellik veya eşik seçiminde kullanılmaz.

## 4. Baseline'lar ve aday

Tüm tahminler log2 fold-change uzayındadır. Yalnız test edilmiş ve sonlu gen değerleri ölçülür.

1. **Zero:** tüm genlerde 0.
2. **Global mean:** eğitim satırlarında gen başına ortalama etki.
3. **Unscaled perturbation mean:** perturbasyonun eğitim bağlamlarındaki gen başına ortalama etkisi; eğitimde hiç yoksa global ortalamaya düşer.
4. **Centered perturbation mean:** `perturbation_mean − global_mean`.
5. **Scaled transfer (aday):** `beta × (perturbation_mean − global_mean)`.
   - Beta, `[0, 1]` aralığında 0,05 adımlı sabit ızgaradan seçilir.
   - Seçim ölçütü: doğrulama satırlarında eşit-ağırlıklı ortalama satır RMSE'si.
   - Eşitlik durumunda daha küçük beta (daha fazla büzülme) seçilir.
6. **Scaled uncentered (duyarlılık):** `beta × perturbation_mean`; beta aynı yöntemle seçilir. Aday değil, duyarlılık analizidir.

## 5. Ölçümler

Birincil ölçüt: **eşit-ağırlıklı ortalama satır RMSE** (her bağlam–perturbasyon satırı eşit).

İkincil ölçütler:

- havuzlanmış RMSE;
- satır başına Pearson korelasyonunun medyanı;
- mutlak etkide top-50 örtüşmesi;
- işaret doğruluğu (yalnız `|true log2FC| > 0.1` girişlerde);
- perturbasyon başına RMSE dağılımı ve başarısız satırlar;
- test satırları üzerinde 2.000 yeniden örneklemeli paired bootstrap ile RMSE farkı için %95 aralık.

## 6. Başarı kuralı

Üç dokunulmamış fold'un **en az ikisinde** aşağıdaki koşulların **tümü** sağlanırsa kapı geçer:

1. Zero baseline'ına göre eşit-ağırlıklı satır RMSE'sinde en az **%3 göreli iyileşme**;
2. Paired bootstrap ile RMSE farkının %95 aralığının tamamı sıfırın üstünde (zero − model > 0);
3. Medyan satır korelasyonu **> 0.20**;
4. Top-50 mutlak etki örtüşmesinde zero'ya göre en az **+0.02**;
5. Global mean baseline'ından daha kötü olmama.

Ek olarak:

- Üç fold'un ikisinde beta 0 ile 1 arasında ve 0'dan büyük olmalı; beta=0 seçilen fold başarısız sayılır.
- Sonuç fold'lar arasında tutarlı değilse, yalnız başarılı fold'lara daraltılır; genel iddia kurulmaz.
- Hiçbir fold'da test RMSE'si zero'dan kötü değilse ve en az iki fold'da anlamlı iyileşme yoksa kapı **başarısız** sayılır ve bu hat durdurulur.

## 7. Yorum sınırı

Bu kapı geçse bile:

- görülmemiş perturbasyon tahmini kanıtlanmış olmaz;
- tek hücre dağılımı, doz/zaman veya başka assay'ler kapsanmaz;
- prospektif deney veya klinik fayda gösterilmez;
- ticari kullanım hakkı doğrulanmamıştır;
- “sanal hücre” iddiası kurulamaz.

Kapı geçerse bir sonraki ayrı ön kayıt, görülmemiş perturbasyon için hedef-gen yan bilgisi (ESM2/STRING/DepMap gibi) kullanan doğrusal modeli sınar. Kapı başarısız olursa bu veri ve görevle model geliştirme durdurulur; daha zengin veri veya farklı bilimsel soru olmadan ilerlenmez.

## 8. Çıktı ve tekrar

- Kod: `scripts/perturbation/benchmark_replogle_transfer.py`
- Çıktı: `data/perturbation/processed/replogle-unseen-ctx-gate.json`
- Hesaplama: yalnız CPU, NumPy; test etiketleri beta seçiminde okunmaz.
- Rapor: `docs/VALIDATION.md` ve `docs/STATUS.md` içine sonuçlar eklenecek.
