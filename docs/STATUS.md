# STATUS — Topiome

**Son güncelleme:** 2026-11-07  
**Aşama:** Bağımsız X-Atlas/Orion tekrarı başarısız; görülmemiş-bağlam hattı durduruldu. Görülmemiş perturbasyon kontrolü de negatif.<br>
**Ürün durumu:** Bağımsız olarak doğrulanmış hesaplamalı sinyal yok; eğitilmiş Topiome modeli, prospektif doğrulama, laboratuvar ortağı veya alıcı kanıtı yok.

## Yapılanlar

### Ürün / bilim

- [x] Kullanıcı kararı: Topiome adı şimdilik korunarak cellular perturbation-response prediction araştırma yönü denenecek.
- [x] RUO sınırı korundu; public benchmark sonucu prospektif deney ve klinik fayda kanıtı gibi sunulmayacak.
- [x] Yeni bilimsel soru ve baseline-first doğrulama kapıları `docs/PRODUCT.md` ile `docs/VALIDATION.md` içinde yazıldı.
- [x] Arc VCC 2025 H1 hESC Perturb-seq ilk fizibilite verisi seçildi; upstream CC0 bilgisi ve aynanın lisans metadata eksikliği manifestte açıkça kaydedildi.
- [x] Hücre düzeyi 15.5 GB ham matris yerine 49.3 MB PIE aggregate etki tabloları indirildi; upstream SHA-256 değerleri doğrulandı.
- [x] 146 train / 44 görülmemiş perturbasyon hedefli baselinelar çalıştırıldı; hedef sızıntısı yok. Sonuç ve kısıtlar `docs/VALIDATION.md` bölüm 10'da.
- [x] Replogle-Nadig essential Perturb-seq preprocessed array'leri (~327 MB) ve PIE canonical split'leri indirildi; 5.459 satır, 6.642 gen, 4 hücre hattı, 1.857 perturbasyon. Tüm split satırları eşleşti, görülmemiş bağlam fold'larında sızıntı yok.
- [x] Görülmemiş bağlam için ön kayıtlı transfer kapısı HepG2/Jurkat/RPE1 fold'larında 3/3 geçti; beta 0,25/0,25/0,30, RMSE iyileşmesi %4,34/%5,84/%4,56, medyan korelasyon 0,357/0,441/0,386. K562 keşifsel fold da geçti.
- [x] Yeniden kullanılabilir `analysis.perturbation` benchmark modülü, 9 test ve `scripts/perturbation/benchmark_replogle_transfer.py` eklendi; sonuç `data/perturbation/processed/replogle-unseen-ctx-gate.json`.
- [x] Görülmemiş perturbasyon keşifsel kontrolü yapıldı: ESM2/STRING/DepMap ridge ve kNN, bağlam ortalamasını RMSE+korelasyon+top-50 birlikte geçmedi. Bu veri/görevde model karmaşıklığını artırma durduruldu.
- [x] X-Atlas/Orion preprocessed array'leri indirildi; `lfc_true.npy` ve `tested.npy` hash'leri doğrulandı. 13.284 satır, 22.182 gen, 2 bağlam, 10.007 perturbasyon; iki bağlamda 3.277 ortak perturbasyon.
- [x] Orion bağımsız tekrarı için ön kayıt, `lfc_true.npy` indirilmeden ve test metriği hesaplanmadan donduruldu; beta Replogle sonucundan 0,25 olarak sabitlendi, doğrulama seti kullanılmadı.
- [x] Orion bağımsız tekrarı **başarısız**: sayısal kapı 0/2, sıralama kapısı 1/2. Aday zero'ya göre HCT116→HEK293T'de −%309,70, HEK293T→HCT116'de −%62,46; global mean'den de kötü. Ortak-destek ve üst-çeyrek alt kümelerinde de üstünlük yok. Görülmemiş-bağlam hattı bu veri/görevde durduruldu.
- [x] `analysis.perturbation` için tek-bağlam doldurma ve ortak-destek skorlama testleri eklendi; analiz test sayısı 11'e çıktı.

### Site

- [x] Landing page perturbasyon yanıtı araştırma önizlemesine dönüştürüldü; illüstrasyon açıkça gerçek sonuç olmadığı şeklinde etiketlendi.
- [x] Kayıt ve fiyat vaadi durduruldu; yeni hesaplar geçici olarak kapalı, ücretli model/ürün erişimi iddia edilmiyor.
- [x] Eski spatial workspace uyarı bandıyla legacy olarak işaretlendi; giriş yapan mevcut kullanıcılar eski kayıtları ayırt edebilir.
- [x] Docs, metadata ve RUO sayfası yeni bilimsel amaç ve henüz model bulunmadığına göre güncellendi.

### Veri temizliği

