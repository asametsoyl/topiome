# KVKK Aydınlatma Metni — Taslak

> **HUKUKİ İNCELEME GEREKLİDİR — BU METİN HUKUKİ TAVSİYE DEĞİLDİR.**
> Bu belge 6698 sayılı Kişisel Verilerin Korunması Kanunu ("KVKK") m. 10 kapsamında
> hazırlanmış bir **taslak şablondur**. Yayımlanmadan önce KVKK uzmanı bir avukat tarafından
> incelenmeli, şirketin gerçek işleme faaliyetlerine ve tüzel kişilik bilgilerine göre
> uyarlanmalıdır. Metin, bir veri koruma görevlisinin atandığı, VERBİS kaydının yapıldığı veya
> herhangi bir sertifikanın alındığı iddiasını içermez.

| Alan | Değer |
|---|---|
| Sürüm | 0.1 — taslak |
| Son güncelleme | 6 Kasım 2026 |
| Yürürlük tarihi | [YÜRÜRLÜK TARİHİ] |
| Veri sorumlusu | [ŞİRKET UNVANI] |
| İlgili kişi grupları | Hesap kullanıcıları, organizasyon yetkilileri, site ziyaretçileri, işlem/destek kişileri |
| Uygulama alanı | Topiome çok kiracılı SaaS platformu ve kurumsal web sitesi |

## 1. Veri sorumlusunun kimliği

KVKK m. 10 uyarınca, kişisel verileriniz aşağıdaki veri sorumlusu tarafından işlenmektedir:

| Bilgi | Değer |
|---|---|
| Ticari unvan | **[ŞİRKET UNVANI]** |
| Adres | **[ADRES]** |
| Vergi dairesi / no | [VERGİ DAİRESİ] / [VERGİ NO] |
| Ticaret sicil no | [TİCARET SİCİL NO] |
| E-posta | **[E-POSTA]** |
| Gizlilik iletişim adresi | [GİZLİLİK E-POSTASI] |
| Telefon | [TELEFON] |
| Veri koruma görevlisi | **[VERİ KORUMA GÖREVLİSİ]** — atanmamışsa "atanmamıştır" yazılmalıdır |
| Türkiye'deki temsilci (varsa) | [TÜRKİYE TEMSİLCİSİ] |
| VERBİS kayıt durumu | [VERBİS KAYIT DURUMU / KAPSAM DIŞI / DEĞERLENDİRİLİYOR] |

> "Topiome" bir ürün/marka adıdır. Sözleşme ve mevzuat bakımından veri sorumlusu
> **[ŞİRKET UNVANI]** olarak doldurulmalıdır. Bu şablon tek başına bir tüzel kişilik, DPO
> ataması veya VERBİS kaydı oluşturmaz.

## 2. Kapsam ve ilgili kişi grupları

Bu aydınlatma metni, Topiome'un **kendi veri sorumlusu sıfatıyla** işlediği kişisel veriler
hakkında bilgi verir. Kapsam:

1. Web sitesini ziyaret edenler ve iletişim formu/ demo talebi bırakanlar.
2. Topiome hesabı oluşturan, bir organizasyona davet edilen veya organizasyon yöneten
   kullanıcılar (owner, admin, analyst, viewer).
3. Faturalama, satın alma ve sözleşme süreçlerindeki ilgili kişiler.
4. Destek talebi oluşturan, hata bildiren veya eğitim/etkinlik talep eden kişiler.
5. Müşteri kurumun yüklediği araştırma verilerinde yer alan kişiler — **bu kişiler bakımından
   veri sorumlusu kural olarak müşteri kurumdur**; Topiome veri işleyendir.

> **Araştırma verileri:** Müşterinin yüklediği örnek dosyaları, `sample.json` metadata'sı,
> analiz parametreleri, türetilmiş sonuçlar ve raporlar için veri sorumlusu müşteri kurumdur.
> Topiome bu verileri yalnızca müşterinin talimatları ve DPA kapsamında işler. Bu kişiler
> hakkında aydınlatma yükümlülüğü ve gerekiyorsa açık rıza/etik kurul süreçleri müşteriye
> aittir. Topiome, müşteriye bu konuda makul destek sağlar.

## 3. Roller: veri sorumlusu ve veri işleyen

