# Veri İşleme Sözleşmesi (DPA) — Taslak

> **HUKUKİ İNCELEME GEREKLİDİR — BU METİN HUKUKİ TAVSİYE DEĞİLDİR.**
> Bu belge, GDPR m. 28 ve KVKK m. 12 ile uyumlu olması amaçlanan bir **taslak** veri işleme
> sözleşmesidir. İmzalanmadan önce tarafların hukukçuları tarafından incelenmeli; ticari
> sözleşme (Ana Sözleşme), hizmet kapsamı ve gerçek veri akışlarıyla uyumlu hale getirilmelidir.
> Metin tek başına bir tüzel kişilik, DPO ataması, alt işleyici ilişkisi veya sertifika
> yaratmaz.

| Alan | Değer |
|---|---|
| Sürüm | 0.1 — taslak |
| Son güncelleme | 6 Kasım 2026 |
| Taraflar | [MÜŞTERİ UNVANI] (Veri Sorumlusu) ve [ŞİRKET UNVANI] (Veri İşleyen) |
| İlişkili belgeler | Ana Sözleşme, [subprocessors.md](./subprocessors.md), [retention-policy.md](./retention-policy.md), [data-classification.md](./data-classification.md) |
| Uygulanacak hukuk | [UYGULANACAK HUKUK] |
| Yetkili mahkeme/arbitrasyon | [YETKİLİ MAHKEME] |

## Taraflar

**Veri Sorumlusu ("Müşteri"):**

| Bilgi | Değer |
|---|---|
| Ticari unvan | **[MÜŞTERİ UNVANI]** |
| Adres | [MÜŞTERİ ADRESİ] |
| Temsilci | [AD SOYAD / UNVAN] |
| E-posta | [MÜŞTERİ E-POSTASI] |
| Vergi/tescil bilgisi | [VERGİ NO / TİCARET SİCİL NO] |

**Veri İşleyen ("Topiome" veya "İşleyen"):**

| Bilgi | Değer |
|---|---|
| Ticari unvan | **[ŞİRKET UNVANI]** |
| Adres | **[ADRES]** |
| Temsilci | [AD SOYAD / UNVAN] |
| E-posta | **[E-POSTA]** |
| Vergi/tescil bilgisi | [VERGİ NO / TİCARET SİCİL NO] |

> "Topiome" bir ürün/marka adıdır; sözleşme tarafı **[ŞİRKET UNVANI]** olarak doldurulmalıdır.

## Arka plan

(A) Müşteri, Topiome çok kiracılı yazılım hizmetini (spatial transcriptomics analizi, veri
depolama, sonuç ve rapor üretimi) kullanmak istemektedir.

(B) Müşteri, hizmete yüklediği araştırma verileri bakımından veri sorumlusu; Topiome ise bu
verileri Müşteri adına ve talimatları doğrultusunda işleyen veri işleyendir.

(C) Taraflar, kişisel verilerin GDPR (özellikle m. 28) ve KVKK (özellikle m. 12) başta olmak
üzere uygulanabilir veri koruma mevzuatına uygun işlenmesini sağlamak için bu Sözleşme'yi
akdetmiştir.

## 1. Tanımlar

Bu Sözleşme'de:

- **Ana Sözleşme:** Taraflar arasındaki Topiome hizmet kullanım sözleşmesi ve ekleri.
- **Kişisel Veri:** Tanımlanmış veya tanımlanabilir bir gerçek kişiye ilişkin her türlü bilgi.
- **Özel Nitelikli Kişisel Veri:** Sağlık, genetik, biyometrik, ırk/etnik köken, siyasi düşünce,
  din, cinsel hayat, ceza mahkûmiyeti gibi özel koruma gerektiren veriler.
- **İşleme:** Toplama, kaydetme, depolama, değiştirme, açıklama, aktarma, silme, yok etme dahil
  her türlü işlem.
- **Veri İhlali:** Kişisel verilerin kazara veya hukuka aykırı olarak imha edilmesi, kaybedilmesi,
  değiştirilmesi, yetkisiz açıklanması veya erişilmesi.
