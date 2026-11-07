# Ön kayıt — Pilot ile kalibre edilmiş bağlam transferi (Tahoe-100M)

**Tarih:** 2026-11-08  
**Durum:** Bu belge ve aynı commit'teki kod, PIE_tahoe100m `lfc_true.npy` (ve `tested.npy`, `fdr.npy`, `fold_changes.npy`, `delta_p.npy`) indirilmeden ve hiçbir Tahoe etki değeri görülmeden sabitlendi. Yalnız yapısal dosyalar (`meta.json`, `ctx_ids.npy`, `pert_ids.npy`, `contexts.yaml`) indirildi.  
**Kod:** `scripts/perturbation/benchmark_tahoe_pilot_transfer.py`, `packages/analysis/analysis/pilot_transfer.py` (bu commit).

## 1. Neden yeni görev

Sıfır atış görülmemiş-bağlam transferi (kaynak bağlamdaki etkileri sabit β ile yeni hücre hattına taşımak) Replogle-Nadig içinde geçti, bağımsız X-Atlas/Orion tekrarında başarısız oldu (VALIDATION §13). Orion tanısı iki nedeni gösterdi: (1) kaynak bağlamın ortalama profili hedefe taşınmıyor, (2) tipik perturbasyon etkileri hücre hatları arasında zayıf ilişkili, uygun ölçek bağlama göre değişiyor. İkisi de hedef bağlamda **küçük bir pilot tarama** ile tahmin edilebilir.

Bu ön kayıt, başarısız sıfır atış iddiasını kurtarma girişimi **değildir**; o sonuç geçerliliğini korur. Burada farklı ve gerçekçi bir görev sınanır: *Yeni bir hücre hattında küçük bir pilot ölçüldüğünde, taramanın geri kalanı pilotun tek başına verdiğinden daha iyi tahmin edilebilir mi?*

## 2. Görev ve yöntem (dondurulmuş)

Sıralı her (kaynak → hedef) hücre hattı çifti için, iki bağlamda da ölçülmüş koşullar `P`:

- **Pilot:** `P` içinden rastgele **k = 100** koşul (hedef etiketlerinden bağımsız; seed `20261108`, çift başına `SeedSequence.spawn`).
- **Değerlendirme:** `P` içindeki kalan koşulların hedef satırları.
- **Birincil yöntem — `pilot_scaled_transfer`:** `ŷ_p = g_t + β · (m_p − g_s)`
  - `g_t`: hedef pilot satırlarının gen ortalaması,
  - `m_p − g_s`: koşulun kaynak bağlamdaki etkisinin kaynak ortalamasından sapması (test edilmeyen gen = 0),
  - `β`: yalnız pilot satırlarında en küçük kareler, [0, 1] aralığına kırpılmış.
- **Karşılaştırma ölçütü — `pilot_mean`:** her test koşulu için `g_t`. Transfer ancak bunu geçerse değer katar.
- İkincil, tanımlayıcı: `zero`, `zero_shot_beta025` (eski aday), `pilot_lowrank_ridge`.

Yöntem ve k, yalnız daha önce etiketleri açılmış veri setlerinde yapılan geliştirmeyle seçildi (`scripts/perturbation/develop_pilot_transfer.py`, `data/perturbation/processed/pilot-transfer-development.json`):

- Replogle-Nadig, 12 sıralı çift: `pilot_scaled_transfer`, `pilot_mean`'i her pilot boyutunda (25/50/100/200) **12/12** çiftte geçti; medyan RMSE kazancı %4,1–4,4, medyan korelasyon kazancı +0,18–0,22. Low-rank ridge daha zayıf (%0,6–2,0), sıfır atış tutarsız (%58–67 çift).
- X-Atlas/Orion, 2 sıralı çift: bkz. §7 (geliştirme, doğrulayıcı değil).

## 3. Veri

- `arcinstitute/PIE_tahoe100m`, commit `0d5089a2b4f13239383f135ef8e2db2462a00808`, `preprocessed/`.
- Tahoe-100M (Zhang et al., 2025): 379 bileşik × 3 doz = 1.137 koşul, 50 kanser hücre hattı, DMSO kontrolü. 56.827 satır, 18.151 gen.
- Lisans: upstream `tahoebio/Tahoe-100M` **CC0 1.0**; PIE aynasının kartında lisans alanı yok (önceki PIE setleri gibi kayıtlı). Yalnız araştırma.
- İndirme sonrası `meta.json` içindeki `array_sha256` ile dosya hash'leri doğrulanır.

