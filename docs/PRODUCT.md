# Ürün — Topiome

## 1. Vizyon

Her araştırmacının, bir dokunun **hücre kompozisyonunu, mekânsal organizasyonunu ve hastalık bölgelerini** tek bir haritada görebilmesini sağlamak.

Topiome, spatial transcriptomics'i "pahalı ve karmaşık bir veri seti" olmaktan çıkarıp, **tekrarlanabilir, karşılaştırılabilir ve raporlanabilir bir doku haritası**na dönüştürür.

## 2. Problem

- Spatial transcriptomics verisi büyük, gürültülü ve çok formatlı.
- Dekonvolüsyon ve spatial domain modelleri çoğu laboratuvarda tekrar üretilemiyor; doğruluk ve belirsizlik raporlanmıyor.
- Sonuçlar görselleştirilse bile yorum, QC ve raporlama manuel.
- Hastalığa özgü marker/bölge tanımları dağınık; ekipler her projede sıfırdan başlıyor.
- Ticari araçlar ya çok pahalı kurumsal platformlar ya da parçalı script'ler.

## 3. Çözüm

**Topiome = hastalıktan bağımsız analiz çekirdeği + hastalık paketleri + işbirliğine açık raporlama.**

1. **Yükle:** Visium (ve ileride Visium HD / Xenium / CosMx) + scRNA-seq referansı.
2. **Seç:** Hastalık paketi (örn. meme kanseri) ve analiz şablonu.
3. **Çalıştır:** QC → dekonvolüsyon → spatial domain → komşuluk → ilaç hedefi → rapor.
4. **İncele:** Etkileşimli doku haritası, belirsizlik katmanı, hücre tipi dağılımı, bölge istatistikleri.
5. **Paylaş:** Yöntem + sınırlamalar + RUO uyarısı içeren rapor; ekip üyeleriyle paylaşım.

## 4. Hedef kullanıcı

| Segment | İhtiyaç | Ürün değeri |
|---|---|---|
| Akademik araştırma laboratuvarları | Hızlı, tekrarlanabilir analiz; yayın için görsel | Düşük kurulum maliyeti, şeffaf metodoloji |
| Kanser araştırma merkezleri | Çok örnekli karşılaştırma, hipotez üretimi | Hastalık paketleri + benchmark |
| Biyoteknoloji / ilaç Ar-Ge | Hedef ve mikroçevre analizi | İlaç hedefi skorlama, mekânsal kanıt |
| Çekirdek tesisler (core facilities) | Hizmet olarak analiz, rapor | Çok kiracılı, markalı rapor |
| Hastane araştırma birimleri | Veri güvenliği, denetim | On-prem / VPC seçeneği, audit log |

**İlk 18 ay odak:** akademik laboratuvarlar + kanser araştırma merkezleri. Klinik kullanım kapsam dışı (RUO).

## 5. Hastalık seçim kriteri

Bir hastalık paketi ancak şu koşullarda açılır:

1. En az **3 bağımsız çalışmada** yeterli sayıda örnek/spot var.
2. Eşleşen **scRNA-seq referansı** kamuya açık veya lisanslı.
3. Hastalığa özgü **hücre tipleri ve bölge tanımları** literatürde yerleşik.
4. En az bir **annotasyonlu** spatial veri seti (held-out validasyon için).
5. Benchmark eşikleri (`docs/VALIDATION.md`) geçilmiş.

İlk 6 paket: meme, akciğer, kolorektal, prostat, melanom, GBM. Gerekçe: TCGA/HTAN/GEO ve 10x public veri bolluğu.

## 6. Fiyatlandırma (taslak)

| Plan | Yıllık | Kapsam |
|---|---|---|
| Academic | Ücretsiz / onaylı | 1 kullanıcı, 3 proje, temel paketler, topluluk desteği |
| Basic | $129 | 1 kullanıcı, 1 cihaz/oturum, 10 proje, standart paketler |
| Lab | $399 | 3 kullanıcı, 30 proje, öncelikli destek, ortak rapor |
| Institution | Teklif | On-prem/VPC, SSO, sınırsız proje, eğitim, DPA |

Fiyatlar pilot geri bildirimiyle değişecek. Ödeme altyapısı Stripe (test modu) üzerinden kurulacak.

## 7. Değer önerisi (kısa)

> **From spots to story.** Topiome turns spatial transcriptomics into a validated, shareable tissue atlas — with uncertainty visible.

Türkçe:

> **Spotlardan doku hikâyesine.** Topiome, spatial transcriptomics verisini doğrulanmış ve paylaşılabilir bir doku atlasına dönüştürür; belirsizliği görünür kılar.

## 8. Ürün ilkeleri

- **Bilim önce:** Her özellik bir yayın/validasyon sorusuna hizmet etmiyorsa ertelenir.
- **Şeffaflık:** Kullanılan yöntem, sürüm, veri ve sınırlamalar raporun parçasıdır.
- **Belirsizlik bir özellik:** Gizlenmez, arayüzde birinci sınıf vatandaştır.
- **Hız, doğruluğu satmaz:** Demo hızlı olabilir; üretim sonucu benchmark kapısından geçer.
- **RUO:** Klinik iddia yok. Bu, ürünün güven sınırıdır.

## 9. RUO uyarısı (zorunlu metin)

> **For Research Use Only.** Topiome is not intended for diagnosis, prognosis, treatment selection, or clinical decision-making. Results are computational inferences from research data and must be independently validated.

## 10. Başarı metrikleri

- Aktif laboratuvar sayısı, aylık analiz edilen örnek sayısı
- İlk analizden rapora süre (hedef: < 30 dk)
- Rapor indirme / paylaşım oranı
- Pilot kurumlarda tekrar kullanım (retention)
- Benchmark eşiklerini geçen hastalık paketi sayısı
- Kullanıcı başına aylık gelir (ARPU), yıllık yenileme (NRR)