- **Alt İşleyici:** Topiome tarafından veri işleme faaliyetlerinin bir kısmını yürütmek üzere
  görevlendirilen üçüncü kişi.
- **SCC:** 2021/914 sayılı AB Komisyonu Uygulama Kararı ile kabul edilen Standart Sözleşme
  Hükümleri.
- **KVKK:** 6698 sayılı Kişisel Verilerin Korunması Kanunu.
- **GDPR:** (EU) 2016/679 sayılı Genel Veri Koruma Tüzüğü.
- **Hizmet:** Ana Sözleşme kapsamında sunulan Topiome SaaS hizmeti.
- **Araştırma Verisi:** Müşterinin yüklediği örnek dosyaları, `sample.json` metadata'sı, analiz
  parametreleri, türetilmiş çıktılar, raporlar ve ilgili manifestler.

## 2. Tarafların rolleri ve kapsam

2.1. **Müşteri veri sorumlusudur.** Araştırma Verisi ve bu verilerde yer alan kişisel veriler
bakımından işleme amaçlarını ve araçlarını belirler; ilgili kişilere karşı aydınlatma, hukuki
dayanak, etik kurul/onam ve veri sahibi hakları yükümlülüklerini taşır.

2.2. **Topiome veri işleyendir.** Kişisel Verileri yalnızca Müşteri'nin belgelenmiş talimatları,
Ana Sözleşme ve bu Sözleşme kapsamında işler. Topiome, kendi hesap, faturalama, güvenlik ve
kullanım verileri bakımından ayrı bir veri sorumlusu olup bu veriler bu Sözleşme'nin kapsamı
dışındadır; bunlar Topiome'un kendi gizlilik bildirimlerine tabidir.

2.3. Müşteri, bir kurum adına hareket ediyorsa veya kendisi de bir veri işleyen ise, veri
sorumlusundan bu Sözleşme'yi akdetme ve Topiome'a talimat verme yetkisini aldığını beyan eder.
Bu durumda Müşteri, kendi alt işleyicileriyle gerekli sözleşmeleri yapmakla sorumludur.

2.4. Topiome, Müşteri'nin Araştırma Verisi'ni kendi amaçları için kullanmaz; açık yazılı
anlaşma olmadan ortak model eğitimi, pazarlama, satış veya üçüncü kişilerle paylaşım yapmaz.
Topiome, verileri yeniden tanımlamaya çalışmaz ve Müşteri'yi de buna teşvik etmez.

2.5. **Klinik sınır:** Hizmet yalnızca araştırma amaçlıdır (RUO). Topiome klinik tanı, tedavi
veya karar desteği sunmaz. Müşteri, hizmeti klinik amaçla kullanmayacağını ve tanımlanabilir
hasta verisi yüklemeyeceğini kabul eder; istisna ancak ayrı yazılı sözleşme ve hukuki
değerlendirme ile mümkündür.

## 3. İşlemenin konusu, süresi, niteliği ve amacı

3.1. **Konu:** Topiome'un, Müşteri'nin Araştırma Verisi'ni ve ilgili kişisel verileri hizmetin
sunulması amacıyla işlemesi.

3.2. **Süre:** Ana Sözleşme'nin yürürlükte olduğu süre ve Ek 13'teki silme/iade süreleri.

3.3. **Niteliği:** Depolama, erişim, kopyalama, hesaplama, analiz, rapor üretimi, yedekleme,
güvenlik izleme, destek ve hata giderme.

3.4. **Amaç:** Müşteri'nin yüklediği örnekleri işlemek, analiz sonuçlarını ve raporları üretmek,
sonuçları Müşteri'nin erişimine sunmak, hizmeti güvenli ve sürekli biçimde sağlamak.

3.5. Ayrıntılı veri kategorileri, ilgili kişi grupları ve talimatlar **Ek A**'da; güvenlik
tedbirleri **Ek B**'de; alt işleyiciler **Ek C**'de; SCC seçimi **Ek D**'de yer alır.

## 4. Talimatlar ve sınırlar

4.1. Topiome, Kişisel Verileri yalnızca Müşteri'nin yazılı talimatları doğrultusunda işler.
Ana Sözleşme, bu Sözleşme ve Ek A bu talimatları oluşturur.