## 4. Çiftler

Bağlam adları (Cellosaurus) sıralanır; çift `i`: `ad[i] → ad[(i+1) mod 50]`. Her hücre hattı bir kez kaynak, bir kez hedef olur. 50 çift; liste SHA-256: `3eacb4bd991ce116489df9b02cf5fe53c37808295646edad046deb38880082ba`.

## 5. Ölçümler

Satır başına (her test koşulu eşit ağırlık), satırın test edilmiş genleri üzerinde: RMSE, Pearson r, mutlak etkide top-50 örtüşmesi. Çift düzeyinde:

- göreli RMSE kazancı = `1 − RMSE(birincil) / RMSE(pilot_mean)` (satır ortalaması RMSE),
- korelasyon kazancı = medyan satır r (birincil) − medyan satır r (pilot_mean).

## 6. Başarı kuralı (tümü gerekli)

1. Birincil yöntem, çiftlerin **≥ %70**'inde `pilot_mean`'den düşük RMSE verir.
2. Çiftler üzerinden medyan göreli RMSE kazancı **≥ %1,0**.
3. Medyan kazancın çift düzeyinde bootstrap %95 aralığının (2.000 yeniden örnekleme, seed `20261108`) alt sınırı **> 0**.
4. Medyan korelasyon kazancı **> 0**.
5. Zarar sınırı: birincil yöntemin `pilot_mean`'den %1'den fazla kötü olduğu çiftlerin oranı **≤ %10**.

Hepsi geçerse: *"Bağımsız bir ilaç tarama veri setinde, 100 koşulluk pilotla kalibre edilen bağlam transferi, pilotun tek başına verdiğinden daha iyi tahmin üretti."* Biri geçmezse sonuç **başarısız** olarak raporlanır; k, β kuralı, çiftler veya eşikler değiştirilip aynı Tahoe etiketlerinde yeniden denenmez. İkincil yöntemler birincil kararı değiştiremez.

## 7. Geliştirme notu (Orion; doğrulayıcı değil)

Orion etiketleri §13 testinde açılmıştı; bu sonuçlar yalnız beklenti içindir ve kuralı belirlemek için kullanılmadı.

| Pilot k | Çift | `pilot_mean` RMSE | `pilot_scaled_transfer` RMSE | göreli kazanç | pilot β |
|---:|---|---:|---:|---:|---:|
| 100 | HCT116→HEK293T | 0,2278 | 0,2276 | %0,1 | 0,033 |
| 100 | HEK293T→HCT116 | 0,3282 | 0,3277 | %0,1 | 0,094 |

- Pilot ortalaması, eski sıfır atış adayının felaket hatasını (0,979 / 0,558) ortadan kaldırıyor ve sıfırı ~%5 geçiyor.
- Transferin pilot ortalamasına ek katkısı Orion'da ~%0,1; §6 kural 2 (≥ %1) Orion'da **geçmezdi**. Kural Replogle'u geçirip Orion'u geçirmeyecek kadar sıkıdır.
- Pilotla öğrenilen β (0,03–0,13), §13'teki test etiketiyle hesaplanan oracle β (0,046 / 0,125) ile uyumlu: pilot doğru ölçeği etiket sızıntısı olmadan buluyor; ölçek küçükken yöntem pilot ortalamasına yaklaşır ve zarar vermez.

## 8. Yorum sınırı

- Görülmemiş perturbasyon tahmini değildir: test koşulu kaynak bağlamda ölçülmüştür.
- Pilot gerektirir; sıfır atış iddiası yoktur.
- Aynı bileşiğin diğer dozları pilotta olabilir; bu, hedef etiket sızıntısı değildir (test satırının kendisi pilotta değildir) ama görevi kolaylaştırabilir. Tanımlayıcı olarak, pilotta bileşiği bulunmayan test koşulları ayrıca raporlanır.
- Hücre hatları kanser hatlarıdır; primer hücre, donör, doku, tek hücre dağılımı, doz-yanıt eğrisi veya klinik fayda iddiası yoktur.
- Çiftler hücre hatlarını paylaşır; bootstrap çift düzeyindedir ve bu bağımlılığı tam yansıtmaz.

## 9. Yeniden üretim

```bash
PYTHONPATH=packages/analysis apps/api/.venv/bin/python \
  scripts/perturbation/benchmark_tahoe_pilot_transfer.py --commit "$(git rev-parse --short HEAD)"
```

Çıktı: `data/perturbation/processed/tahoe-pilot-transfer-gate.json`.
