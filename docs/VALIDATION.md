# Doğrulama — perturbasyon yanıtı araştırması

**Durum (2026-11-07):** ön kayıtlı görülmemiş-bağlam transfer kapısı üç onaylayıcı hücre hattında geçti. Bu, ölçülmüş perturbasyon etkilerinin basit ölçeklemeyle yeni bir hücre hattına taşınabildiğini gösteren dar bir hesaplamalı sinyaldir; Topiome'un eğitilmiş/doğrulanmış modeli, görülmemiş-perturbasyon sonucu veya prospektif doğrulaması yoktur. Görülmemiş-perturbasyon keşifsel kontrolü negatiftir.

## 1. Test edilecek bilimsel iddia

Bir model, ölçülmüş başlangıç hücre bağlamı ve tanımlı müdahaleden, perturbasyon sonrası ölçülen single-cell yanıtını tahmin edebilir; bu tahmin, görülmemiş müdahale veya hücre bağlamına taşınır ve basit baseline'ları geçer.

Bu iddia tek bir görev ve assay için sınanır. Farklı perturbasyon türleri, hücre bağlamları, assay platformları ve zaman/doz kombinasyonları tek bir başarı metriğinde birleştirilmez.

## 2. Veri yeterlilik kapısı

Bir dataset şu bilgiler açıkça eşleşmeden modele alınmaz:

- kontrol ve perturbasyon hücrelerinin tanımı;
- müdahalenin hedefi, türü ve perturbasyon verimliliği (varsa);
- hücre hattı / donör / durum / bağlam;
- assay platformu, batch, doz ve ölçüm zamanı (mevcutsa);
- ham/işlenmiş ifade semantiği, normalizasyon ve kalite filtreleri;
- kaynak, lisans, indirme tarihi, hash ve kullanım sınırlaması.

Her dataset ayrı kaynak ve domain olarak değerlendirilir. Aynı deneyin hücreleri ya da aynı kültür/örnek farklı bölmelere ayrılmaz. Tekrarlı ölçümler bağımsız biyolojik tekrar gibi sayılmaz.

## 3. Bölme planı — önce biyolojik genelleme

1. **Görülmemiş perturbasyon:** hedef gen/ilaç tümüyle testte tutulur.
2. **Görülmemiş bağlam:** hücre hattı, donör veya deney bağlamı tümüyle testte tutulur.
3. **Çapraz çalışma/platform:** mümkünse kaynak çalışma veya assay platformu dışarıda tutulur.
4. **Görülmemiş kombinasyon:** kombinasyon perturbasyonları yalnızca iddia ayrı tanımlanırsa değerlendirilir.

Rastgele hücre bölmesi genelleme kanıtı değildir. Split ve test metriği model karşılaştırmasına başlamadan sabitlenir. Gen seçimi, normalizasyon, hiperparametre, kalibrasyon ve eşik seçimi test etiketlerine bakmadan eğitim verisinde yapılır.

## 4. Baseline'lar ve aday modeller

Her görevde en az:

- değişiklik yok / kontrol profili baseline'ı;
- eşleşen ortalama perturbasyon yanıtı;
- basit doğrusal veya additif model;
- uygun yayınlanmış yöntemler (ör. GEARS, CPA veya güncel adaylar).

Karmaşık GNN, foundation ya da generatif model yalnızca baselinelara karşı aynı veri bölmesi ve metriklerle katkı sınanırsa tutulur. Mimarinin yeniliği biyolojik doğruluk kanıtı değildir.

## 5. Ölçümler

Birden fazla tamamlayıcı ölçüm raporlanır:

- hücre/perturbasyon yanıt dağılımı için uygun kalibrasyon ve dağılım uyumu;
- perturbasyon etkisi için etki-korelasyonu ve gen düzeyinde sıralama;
- önceden belirlenmiş diferansiyel genlerde precision/recall veya top-k örtüşmesi;
- yolak/işlev düzeyi tutarlılık — keşifsel ve bağımsız biyolojik kanıt yerine geçmez;
- perturbasyon bazında skorlar, örnek desteği, belirsizlik aralıkları ve başarısız bağlamlar;
- compute maliyeti ve baselinelara göre fark.

Tek bir bütünleştirilmiş ortalama; zayıf sınıfları, başarısız bağlamları veya dataset heterojenliğini gizleyemez. Metrik, split, kapsam ve başarı eşiği koşu öncesi kayıt altına alınır.

## 6. İlerleme kapıları

### A — Veri ve benchmark çalışıyor

Küçük, lisansı uygun public dataset tekrarlanabilir biçimde okunur; etiketler, kontroller, split ve baseline'lar doğrulanır.