4.2. Topiome, bir talimatın GDPR, KVKK veya diğer uygulanabilir veri koruma mevzuatını ihlal
ettiğini düşünürse Müşteri'yi derhal bilgilendirir ve talimatın hukuka uygun hale getirilmesini
bekleyebilir. Topiome, hukuken zorunlu olduğu hallerde talimat olmadan da işleyebilir; bu
durumda Müşteri'yi, hukuken yasak değilse, önceden bilgilendirir.

4.3. Topiome, Müşteri'nin yazılı talimatı olmadan:

- Kişisel Verileri üçüncü kişilerle paylaşmaz (alt işleyiciler ve hukuki zorunluluklar hariç);
- verileri kendi pazarlama, reklam veya satış faaliyetlerinde kullanmaz;
- ortak model eğitimi için kullanmaz;
- verileri başka bir müşteriyle karıştırmaz;
- verileri yeniden tanımlamaya çalışmaz.

4.4. Müşteri, talimatlarının hukuka uygunluğundan ve yüklediği verilerin gerekli haklara/onamlara
dayanmasından sorumludur. Topiome, Müşteri'nin veri sahiplerinden gerekli izinleri aldığını
varsayar; ancak makul şüphe halinde ek bilgi talep edebilir.

## 5. Gizlilik ve personel

5.1. Topiome, Kişisel Verilere yalnızca hizmetin sunulması için gerekli olan personel ve
yüklenicilerin erişmesini sağlar (need-to-know).

5.2. Erişimi olan personel, gizlilik yükümlülüğü altındadır; uygun olduğu ölçüde yazılı gizlilik
taahhüdü alınır ve veri koruma eğitimi verilir.

5.3. Topiome, personelinin erişim yetkilerini rol bazlı olarak sınırlar, periyodik olarak gözden
geçirir ve işten ayrılan personelin erişimini derhal kaldırır.

5.4. Topiome, Müşteri'nin yazılı izni olmadan Kişisel Verileri kendi çalışanları dışında
üçüncü kişilere açıklamaz; alt işleyiciler bu kuralın istisnasıdır ve Bölüm 7'ye tabidir.

## 6. Güvenlik tedbirleri

6.1. Topiome, GDPR m. 32 ve KVKK m. 12 kapsamında uygun teknik ve idari tedbirleri uygular.
Tedbirler, verinin niteliği, risk düzeyi ve teknolojik gelişmeler dikkate alınarak belirlenir.

6.2. Asgari tedbirler **Ek B**'de sayılmıştır. Topiome, Ek B'deki tedbirleri Müşteri'nin
onayı olmadan önemli ölçüde zayıflatamaz; eşdeğer veya daha güçlü bir tedbirle değiştirebilir.

6.3. Topiome, güvenlik olaylarını tespit, müdahale ve kayıt altına alma süreçlerini yürütür;
Müşteri'yi Bölüm 9'a göre bilgilendirir.

6.4. Bu Sözleşme, Topiome'un ISO 27001, SOC 2, HIPAA veya benzeri bir sertifikaya sahip olduğu
iddiasını içermez. Mevcut kontroller [../SECURITY.md](../SECURITY.md) ve Ek B'de açıklanmıştır.

## 7. Alt işleyiciler

7.1. Müşteri, Topiome'un Ek C'de listelenen alt işleyicileri kullanmasına **genel yazılı
onay** verir. Güncel liste [subprocessors.md](./subprocessors.md) adresinde tutulur.

7.2. Topiome, yeni bir alt işleyici görevlendirmeden veya mevcut bir alt işleyiciyi önemli
ölçüde değiştirmeden önce Müşteri'ye **en az 30 gün önce** yazılı bildirim yapar. Bildirim,
alt işleyicinin adı, hizmeti, veri kategorileri, işleme yeri ve aktarım mekanizmasını içerir.

7.3. Müşteri, bildirimi takip eden 30 gün içinde makul veri koruma gerekçeleriyle yazılı olarak
itiraz edebilir. Taraflar makul sürede uzlaşamazsa Müşteri, etkilenen hizmeti feshedebilir ve
önceden ödenmiş ücretin kullanılmayan kısmını iade alabilir. Bu, Müşteri'nin diğer fesih
haklarını sınırlamaz.

