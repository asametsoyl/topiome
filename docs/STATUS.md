# STATUS — Topiome

**Son güncelleme:** 2026-11-07  
**Aşama:** Görülmemiş bağlam transferi için ön kayıtlı kapı geçti; görülmemiş perturbasyon tahmini gösterilemedi.<br>
**Ürün durumu:** Dar bir hesaplamalı sinyal var; eğitilmiş Topiome modeli, prospektif doğrulama, laboratuvar ortağı veya alıcı kanıtı yok.

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
8. [ ] Görülmemiş-bağlam transferini bağımsız ikinci bir veri seti veya assay üzerinde tekrarla; aynı veri içindeki fold'lar bağımsız çalışma sayılmaz.
9. [ ] Daha güçlü hesaplamalı kapı sonrası deney ortağıyla önceden dondurulmuş tahminlerin prospektif testi.

### P1 — Ürün kararı

- [ ] Bilimsel sinyal ve deney partneri bulunmadan prediction SaaS, fiyatlandırma veya doğruluk pazarlaması açma.
- [ ] Alıcı ve ödeme nedeni araştırmasını modelin çözebildiği spesifik bilimsel görev ortaya çıktıktan sonra yap.
- [ ] Eski spatial backend ve app akışını kaldırma/arşivleme kararı ayrı ADR ile ver.

## Açık kararlar

| Konu | Durum |
|---|---|
| İlk hücre bağlamı ve perturbasyon görevi | H1 hESC CRISPRi (Arc VCC) ve Replogle-Nadig dört hücre hattı; görülmemiş bağlam ve görülmemiş perturbasyon ayrı değerlendirilir |
| Public benchmark verileri | Arc VCC 2025 / PIE aggregate arrays ve PIE Replogle-Nadig essential Perturb-seq; iki kaynağın da lisans/mirror kısıtı kayıtlı |
| Görülmemiş bağlam transferi | Ön kayıtlı kapı 3/3 onaylayıcı hücre hattında geçti; bu bir Topiome modeli değil, dar ölçekli transfer sinyali |
| Görülmemiş perturbasyon | Keşifsel kontrol negatif; bu veri ve görevde durduruldu |
| Deney ortağı | Gerekiyor; henüz yok |
| Topiome marka adı | Şimdilik korunuyor; yasal tescil yok |
| Eski spatial kodu | Çalışma ağacında legacy; silinmedi |

## Kanıt ve kısıt

- Yeni yönde **eğitilmiş Topiome modeli, prospektif doğrulama, laboratuvar ortağı veya alıcı kanıtı yok**. Ön kayıtlı görülmemiş-bağlam kapısı 3/3 geçti; bu, ölçülmüş etkilerin basit ölçekli transferinin dar bir sinyalidir.
- Görülmemiş-perturbasyon keşifsel kontrolü negatif: ESM2/STRING/DepMap ridge ve kNN, bağlam ortalamasını RMSE+korelasyon+top-50 birlikte geçmedi.
- Bağlam kapısında top-50 mutlak etki sıralaması HepG2 ve RPE1'de global mean'in altında kaldı; “gen sıralamasını iyileştiriyor” iddiası yok. Kapı kuralı top-50'yi yalnız zero'ya göre sınadı.
- Arc VCA'daki toplam hücre sayısı Topiome'un kullanılabilir örnek/perturbasyon sayısı değildir. İlk set aynı hücre hattında 146/44 perturbasyon split'i, aggregate etki tablolarıyla sınırlı.
- 2026-Nat Methods karşılaştırması genellemenin zor olduğunu, 2026-Nat Biotech çalışması ise bazı metriklerde derin modellerin katkı sağlayabildiğini gösteriyor. Split ve metrik göreve göre belirlenmeli; ölçek tek başına başarı sayılmaz.
- PIE Replogle-Nadig ve PIE_sources veri kartlarında lisans alanı yok; ticari kullanım doğrulanmadı. Bu koşular yalnız araştırma amaçlıdır.
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
- Landing page yerel tarayıcıda görsel olarak açıldı; API başlatılmadığı için eski giriş gerektiren workspace akışları bu oturumda incelenmedi.
- İlk baseline oturumunda kod testleri çalıştırılmamıştı; sonraki doğrulamada analiz ve API testleri, ruff, web typecheck, lint ve production build çalıştırıldı.
