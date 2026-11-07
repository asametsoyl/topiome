# Hukuki ve Uyum Belgeleri — Topiome

> ## ⚠️ HUKUKİ İNCELEME GEREKLİDİR — BU BELGELER HUKUKİ TAVSİYE DEĞİLDİR
>
> Bu klasördeki metinler **taslak şablonlardır**. Yayımlanmadan, müşteriye gönderilmeden veya
> sözleşmeye eklenmeden önce Türkiye'de KVKK ve gerekiyorsa AB'de GDPR konusunda uzman bir
> avukat tarafından incelenmelidir. Metinler hiçbir şirket, veri koruma görevlisi, temsilci,
> sertifika veya resmi makam onayı iddiası içermez. Köşeli parantezli alanlar
> (`[ŞİRKET UNVANI]`, `[ADRES]`, `[E-POSTA]` vb.) doldurulmadan yayımlanmamalıdır.

| Alan | Değer |
|---|---|
| Durum | Taslak / şablon — hukuki inceleme yapılmadı |
| Sürüm | 0.1 |
| Son güncelleme | 6 Kasım 2026 |
| Doküman sahibi | [ŞİRKET UNVANI] — Hukuk / Uyum |
| Hukuki inceleme | **Yapılmadı** — [HUKUK BÜROSU / DANIŞMAN] |
| Yürürlük tarihi | [YÜRÜRLÜK TARİHİ] |
| Kapsam | Topiome çok kiracılı SaaS; AB / ABD / Türkiye müşterileri |
| Ürün sınırı | Yalnızca araştırma amaçlı (RUO); klinik tanı, tedavi veya karar desteği değildir |

## 1. Belge dizini

| Belge | Dil | Hedef kitle | Ne için? | Durum |
|---|---|---|---|---|
| [kvkk-aydinlatma.md](./kvkk-aydinlatma.md) | Türkçe | Hesap kullanıcıları, organizasyon yetkilileri, site ziyaretçileri | KVKK m. 10 aydınlatma metni | Taslak |
| [gdpr-privacy-notice.md](./gdpr-privacy-notice.md) | İngilizce | AB/EEA veri sahipleri, AB müşterileri | GDPR m. 13–14 gizlilik bildirimi | Taslak |
| [dpa.md](./dpa.md) | Türkçe + kısa İngilizce özet | Kurumsal müşteriler / veri sorumluları | GDPR m. 28 veri işleme sözleşmesi | Taslak |
| [retention-policy.md](./retention-policy.md) | Türkçe | İç operasyon, müşteri başarı, hukuk | Veri sınıfı bazında saklama ve imha çizelgesi | Taslak |
| [subprocessors.md](./subprocessors.md) | Türkçe | Müşteriler, satın alma, güvenlik | Alt işleyici envanteri ve bildirim süreci | Taslak |
| [data-classification.md](./data-classification.md) | Türkçe | Tüm ekip, ürün, mühendislik, destek | Veri sınıflandırma ve işleme kuralları | Taslak |

## 2. Önerilen okuma sırası

1. **Bu README** — rol modeli, kapsam ve açık kararlar.
2. **[data-classification.md](./data-classification.md)** — hangi veri hangi sınıfta, nasıl davranılır.
3. **[retention-policy.md](./retention-policy.md)** — ne kadar süre saklanır, nasıl silinir.
4. **[kvkk-aydinlatma.md](./kvkk-aydinlatma.md)** — Türkiye'deki ilgili kişilere yapılan bildirim.
5. **[gdpr-privacy-notice.md](./gdpr-privacy-notice.md)** — AB/EEA'daki veri sahiplerine yapılan bildirim.
6. **[dpa.md](./dpa.md)** — müşteriyle imzalanacak veri işleme sözleşmesi.
7. **[subprocessors.md](./subprocessors.md)** — hizmet sağlayıcı listesi ve değişiklik süreci.

## 3. Rol modeli (özet)

Topiome'un rolü veri türüne göre değişir. Bu ayrım, hangi belgenin uygulanacağını belirler.

| Veri türü | Veri sorumlusu | Topiome'un rolü | Uygulanacak belge |
|---|---|---|---|
| Hesap, iletişim, organizasyon üyeliği, faturalama, kullanım/audit kayıtları | [ŞİRKET UNVANI] (Topiome) | **Veri sorumlusu** (controller) | KVKK aydınlatma metni / GDPR gizlilik bildirimi |
| Müşterinin yüklediği araştırma verileri, örnek metadata'sı, analiz parametreleri, türetilmiş sonuçlar ve raporlar | Müşteri kurum (veya kurumunun belirlediği sorumlu) | **Veri işleyen** (processor) | DPA + müşterinin kendi aydınlatma metni |
| Alt işleyici hizmetleri (barındırma, depolama, e-posta, ödeme, hata izleme) | Müşteri (araştırma verisi için) / Topiome (kendi verisi için) | Veri işleyen zincirinin parçası | DPA + [subprocessors.md](./subprocessors.md) |

