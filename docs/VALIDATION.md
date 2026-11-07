# Doğrulama — perturbasyon yanıtı araştırması

**Durum (2026-11-07):** ilk keşifsel aggregate baseline çalışması yapıldı. Topiome perturbasyon tahmin modeli ve bağımsız doğrulama yok; başarı iddiası yok.

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