- [x] Yerel eski spatial raw/public ve işlenmiş veriler ile kısmi indirmeler silindi: yaklaşık **9.2 GB**.
- [x] Küçük tarihsel spatial validasyon raporları `docs/legacy/spatial/validation/` altında korundu.
- [x] Yeni `data/perturbation/` yerel benchmark alanı hazırlandı; public benchmark girdileri repo dışında ve checksum manifestiyle tutuluyor.

## Sıradaki işler

### P0 — Hesaplamalı fizibilite

1. [x] İlk görev ve veri seçildi: aynı H1 hücre hattında görülmemiş gen perturbasyonları; held-out bağlam iddiası yok.
2. [x] PIE aggregate subset alındı; lisans notu, dosya hash'i, kontrol etiketleri ve kaynak manifesti oluşturuldu.
3. [x] İşlenmiş tabloda perturbasyon başına gen etkileri ve test maskesi doğrulandı; raw-cell `.h5ad` indirilmedi.
4. [x] Yayınlanmış train/validation target split'i denetlendi; ortak hedef yok.
5. [x] Sıfır etkisi ve eğitim gen ortalaması baseline'ları eşit validation ölçümünde kıyaslandı.
6. [x] Replogle-Nadig görülmemiş-bağlam transfer kapısı ön kayıtla çalıştırıldı; 3/3 onaylayıcı fold geçti.
7. [x] Görülmemiş-perturbasyon keşifsel kontrolü yapıldı; basit özellik modelleri bağlam ortalamasını net geçmedi, hat durduruldu.
8. [x] Görülmemiş-bağlam transferi bağımsız X-Atlas/Orion verisinde ön kayıtla denendi; 0/2 sayısal fold ile başarısız. Hat durduruldu.
9. [ ] Bağımsız tekrar başarısız olduğu için prospektif doğrulama, yeni bir veri/soru ve ayrı bir ön kayıt olmadan başlatılmayacak.

**Durdurulan hat:** Aynı Orion test setinde beta, metrik veya aday değiştirerek yeniden deneme yapılmayacak. Replogle-Nadig içi 3/3 sonucu bağımsız tekrar olarak sunulmayacak.

### P1 — Ürün kararı

- [ ] Bilimsel sinyal ve deney partneri bulunmadan prediction SaaS, fiyatlandırma veya doğruluk pazarlaması açma.
- [ ] Alıcı ve ödeme nedeni araştırmasını modelin çözebildiği spesifik bilimsel görev ortaya çıktıktan sonra yap.
- [ ] Eski spatial backend ve app akışını kaldırma/arşivleme kararı ayrı ADR ile ver.

## Açık kararlar

| Konu | Durum |
|---|---|
| İlk hücre bağlamı ve perturbasyon görevi | H1 hESC CRISPRi (Arc VCC), Replogle-Nadig dört hücre hattı ve X-Atlas/Orion HCT116/HEK293T; görülmemiş bağlam ve görülmemiş perturbasyon ayrı değerlendirilir |
| Public benchmark verileri | Arc VCC 2025 / PIE aggregate arrays, PIE Replogle-Nadig essential Perturb-seq ve PIE X-Atlas/Orion; lisans/mirror kısıtları kayıtlı |
| Görülmemiş bağlam transferi | Replogle içi 3/3 geçti; Orion bağımsız tekrarı 0/2 sayısal, 1/2 sıralama ile başarısız; hat durduruldu |
| Görülmemiş perturbasyon | Keşifsel kontrol negatif; bu veri ve görevde durduruldu |
| Deney ortağı | Gerekiyor; henüz yok |
| Topiome marka adı | Şimdilik korunuyor; yasal tescil yok |
| Eski spatial kodu | Çalışma ağacında legacy; silinmedi |

## Kanıt ve kısıt