| Veri grubu | Veri sorumlusu | Topiome'un rolü | Dayanak |
|---|---|---|---|
| Hesap, iletişim, organizasyon üyeliği, oturum, faturalama, kullanım/audit | [ŞİRKET UNVANI] | Veri sorumlusu | KVKK m. 5, m. 6, m. 10 |
| Müşteri tarafından yüklenen araştırma verileri ve türetilmiş çıktılar | Müşteri kurum | Veri işleyen | KVKK m. 12 + DPA |
| Alt işleyici hizmetleri | Müşteri (araştırma verisi) / Topiome (kendi verisi) | Veri işleyen zinciri | DPA + alt işleyici sözleşmeleri |

Topiome, müşterinin araştırma verilerini kendi amaçları için kullanmaz; açık yazılı anlaşma
olmadan ortak model eğitimi, pazarlama veya üçüncü kişilerle paylaşım yapmaz. Topiome'un
kendi hesap ve faturalama verileri bu aydınlatma metninin konusudur.

## 4. İşlenen kişisel veri kategorileri

Aşağıdaki tablo, Topiome'un veri sorumlusu sıfatıyla işlediği verileri gösterir. Müşteri
araştırma verileri ayrıca ve yalnızca DPA kapsamında işlenir.

| Kategori | Örnek veriler | Kaynak | Zorunlu mu? |
|---|---|---|---|
| **Kimlik ve iletişim** | Ad, soyad, e-posta, telefon (opsiyonel), kurum, unvan, ülke | Kullanıcı, müşteri kurum | Hesap açmak için ad/e-posta zorunlu; telefon opsiyonel |
| **Hesap ve organizasyon** | Kullanıcı adı, parola özeti (hash), rol, organizasyon adı, üyelik/davet kaydı, dil ve bildirim tercihleri | Kullanıcı, organizasyon yöneticisi | Zorunlu |
| **Kimlik doğrulama ve oturum** | Oturum çerezi, oturum süresi, IP adresi, tarayıcı/cihaz bilgisi, başarısız giriş kayıtları, MFA durumu (planlanıyorsa) | Teknik sistem | Güvenlik için zorunlu |
| **Kullanım ve audit** | Sayfa/aksiyon kayıtları, analiz başlatma/bitirme, dosya yükleme/indirme/silme, rapor oluşturma/paylaşma, API anahtarı işlemleri, hata kayıtları | Teknik sistem | Güvenlik ve hizmet için zorunlu |
| **Faturalama ve finans** | Plan, fatura, ödeme durumu, vergi bilgileri, Stripe müşteri kimliği/işlem referansı; **kart numarası Topiome'da saklanmaz** | Müşteri, ödeme sağlayıcısı | Sözleşme/mevzuat için zorunlu |
| **Destek ve iletişim** | Talep içeriği, ekler, yazışma, çözüm notları | Kullanıcı | Talep oluşturulursa |
| **Pazarlama ve tercih** | E-posta izni, açılma/tıklama verileri (varsa), etkinlik kaydı, çerez tercihleri | Kullanıcı, teknik sistem | Opsiyonel; rızaya tabi |
| **Güvenlik ve ihlal** | Olay kayıtları, erişim logları, ihlal değerlendirme notları, hukuki saklama kayıtları | Teknik sistem, hukuk/uyum | Güvenlik ve hukuki yükümlülük için zorunlu |

### 4.1 Araştırma verileri hakkında önemli sınır

- Müşteri, yüklediği araştırma verilerinin **de-identifiye edilmiş** olmasını sağlamalıdır.
- **Tanımlanabilir hasta verisi** (ad, hasta numarası, doğum tarihi, tam adres, yüz görüntüsü,
  serbest metinde kimlik bilgisi vb.) Phase 1'de kabul edilmez.
- **Özel nitelikli kişisel veri** (sağlık, genetik, biyometrik, ırk/etnik köken, siyasi
  düşünce, din, cinsel hayat, ceza mahkûmiyeti vb.) içeren yüklemeler, ayrı yazılı sözleşme,
  açık rıza/uygun hukuki dayanak ve ek güvenlik tedbirleri olmadan kabul edilmez.
- De-identifikasyon her zaman anonimleştirme anlamına gelmez. Genetik veri, küçük kohortlar,
  nadir hastalıklar ve birleşik metadata yeniden tanımlamaya yol açabilir. Müşteri, yüklediği
  verinin hukuki niteliğini ve etik/onam yükümlülüklerini değerlendirmekle sorumludur.