7.4. Topiome, alt işleyicilerle yazılı sözleşme yapar; bu sözleşmeler en az bu Sözleşme'deki
veri koruma yükümlülüklerine eşdeğer koruma sağlar. Topiome, alt işleyicilerin yükümlülüklerini
yerine getirmesinden Müşteri'ye karşı sorumludur.

7.5. Alt işleyici listesinde yalnızca gerçekten sözleşmesi olan sağlayıcılar "Aktif" olarak
işaretlenir. Aday veya planlanan sağlayıcılar "Planlandı" olarak gösterilir ve sözleşme
imzalanmadan veri işlemeye başlamaz.

## 8. Veri sahibi hakları

8.1. Topiome, Müşteri'ye veri sahibi taleplerini yanıtlama konusunda makul teknik ve idari
destek sağlar. Hizmet, verilerin görüntülenmesi, düzeltilmesi, indirilmesi ve silinmesi için
self-servis araçlar sunar.

8.2. Topiome, kendisine ulaşan bir veri sahibi talebini, hukuken doğrudan yanıtlaması
gerekmiyorsa, gecikmeksizin Müşteri'ye yönlendirir; Müşteri'yi bilgilendirir ve talebi doğrudan
yanıtlamaz.

8.3. Topiome, GDPR m. 28(3)(e) ve KVKK m. 12 kapsamında, veri sahibi haklarının kullanılması
için gerekli bilgileri sağlar. Müşteri, talebin hukuka uygunluğunu ve kapsamını değerlendirir.

## 9. Veri ihlali bildirimi

9.1. Topiome, bir Kişisel Veri ihlalinden haberdar olduğunda:

- derhal containment, etki değerlendirmesi ve delil koruma sürecini başlatır;
- Müşteri'ye **en geç 48 saat içinde** (kritik/P1 olaylarda hedef 24 saat) ön bildirim yapar;
- bildirimde ihlalin niteliği, etkilenen veri kategorileri, olası sonuçlar, alınan/acil
  tedbirler ve iletişim noktası hakkında mevcut bilgileri paylaşır;
- ek bilgiler netleştikçe bildirimi günceller;
- Müşteri'nin yasal bildirimlerini yapması için makul destek sağlar.

9.2. Topiome, Müşteri'nin yazılı onayı olmadan ihlal hakkında kamuya açıklama yapmaz; ancak
hukuken zorunlu olduğu haller saklıdır.

9.3. Topiome, ihlal kayıtlarını, müdahale adımlarını ve düzeltici tedbirleri saklar. Müşteri,
kendi veri sorumlusu yükümlülükleri kapsamında yetkili otoriteye ve ilgili kişilere bildirim
yapmaktan sorumludur.

9.4. Bildirim süreleri, ihlalin niteliği ve mevcut bilgilerle sınırlıdır; Topiome makul olmayan
bir gecikme olmadan hareket eder.

## 10. Veri koruma etki değerlendirmesi (DPIA)

10.1. Müşteri, kendi işleme faaliyetleri için DPIA yapmakla yükümlüdür. Topiome, makul talep
üzerine DPIA için gerekli bilgileri (işleme niteliği, veri kategorileri, güvenlik tedbirleri,
alt işleyiciler, aktarımlar) sağlar.

10.2. Topiome, yüksek riskli bir işleme fark ederse Müşteri'yi bilgilendirir ve makul destek
verir; ancak DPIA'nın hukuki sorumluluğu Müşteri'ye aittir.

## 11. Denetim

11.1. Topiome, Müşteri'ye bu Sözleşme'ye uyum konusunda makul kanıt sağlar. Bu kapsamda yılda
en fazla bir kez:

- yazılı güvenlik/uyum anketi veya denetim raporu paylaşılabilir;
- Müşteri'nin makul talebi üzerine, 30 gün önceden yazılı bildirimle ve iş saatleri içinde
  yerinde denetim yapılabilir.