> **Önemli:** Topiome, müşterinin araştırma verileri için kural olarak veri işleyendir.
> Müşteri, kendi kurumunun veri sorumlusu olduğunu ve Topiome'a talimat verme yetkisini
> teyit etmelidir. Topiome'un kendi hesap/faturalama verileri bu DPA'nın dışındadır ve
> kendi gizlilik bildirimleriyle yönetilir.

## 4. Araştırma verisi sınırı (RUO)

- Topiome **yalnızca araştırma amaçlıdır (Research Use Only)**. Klinik tanı, prognoz, tedavi
  seçimi, terapi izlemi veya klinik karar desteği için tasarlanmamıştır; tıbbi cihaz değildir.
- Müşteri, yüklediği araştırma verilerinin **de-identifiye edilmiş** olduğunu; etik kurul
  onayı, gerekiyorsa katılımcı onamı/rızası ve veri kullanım haklarını aldığını beyan ve
  taahhüt eder.
- **Tanımlanabilir hasta verisi** (ad, hasta numarası, doğum tarihi, tam adres, yüz görüntüsü
  vb.) Phase 1'de kabul edilmez. İstisna ancak ayrı yazılı sözleşme, ek güvenlik tedbirleri ve
  hukuki değerlendirme ile mümkündür.
- Özel nitelikli veri (sağlık, genetik, biyometrik vb.) içeren yüklemeler, ayrı sözleşme ve
  açık rıza/uygun hukuki dayanak olmadan kabul edilmez. De-identifikasyon, verinin her zaman
  anonim hale geldiği anlamına gelmez; genetik veri ve küçük kohortlar yeniden
  tanımlanabilir olabilir.
- Müşteri, paylaştığı raporlarda ve yayınlarda **RUO uyarısını** korumakla yükümlüdür.
- Topiome, müşteri araştırma verilerini açık yazılı anlaşma olmadan ortak model eğitimi,
  genel ürün geliştirme veya pazarlama için kullanmaz.

## 5. Placeholder sözlüğü

Yayın öncesi tüm placeholder'lar doldurulmalı veya bilinçli olarak kaldırılmalıdır.

| Placeholder | Anlamı / not |
|---|---|
| `[ŞİRKET UNVANI]` | Sözleşme tarafı olan tüzel kişilik. "Topiome" bir ürün/marka adıdır; kendiliğinden tüzel kişilik değildir. |
| `[ADRES]` | Kayıtlı merkez adresi. |
| `[E-POSTA]` | Genel iletişim adresi; gizlilik için ayrıca `[GİZLİLİK E-POSTASI]` kullanılabilir. |
| `[VERİ KORUMA GÖREVLİSİ]` | Atanmışsa ad/unvan ve iletişim. **Atanmamışsa "atanmamıştır" yazılmalı; boş bırakılmamalıdır.** |
| `[AB TEMSİLCİSİ]` | GDPR m. 27 kapsamında gerekliyse ad, adres, e-posta. Gerekli değilse gerekçesi kaydedilmeli. |
| `[MÜŞTERİ UNVANI]` | DPA'daki veri sorumlusu müşteri. |
| `[HUKUK BÜROSU / DANIŞMAN]` | İnceleme yapan avukat/danışman. |
| `[YÜRÜRLÜK TARİHİ]` | Yayımlanan sürümün yürürlük tarihi. |
| `[SAĞLAYICI ADI]` | Alt işleyici firma; sözleşme imzalanmadan somut ad yazılmamalı. |
| `[BÖLGE]` | Veri ikametgahı: örn. AB (Frankfurt), Türkiye, ABD. |
| `[YETKİLİ MAHKEME]` | DPA'da seçilecek mahkeme/arbitrasyon. |
| `[DPA TARİHİ]` | Alt işleyiciyle imzalanan DPA'nın tarihi. |

## 6. Açık hukuki kararlar (yayın öncesi)