- Topiome, dosya içeriğini loglara, demo ortamına, repoya veya üçüncü kişi prompt'larına
  yazmaz.

## 5. İşleme amaçları

Kişisel veriler aşağıdaki amaçlarla işlenir:

1. **Hesap ve hizmet yönetimi:** hesap oluşturma, organizasyon/rol yönetimi, oturum açma,
   hizmetin sunulması, örnek yükleme, analiz çalıştırma, sonuç ve rapor üretme.
2. **Sözleşme ve faturalama:** plan yönetimi, ödeme, fatura, vergi ve tahsilat süreçleri.
3. **Güvenlik:** kimlik doğrulama, yetki kontrolü, organizasyon izolasyonu, kötüye kullanım
   ve sahtecilik tespiti, audit log, olay müdahalesi.
4. **Destek:** soruların yanıtlanması, hata giderme, analiz sorunlarının çözülmesi, eğitim.
5. **Hukuki yükümlülükler:** mevzuat, mahkeme/ yetkili kurum talepleri, saklama ve imha
   yükümlülükleri, ihlal bildirimleri.
6. **Ürün geliştirme:** toplulaştırılmış ve de-identifiye kullanım metrikleriyle hizmetin
   iyileştirilmesi; müşteri araştırma verisiyle model eğitimi **ancak açık yazılı anlaşma**
   varsa.
7. **İletişim ve pazarlama:** hizmet duyuruları, güvenlik bildirimleri, etkinlik/eğitim
   davetleri; pazarlama iletileri yalnızca rıza veya mevzuatın izin verdiği ölçüde.
8. **İş sürekliliği:** yedekleme, felaket kurtarma, hata izleme, kapasite planlama.

Topiome, kişisel verileri bu amaçlarla bağdaşmayan bir şekilde kullanmaz. Araştırma verileri
pazarlama, reklam veya üçüncü kişilere satış amacıyla kullanılmaz.

## 6. Hukuki dayanaklar

KVKK m. 5 ve m. 6 uyarınca işleme, aşağıdaki dayanaklardan birine veya birkaçına dayanır.
Aşağıdaki eşleştirme **taslaktır**; fiili işleme faaliyetleri için veri işleme envanteri
(ROPA) ve hukuki değerlendirme yapılmalıdır.

| İşleme faaliyeti | Başlıca hukuki dayanak | Not |
|---|---|---|
| Hesap açma, hizmet sunma, organizasyon/rol yönetimi | KVKK m. 5/2-(c) sözleşmenin kurulması veya ifası | Hesap açmadan hizmet sunulamaz. |
| Faturalama, ödeme, vergi | m. 5/2-(c) sözleşme; m. 5/2-(ç) hukuki yükümlülük | Muhasebe/vergi mevzuatı ayrıca uygulanır. |
| Güvenlik, audit, kötüye kullanım tespiti | m. 5/2-(f) meşru menfaat | Menfaat dengelemesi yapılmalı ve kayıt altına alınmalıdır. |
| Destek talepleri | m. 5/2-(c) sözleşme; m. 5/2-(f) meşru menfaat | Talep kapsamına göre değerlendirilir. |
| Hukuki talepler, ihlal bildirimi, saklama | m. 5/2-(ç) hukuki yükümlülük; m. 5/2-(f) meşru menfaat | Yetkili kurum talepleri hukuken değerlendirilir. |
| Toplulaştırılmış ürün metrikleri | m. 5/2-(f) meşru menfaat | Mümkünse anonim/toplulaştırılmış veri kullanılır. |
| Pazarlama e-postası | m. 5/1 açık rıza; mevzuatın izin verdiği hallerde m. 5/2-(f) | Ticari elektronik ileti mevzuatı (İYS vb.) ayrıca uygulanır. |
| Opsiyonel çerezler/analitik | m. 5/1 açık rıza | Zorunlu çerezler hizmetin sunulması için m. 5/2-(c)/(f). |
| Özel nitelikli veri (istisnai) | m. 6 kapsamında açık rıza veya kanunda öngörülen istisna | **Araştırma amacı tek başına yeterli değildir; ayrı hukuki inceleme gerekir.** |

**Açık rıza** gerektiğinde, rıza belirli bir konuya ilişkin, bilgilendirmeye dayalı ve özgür
iradeyle açıklanmalıdır. Pazarlama rızası hizmetin kullanımına şart koşulmaz; geri alınabilir.
Açık rıza kayıtları, verildiği kanal, tarih/saat ve kapsamla birlikte saklanır.