11.2. Denetim, Müşteri'nin kendi verileriyle sınırlıdır; diğer müşterilerin verilerine, ticari
sırlara ve güvenlik kontrollerinin zayıflatılmasına yol açacak şekilde yapılamaz. Denetçi
gizlilik yükümlülüğü altında olmalıdır.

11.3. Denetim masrafları kural olarak Müşteri'ye aittir; ancak Topiome'un esaslı sözleşme
ihlali tespit edilirse makul denetim masrafları Topiome tarafından karşılanır.

11.4. Topiome, tespit edilen eksiklikleri makul sürede giderir ve Müşteri'ye düzeltici tedbir
planını bildirir.

## 12. Uluslararası aktarımlar

12.1. Topiome, Kişisel Verileri Ek A/C'de belirtilen ülkelerde işleyebilir. Varsayılan bölge
**[BÖLGE]** olup Türkiye bölgesi [DURUM] durumundadır.

12.2. AB/EEA dışına aktarımda, yeterlilik kararı yoksa **SCC (EU) 2021/914, Modül 2**
(veri sorumlusundan veri işleyene) ve Ek D'de belirtilen ekler uygulanır. Gerekli hallerde
Modül 3 (işleyenden işleyene) kullanılır. Transfer etki değerlendirmesi (TIA) yapılır ve
tamamlayıcı tedbirler kaydedilir.

12.3. Türkiye'den yurt dışına aktarımda KVKK m. 9 kapsamındaki uygun mekanizma (yeterlilik
kararı, standart sözleşme, bağlayıcı şirket kuralları veya Kanun'daki diğer şartlar) kullanılır;
standart sözleşmenin bildirim/saklama yükümlülükleri yerine getirilir.

12.4. Topiome, yeni bir ülkeye aktarım veya alt işleyici değişikliği durumunda Müşteri'yi
Bölüm 7'ye göre bilgilendirir ve gerekli sözleşmesel ekleri günceller.

12.5. Taraflar, SCC'lerin bu Sözleşme ile çeliştiği ölçüde SCC'lerin uygulanacağını kabul eder.
SCC Ek I (taraflar), Ek II (güvenlik tedbirleri) ve Ek III (alt işleyiciler) bu Sözleşme'nin
Ek A/B/C'siyle eşleştirilir; çelişki halinde SCC'ler üstün gelir.

## 13. Verilerin iadesi ve silinmesi

13.1. Ana Sözleşme'nin sona ermesinden itibaren **30 gün** içinde Müşteri, verilerini
self-servis araçlarla veya yazılı taleple dışa aktarabilir. İhracat; ham dosyalar, türetilmiş
çıktılar, raporlar, `sample.json` ve manifestleri kapsar.

13.2. İhracat süresi sonunda Topiome, Müşteri'nin Kişisel Verilerini ve Araştırma Verisi'ni
**30 gün içinde** siler veya iade eder; hangisinin seçileceği Müşteri'nin yazılı talimatına
göre belirlenir. Silme; birincil sistemler, nesne depolama ve aktif yedekleri kapsar. Yedek
kopyaları 30 günlük döngü içinde kendiliğinden silinir.

13.3. Topiome, yasal saklama yükümlülüğü veya hukuki saklama (legal hold) nedeniyle silme
yapamıyorsa, bunu Müşteri'ye yazılı olarak bildirir; veriler yalnızca bu amaçla ve erişim
kısıtlamasıyla saklanır.

13.4. Müşteri'nin talebi üzerine Topiome, silme işlemini makul ölçüde belgeleyen bir yazı
sağlar. Bu belge, bir bağımsız denetim/ sertifikasyon iddiası değildir.

13.5. Silme sonrası Topiome, yalnızca anonim/toplulaştırılmış istatistikleri ve yasal olarak
saklaması gereken audit/fatura kayıtlarını tutabilir; bunlar kişisel veri içermeyecek şekilde
minimize edilir.

## 14. Sorumluluk ve tazminat

14.1. Her taraf, bu Sözleşme'yi ihlal etmesi nedeniyle diğer tarafın uğradığı doğrudan zararları
karşılar. Sorumluluk, Ana Sözleşme'deki sorumluluk sınırlamalarına tabidir.

