# Ürün yönü — Topiome

**Son karar:** Topiome adı korunuyor. Ürün yönü, tek hücre ölçümlerinden tanımlı genetik perturbasyonlara verilen hücresel yanıtları araştırma amaçlı tahmin etme ve aday deneyleri önceliklendirme olarak değiştirildi.

Bu bir ürün iddiası değil, sınanacak araştırma programıdır. Şu an Topiome'un bu alanda eğitilmiş veya doğrulanmış modeli yoktur.

## Bilimsel amaç

Bir başlangıç hücre bağlamı ve tanımlı müdahale verildiğinde, ölçülen hücresel yanıtı tahmin etmek; tahminin hangi perturbasyonlarda ve bağlamlarda desteklendiğini, hangi alanlarda verinin dışına çıktığını göstermek.

Araştırma sorusu: **Model, eğitimde görmediği bir perturbasyon veya hücre bağlamındaki yanıtı basit yöntemlerden daha iyi tahmin edebiliyor mu?**

## Dar ilk kapsam

1. Lisans ve metadatası kaydedilmiş açık Perturb-seq / CRISPR-perturbation verisini seç.
2. Kontrol hücresi, hedef perturbasyon, hücre bağlamı, assay ve mümkünse doz/zaman bilgisini standartlaştır.
3. Perturbasyon ve bağlam düzeyinde sızıntısız test kümeleri kur.
4. No-change, ortalama yanıt, doğrusal/additif modeller gibi basit baseline'ları öncele.
5. Yalnız benchmark'ta katkı gösteren modelleri araştır; belirsizliği ve kapsam dışını raporla.
6. Sonraki kapıda, bağımsız laboratuvar ölçümüyle önceden belirlenmiş tahminleri test et.

İlk hesaplamalı fizibilite sistemi Arc VCC 2025 H1 hESC CRISPRi Perturb-seq'tir. Bu, bir hastalık modeli değildir; yalnız aynı hücre hattında görülmemiş perturbasyon hedeflerine genellenme için dar bir ilk testtir. İkinci benchmark, Replogle-Nadig essential Perturb-seq'in dört hücre hattıdır; görülmemiş bağlam transferi burada sınandı ve 3/3 onaylayıcı fold geçti. Üçüncü, bağımsız benchmark X-Atlas/Orion'un HCT116/HEK293T hücre hatlarıdır; aynı transfer adayı Orion'da 0/2 sayısal fold ile başarısız oldu.

Görülmemiş-bağlam hattı bu veri ve görevde durduruldu; Replogle içi sonuç bağımsız olarak tekrarlanmış bir sinyal sayılmaz. Görülmemiş-perturbasyon hattı da bu veri ve görevde negatif sonuçlandı. Daha zengin veri, yeni bir bilimsel soru ve ayrı bir ön kayıt olmadan model karmaşıklığı artırılmayacak; aynı Orion test setinde beta veya metrik değiştirilerek yeniden deneme yapılmayacak.

## İlk kullanıcı ve olası değer

İlk kullanıcı hipotezi, deney sayısını ve maliyetini yöneten hücre biyolojisi veya keşif Ar-Ge ekibidir. Olası değer, deney yapılmadan önce aday perturbasyonları sıralamaktır. Bu ödeme isteği doğrulanmış değildir; teknik benchmark başarısı tek başına satın alma gerekçesi sayılmaz.

## Ürünün kanıt düzeyi

- **Bugün:** üç public Perturb-seq benchmark kaynağı ve basit baselinelar. Replogle-Nadig içi ön kayıtlı görülmemiş-bağlam kapısı HepG2/Jurkat/RPE1'de 3/3 geçti; ancak bağımsız X-Atlas/Orion tekrarı 0/2 sayısal fold ile başarısız oldu. Orion'da aday zero ve global mean'den kötü; ortak-destek ve üst-çeyrek alt kümelerinde de üstünlük yok. Görülmemiş-perturbasyon keşifsel kontrolü de negatiftir.
- **Yeni (2026-11-08):** Görev pilotla kalibre edilmiş transfere çevrildi: yeni hücre hattında 100 koşulluk pilot ölçülünce kalanı tahmin etmek. Hiç açılmamış Tahoe-100M'de ön kayıtlı test 5/5 kuralı geçti: 50 hücre hattı çiftinin %90'ında pilot ortalamasından iyi, medyan RMSE kazancı %2,05 [1,24–4,04], korelasyon +0,037; çiftlerin %8'inde zarar. Etki mütevazı; gen sıralaması iyileşmedi (VALIDATION §14).
- **Henüz yok:** Topiome perturbasyon modeli, sıfır atış bağlam transferi, görülmemiş perturbasyon tahmini, tek hücre dağılımı, prospektif deney doğrulaması, laboratuvar ortağı, alıcı/ödeme kanıtı veya ücretli analiz hizmeti.
- **Gerekli kanıt:** pilot transferinin genetik perturbasyon verisinde ve zarar gören çiftleri azaltan sağlam bir sürümle yeni ön kayıtlarla tekrarı; aynı test setlerinde ayar yapmadan. Ardından önceden dondurulmuş tahminlerin bağımsız laboratuvar ölçümüyle prospektif testi ve alıcı görüşmesi.
- **Kanıtlanmayan:** bağımsız tekrar, gen sıralaması (Replogle'da top-50 HepG2/RPE1'de global mean'in altında; Orion'da da üstünlük yok), görülmemiş perturbasyon, doz/zaman, başka assay/platform, klinik veya ticari fayda.
- **Durdurulan hat:** Replogle-Nadig içi görülmemiş-bağlam transferi ve Orion bağımsız tekrarı; yeni veri/soru ve ayrı ön kayıt olmadan yeniden açılmayacak.
- **RUO:** tanı, prognoz, tedavi seçimi, klinik karar veya kişiye özel müdahale iddiası yok.

## Dağıtım ve iş modeli

Önce laboratuvarsız hesaplamalı fizibilite yapılacak. Ürünleştirme ve ücretlendirme kararı; bilimsel kapı, deney ortağı ve potansiyel alıcı görüşmeleri tamamlanmadan verilmeyecek. Uzun vadeli olası ürün, araştırmacının kendi perturbasyon/bağlam verisinde belirsizlikle yanıt tahmini ve deney önceliklendirmesidir; henüz kesinleşmiş paket veya fiyat yoktur.

## Eski spatial ürün

Önceki spatial-transkriptomik uygulaması kod ve sonuçlarıyla legacy olarak korunur. Yerel spatial veri dosyaları temizlendi. Eski GNN, disease-pack ve Visium sonuçları yeni perturbasyon ürününün kanıtı veya modeli değildir. Ayrıntı: `docs/legacy/spatial/`.

## RUO ifadesi

> **For Research Use Only.** Topiome is not intended for diagnosis, prognosis, treatment selection, patient management, or clinical decision-making. Predictions are research hypotheses and require independent validation.