### B — Hesaplamalı sinyal

Aday yöntem, önceden belirlenmiş görülmemiş-perturbasyon veya bağlam testinde ilgili baselineları birden fazla bağımsız dataset üzerinde tekrarlanabilir biçimde geçer. Başarı yalnız bazı perturbasyonlarda görülüyorsa kullanım kapsamı o alt kümeyle sınırlanır.

### C — Prospektif bilimsel fayda

Model tahminleri deneyden önce dondurulur. Bağımsız deney ortağı, seçilen perturbasyonlar için kontrol ve sonuçları ölçer. Model, random/mean ve uzman seçimi gibi uygun alternatiflerle karşılaştırılır. Sonuç modeli güncellemek için kullanılsa bile sonraki tur ayrı tutulur.

### D — Ürün kararı

Bilimsel katkı, alıcının deney seçimini iyileştirdiği ve gerçek satın alma ihtiyacının doğrulandığı gösterilirse ürünleşme incelenir. Benchmark liderliği tek başına pazar veya şirket kanıtı değildir.

## 7. Karar kuralı

- Baseline'lar geçilmezse model karmaşıklığı ve özellik kapsamı artırılmaz; bilimsel hedef/veri yeniden incelenir.
- Performans yalnız in-distribution ise ürün iddiası ve hedef kapsamı buna göre daraltılır.
- Public holdout geçilse bile bağımsız deney olmadan “deney sonucu tahmin eder” veya “deney sayısını azaltır” iddiası kullanılmaz.
- Herhangi bir doğruluk iddiası RUO sınırlarını aşamaz.

## 8. Veri ve raporlama izi

Her koşuda veri source ID/hash/lisans, perturbasyon tanımı, bağlam, kontrol, filtre ve normalizasyon, split, baseline, metrik, kod commit'i, ortam, parametreler, model hash'i ve sınırlar saklanır. Ham veri git'e veya demo'ya konmaz.

## 9. Araştırma kaynakları

- Arc Virtual Cell Atlas: <https://arcinstitute.org/tools/virtualcellatlas> — atlas bileşenleri ve lisansları dataset bazında incelenir; Arc VCC 2025 ve Tahoe-100M sayfada CC0 olarak listeleniyor.
- Wei et al., *Benchmarking algorithms for generalizable single-cell perturbation response prediction*, Nature Methods (2026): <https://www.nature.com/articles/s41592-025-02980-0> — 27 yöntemi ve 29 dataset'i birden çok genelleme senaryosunda değerlendiriyor.
- *Deep-learning perturbation models can outperform baselines on calibrated metrics*, Nature Biotechnology (2026): <https://www.nature.com/articles/s41587-026-03307-w> — sonuçların metrik/kalibrasyon seçimine duyarlı olduğuna dair karşı kanıt ve güncel yöntemler.
- Eski spatial-transkriptomik validasyonları: `docs/legacy/spatial/validation/`; yeni ürünün kanıtı değildir.

## 10. İlk fizibilite çalışması — Arc VCC 2025 PIE aggregate arrays

**Durum:** başlangıç baseline'ı çalıştırıldı; bu Topiome model eğitimi veya doğrulaması değildir.

- Girdi: `data/perturbation/raw/arc-vcc-2025-pie/`; Arc VCC 2025 H1 hESC CRISPRi Perturb-seq verisinden PIE ile üretilmiş aggregate log2 fold-change tabloları.
- Bölme: `ARC_H1` 146 perturbasyon hedefi → `ARC_H1_VAL` 44 görülmemiş hedef. Hedef örtüşmesi 0. Her ikisi aynı H1 hücre hattıdır; validation context adının farklı olması ayrı biyolojik bağlam anlamına gelmez.
- Ölçüm: 44 hedef × toplam 472.187 test edilmiş perturbasyon-gen etkisi. Pooled metriklerin yanında her hedef eşit ağırlıklı RMSE/MAE, hedef başına gen korelasyonu ve top-50 mutlak etki örtüşmesi raporlandı.
- Baseline: tüm etkileri sıfır tahmin etmek pooled RMSE 0.2445, eşit-ağırlıklı hedef RMSE 0.1909 verdi. Eğitim perturbasyonlarının gen başına ortalama etkisini tahmin etmek pooled RMSE 0.2220, eşit-ağırlıklı hedef RMSE 0.1818, medyan hedef başına gen korelasyonu 0.2113 ve ortalama top-50 örtüşme 0.2064 verdi.
- Gen ortalaması pooled RMSE'yi 9.2%, hedefleri eşit ağırlıklı RMSE'yi 4.8% düşürdü. Hedef bazında bootstrap delta için yüzde 95 percentile aralığı −0.0183 ile −0.0012 log2-FC RMSE; bootstrap birimi 44 validation perturbasyon hedefidir. Bu, yalnız bu paneldeki hedefler arası betimleyici belirsizliktir; bağımsız deney/çalışma varyansını ölçmez.
- Ortalama gen etkisi hedef kimliğine özgü değil. Sonuç ortak gen/assay örüntüsünün yararlı olabileceğini düşündürür; model katkısı, biyolojik mekanizma, deney faydası veya diğer bağlamlara genelleme kanıtı değildir.
- Çıktı: `data/perturbation/processed/vcc-pie-baseline-metrics.json`; tekrarlanabilir komut: `python scripts/perturbation/benchmark_vcc_pie_baselines.py`.
- Sınırlar: hücre düzeyinde çıktı tahmin edilmedi; tek hücre dağılımı veya yeni hücre bağlamı test edilmedi; 44 public validation perturbasyonu bağımsız deney/çalışma değildir. Bu sonuç ürün doğruluğu iddiası için kullanılmaz.