14.2. Bu Sözleşme'deki sorumluluk sınırlamaları, emredici hukuk kuralları, kasıt, ağır ihmal
veya kişisel verilerin hukuka aykırı işlenmesinden doğan ve sınırlandırılması mümkün olmayan
yükümlülükleri sınırlamaz.

14.3. GDPR m. 82 ve KVKK kapsamındaki sorumluluk, ilgili mevzuatın emredici hükümlerine tabidir.
Taraflar, zararın doğmasına birlikte sebep oldukları ölçüde sorumluluğu aralarında paylaşır.

## 15. Süre ve fesih

15.1. Bu Sözleşme, Ana Sözleşme'nin yürürlüğe girdiği tarihte yürürlüğe girer ve Ana
Sözleşme'nin sona ermesine kadar devam eder.

15.2. Ana Sözleşme'nin sona ermesi, bu Sözleşme'yi de sona erdirir; ancak Bölüm 5 (gizlilik),
Bölüm 9 (ihlal kayıtları), Bölüm 11 (denetim kayıtları), Bölüm 13 (iade/silme), Bölüm 14
(sorumluluk) ve Bölüm 17 (uygulanacak hukuk) yürürlükte kalır.

15.3. Taraflardan biri bu Sözleşme'yi esaslı olarak ihlal ederse, diğer taraf yazılı bildirimle
ve makul düzeltme süresi tanıyarak Sözleşme'yi feshedebilir. Veri koruma ihlali acil risk
oluşturuyorsa düzeltme süresi beklenmeyebilir.

## 16. Değişiklikler

16.1. Bu Sözleşme'deki değişiklikler yazılı olarak yapılır ve tarafların yetkili temsilcileri
tarafından imzalanır.

16.2. Mevzuat değişikliği veya yeni bir alt işleyici/aktarım nedeniyle yapılması gereken
değişiklikler, tarafların makul işbirliğiyle ve veri koruma seviyesini azaltmadan uygulanır.

16.3. Topiome, standart DPA'sının yeni bir sürümünü yayımlarsa, Müşteri'nin yazılı onayı
olmadan Müşteri aleyhine esaslı değişiklik uygulamaz.

## 17. Uygulanacak hukuk ve uyuşmazlık

17.1. Bu Sözleşme **[UYGULANACAK HUKUK]** hukukuna tabidir. Ana Sözleşme'deki hukuk seçimiyle
çelişki halinde, veri koruma yükümlülükleri bakımından emredici hükümler saklı kalmak kaydıyla
Ana Sözleşme esas alınır.

17.2. Uyuşmazlıklarda **[YETKİLİ MAHKEME / ARBITRASYON]** yetkilidir. Tüketici veya zayıf taraf
koruyan emredici yetki kuralları saklıdır.

## 18. Öncelik sırası

18.1. Çelişki halinde sırasıyla: (i) SCC'ler (uygulanabildiği ölçüde), (ii) bu Sözleşme,
(iii) Ana Sözleşme, (iv) diğer ekler uygulanır.

18.2. Bir hüküm geçersizse, kalan hükümler yürürlükte kalır; taraflar geçersiz hükmün amacına
uygun geçerli bir hükümle değiştirilmesi için makul çaba gösterir.

## İmza

| Veri Sorumlusu — [MÜŞTERİ UNVANI] | Veri İşleyen — [ŞİRKET UNVANI] |
|---|---|
| Ad soyad: | Ad soyad: |
| Unvan: | Unvan: |
| Tarih: | Tarih: |
| İmza: | İmza: |

---

## Ek A — İşleme detayları

