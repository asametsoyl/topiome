# İş Modeli ve Şirketleşme — Topiome

> **Eski varsayımlar (2026-11-07):** Aşağıdaki abonelik, fiyat ve gelir hedefleri spatial ürün için yazılmıştır; yeni araştırma yönünde iş modeli henüz belirlenmedi. Bilimsel fizibilite ve kullanıcı ihtiyacı görülmeden bu varsayımlar kullanılmamalıdır.

> Hukuki/mali tavsiye değildir. Kuruluş öncesi mali müşavir ve avukatla görüşülmelidir.

## 1. Şirket yapısı (öneri)

- **Türkiye'de:** Teknoloji odaklı Limited Şirket veya A.Ş. (yatırım alacaksa A.Ş. daha uygun).
- **Faaliyet:** yazılım geliştirme, bilimsel Ar-Ge, veri analizi hizmeti.
- **Fikri mülkiyet:** Kurucuların eski projedeki katkıları yazılı olarak şirkete devredilmeli (IP assignment).
- **Teknofest:** Eski proje kapsamındaki haklar/taahhütler kontrol edilmeli; ticari ürün ayrı marka ve kod tabanıyla ilerlemeli.
- **Yurt dışı satış:** İlk aşamada Türkiye'den hizmet ihracı; ölçekte AB/ABD şubesi opsiyonel.

## 2. Gelir modeli

| Kalem | Model | Not |
|---|---|---|
| Abonelik | Yıllık, kullanıcı/org | Ana gelir |
| On-prem kurulum | Yıllık lisans + kurulum | Kurumsal |
| Hizmet | Analiz/rapor, eğitim | Akademik core facility |
| API kullanımı | Kredi paketi | Faz 2 |
| Veri/model işbirliği | Proje bazlı | Faz 3, dikkatli sözleşme |

## 3. Fiyatlandırma ilkeleri

- Akademik için ücretsiz/indirimli katman → benimseme + referans.
- Laboratuvar planı, tek kullanıcı planının 3× değerini sunmalı.
- Kurumsal fiyat teklif bazlı; on-prem ve destek maliyeti yansıtılır.
- Yıllık ödeme teşvik edilir (2 ay indirim).
- Pilot: 3 ay ücretsiz/indirimli, karşılığında vaka çalışması + geri bildirim.

## 4. İlk 12 ay hedefleri

| Çeyrek | Hedef |
|---|---|
| Q1 | Çalışan ürün, 3 pilot kurum, 10 kullanıcı |
| Q2 | 6 hastalık paketi beta, ilk ödeme yapan 5 müşteri |
| Q3 | 20 ödeyen müşteri, $25k ARR, 2 vaka çalışması |
| Q4 | 40 müşteri, $75k ARR, on-prem 1 kurum, yatırım/fon başvurusu |

## 5. Go-to-market

1. **Akademik ağ:** Teknofest çevresi, üniversite laboratuvarları, kanser araştırma merkezleri.
2. **İçerik:** Metodoloji yazıları, benchmark raporları, "spatial transcriptomics 101" rehberleri.
3. **Konferans:** AACR, EACR, single-cell/spatial toplulukları, Türkiye biyoinformatik günleri.
4. **Core facility işbirlikleri:** Hizmet olarak Topiome raporu.
5. **Açık kaynak / topluluk:** Benchmark kodu ve veri şeması açık; ürün kapalı.
6. **Referans:** Her pilot için ölçülebilir vaka çalışması (süre, maliyet, keşif).

## 6. Rekabet

| Rakip türü | Örnek | Topiome farkı |
|---|---|---|
| Kurumsal spatial platformlar | 10x Cloud, NanoString/Lunaphore yazılımları | Hastalık paketleri + şeffaf validasyon + fiyat |
| Genel bioinformatics araçları | Partek, Qlucore, GSEA | Uçtan uca workflow + rapor + işbirliği |
| Açık kaynak pipeline'lar | Scanpy/Squidpy, Cell2location | Kullanım kolaylığı, tekrarlanabilirlik, destek |
| Kod servisleri | Danışmanlık | Ölçeklenebilir SaaS + düşük marjinal maliyet |

## 7. Savunulabilirlik (moat)

- Doğrulanmış disease pack'ler + benchmark verisi (zamanla biriken).
- Kullanıcı geri bildirimiyle iyileşen annotasyon ve rapor şablonları.
- Kurum içi veri ağı etkisi (aynı org içinde karşılaştırma).
- Regülasyon ve güven (RUO, audit, KVKK) — kopyalaması pahalı.
- Marka ve akademik referanslar.

## 8. Ekip ve roller (ilk 6 ay)

| Rol | Sorumluluk | Kim |
|---|---|---|
| CEO / ürün | Strateji, satış, pilotlar | kurucu |
| CTO / bilim | Pipeline, validasyon, mimari | kurucu |
| Bioinformatician | Disease pack, benchmark, veri | 1 kişi (part-time olabilir) |
| Full-stack | Web/API/UI | 1 kişi |
| Danışman | Patoloji/onkoloji, regülasyon | 2 kişi |

## 9. Yatırım / fon

- Teknofest sonrası: TÜBİTAK 1512 BiGG, KOSGEB Ar-Ge, üniversite teknoparkı.
- Melek/yatırım: $250k–500k pre-seed; milestone bazlı.
- Kullanım: ürün, validasyon, ilk satış, regülasyon danışmanlığı.
- Yatırımcıya gösterilecek metrikler: pilot sayısı, aktif kullanıcı, ARR, benchmark sonuçları.

## 10. Riskler ve azaltma

| Risk | Azaltma |
|---|---|
| Bilimsel doğruluk iddiası kanıtlanmazsa | RUO + beta etiketi; doğruluk iddiasını ertele |
| Veri lisansı ihlali | Lisans kaydı + hukuk kontrolü |
| Klinik kullanım baskısı | Ayrı ürün hattı; RUO sınırını koru |
| Tek kurucuya bağımlılık | Dokümantasyon + ekip |
| Uzun satış döngüsü | Akademik self-serve + pilot |
| Fiyat baskısı | Değer bazlı fiyat; core facility kanalı |

## 11. İlk 90 gün yapılacaklar

1. Şirket türü ve ortaklık yapısı kararı.
2. Marka tescili başvurusu + domain alımı.
3. IP devir sözleşmeleri.
4. 3 pilot kurumla görüşme ve niyet mektubu.
5. Ürün demo + benchmark sonuçları.
6. KVKK/GDPR taslak metinleri.
7. Fiyatlandırma testi (5 görüşme).
8. TÜBİTAK/KOSGEB başvuru takvimi.
