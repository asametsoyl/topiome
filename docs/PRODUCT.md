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

İlk hesaplamalı fizibilite sistemi Arc VCC 2025 H1 hESC CRISPRi Perturb-seq'tir. Bu, bir hastalık modeli değildir; sadece aynı hücre hattında görülmemiş perturbasyon hedeflerine genellenme için dar bir ilk testtir. Hücre bağlamı dış testi için ayrıca uygun veri gerekir.

## İlk kullanıcı ve olası değer

İlk kullanıcı hipotezi, deney sayısını ve maliyetini yöneten hücre biyolojisi veya keşif Ar-Ge ekibidir. Olası değer, deney yapılmadan önce aday perturbasyonları sıralamaktır. Bu ödeme isteği doğrulanmış değildir; teknik benchmark başarısı tek başına satın alma gerekçesi sayılmaz.

## Ürünün kanıt düzeyi

- **Bugün:** ilk public aggregate dataset ve iki basit baseline ile keşifsel fizibilite; dış doğrulama yok.
- **Henüz yok:** Topiome perturbasyon modeli, doğrulanmış tahmin, deney tasarım önerisi veya ücretli analiz hizmeti.
- **Gerekli kanıt:** görülmemiş perturbasyon/bağlam testinde baselinelara karşı tekrarlanabilir katkı; ardından bağımsız deneysel test.
- **RUO:** tanı, prognoz, tedavi seçimi, klinik karar veya kişiye özel müdahale iddiası yok.

## Dağıtım ve iş modeli

Önce laboratuvarsız hesaplamalı fizibilite yapılacak. Ürünleştirme ve ücretlendirme kararı; bilimsel kapı, deney ortağı ve potansiyel alıcı görüşmeleri tamamlanmadan verilmeyecek. Uzun vadeli olası ürün, araştırmacının kendi perturbasyon/bağlam verisinde belirsizlikle yanıt tahmini ve deney önceliklendirmesidir; henüz kesinleşmiş paket veya fiyat yoktur.

## Eski spatial ürün

Önceki spatial-transkriptomik uygulaması kod ve sonuçlarıyla legacy olarak korunur. Yerel spatial veri dosyaları temizlendi. Eski GNN, disease-pack ve Visium sonuçları yeni perturbasyon ürününün kanıtı veya modeli değildir. Ayrıntı: `docs/legacy/spatial/`.

## RUO ifadesi

> **For Research Use Only.** Topiome is not intended for diagnosis, prognosis, treatment selection, patient management, or clinical decision-making. Predictions are research hypotheses and require independent validation.