| Alan | Açıklama |
|---|---|
| İşlemenin konusu | Topiome SaaS üzerinden spatial transcriptomics araştırma verilerinin depolanması, işlenmesi, analizi ve raporlanması |
| Süre | Ana Sözleşme süresi + Bölüm 13'teki iade/silme süresi |
| İşlemenin niteliği | Toplama, depolama, kopyalama, hesaplama, analiz, rapor üretimi, yedekleme, güvenlik izleme, destek |
| Amaç | Müşteri'nin araştırma verilerini işlemek ve hizmeti sunmak |
| Veri kategorileri | Araştırma Verisi (Visium dosyaları, scRNA-seq referansı, `sample.json`, parametreler, türetilmiş çıktılar, raporlar); hesap/audit verileri (Müşteri kullanıcılarına ait) |
| İlgili kişi grupları | Müşteri personeli/kullanıcıları; Araştırma Verisi'nde yer alan kişiler (de-identifiye) |
| Özel nitelikli veri | Kural olarak yok. İstisna: ayrı yazılı sözleşme, açık rıza/uygun dayanak ve ek tedbirlerle sınırlı. |
| İşleme sıklığı | Sürekli (hizmet kullanımı boyunca) |
| Talimatlar | Ana Sözleşme, bu DPA, ürün dokümantasyonu ve Müşteri'nin yazılı talepleri |

## Ek B — Asgari güvenlik tedbirleri

| Alan | Tedbir |
|---|---|
| Erişim kontrolü | Rol bazlı erişim (owner/admin/analyst/viewer), en az yetki, organizasyon izolasyonu, periyodik erişim gözden geçirmesi |
| Kimlik doğrulama | Argon2id parola özeti, güvenli oturum çerezi, oturum süresi/iptali; MFA (TOTP) yol haritasında, bu taslakta garanti edilmez |
| Şifreleme (transit) | TLS 1.2+, HSTS, güvenli çerez ayarları |
| Şifreleme (rest) | Sağlayıcı disk şifrelemesi; hassas alanlar için uygulama seviyesinde şifreleme (Faz 2) |
| Ağ | Veritabanı dışarı açık değil; internal network; yönetim erişimi kısıtlı |
| Dosya erişimi | 15 dk indirme / 60 dk yükleme imzalı URL; public bucket yok; tenant bazlı yol |
| Loglama | Audit log (giriş, rol, yükleme/indirme/silme, run, rapor, API anahtarı, faturalama); dosya içeriği ve hasta verisi loglanmaz |
| Yedekleme | Şifreli, ayrı hesap/bölge, 30 gün döngü; aylık restore testi |
| Güvenlik açığı | Bağımlılık taraması (npm audit/pip-audit), Dependabot, güvenli geliştirme, code review |
| Olay müdahalesi | Tespit → sınıflandırma (P1–P4) → containment → delil → düzeltme → bildirim → post-mortem |
| Personel | Gizlilik taahhüdü, need-to-know, eğitim, ayrılışta erişim kaldırma |
| Fiziksel | Bulut sağlayıcısının veri merkezi kontrolleri; Topiome ofisinde kilitli/kısıtlı erişim |
| İmha | Güvenli silme/yok etme; yedeklerde döngüsel silme; imha kaydı |
| Ortamlar | Dev/staging/prod ayrı; prod verisi dev'e kopyalanmaz |

> Bu tablo, bir sertifikasyon veya bağımsız denetim iddiası değildir. Güncel kontroller ve
> bilinen eksikler [../SECURITY.md](../SECURITY.md) dosyasındadır.

## Ek C — Alt işleyiciler

| Kategori | Sağlayıcı | Hizmet | Veri kategorileri | İşleme yeri | Aktarım mekanizması | Durum |
|---|---|---|---|---|---|---|
| Bulut barındırma / veritabanı | [SAĞLAYICI ADI] | Uygulama, Postgres, loglar | Hesap, kullanım, Araştırma Verisi | [BÖLGE] | SCC / KVKK standart sözleşme | Planlandı |
| Nesne depolama | [SAĞLAYICI ADI] | Ham/türetilmiş dosyalar, raporlar | Araştırma Verisi | [BÖLGE] | SCC / KVKK standart sözleşme | Planlandı |
| E-posta/SMTP | [SAĞLAYICI ADI] | İşlemsel e-posta, davet, parola sıfırlama | Kimlik, iletişim, hesap | [BÖLGE] | SCC / KVKK standart sözleşme | Planlandı |
| Ödeme | [SAĞLAYICI ADI] (Stripe adayı) | Plan, fatura, ödeme durumu | Faturalama, iletişim | [BÖLGE] | SCC; sağlayıcı mekanizması teyit edilecek | Planlandı |
| Hata izleme | [SAĞLAYICI ADI] | Hata/performans izleme | Kullanım, teknik log (dosya içeriği hariç) | [BÖLGE] | SCC / KVKK standart sözleşme | Planlandı |
| Ürün analitiği | [SAĞLAYICI ADI] | Toplulaştırılmış kullanım metrikleri | Kullanım (rızaya tabi) | [BÖLGE] | SCC / KVKK standart sözleşme | Planlandı |
| Destek/helpdesk | [SAĞLAYICI ADI] | Destek talepleri | Kimlik, iletişim, talep içeriği | [BÖLGE] | SCC / KVKK standart sözleşme | Planlandı |

