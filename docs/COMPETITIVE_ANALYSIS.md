# Spatial transcriptomics rakip analizi

> **Legacy / kapsam dışı (2026-11-07):** Bu belge arşivlenmiş spatial-transkriptomik ürününe aittir. Topiome'un güncel perturbasyon-yanıtı araştırma yönünün rakip analizi değildir; perturbasyon/sanal hücre oyuncuları için ayrı ve kaynaklı bir analiz henüz tamamlanmamıştır. Güncel bilimsel kanıt durumu için `docs/VALIDATION.md` ve `docs/PRODUCT.md` okunmalıdır.

**Tarih:** 2026-11-06  
**Kapsam:** Topiome'un ilk odağı olan araştırma amaçlı kanser spatial-transcriptomics analizini, ürünlerin herkese açık resmî sayfalarına göre karşılaştırır. Bu, ürünleri kurup aynı veri üzerinde çalıştıran bağımsız performans benchmark'ı değildir. Ürün sayfalarındaki yetenekler üretici beyanıdır; bilimsel üstünlük kanıtı sayılmaz.

## Kısa değerlendirme

Pazarın güçlü oyuncuları doku üstü keşif, assay'e özgü veri aktarımı, interaktif gen/spot inceleme, hazır analiz adımları, ekip çalışması ve yayın kalitesinde görselleri iyi paketliyor. Topiome şu anda bunların bazı temel parçalarına sahip: Visium H&E üstü spot haritası, domain/hücre tipi/belirsizlik katmanları, run kıyaslama, sürüm izi ve rapor onay kapısı. Rakiplerden daha iyi olduğunu söylemek için henüz bilimsel benchmark kanıtı yok.

Topiome'un savunulabilir yönü “daha büyük GNN” olmamalı. Daha iyi fırsat, **hastalık paketleri + patolog ground truth'u + çalışma dışı validasyon + spot başına belirsizlik + yeniden üretilebilir rapor** birleşimini araştırmacının kullanacağı basit bir iş akışına dönüştürmek. Bu farklılaşma ancak benchmark kapıları geçildikçe iddia edilebilir.

## Rakipler ve ürün güçlü yanları