- Yeni yönde **eğitilmiş Topiome modeli, bağımsız olarak tekrarlanmış transfer sinyali, prospektif doğrulama, laboratuvar ortağı veya alıcı kanıtı yok**. Replogle-Nadig içi ön kayıtlı kapı 3/3 geçti; ancak X-Atlas/Orion bağımsız tekrarı 0/2 sayısal fold ile başarısız oldu.
- Orion'da aday zero ve global mean'den kötü: HCT116→HEK293T RMSE 0,9789 vs zero 0,2389; HEK293T→HCT116 0,5581 vs zero 0,3436. Ortak-destek ve üst-çeyrek alt kümelerinde de üstünlük yok. Bu, Replogle sonucunun veri setine özgü olabileceğini gösterir.
- Post-hoc ölçek tanısı (yalnız açıklama): Orion'da bağlamlar arası perturbasyon korelasyonu çoğunlukla zayıf; eğitim global mean'i test bağlamına taşınmıyor; oracle beta 0,046/0,125. Beta=0,25 fazla büyük, ama asıl sorun global mean bileşeni. Bu tanıyla model seçimi yapılmadı.
- Görülmemiş-perturbasyon keşifsel kontrolü negatif: ESM2/STRING/DepMap ridge ve kNN, bağlam ortalamasını RMSE+korelasyon+top-50 birlikte geçmedi.
- Replogle bağlam kapısında top-50 mutlak etki sıralaması HepG2 ve RPE1'de global mean'in altında kaldı; “gen sıralamasını iyileştiriyor” iddiası yok. Kapı kuralı top-50'yi yalnız zero'ya göre sınadı.
- Arc VCA'daki toplam hücre sayısı Topiome'un kullanılabilir örnek/perturbasyon sayısı değildir. İlk set aynı hücre hattında 146/44 perturbasyon split'i, aggregate etki tablolarıyla sınırlı.
- 2026-Nat Methods karşılaştırması genellemenin zor olduğunu, 2026-Nat Biotech çalışması ise bazı metriklerde derin modellerin katkı sağlayabildiğini gösteriyor. Split ve metrik göreve göre belirlenmeli; ölçek tek başına başarı sayılmaz.
- PIE Replogle-Nadig ve PIE_sources veri kartlarında lisans alanı yok; Orion CC BY-NC-SA 4.0. Hiçbiri ticari kullanım için doğrulanmadı; bu koşular yalnız araştırma amaçlıdır.
- Eski breast GNN ARI 0.260 / Macro-F1 0.446 ve GBM Ivy GAP sonucu yeni yön için kanıt değildir.

## Oturum kaydı — 2026-11-07

- Kurucu kararıyla ürün yönü spatial tissue atlas'tan perturbasyon yanıtı araştırmasına çevrildi; Topiome adı korundu.
- Beyaz araştırma önizleme sitesi, gerçek olmayan görsel için açık illüstrasyon etiketi ve model yok durumunu görünür yapan RUO metinleri hazırlandı.
- Kayıt ve pricing CTA'ları durduruldu; mevcut spatial uygulama legacy bandıyla ayrıştırıldı.
- Yaklaşık 9.2 GB eski public/processed spatial veri temizlendi; küçük AppleDouble metadata yan dosyaları da ayıklandı.
- Arc VCC 2025'ten checksum doğrulanmış 49.3 MB aggregate etki tabloları alındı; büyük ham single-cell H5AD indirilmedi.
- 146 train / 44 unseen-target validation üstünde sıfır ve gen-başına ortalama etkisi baseline'ları çalıştırıldı; ortalama baseline pooled RMSE'yi 9.2%, hedef-eşit ağırlıklı RMSE'yi 4.8% düşürdü. Bootstrap aralığı yalnız aynı 44 hedef panelini özetler; sonuç keşifsel ve tek bağlamlı.
- Replogle-Nadig preprocessed array'leri ve PIE canonical split'leri indirildi; split satırları, bağlam izolasyonu ve test perturbasyon kapsaması doğrulandı.
- Görülmemiş-bağlam transferi ön kaydı test setleri açılmadan sabitlendi; HepG2/Jurkat/RPE1 fold'larında 3/3 geçti. Sonuç `docs/VALIDATION.md` bölüm 11'de.
- Görülmemiş-perturbasyon keşifsel kontrolü negatif sonuçlandı; `docs/VALIDATION.md` bölüm 12. Bu hat için model karmaşıklığı artırılmayacak.
- X-Atlas/Orion preprocessed array'leri indirildi; `lfc_true.npy` ve `tested.npy` hash'leri doğrulandı. 13.284 satır, 22.182 gen, 2 bağlam, 10.007 perturbasyon; iki bağlamda 3.277 ortak perturbasyon.
- Orion ön kaydı `lfc_true.npy` indirilmeden ve test metriği hesaplanmadan donduruldu; beta Replogle sonucundan 0,25 olarak sabitlendi, doğrulama seti kullanılmadı.
- Orion bağımsız tekrarı 0/2 sayısal fold ile başarısız oldu; aday zero ve global mean'den kötü, ortak-destek ve üst-çeyrek alt kümelerinde de üstünlük yok. Sonuç `docs/VALIDATION.md` bölüm 13'te; hat durduruldu.
- Orion post-hoc ölçek tanısı yalnız açıklama olarak kaydedildi; beta/metrik değiştirilerek aynı test setinde yeniden deneme yapılmayacak.
- Landing page yerel tarayıcıda görsel olarak açıldı; API başlatılmadığı için eski giriş gerektiren workspace akışları bu oturumda incelenmedi.
- İlk baseline oturumunda kod testleri çalıştırılmamıştı; sonraki doğrulamada analiz ve API testleri, ruff, web typecheck, lint ve production build çalıştırıldı.