Güncel ve ayrıntılı liste: [subprocessors.md](./subprocessors.md). Yalnızca gerçekten sözleşmesi
olan sağlayıcılar "Aktif" olarak işaretlenir; "Planlandı" kayıtları veri işlemez.

## Ek D — SCC seçimi ve ekler

| SCC unsuru | Seçim |
|---|---|
| Modül | Modül 2 (veri sorumlusundan veri işleyene); gerekiyorsa Modül 3 |
| Madde 7 (docking clause) | [UYGULANACAK / UYGULANMAYACAK] |
| Ek I — Taraflar | Bu DPA'nın taraf bilgileri |
| Ek I — İşleme detayları | Ek A |
| Ek II — Güvenlik tedbirleri | Ek B |
| Ek III — Alt işleyiciler | Ek C |
| Uygulanacak hukuk (Madde 17) | [AB ÜYE DEVLETİ HUKUKU] |
| Yetkili mahkeme (Madde 18) | [MAHKEME] |
| TIA referansı | [TIA DOSYA/DOSYA NO] |
| KVKK standart sözleşme | [VAR / YOK / GEREKLİ DEĞİL] — [BİLDİRİM TARİHİ] |

---

## Short English summary

*This summary is for convenience only; the Turkish text prevails. It is a template, not legal
advice.*

- **Roles:** The customer is the controller of research data it uploads; Topiome is the
  processor. Topiome is an independent controller for its own account, billing, and usage data.
- **Instructions:** Topiome processes personal data only on the customer's documented
  instructions, under the MSA, this DPA, and Annex A. Topiome does not use research data for
  shared model training, marketing, or sale without written agreement.
- **Research boundary:** Research data must be de-identified. Identifiable patient data and
  special category data are not accepted without a separate agreement, legal basis, and
  additional safeguards. The service is RUO, not for clinical use.
- **Security:** Annex B lists minimum measures (tenant isolation, RBAC, TLS, encryption at rest,
  signed URLs, audit logs, encrypted backups, incident response). No ISO 27001/SOC 2/HIPAA
  certification is claimed.
- **Subprocessors:** General written authorization; the current list is in Annex C and
  `subprocessors.md`; 30 days' prior notice of changes; a right to object and terminate the
  affected service.
- **Breach:** Topiome notifies the customer without undue delay and within 48 hours (24-hour
  target for critical incidents), provides available details, and supports the customer's
  regulatory notifications. The customer remains responsible for notifying authorities and data
  subjects.
- **Data subject rights:** Topiome provides self-service tools and reasonable assistance;
  requests are forwarded to the customer as controller.
- **Audit:** Annual written security questionnaire or report; one on-site audit per year with
  30 days' notice, limited to the customer's data and subject to confidentiality.
- **International transfers:** SCC Module 2 (or Module 3 where applicable) and a TIA for
  transfers outside the EEA; KVKK Article 9 mechanisms for transfers from Türkiye.
- **Return and deletion:** 30-day export window after termination, then deletion/return within
  30 days; backups age out within the 30-day cycle; legal holds are notified.
- **Liability and law:** Subject to the MSA's liability limits and mandatory law; governing law
  and forum are placeholders to be completed by counsel.

> **Legal review required.** Complete all placeholders, attach the SCCs and TIA where applicable,
> and have qualified counsel review this DPA before signature.