| Ürün | Güçlü yaptığı işler | Topiome için çıkarım |
|---|---|---|
| **10x Space Ranger + Loupe Browser** | Visium verisini görüntüye hizalayan doğal assay iş akışı; H&E/IF üstünde gen ve cluster gösterimi; morfoloji anotasyonu; referanssız spot dekonvolüsyonu; mekânsal değişken genler; ROI/threshold seçimi ve figür dışa aktarımı. [10x Visium analiz sayfası](https://www.10xgenomics.com/products/visium-analysis), [Loupe spatial guide](https://www.10xgenomics.com/support/software/loupe-browser/latest/getting-started/lb-what-is-loupe-browser) | Visium yükleme ve viewer kalitesi için doğrudan çıta. Spot/gen katmanı, ROI seçimi, cluster/gene istatistiği ve SVG/PNG export eksikleri kapatılmalı. 10x assay entegrasyonunu assay'ler arası veri/validasyon ve hastalık karşılaştırmasıyla tamamlayabiliriz. |
| **BioTuring SpatialX** | En sert çoklu-platform rakip: Visium, Visium HD, GeoMx, Xenium, CosMx, MERSCOPE ve multiplex imaging; çok katmanlı görüntü; anotasyon/segmentasyon; DGE, komşuluk, hücre tipi, region search/segmentation ve transcript query. Şirket ayrıca geniş scRNA referans veritabanıyla otomatik hücre etiketleme beyan ediyor. [SpatialX](https://bioturing.com/spatialx), [SpatialX feature overview](https://bioturing.com/visualize-analyze-spatial-data-lens) | Viewer/format genişliğinde bugün Topiome'dan ileride. Burada kısa sürede özellik sayısıyla yarışamayız. Topiome'un olası üstünlüğünü patolog etiketli, hastalık bazlı dış benchmark ve spot belirsizliğine kanıt üretmeden söylememeliyiz. |
| **Illumina Connected Multiomics** | Bulut tabanlı çoklu-omik çalışma akışı, interaktif görseller, özelleştirilebilir analizler, biyolojik bilgi bağlantısı, ölçeklenebilir depolama ve güvenli veri yönetimi. Spatial sonuçlarda doku görüntüsü üstünde gösterim, gerçek zamanlı filtre/seçim, DE, marker ve hücre tipi analizi sunuyor. [Ürün sayfası](https://www.illumina.com/products/by-type/informatics-products/connected-multiomics.html) | Bulut güvenilirliği, filtreleme ve çoklu-omik bağlantısı çıtası. Topiome önce küçük ve izlenebilir bir spatial analiz deneyimini sağlamlaştırmalı; sonra assay/modality genişletmeli. |
| **Bruker AtoMx SIP** | CosMx merkezli SaaS; görüntü ve sayım verisini buluta alma; depolama, paylaşım, hazır analiz modülleri/pipeline'lar ve araştırmacının özelleştirebildiği R modülleri. [AtoMx overview](https://brukerspatialbiology.com/products/atomx-spatial-informatics-platform/atomx-sip-overview/) | Bir araştırmacının “dosya yükle → analiz → ekipçe incele → dışa aktar” akışını tamamlıyor. Topiome'un davet/rolleri, audit, worker ve depolama arayüzleri gerçek sağlayıcılarla doğrulanmalı; veri izolasyonu ve pipeline izi görünür olmalı. |
| **Vizgen MERSCOPE Vizualizer** | MERFISH için tek hücre/tek transkript ölçeğinde doku gezintisi; hücre sınırları, yüksek çözünürlüklü görüntüler, gen grupları, ROI, heatmap ve dışarıdan üretilen anotasyon/UMAP sonuçlarını içe alma. [Vizualizer](https://vizgen.com/vizualizer-software/) | Tek hücre ve görüntü odaklı platformların görsel ayrıntı seviyesi çok yüksek. Topiome Visium spotlarını şu anda dürüstçe gösteriyor; Visium HD/Xenium/CosMx desteği ayrı okuyucu ve doğrulama işi olarak planlanmalı, mevcut kabiliyet gibi pazarlanmamalı. |

## Topiome'un bugünkü konumu

**Şimdiden mevcut:** gerçek Visium H5/MTX okuma; sınırlı Visium HD `square_016um` (12.000 tissue spot sınırı); H&E hires görüntüsü üstüne spot bindirme; domain/hücre tipi/belirsizlik; hastalık paketi yapılandırması; iki tamamlanmış run'ı karşılaştırma; pipeline/model/veri izi; RUO ve rapor dışa aktarma onay kapısı.

**Bilimsel sınır:** Breast GNN held-out Macro-F1 0.446 ve ARI 0.260 ile minimum eşikleri geçmedi; breast beta. GBM atlas karşılaştırması olumsuz; GBM beta. Beş hedef hastalık odağı için kayıtların bulunması patolog etiketli eğitim verisi bulunduğu anlamına gelmiyor. Dolayısıyla “doğrulanmış beş hastalık haritası” veya “rakiplerden daha doğru” iddiası şu an kullanılamaz.

**Uygulanan viewer kapsamı:** tek-gen log1p(CP10K) katmanı ve eşik tabanlı spot seçimi; serbest ROI özeti; ROI içi/dışı QC-pass betimleyici gen ve hücre kompozisyonu farkı; iki run'ı yan yana spatial viewer'da inceleme; bir haritada seçilen aynı geni diğer örneğe yükleme, ortak renk ölçeği/eşik; onay/audit kontrollü ROI CSV ve PNG export (ADR-023–025, ADR-027). Bu görsel kıyas istatistiksel test değildir; çok örnekli/cohort analizi hâlâ yok. ROI farkları p-değeri/FDR vermez.

**Kalan ürün boşlukları:** yayınlık SVG (PNG var); mekânsal değişken genler ve doğru hasta/örnek düzeyi diferansiyel analiz; performanslı çok-spot çizim; platform okuyucuları/segmentasyon. Visium HD ve görüntüleme-temelli platformlar için sparse/tiles altyapısı ve assay başına koordinat/validasyon fixture'ları yok; SpatialX kapsamına yetişmek için acele edip uyumsuz veriyi Visium varsayımlarıyla okumamalıyız.

## Rakiplerden daha iyi olabileceğimiz yol

### 1. Önce bilimsel güveni ürünün ana avantajı yap

- Her paket için hasta, kesit, çalışma/site, assay, etiket kaynağı, lisans ve matris hash'ini manifestte tut.
- Patolog etiketlerini ekspresyon/model çıktısından ayrı ground truth olarak kaydet; etiketsiz örnekleri denetimli eğitim veya doğruluk hesabına sokma.
- Her ana sınıfta spot desteği ve hasta sayısını sonuçla birlikte göster; spot sayısını bağımsız örnek sayısı gibi sunma.
- Grafsız/marker baseline'ını ve dış çalışma testini aynı raporda sun. Başarısız kapıları saklama; paket beta/draft kalır.
- Spot başına belirsizlik, QC uyarısı, model kartı ve tam provenance'ı tek tıklamayla dışa aktarılabilir rapora bağla.

### 2. Viewer'da analistin günlük işini tamamla

1. **H&E + spot overlay** temeli var; görüntüyü ve spotları aynı koordinatta doğrulayarak kaliteyi koru.
2. **Gene mode:** tamamlandı — gen arama, normalize ekspresyon katmanı; karşılaştırma ekranında aynı geni iki örneğe yükleme ve ortak renk ölçeği/eşik.
3. **ROI seçimi:** tamamlandı — serbest alan/eşik tabanlı seçim, spot/QC/belirsizlik/domain özeti, QC-pass gen ve hücre kompozisyonu farkları ve onaylı CSV export. Farklar keşif amaçlıdır; patolog ground truth'u veya doğrulayıcı istatistik değildir.
4. **Karşılaştırma ve dışa aktarma:** iki tamamlanmış run'ın spatial map'i, aynı gen katmanı, metrikleri, assay/tür/koşul bağlamı yan yana; PNG/ROI CSV export. Kalan: hasta/çalışma düzeyinde cohort görünümü ve SVG.
5. **Görsel performans:** şu an canvas ile standart Visium; binning/WebGL/tiles, büyük kesitlerde akıcı pan/zoom ve görsel örneklemenin sayısal sonucu değiştirmediği test hâlâ gerekli.

### Topiome için farklılaştırıcı ürün fikirleri

Bunlar rakiplerin sahip olmadığına dair doğrulanmış pazar iddiası değildir; Topiome'un bilimsel güven odağından çıkan, kullanıcılarla test edilmesi gereken farklılaştırıcı tasarım hipotezleridir.

- **Comparability guard:** assay, tür, koşul, disease pack ve pipeline uyumsuzluklarını harita ve tablolarda görünür kıl; doğrudan kıyasın kapsamını belirt. İlk assay/tür/koşul uyarıları eklendi.
- **No-pseudoreplication ROI explorer:** ROI gen farkını keşif olarak göster; komşu spotları bağımsız hasta tekrarı sayıp p-değeri üretme. Doğrulama analizi gerekiyorsa sample/patient düzeyi tasarıma yönlendir.
- **Evidence-to-map audit trail:** her işaretli bölgeden ham barcode, QC, model sürümü, referans ve rapor onayına tek tıkla geri izleme; ileride anotasyon/inceleme kararlarını rol ve audit ile sakla.
- **Fail-closed scientific releases:** hastalık paketi benchmark kapısını geçmeden yayına/"validated" diline açılmasın; negatif veya yetersiz sonuçları aynı görünürlükle göster.

### 3. Ürün genişlemesini kanıta bağla

- Önce meme cohort'unda bağımsız çalışma ve etiket eşleşmesi; sonra CRC, akciğer, prostat, melanom için aynı veri/lisans/etiket protokolü.
- Hemen beş ayrı GNN veya ortak beş-sınıf modeli üretme. Model seçimini dış hasta/çalışma setinde marker/MLP/GNN karşılaştırmasıyla yap.
- Cross-platform iddiasından önce Visium HD ve Xenium/CosMx reader + koordinat + görüntü fixture'ları, assay başına benchmark ve ürün kapasite ölçümü gerekir.
- Kurumsal SaaS farkı için çalışır S3, SMTP, yedekleme, gizli anahtar yönetimi, audit ve tenant-izolasyon kontrollerini gerçek provider'larda doğrula.

## Önerilen başarı ölçütleri

| Alan | Ölçüm | Lansman kapısı |
|---|---|---|
| Bilimsel doğruluk | Pack başına dış çalışma, hasta düzeyi Macro-F1/ARI, sınıf support'u ve kalibrasyon | `docs/VALIDATION.md` minimumları; geçmeyen paket beta/draft |
| Araştırmacı akışı | Ham veriden ilk H&E + spot katmanına süre; okuyucu hatası oranı | Yerel ve cloud ingest senaryolarında süre/başarı raporu |
| Harita kullanımı | Gene/ROI kullanımı, export oranı, oturum başına kesit karşılaştırması | Pilot kullanıcı gözlemi; üretici beyanıyla değil gerçek kullanım verisiyle |
| Tekrarlanabilirlik | Aynı girdi/sürüm/parametrede sonuç özeti ve artifact hash'i | Run manifesti yeniden çalıştırmada eşleşmeli |
| Güven | Belirsiz spotların doğru “incele” uyarısı üretmesi; rapor onayı/audit | Kalibrasyon + uçtan uca audit izi |

## İlk uygulama sırası

1. İndirilen açık veriyi sample/patient/study düzeyinde envantere al; lisans ve anotasyonları doğrula.
2. Meme validasyonunu tek-çalışma sonucu diye açıkça göster; bağımsız test olmadan validated etiketi kullanma.
3. Viewer'da cohort düzeyi gen karşılaştırması, SVG ve ROI kompozisyon farkını tamamla.
4. Aynı protokolle ikinci hastalık paketini ancak bağımsız etiket/çalışma bulunduğunda aç.
5. Sparse/tiles okuyucu ve gerçek assay fixture'larıyla Visium HD, sonra Xenium/CosMx kapsamını ölçülmüş pilot gereksinimine göre sırala.

## Kaynaklar ve sınırlamalar

- [10x Visium Analysis](https://www.10xgenomics.com/products/visium-analysis) — ürün özellikleri ve Loupe/Space Ranger akışı.
- [10x Loupe Browser Spatial guide](https://www.10xgenomics.com/support/software/loupe-browser/latest/getting-started/lb-what-is-loupe-browser) — spatial gene overlay, cluster, DGE ve export.
- [BioTuring SpatialX](https://bioturing.com/spatialx) — çoklu-platform, hücre anotasyonu, DGE, komşuluk ve bölge analizi özellik beyanı.
- [Illumina Connected Multiomics](https://www.illumina.com/products/by-type/informatics-products/connected-multiomics.html) — cloud/multiomic özellik beyanı.
- [Bruker AtoMx SIP](https://brukerspatialbiology.com/products/atomx-spatial-informatics-platform/atomx-sip-overview/) — CosMx odaklı SaaS, pipeline ve custom modules.
- [Vizgen MERSCOPE Vizualizer](https://vizgen.com/vizualizer-software/) — transcript/cell/ROI viewer ve import/export.

Özellikler ürün sağlayıcılarının herkese açık sayfalarından derlenmiştir. Gerçek kullanıcı deneyimi, performans, doğruluk ve fiyat kıyası yapılmadı. Marka sayfaları “kanıtlanmış üstünlük” olarak yorumlanmamalı.