## 11. Ön kayıtlı görülmemiş bağlam transferi — Replogle-Nadig

**Durum:** ön kayıtlı kapı 3/3 onaylayıcı fold'da geçti. Bu bir Topiome modeli değil, ölçülmüş perturbasyon etkilerinin basit ölçekli transferidir.

- Ön kayıt: `docs/experiments/2026-11-07-replogle-unseen-context-preregistration.md`; test setleri açılmadan önce sabitlendi. K562, ön kayıttan önce keşifsel sinyal kontrolünde kullanıldığı için onaylayıcı kapıya dahil edilmedi.
- Veri: `arcinstitute/PIE_replogle_nadig_essential` preprocessed array'leri; 5.459 (bağlam, perturbasyon) satırı, 6.642 gen, 4 hücre hattı, 1.857 perturbasyon. Replogle et al. 2022 (K562, RPE1) ve Nadig et al. 2025 (HepG2, Jurkat) CRISPRi essential-gene Perturb-seq ekranları.
- Split: `arcinstitute/PIE_splits`, `replogle_wdataset/unseen_ctx/<fold>/{train,val,test}.json`. Her fold'da eğitim diğer üç hücre hattı, test tamamen dışarıda tutulan hücre hattı. Test hücre hattı eğitimde/doğrulamada yok; satır örtüşmesi yok. Test perturbasyonları eğitimde görülmüş (kapsama 1.0).
- Aday: `beta × (perturbasyon ortalaması − global ortalama)`; beta [0, 1] aralığında 0,05 adımlı ızgaradan yalnız doğrulama satırlarında seçildi. Baseline'lar: zero, global mean, ölçeksiz perturbasyon ortalaması ve merkezlenmiş perturbasyon ortalaması.
- Onaylayıcı fold'lar: HepG2, Jurkat, RPE1. Kapı kuralı: en az 2/3 fold'da ≥%3 göreli satır-RMSE iyileşmesi, bootstrap %95 aralığının tamamı sıfırın üstünde, medyan satır korelasyonu >0,20, top-50 örtüşmesinde zero'ya göre +0,02, global mean'den kötü olmama ve beta>0.

| Fold | beta | zero RMSE | aday RMSE | göreli iyileşme | medyan r | top-50 Δ (zero) | bootstrap zero farkı %95 | bootstrap global farkı %95 | kapı |
|---|---:|---:|---:|---:|---:|---:|---|---|---|
| HepG2 | 0,25 | 0,7579 | 0,7250 | %4,34 | 0,357 | +0,0796 | 0,0305–0,0354 | 0,0152–0,0213 | geçti |
| Jurkat | 0,25 | 0,5643 | 0,5313 | %5,84 | 0,441 | +0,0645 | 0,0304–0,0354 | 0,0571–0,0629 | geçti |
| RPE1 | 0,30 | 0,8724 | 0,8326 | %4,56 | 0,386 | +0,0780 | 0,0375–0,0419 | 0,0173–0,0226 | geçti |
| K562 (keşifsel) | 0,25 | 0,4854 | 0,4590 | %5,43 | 0,427 | +0,0604 | 0,0228–0,0299 | 0,0568–0,0640 | keşifsel geçti |