**Meşru menfaat** dayanağında Topiome, ilgili kişinin haklarına etkisini dikkate alarak bir
menfaat dengelemesi yapar; güvenlik ve hizmet iyileştirme dışındaki amaçlarda bu dayanağı
geniş yorumlamaz.

## 7. Toplama yöntemi ve zorunluluk

Kişisel veriler; web sitesi formları, hesap kaydı, organizasyon davetleri, destek talepleri,
e-posta yazışmaları, API/uygulama kullanımı, çerezler ve ödeme sağlayıcısı aracılığıyla
elektronik ortamda toplanır.

- Hesap açmak için gereken ad, e-posta ve organizasyon bilgileri **sözleşmenin ifası için
  zorunludur**. Bu bilgiler verilmezse hizmet sunulamaz.
- Faturalama bilgileri, ödeme ve vergi mevzuatı nedeniyle zorunludur.
- Pazarlama izni, opsiyonel çerezler ve opsiyonel profil bilgileri **zorunlu değildir**;
  verilmemesi hizmetin kullanımını engellemez.
- Destek talebine eklenen dosyalarda kişisel/araştırma verisi bulunabilir; kullanıcı, eklediği
  dosyalardan ve bunların de-identifiye olmasından sorumludur. Destek kanalına tanımlanabilir
  hasta verisi gönderilmemelidir.

## 8. Saklama süreleri

Saklama süreleri, veri sınıfına ve amaca göre belirlenir. Ayrıntılı çizelge için
[retention-policy.md](./retention-policy.md) dosyasına bakınız. Özet:

| Veri grubu | Varsayılan saklama |
|---|---|
| Hesap ve organizasyon verileri | Hesap aktif olduğu sürece + kapanıştan sonra 12 ay |
| Oturum verileri | 7 gün (oturum süresi); başarısız giriş kayıtları 90 gün |
| Müşteri araştırma verileri (ham/ türetilmiş/ rapor) | Son aktiviteden sonra 24 ay (org tarafından yapılandırılabilir) |
| Audit log | 24 ay (kurumsal sözleşmeyle uzatılabilir) |
| Uygulama/erişim logları | 90 gün sıcak, 1 yıl arşiv |
| Yedekler | 30 gün döngüsel |
| Fatura/mali kayıtlar | 10 yıl (mevzuat; mali müşavir teyidi gerekir) |
| Destek talepleri | Kapanıştan sonra 24 ay |
| Pazarlama izinleri | Geri alınıncaya kadar + 24 ay |

Süre sonunda veriler silinir, yok edilir veya anonim hale getirilir. Yasal saklama
yükümlülüğü, devam eden bir ihtilaf veya hukuki saklama (legal hold) varsa silme askıya
alınabilir; bu durum kayıt altına alınır.

## 9. Kişisel verilerin aktarılması

### 9.1 Yurt içi aktarım

Topiome, hizmetin sunulması için barındırma, depolama, e-posta, ödeme, hata izleme ve destek
gibi alt işleyicilerden yararlanabilir. Alt işleyici listesi
[subprocessors.md](./subprocessors.md) dosyasında tutulur. Aktarım, DPA ve KVKK m. 8
kapsamında, amaçla sınırlı ve gerekli olduğu ölçüde yapılır.

### 9.2 Yurt dışına aktarım

Varsayılan barındırma bölgesi **[BÖLGE — örn. AB / Frankfurt]** olarak planlanmıştır; Türkiye
bölgesi opsiyonu [DURUM] durumundadır. Yurt dışına aktarım gerektiğinde:

