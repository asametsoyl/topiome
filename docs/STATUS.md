# STATUS — Topiome

**Son güncelleme:** 2026-11-07  
**Aşama:** Perturbasyon yanıtı araştırma fizibilitesi  
**Ürün durumu:** Yeni yön tanımlandı; hesaplamalı model henüz yok.

## Yapılanlar

### Ürün / bilim

- [x] Kullanıcı kararı: Topiome adı şimdilik korunarak cellular perturbation-response prediction araştırma yönü denenecek.
- [x] RUO sınırı korundu; public benchmark sonucu prospektif deney ve klinik fayda kanıtı gibi sunulmayacak.
- [x] Yeni bilimsel soru ve baseline-first doğrulama kapıları `docs/PRODUCT.md` ile `docs/VALIDATION.md` içinde yazıldı.
- [x] Arc VCC 2025 H1 hESC Perturb-seq ilk fizibilite verisi seçildi; upstream CC0 bilgisi ve aynanın lisans metadata eksikliği manifestte açıkça kaydedildi.
- [x] Hücre düzeyi 15.5 GB ham matris yerine 49.3 MB PIE aggregate etki tabloları indirildi; upstream SHA-256 değerleri doğrulandı.
- [x] 146 train / 44 görülmemiş perturbasyon hedefli baselinelar çalıştırıldı; hedef sızıntısı yok. Sonuç ve kısıtlar `docs/VALIDATION.md` bölüm 10'da.

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
6. [ ] Birden fazla bağımsız dataset üzerinde uygun model baseline'ı ve perturbasyon bazında belirsizlik/robustness analizi.
7. [ ] Daha güçlü hesaplamalı kapı sonrası deney ortağıyla önceden dondurulmuş tahminlerin prospektif testi.

### P1 — Ürün kararı

- [ ] Bilimsel sinyal ve deney partneri bulunmadan prediction SaaS, fiyatlandırma veya doğruluk pazarlaması açma.
- [ ] Alıcı ve ödeme nedeni araştırmasını modelin çözebildiği spesifik bilimsel görev ortaya çıktıktan sonra yap.
- [ ] Eski spatial backend ve app akışını kaldırma/arşivleme kararı ayrı ADR ile ver.

## Açık kararlar

| Konu | Durum |
|---|---|
| İlk hücre bağlamı ve perturbasyon görevi | H1 hESC, CRISPRi; yalnız aynı bağlamda görülmemiş hedef testi |
| İlk public dataset | Arc VCC 2025 / PIE aggregate arrays; lisans ve mirror kısıtı kayıtlı |
| Deney ortağı | Gerekiyor; henüz yok |
| Topiome marka adı | Şimdilik korunuyor; yasal tescil yok |
| Eski spatial kodu | Çalışma ağacında legacy; silinmedi |

## Kanıt ve kısıt

- Yeni yönde **öğrenilmiş Topiome modeli, bağımsız benchmark sonucu, prospective validation veya kullanıcı talebi yok**. Bir exploratory baseline sonucu var.
- Arc VCA'daki toplam hücre sayısı Topiome'un kullanılabilir örnek/perturbasyon sayısı değildir. İlk set aynı hücre hattında 146/44 perturbasyon split'i, aggregate etki tablolarıyla sınırlı.
- 2026-Nat Methods karşılaştırması genellemenin zor olduğunu, 2026-Nat Biotech çalışması ise bazı metriklerde derin modellerin katkı sağlayabildiğini gösteriyor. Split ve metrik göreve göre belirlenmeli; ölçek tek başına başarı sayılmaz.
- Eski breast GNN ARI 0.260 / Macro-F1 0.446 ve GBM Ivy GAP sonucu yeni yön için kanıt değildir.

## Oturum kaydı — 2026-11-07

- Kurucu kararıyla ürün yönü spatial tissue atlas'tan perturbasyon yanıtı araştırmasına çevrildi; Topiome adı korundu.
- Beyaz araştırma önizleme sitesi, gerçek olmayan görsel için açık illüstrasyon etiketi ve model yok durumunu görünür yapan RUO metinleri hazırlandı.
- Kayıt ve pricing CTA'ları durduruldu; mevcut spatial uygulama legacy bandıyla ayrıştırıldı.
- Yaklaşık 9.2 GB eski public/processed spatial veri temizlendi; küçük AppleDouble metadata yan dosyaları da ayıklandı.
- Arc VCC 2025'ten checksum doğrulanmış 49.3 MB aggregate etki tabloları alındı; büyük ham single-cell H5AD indirilmedi.
- 146 train / 44 unseen-target validation üstünde sıfır ve gen-başına ortalama etkisi baseline'ları çalıştırıldı; ortalama baseline pooled RMSE'yi 9.2%, hedef-eşit ağırlıklı RMSE'yi 4.8% düşürdü. Bootstrap aralığı yalnız aynı 44 hedef panelini özetler; sonuç keşifsel ve tek bağlamlı.
- Landing page yerel tarayıcıda görsel olarak açıldı; API başlatılmadığı için eski giriş gerektiren workspace akışları bu oturumda incelenmedi.
- Kod testleri ve production build çalıştırılmadı; bu aşamada yalnız sayısal baseline deneyi yürütüldü.