- Bootstrap birimi bağlam–perturbasyon satırıdır; aralıklar paired bootstrap ile 2.000 yeniden örneklemeden elde edildi. Aday, üç onaylayıcı foldda da hem zero hem global mean'e göre RMSE'de daha iyi.
- **Önemli sınır:** top-50 mutlak etki örtüşmesi HepG2 ve RPE1'de global mean'in altında kaldı (HepG2 0,0858 vs 0,0957; RPE1 0,0878 vs 0,1117). Kaydedilen kapı top-50'yi yalnız zero'ya göre sınadığı için kapı geçti; ancak “gen sıralamasını iyileştiriyor” iddiası kurulamaz. Jurkat'ta global mean çok zayıf olduğu için aday daha iyi görünüyor.
- Beta'nın 0,25–0,30 olması, ham perturbasyon etkilerinin yeni bağlama taşınırken güçlü büzülmeye ihtiyaç duyduğunu gösterir. Ölçek seçilmezse ham transfer RMSE'de zero'nun gerisinde kalıyor.
- Post-hoc ölçeksiz (uncentered) varyant 3/4 foldda RMSE'de biraz daha iyiydi (ör. HepG2 0,7139 vs 0,7250); kayıtlı aday olmadığı için kapı sonucu sayılmaz ve model seçiminde kullanılmaz.
- Bu sonuç görülmemiş perturbasyon, tek hücre dağılımı, doz/zaman, başka assay veya prospektif deney hakkında kanıt değildir. Veri kartında lisans alanı yok; ticari kullanım doğrulanmamıştır ve bu koşu yalnız araştırma amaçlıdır.
- Çıktı: `data/perturbation/processed/replogle-unseen-ctx-gate.json`. Kod: `packages/analysis/analysis/perturbation.py`, `scripts/perturbation/benchmark_replogle_transfer.py`; 9 birim test.

## 12. Keşifsel görülmemiş perturbasyon kontrolü — negatif

**Durum:** bu bir ön kayıtlı kapı değildir; keşifsel kontrol negatif sonuçlandı. Bu veri ve görevle model karmaşıklığını artırma durduruldu.

- Split: PIE `unseen_pert`, K562 fold adı; test perturbasyonları eğitimde yok, test satırları HepG2/Jurkat/RPE1'de. Eğitim ve doğrulama aynı üç hattan; doğrulama perturbasyonları eğitimde görülmüş olduğu için hiperparametre seçimi sınırlıdır.
- Özellikler: PIE_sources ESM2 (1.280 boyut), STRING (512), DepMap (1.186); 1.857 perturbasyonun sırasıyla 47/22/53'ünde eksik. Eksikler eğitim perturbasyon sütun ortalamasıyla dolduruldu ve eğitim perturbasyonlarında standardize edildi.
- Modeller: mesafe ağırlıklı kNN (k=5, 10, 25, 50, 100) ve ridge (alpha 0,01–10.000; birleşik ve tek blok). Seçim yalnız doğrulama satırlarında yapıldı.
- Baseline'lar (test): zero RMSE 0,7170, global mean 0,7118, bağlam ortalaması 0,7066; medyan korelasyon 0 / 0,120 / 0,170; top-50 0,0079 / 0,0802 / 0,1097.
- Doğrulama-seçimli birincil aday: DepMap ridge alpha=1000; test RMSE 0,7051 (bağlam ortalamasına göre +%0,21), medyan korelasyon 0,1367 (baseline 0,1704), top-50 0,0911 (baseline 0,1097), bootstrap farkı %95 [−0,0015, +0,0047] (sıfırı içeriyor).
- Diğer doğrulama-seçimli adaylar: STRING ridge alpha=10.000 test RMSE 0,7017 (+%0,69), korelasyon 0,1502, top-50 0,0968; kNN k=100 test RMSE 0,7020 (+%0,65), korelasyon 0,1487, top-50 0,1018. İkisinde de bootstrap aralığı sıfırın üstünde, ancak sıralama metrikleri bağlam ortalamasının altında.
- Test RMSE'sine göre en iyi görünen DepMap alpha=10.000 (0,6966, +%1,42) doğrulama tarafından seçilmedi; test setine bakarak model seçmek sızıntı olur ve bu sonuç kullanılmaz.
- Sonuç: hiçbir basit özellik modeli bağlam ortalamasını RMSE, korelasyon ve top-50 birlikte geçmedi. DepMap zaten perturbasyon yanıtı/essentiality verisi olduğu için olası sızıntı riski taşır; buna rağmen net üstünlük yok. Görülmemiş-perturbasyon hattı bu veri ve görevde durduruldu; daha zengin veri veya farklı bilimsel soru olmadan karmaşık model denenmeyecek.
- Çıktı: `data/perturbation/processed/replogle-unseen-pert-exploratory.json`. Script: `scripts/perturbation/explore_replogle_unseen_pert.py`. PIE_sources kartlarında lisans alanı yok; yalnız araştırma amaçlıdır.