- KVKK m. 9 kapsamında uygun aktarım mekanizması (yeterlilik kararı, standart sözleşme,
  bağlayıcı şirket kuralları veya Kanun'daki diğer şartlar) kullanılır.
- Standart sözleşme kullanılıyorsa, mevzuatın öngördüğü bildirim/saklama yükümlülükleri
  yerine getirilir.
- AB/EEA'dan Türkiye'ye veya ABD'ye aktarımda GDPR kapsamında Standart Sözleşme Hükümleri
  (SCC) ve transfer etki değerlendirmesi (TIA) uygulanır.
- Aktarımın hukuki dayanağı, alıcı ülke, alıcı kategori ve güvenlik tedbirleri kayıt altına
  alınır.

Topiome kişisel verileri **satmaz** ve pazarlama amacıyla üçüncü kişilere kiralamaz. Yetkili
kamu kurumlarının hukuka uygun talepleri, kapsamı ve hukukiliği değerlendirilerek yanıtlanır;
mümkün olduğunda ilgili kişi bilgilendirilir.

## 10. Veri güvenliği

Topiome, KVKK m. 12 ve ilgili mevzuat kapsamında uygun teknik ve idari tedbirleri uygular.
Mevcut ürün ve altyapı kapsamında planlanan/uygulanan başlıca tedbirler:

- TLS 1.2+ ile transit şifreleme; HSTS ve güvenli çerez ayarları.
- Bulut sağlayıcısının disk şifrelemesi; hassas alanlar için uygulama seviyesinde şifreleme
  (Faz 2).
- Parolaların Argon2id ile özetlenmesi; oturum süresi ve iptali.
- Organizasyon bazlı veri izolasyonu; owner/admin/analyst/viewer rol kontrolü; her istekte
  yetki doğrulaması.
- 15 dakika indirme / 60 dakika yükleme süreli imzalı URL'ler; public bucket yok.
- Audit log (giriş, rol değişikliği, yükleme/indirme/silme, run, rapor, API anahtarı,
  faturalama); dosya içeriği loglanmaz.
- Yedeklerin şifrelenmesi ve ayrı hesap/bölgede tutulması; 30 gün döngü.
- Düzenli bağımlılık taraması, güvenli geliştirme, olay müdahale planı ve erişim
  gözden geçirmeleri.
- MFA (TOTP) yol haritasında olup bu şablonun yayımlandığı tarihte garanti edilmez.

> Bu metin ISO 27001, SOC 2, HIPAA veya benzeri bir sertifikasyon/uygunluk iddiası içermez.
> Güvenlik kontrollerinin güncel durumu [../SECURITY.md](../SECURITY.md) dosyasında tutulur.

## 11. Veri ihlali bildirimi

Bir kişisel veri ihlali tespit edildiğinde Topiome:

1. İhlali derhal containment/eradication sürecine alır ve etkiyi değerlendirir.
2. KVKK m. 12 ve ilgili rehber doğrultusunda, öğrenildiği tarihten itibaren **en kısa sürede**
   ve uygulamadaki bildirim süreleri (hedef: 72 saat) içinde Kişisel Verileri Koruma Kurumu'na
   bildirim yapar.
3. Etkilenen ilgili kişilere, ihlalin niteliği, olası sonuçları ve alınması gereken önlemler
   hakkında makul olan en kısa sürede bilgi verir.
4. İhlal kaydını, müdahale adımlarını ve alınan düzeltici tedbirleri saklar.

Müşteri araştırma verilerine ilişkin bir ihlalde Topiome, veri sorumlusu müşteriye **en geç
48 saat içinde** (kritik olaylarda hedef 24 saat) ön bildirim yapar; müşteri kendi yasal
bildirim yükümlülüklerini yerine getirir. Ayrıntılar DPA'da düzenlenir.

## 12. İlgili kişinin hakları (KVKK m. 11)

KVKK m. 11 uyarınca ilgili kişi olarak:

1. Kişisel verilerinizin işlenip işlenmediğini öğrenme,
2. İşlenmişse buna ilişkin bilgi talep etme,
3. İşlenme amacını ve amacına uygun kullanılıp kullanılmadığını öğrenme,
4. Yurt içinde veya yurt dışında aktarıldığı üçüncü kişileri bilme,
5. Eksik veya yanlış işlenmişse düzeltilmesini isteme,
6. KVKK m. 7 şartları çerçevesinde silinmesini veya yok edilmesini isteme,
7. Düzeltme/silme işlemlerinin aktarıldığı üçüncü kişilere bildirilmesini isteme,
8. Münhasıran otomatik sistemlerle analiz edilme suretiyle aleyhinize bir sonucun ortaya
   çıkmasına itiraz etme,
9. Kanuna aykırı işleme nedeniyle zarara uğramanız halinde zararın giderilmesini talep etme
   haklarına sahipsiniz.

**Başvuru yöntemi:** Talebinizi yazılı olarak **[ADRES]** adresine veya **[GİZLİLİK
E-POSTASI]** adresine iletebilirsiniz. Başvuruda ad-soyad, iletişim bilgisi ve talebin konusu
belirtilmeli; kimlik doğrulaması için makul bilgi istenebilir. **Başvuruya tanımlanabilir hasta
verisi veya araştırma dosyası eklenmemelidir.**

Topiome talepleri, niteliğine göre **en geç 30 gün içinde** ücretsiz olarak yanıtlar. Mevzuatta
öngörülen bir ücret tarifesi varsa ilgili kişi önceden bilgilendirilir. Talebin reddedilmesi
halinde gerekçe yazılı olarak bildirilir; ilgili kişi Kişisel Verileri Koruma Kurulu'na şikâyet
edebilir.

> Araştırma verileri bakımından veri sorumlusu müşteri kurum olduğundan, bu verilere ilişkin
> hak talepleri öncelikle müşteriye yönlendirilmelidir. Topiome, veri işleyen olarak müşteriye
> makul destek sağlar ve talebi doğrudan yanıtlamaz; ancak hukuki zorunluluk varsa hareket eder.

## 13. Çocukların verileri

Topiome kurumsal araştırma kullanıcılarına yöneliktir ve 18 yaş altındaki kişilere doğrudan
hizmet sunmak için tasarlanmamıştır. Araştırma verilerinde çocuklara ait de-identifiye veri
bulunabilir; bu durumda etik kurul onayı, onam/rıza ve yerel mevzuat yükümlülükleri müşteriye
aittir.

## 14. Değişiklikler

Topiome bu metni mevzuat, ürün veya alt işleyici değişikliklerine göre güncelleyebilir.
Önemli değişiklikler yayımlandığı tarihte sitede duyurulur ve organizasyon sahiplerine e-posta
ile bildirilir. Önceki sürümler [SÜRÜM ARŞİVİ] adresinde saklanır.

## 15. İletişim

| Konu | İletişim |
|---|---|
| Genel gizlilik/KVKK soruları | **[GİZLİLİK E-POSTASI]** |
| Veri koruma görevlisi | **[VERİ KORUMA GÖREVLİSİ]** — atanmamışsa "atanmamıştır" |
| Posta adresi | **[ADRES]** |
| Güvenlik olayları | [GÜVENLİK E-POSTASI] |
| Ticari ileti tercihleri | [İYS / E-POSTA] |

## Ek A — Müşteri için araştırma verisi kontrol listesi

Bu ek, Topiome'un müşteriye sağladığı pratik bir hatırlatmadır; hukuki görüş değildir.

- [ ] Yüklenen veri de-identifiye edildi; doğrudan tanımlayıcılar çıkarıldı.
- [ ] Dosya adları, metadata, görüntü/header ve serbest metin alanları kontrol edildi.
- [ ] Etik kurul onayı alındı; gerekiyorsa katılımcı onamı/rızası mevcut.
- [ ] Veri kullanım hakkı ve lisansı var; üçüncü kişi verisi için izin alındı.
- [ ] Özel nitelikli veri varsa ayrı hukuki dayanak ve ek tedbirler değerlendirildi.
- [ ] Küçük kohort/nadir hastalık nedeniyle yeniden tanımlama riski değerlendirildi.
- [ ] Saklama süresi ve silme planı organizasyon politikasıyla uyumlu.
- [ ] Rapor/paylaşımda RUO uyarısı korunuyor.
- [ ] Destek taleplerine tanımlanabilir hasta verisi eklenmiyor.
- [ ] Müşterinin kendi aydınlatma metni, veri sahiplerine ulaştırıldı.

## Ek B — İşleme envanteri için minimum alanlar

| Alan | Açıklama |
|---|---|
| İşleme faaliyeti | Örn. hesap yönetimi, faturalama, audit log |
| Veri kategorileri | Kimlik, iletişim, araştırma verisi, kullanım vb. |
| İlgili kişi grupları | Kullanıcı, organizasyon yöneticisi, faturalama kişisi |
| Amaç | Somut ve meşru amaç |
| Hukuki dayanak | KVKK m. 5/6; GDPR m. 6/9 (varsa) |
| Alıcılar/alt işleyiciler | [subprocessors.md](./subprocessors.md) |
| Yurt dışı aktarım | Ülke, mekanizma, TIA referansı |
| Saklama süresi | [retention-policy.md](./retention-policy.md) |
| Güvenlik tedbirleri | [data-classification.md](./data-classification.md) |
| Silme yöntemi | Otomatik/manuel, yedekler dahil |