- [ ] Sözleşme tarafı tüzel kişilik: Türkiye'de Limited/Anonim Şirket mi, AB/ABD şubesi mi?
- [ ] Merkez adres, ticaret sicil/vergi bilgileri ve yetkili imza.
- [ ] Veri koruma görevlisi atanacak mı? Atanmayacaksa gerekçe kayıtlı mı?
- [ ] GDPR m. 27 kapsamında AB temsilcisi gerekli mi?
- [ ] Varsayılan barındırma bölgesi (AB Frankfurt mu, Türkiye mi?) ve müşteriye sunulacak bölge seçenekleri.
- [ ] Barındırma ve nesne depolama sağlayıcısı (AWS / Hetzner / diğer) ve sözleşmeleri.
- [ ] E-posta/SMTP sağlayıcısı; işlemsel e-posta loglarının saklama süresi.
- [ ] Stripe entegrasyonu: hesap modeli, vergi/fatura akışı, kart verisinin saklanmaması.
- [ ] Hata izleme ve ürün analitiği sağlayıcıları; analitik için çerez rızası.
- [ ] AB'den Türkiye'ye / ABD'ye aktarım için SCC ve transfer etki değerlendirmesi (TIA).
- [ ] Türkiye'den yurt dışına aktarım için KVKK standart sözleşmesi veya diğer mekanizma.
- [ ] Saklama varsayılanları (24 ay) ve kurumsal müşteri için azami uzatma süresi.
- [ ] VERBİS kayıt yükümlülüğü var mı; varsa kayıt durumu.
- [ ] ABD eyalet gizlilik yasaları (CCPA/CPRA vb.) ve gerekiyorsa HIPAA/BAA kapsamı.
- [ ] Çerez politikası ve rıza yönetimi (yalnızca zorunlu çerezlerle başlanması önerilir).
- [ ] Denetim/audit hakkının kapsamı ve sıklığı (yılda bir uzaktan anket + gerekirse yerinde).
- [ ] Sigorta (siber sorumluluk) ve sözleşmesel sorumluluk sınırları.
- [ ] Alt işleyici listesinin herkese açık URL'de mi, talep üzerine mi yayımlanacağı.

> Bu maddelerin hiçbiri bu şablonlarda "yapıldı" olarak varsayılmaz. Özellikle **DPO atandığı,
> ISO 27001 / SOC 2 / HIPAA uyumlu olunduğu veya bir sertifika alındığı iddia edilmez.**

## 7. Yayın öncesi kontrol listesi

- [ ] Tüm placeholder'lar dolduruldu; "Topiome" ile tüzel kişilik adı tutarlı.
- [ ] KVKK aydınlatma metni ve GDPR bildirimi aynı veri kategorilerini/saklama sürelerini anlatıyor.
- [ ] DPA, Saklama Politikası ve Alt İşleyici listesi birbiriyle çelişmiyor.
- [ ] Araştırma verisi için "de-identifiye" ve "etik kurul/onam müşteri sorumluluğu" ifadeleri korundu.
- [ ] RUO / klinik olmayan kullanım sınırı tüm belgelerde açık.
- [ ] Alt işleyici listesinde yalnızca gerçekten sözleşmesi olan sağlayıcılar "Aktif" olarak işaretli.
- [ ] Aktarım mekanizması (SCC / KVKK standart sözleşme) ve TIA dosyada.
- [ ] Saklama süreleri ürün ayarları ve otomasyonla uyumlu.
- [ ] Veri ihlali bildirim akışı (iç sorumlular, 24/48/72 saat) test edildi.
- [ ] Hukukçu onayı ve sürüm numarası kaydedildi.
- [ ] Yayımlanan metinler uygulamadaki `/legal/*` sayfalarıyla bağlantılı.
- [ ] Yürürlük tarihi ve değişiklik bildirimi süreci tanımlı.

## 8. Sürüm geçmişi

| Sürüm | Tarih | Değişiklik | Hazırlayan | İnceleyen |
|---|---|---|---|---|
| 0.1 | 6 Kasım 2026 | İlk taslak şablon seti | [ŞİRKET UNVANI] / Ürün | — (hukuki inceleme bekliyor) |

## 9. İlgili dokümanlar

- [../SECURITY.md](../SECURITY.md) — güvenlik kontrolleri, olay müdahalesi, audit log.
- [../DATA.md](../DATA.md) — veri formatları, depolama düzeni, gizlilik sınıfları, silme.
- [../PRODUCT.md](../PRODUCT.md) — ürün kapsamı, RUO, hastalık paketleri.
- [../BUSINESS.md](../BUSINESS.md) — şirketleşme, fiyatlandırma, kurumsal plan.
- [../../apps/web/src/app/legal/privacy/page.tsx](../../apps/web/src/app/legal/privacy/page.tsx) — mevcut gizlilik sayfası.
- [../../apps/web/src/app/legal/terms/page.tsx](../../apps/web/src/app/legal/terms/page.tsx) — mevcut kullanım koşulları.
- [../../apps/web/src/app/legal/ruo/page.tsx](../../apps/web/src/app/legal/ruo/page.tsx) — mevcut RUO politikası.
