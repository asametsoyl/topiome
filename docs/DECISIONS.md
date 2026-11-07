# Karar Kayıtları (ADR) — Topiome

> Mimariyi etkileyen her karar buraya eklenir. Format: bağlam → karar → sonuçlar.

## ADR-001 — Web SaaS + Python analiz motoru
**Tarih:** 2026-11-06
**Bağlam:** Eski ürün Electron masaüstüydü; lisans dağıtımı ve güncelleme zor. Ticari ürün çok kullanıcılı olmalı.
**Karar:** Next.js web uygulaması + FastAPI/Python analiz servisi. Gerekirse ileride on-prem paket.
**Sonuç:** Uzaktan erişim, kolay güncelleme, abonelik. Dezavantaj: veri yükleme ve gizlilik yönetimi gerekir.

## ADR-002 — Hastalıktan bağımsız çekirdek + YAML disease packs
**Tarih:** 2026-11-06
**Bağlam:** "Her hastalık" ancak ortak çekirdek + konfigürasyonla ölçeklenir.
**Karar:** Pipeline kodu hastalıktan bağımsız; marker, zone, hedef, rapor şablonu YAML'da.
**Sonuç:** Yeni hastalık = veri + validasyon işi. Şema ve sürümleme zorunlu.

## ADR-003 — RUO konumlandırma
**Tarih:** 2026-11-06
**Bağlam:** Klinik ürün regülasyonu (IVDR/ISO 13485) ağır; ekip ve kanıt henüz hazır değil.
**Karar:** Ürün Research Use Only. Klinik iddia yok; klinik yol ayrı faz/ürün.
**Sonuç:** Hızlı lansman, düşük regülasyon yükü. Ticari sınır: hastane klinik kullanımı kapsam dışı.

## ADR-004 — Next.js ve FastAPI ayrımı
**Tarih:** 2026-11-06
**Bağlam:** UI/SEO için JS ekosistemi; analiz için Python ekosistemi.
**Karar:** İki uygulama, tek repo; `/api/*` Next.js rewrite ile FastAPI'ye proxy.
**Sonuç:** Doğru araçlar, bağımsız ölçekleme. Dezavantaj: iki deploy, tip paylaşımı için OpenAPI.

## ADR-005 — Faz 1'de NNLS baseline
**Tarih:** 2026-11-06
**Bağlam:** Ağır modeller (Cell2location/Tangram/GraphST) kurulumu zorlaştırır; önce ölçülebilir bir baseline gerek.
**Karar:** Faz 1'de NumPy/SciPy NNLS + grafik smoothing + KMeans/Leiden. Ağır modeller opsiyonel adaptör.
**Sonuç:** Hızlı, şeffaf, test edilebilir. Doğruluk sınırlı; benchmark ile ölçülür.

## ADR-006 — SQLite (dev) / PostgreSQL (prod)
**Tarih:** 2026-11-06
**Bağlam:** Yerel kurulum sürtünmesini azaltmak; prod'da eşzamanlılık ve JSONB.
**Karar:** SQLAlchemy ile her ikisi; Alembic migration.
**Sonuç:** Tek komutla dev. Prod'da Postgres zorunlu.

## ADR-007 — exFAT diskte geliştirme
**Tarih:** 2026-11-06
**Bağlam:** Kullanıcı projeyi Samsung exFAT diskte istiyor.
**Karar:** Repo diskte; symlink çalışıyor. Performans sorun olursa `node_modules`/`.venv` APFS'e taşınıp symlink verilecek.
**Sonuç:** Taşınabilirlik. Risk: yavaş I/O, bazı araçlarda sert bağlantı sorunu.

## ADR-008 — Marka: Topiome (çalışma adı)
**Tarih:** 2026-11-06
**Bağlam:** Glio adı tek hastalığa bağlı; yeni çatı marka gerek.
**Karar:** Topiome. Domainler boş; tescil kontrolü bekliyor.
**Sonuç:** Hastalıktan bağımsız marka. Yedek: Mappiome, Cartiome, Tissiome.

## ADR-009 — Auth: kendi JWT cookie + Argon2
**Tarih:** 2026-11-06
**Bağlam:** Dış auth servisi maliyet/bağımlılık; ihtiyaç basit.
**Karar:** FastAPI içinde Argon2id + httpOnly JWT cookie; ileride MFA/SSO.
**Sonuç:** Tam kontrol, düşük maliyet. Güvenlik testleri kritik.

## ADR-010 — Hastalık önceliği: veri zenginliği
**Tarih:** 2026-11-06
**Bağlam:** Eski model doğruluğu düşüktü; az veri ana neden.
**Karar:** İlk 6 paket: breast, colorectal, lung, melanoma, prostate, GBM. Veri zenginliği düşük hastalık açılmaz.
**Sonuç:** Daha güvenilir benchmark; kapsam daha yavaş büyür.

## ADR-011 — Alembic migration'ları + exFAT uyumlu çalıştırıcı
**Tarih:** 2026-11-06
**Bağlam:** Şema `create_all` ile kuruluyordu; yeni kolonlar (rapor onayı, run provenance) mevcut veritabanlarına eklenemiyordu. Ayrıca exFAT diskte macOS her dosyanın yanına `._*.py` yazıyor ve stok Alembic bunları migration sanıp çöküyor.
**Karar:** `apps/api/migrations` (0001 başlangıç şeması, 0002 onay+provenance). Uygulama açılışında `upgrade_db()` çalışır; Alembic'ten önce oluşturulmuş DB'ler 0001'e damgalanıp yükseltilir. CLI her zaman `uv run python -m app.migrate …` ile çağrılır (`._*` dosyalarını atlayan yama burada).
**Sonuç:** Şema değişiklikleri izlenebilir ve geri alınabilir. Bare `alembic` komutu bu diskte kullanılmamalı.

## ADR-012 — Rapor onay kapısı (kural #6)
**Tarih:** 2026-11-06
**Karar:** Rapor `draft` doğar; önizlemede görünür "Draft — not approved" bandı vardır. `POST /runs/{id}/report/approve` (analyst+) RUO onay kutusu ister, onaylayanı/zamanı/notu kaydeder ve raporu yeniden üretir. `GET /runs/{id}/report/export` yalnızca onaylı raporu indirir; her onay ve dışa aktarma audit log'a yazılır. Viewer rolü okuyabilir ve onaylı raporu indirebilir, veri değiştiremez/onaylayamaz.
**Sonuç:** İnsan onayı olmadan rapor dışarı çıkmaz. İleride "dört göz" (onaylayan ≠ run sahibi) eklenebilir.

## ADR-013 — Run provenance kaydı (kural #5)
**Tarih:** 2026-11-06
**Karar:** Her run `runs.provenance` JSON'unda pipeline sürümü, paket id/sürüm/SHA-256 parmak izi, referans sürümü, parametreler, girdi dosyası SHA-256'ları, sentetik seed ve yazılım sürümleri (commit, Python, NumPy, SciPy, scikit-learn, pandas) tutar. Commit sırası: `TOPIOME_GIT_COMMIT` → `git rev-parse` (+`-dirty`) → `unversioned`.
**Sonuç:** Repo henüz git deposu olmadığı için commit şu an `unversioned`; `git init` sonrası otomatik dolar.

## ADR-014 — Glio-Cartography'den taşınanlar ve bilinçli olarak taşınmayanlar
**Tarih:** 2026-11-06
**Bağlam:** Eski ürünün (v3.2.9, `~/Downloads/glio-cartography-main`) bağımsız validasyon raporları (GSE237183, GSE331374) ve kod denetimi incelendi.
**Taşınanlar:**
1. *Yöntemler arası uyum* (Tangram–NNLS kontrolünün karşılığı): NNLS + marker z-skor softmax; spot başına 1−JSD uyumu belirsizliğe %25 ağırlıkla girer, ortalama < 0.7 ise uyarı.
2. *Uzamsal ligand–reseptör skoru* (otokrin + satır-normalize parakrin). **Değişiklik:** eski sıfır model (hücre tipi oranlarını karıştırmak) liberaldi — ifade edilen hemen her çift anlamlı çıkıyordu (sentetik GBM'de 10/10). Yeni sıfır model alıcı sinyalini spotlar arasında karıştırır (sentetik GBM'de 3/10) ve BH-FDR uygulanır.
3. *Bağımsız Ivy GAP atlas kontrolü* (GBM; 28 gen × 5 yapı). **Değişiklik:** zon etiketlemede kullanılan marker genleri karşılaştırmadan otomatik dışlanır (eski uygulamada döngüsellik vardı). Sentetik veride çalıştırılmaz.
4. *"Not assessed" sınırları* (IDH/MGMT/WHO derecesi vb.) her pakette ve raporda.
**Taşınmayanlar:** GNN zon modeli (hedefi dekonvolüsyon çıktısı → döngüsel), knockout simülasyonu, TCGA risk / sağkalım, eğitilmemiş ilaç yanıtı başlıkları, lisans/makine kimliği, Electron güncelleyici. RUO ve bilimsel geçerlilik gerekçesiyle.
**Not:** GBM paketine Ivy GAP "cellular tumor" zonu eklemek sentetik domain ARI'yi 0.60 → 0.48'e düşürdü (kapı 0.55); geri alındı, atlas kontrolü 4 eşleşen yapıyla yapılır.

## ADR-015 — Turbopack dosya önbelleği kapalı (exFAT)
**Tarih:** 2026-11-06
**Bağlam:** `next build` "Failed to open database / invalid digit found in string" ile düşüyordu; sebep `.next/cache/turbopack` içindeki `._v16…` AppleDouble dosyaları.
**Karar:** `turbopackFileSystemCacheForDev/Build` varsayılan kapalı; `TOPIOME_TURBOPACK_FS_CACHE=1` ile açılabilir (APFS'te).
**Sonuç:** Derleme biraz daha yavaş ama güvenilir.

## ADR-016 — Sürümlü referanslar + patolog etiketli GNN

**Tarih:** 2026-11-06
**Bağlam:** Eski GNN, pipeline'ın kendi dekonvolüsyon çıktısını hedef aldığı için döngüseldi. Gerçek doku-domain doğruluğu ölçülmemişti.
**Karar:** Referans imzalar ve domain modelleri paket içinde sürümlenir (`references/`, `models/`) ve SHA-256 ile provenance'a yazılır. Meme modeli Wu 2021 patolog spot etiketleriyle, hasta düzeyi 4/2 split ile eğitilir; test hastaları referans, gen seçimi, epoch seçimi ve kalibrasyonda kullanılmaz. Eğitim PyTorch (offline), çıkarım NumPy (API imajında torch yok).
**Sonuç:** Held-out ARI 0.260 < 0.35 kapısı geçilmedi → breast beta. Model gerçek örnekte uygulanır, sentetikte ve gen kapsamı < %80'de atlanır. Bağımsız kohort ve GBM modeli hâlâ yok.

## ADR-017 — Redis/RQ yerine Postgres tabanlı worker kuyruğu

**Tarih:** 2026-11-06
**Bağlam:** Faz 1'de ek servis (Redis) işletme maliyeti ve hata yüzeyi getirir; run hacmi düşük.
**Karar:** `runs.status` Postgres'te kuyruk görevi görür. API yalnızca `queued` kaydı açar; `python -m app.worker` tek UPDATE ile atomik sahiplenir. `QUEUE_MODE=inline` geliştirmede aynı kodu BackgroundTasks ile çalıştırır. Kesinti kurtarma ve `RUN_TIMEOUT_HOURS` vardır.
**Sonuç:** Daha az bileşen, aynı izolasyon. Polling gecikmesi ~2 sn, otomatik retry/backoff yok. Ölçek/retry gerekince Redis/RQ veya Celery'ye geçilebilir; arayüz `services/queue.py` içinde izole.

## ADR-018 — Docker imajlarında non-root sahiplik + exFAT build bağlamı

**Tarih:** 2026-11-06
**Bağlam:** İlk gerçek Docker build'inde API konteyneri "Could not import module app.main" verdi. Sebep: exFAT kaynak dosyaları 0700 ve `COPY` sonrası root'a aitti; `USER topiome` okuyamıyordu. Ayrıca BuildKit, `._*` AppleDouble dosyalarının xattr'ında `operation not permitted` veriyordu.
**Karar:** API imajında kullanıcı erken oluşturulur ve tüm kaynak `COPY --chown=topiome:topiome` ile alınır. exFAT'te build, `._*` içermeyen temiz kopyadan yapılır (`docs/DEPLOY.md`).
**Sonuç:** Dört servisli compose gerçekten build edilip healthy durumda çalıştırıldı; worker run'ı tamamladı. CI/Linux checkout'ta ek işlem gerekmez.

## ADR-019 — Faz 2 ürünleşme sınırları: davet, MFA, API anahtarı, ödeme ve depolama

**Tarih:** 2026-11-06
**Bağlam:** Pilot kullanım için ekip erişimi, hesap güvenliği, programatik erişim, plan limitleri ve harici depolama temeli gerekiyor; ancak gerçek Stripe/S3/SMTP/Redis hesapları henüz seçilmedi.
**Karar:**
1. Organizasyon davetleri tek kullanımlık rastgele token içerir; veritabanında yalnız SHA-256 özeti saklanır, süre sonunda kabul edilemez ve kabul/iptal audit'e yazılır.
2. MFA TOTP + tek kullanımlık recovery code kullanır. MFA yönetimi interaktif session gerektirir; API key TOTP kuramaz veya kapatamaz.
3. API key secret'i yalnız oluşturma yanıtında döner, DB'de SHA-256 özeti kalır ve anahtarlar en fazla analyst rolüyle çalışır. Admin, faturalama ve güvenlik ayarları için session gerekir.
4. Plan limitleri yazma anında API'de uygulanır. Stripe Checkout ve imzalı webhook kullanılır; secret/price ID yoksa faturalama kapalı kalır.
5. S3 uyumlu backend dosyaları nesne depolamada tutar; analiz worker'ı gereken prefix'i yerel cache'e materialize eder. İndirme signed URL ile yapılır.
6. Postgres run kuyruğu korunur. Retry/backoff bu kuyrukta uygulanır; Redis bu aşamada yalnız rate-limit sayaçlarını paylaşmak için opsiyoneldir.
7. E-posta SMTP ile gönderilir; SMTP yoksa davet oluşturma yine çalışır ve admin'e kabul bağlantısı gösterilir.
**Sonuç:** Çekirdek servislere erişim olmadan yerel geliştirme çalışır. Gerçek provider doğrulaması, fiyat/vergi politikası ve veri bölgesi kararı ayrıca tamamlanmalıdır. MFA TOTP secret'larının at-rest şifrelemesi ayrı bir güvenlik işi olarak açık kalır.

## ADR-020 — Web'den API'ye büyük dosya aktarımını akışlı yap

**Tarih:** 2026-11-06
**Bağlam:** Next.js rewrite proxy varsayılan 10 MB gövde sınırını aşıyor ve multipart yüklemeyi sessizce kesiyordu. GSE331374 `.h5` + spatial arşivi toplam 13 MB olduğundan UI'dan gerçek örnek yükleme bu sınırda bozuldu.
**Karar:** `/api/*` çağrıları Next.js catch-all Route Handler üzerinden FastAPI'ye aktarılır. İstek gövdesi okunup belleğe alınmaz; Web Streams doğrudan upstream `fetch`'e, yanıt gövdesi de istemciye aktarılır. Same-origin URL ve httpOnly cookie davranışı korunur; hedef `API_URL` ile belirlenir.
**Sonuç:** 13 MB gerçek Visium yüklemesi UI E2E'den geçti; Next.js'in 10 MB rewrite proxy sınırı ve büyük gövdeyi yükselterek bellekte tutma gereği ortadan kalktı. Uygulama API'nin mevcut 2 GB kota/yükleme sınırına bağlı kalır. Ürün hacmi büyüdüğünde API'yi doğrudan internete açmadan S3 multipart/presigned upload ayrıca değerlendirilmelidir.

## ADR-021 — GNN iddiası için etiket ve dış kohort kapısı

**Tarih:** 2026-11-06
**Bağlam:** Mevcut gerçek etiketli domain modeli yalnız meme Wu 2021 kohortunda 6 hastaya (4 eğitim, 2 aynı çalışma içi test) dayanıyor ve minimum ARI/Macro-F1 kapılarını geçmiyor. Diğer kanserlerde indirilmiş expression matrisi olması patolog etiketli GNN örneği olduğu anlamına gelmez; hastalık domain ontolojileri de aynı değil.
**Karar:** Beş kanser için beş ayrı denetimli GNN hemen eğitilmeyecek; mevcut GNN beta kalır. Her görev önce patolog/bağımsız referans ground truth, çoğunluk ve marker baseline, aynı özelliklerle grafsız MLP karşılaştırması ve hasta/tercihen çalışma dışı test alır. GNN yalnızca bu adil karşılaştırmada grafsız baseline'a tekrarlanabilir katkı gösterip önceden belirlenmiş kapıları geçerse tutulur. Ortak encoder olasılığı ancak yeterli çok-hastalık etiketli/self-supervised veri ve doğrulanabilir ortak hedef bulunduğunda yeniden değerlendirilir; farklı ontolojiler tek sınıf kafasına zorlanmaz.
**Sonuç:** Örnek sayısı model eğitimi için yanlış sinyal olmaz; başarı iddiası bağımsız hasta/çalışma genellemesine bağlı kalır. Veri ve metrik protokolü `docs/VALIDATION.md` bölüm 11'de tutulur.

## ADR-022 — Hazır uzamsal GNN ağırlıklarını Visium'a uygunluk kanıtı olmadan kullanma

**Tarih:** 2026-11-06
**Bağlam:** Sıfırdan eğitilen Topiome GraphSAGE mevcut küçük Wu 2021 setinde ARI 0.260 ve Macro-F1 0.446 aldı; ikisi de minimum kapının altında. Kullanıcı hazır GNN seçeneğini sordu. Novae makalesi çok sayıda hücre/doku üzerinde ön eğitimli, ancak resmi spot-resolution kılavuzu "Visium için henüz foundation model yok" diyor ve Visium akışında modelin veri üzerinde eğitilmesini öneriyor.
**Karar:** Novae şu anda hazır ağırlıkla Visium tahmini yapacak drop-in model sayılmayacak. İleride GraphST/STAGATE veya Novae yöntemleri araştırma baseline'ı olarak aynı hasta split'inde karşılaştırılabilir. Herhangi biri yalnızca aynı etiketli görevde grafsız ve mevcut graph baselines'a tekrarlanabilir katkı gösterirse ürüne alınabilir. Sıfır-atış domain çıktısı patoloji sınıfı diye sunulmayacak.
**Sonuç:** Hazır model etiket azlığını veya Visium'a aktarım açığını sihirli biçimde çözmez. Mevcut GNN'nin yerine hiçbir ağırlık konmadı; karar yalnızca adil benchmark sonrasında verilecek.

## ADR-023 — Gen katmanı ve ROI dışa aktarımında veri izi
**Tarih:** 2026-11-06
**Bağlam:** Rakip spatial viewer'larda gen ekspresyonu katmanı ve doku bölgesi (ROI) seçimi temel keşif özellikleri. Topiome sonuçları ise model girdisi olarak seçilmiş genlerle sınırlıdır.
**Karar:** Gen katmanı tüm matrisi kalıcı sonuç JSON'una eklemek yerine istenen tek geni orijinal Visium girdisinden okur; barkodla spotlara eşleyip log1p(CP10K) olarak gösterir. Sentetik örnekte sahte gen değerleri üretilmez. ROI özeti keşif amaçlıdır; patolog anotasyonu/validasyon etiketi değildir. ROI CSV yalnız onaylı rapor sonrasında dışa aktarılır ve audit edilir.
**Sonuç:** Viewer tüm sayım matrisini sonuç payload'ında çoğaltmaz; dışa aktarımlar kullanıcı ve run kimliğiyle izlenir. İlk sürüm yalnız Visium tek-gen görünümünü destekler; çok-gen karşılaştırması ve yeni platformlar ayrı doğrulama dilimleridir.

## ADR-024 — Run kıyaslamasında assay bağlamı ve uzamsal görseller
**Tarih:** 2026-11-06
**Bağlam:** Benzer metrikler, farklı platform/tür/koşullarda doğrudan kıyaslanabilir görünerek yanlış bilimsel çıkarıma yol açabilir. Mevcut kıyas ekranı kompozisyon ve domain özetlerini gösteriyor, doku görsellerini göstermiyordu.
**Karar:** Run karşılaştırmasına her tarafın platform, tür ve kaydedilmiş koşul bilgisi eklenir; farklar açık uyarı olarak gösterilir. İki sample'ın uzamsal haritaları aynı viewer kontrolleriyle yan yana açılır. PNG ve ROI export yalnız onaylı rapor sonrasında yapılır ve audit edilir. Karşılaştırma tek başına iki örnekten istatistiksel anlamlılık veya biyolojik etki iddia etmez.
**Sonuç:** Kullanıcı hem doku bağlamını hem assay uyumunu görür. Çoklu-kesit cohort istatistiği, aynı-gen spatial fark testi ya da cross-platform normalizasyon bu ADR kapsamı dışındadır; bunlar ayrıca metodoloji ve benchmark gerektirir.

## ADR-025 — ROI gen farklarını spot düzeyinde betimleyici tut
**Tarih:** 2026-11-06
**Bağlam:** ROI içi/dışı gen karşılaştırması araştırmacı akışını tamamlar; ancak komşu spotlar bağımsız biyolojik tekrar değildir ve spot düzeyi p-değeri sahte kesinlik yaratabilir.
**Karar:** ROI aracı QC-pass spotlarda log1p(CP10K) ortalama farkı ve algılanma oranı farkını hesaplar; p-değeri, FDR veya anlamlılık etiketi üretmez. En az 10 QC-pass spot ROI içinde ve dışında gereklidir; dış kohort istatistiksel çıkarımına dönüştürülmez.
**Sonuç:** Keşif ve hipotez üretimi yapılabilir; doğrulayıcı DGE iddiası için hasta/örnek düzeyinde tasarım, covariate kontrolü ve uygun pseudobulk/karma model analizi gerekir.

## ADR-026 — Visium HD için önce yalnız 16 µm bin ve sınırlı in-memory analiz
**Tarih:** 2026-11-06
**Bağlam:** Space Ranger HD çıktısı 2/8/16 µm binned matrisler, Parquet koordinatlar ve milyonlarca düşük çözünürlüklü bin içerebilir. Topiome'un aşağı akış hattı şu an yoğun spots × genes tablolarını kullanıyor; ince binleri doğrudan seçmek bellek taşmasına ve API/worker çökmesine yol açabilir.
**Karar:** İlk HD okuyucusu yalnız `binned_outputs/square_016um` H5 matrisiyle aynı bin klasöründeki Parquet tissue positions dosyasını eşler. 2/8 µm çıktıları açık hata ile reddedilir. In-tissue spot sayısı varsayılan 12.000 sınırını aşarsa analiz başlamadan reddedilir; kullanıcıya crop kullanımı söylenir. HD sonucu `platform=visium_hd`, `bin_size_um=16` olarak provenance/metadata'ya yazılır.
**Sonuç:** Bu, sınırlı ilk okuyucu uyumluluğudur; assay doğrulaması veya tam HD desteği iddiası değildir. Tiled/sparse pipeline ve temsilî gerçek HD benchmark'ı olmadan spot sınırı yükseltilmez.

## ADR-027 — İki örnekli aynı-gen görselinde ortak renk ölçeği kullan
**Tarih:** 2026-11-06
**Bağlam:** Ayrı ayrı otomatik ölçeklenen iki gen haritası, aynı renk farklı normalize ekspresyon değerlerini temsil ederken görsel farkı abartabilir veya gizleyebilir.
**Karar:** İki run karşılaştırma ekranında bir örnekte yüklenen gen diğer haritaya da yüklenir. Her iki log1p(CP10K) katmanı bu iki örnek arasındaki ortak maksimuma göre aynı renk ölçeğini kullanır. Başlık, bunun betimleyici görsel kıyas olduğunu ve test/istatistiksel anlamlılık üretmediğini belirtir.
**Sonuç:** Görsel renkler karşılaştırılabilir ölçeğe bağlanır; biyolojik çıkarım için bağımsız örnekler, uygun normalizasyon ve örnek düzeyi istatistik ayrıca gerekir. Bir örnekte gen yoksa o haritadaki API uyarısı görünür kalır.

## ADR-028 — GEO/ArrayExpress envanterinde tekil ortak sidecar ve kesit sayımı
**Tarih:** 2026-11-06
**Bağlam:** Bazı public Visium kohortlarında MTX barcode/feature tabloları seri düzeyinde paylaşılır, doku pozisyonları başka alt klasörde durur ya da her H5'e ayrı `spatial.tar` eşlik eder. exFAT ayrıca geçersiz `._*` AppleDouble kopyaları üretir. Basit klasör/dosya sayımı örnekleri kaçırabilir veya yanlış dosyayı sessizce okuyabilir.
**Karar:** Reader yerel MTX sidecar'larını önce seçer; yerelde yoksa yalnız tekil olan seri düzeyi barcode/feature dosyasını kabul eder, AppleDouble dosyalarını atlar ve belirsiz eşleşmede fail-closed kalır. Envanter H5+spatial arşiv çiftlerini geçici/güvenli klasörde açar, matrix/position/sidecar SHA-256'larını kaydeder ve kesit/spot sayılarını bağımsız kişi sayısından ayrı raporlar. Expression örneği ve spot sayısı tek başına denetimli GNN ground truth'u sayılmaz.
**Sonuç:** GEO public cohortları okuyucuda yeniden üretilebilir biçimde sayılabilir; çoklu kesitler bağımsız hasta gibi yorumlanmaz, eksik/bozuk eşleşmeler yayına hazır sayılmaz.

## ADR-029 — Topiome'u perturbasyon yanıtı araştırmasına çevir
**Tarih:** 2026-11-07
**Bağlam:** Spatial transcriptomics alanı kalabalık; mevcut spatial uygulamanın hücre tipi çözünürlüğü ve held-out doğrulama kanıtı ticari pilot için yetersiz. Kullanıcı, bilimsel etkisi daha yüksek olabilecek yeni bir yönü hesaplamalı olarak denemeyi; deney güveninin ortaklık gerektirdiğini ve bunun RUO araştırması olarak açıkça belirtilmesini onayladı.
**Karar:** Topiome adı şimdilik korunur. Yeni araştırma yönü, tanımlı genetik perturbasyonlara tek hücre yanıtını görülmemiş perturbasyon ve biyolojik bağlamlarda tahmin etmenin hesaplamalı fizibilitesidir. Site araştırma önizlemesine dönüşür; kayıt ve fiyat/ürün iddiaları kapalı kalır. Eski spatial app ve kodu silinmeden legacy tutulur; indirilen yaklaşık 9.2 GB public/processed spatial veri yerelden temizlenir, küçük tarihsel raporlar arşivlenir. İlk benchmark verisi bileşen/lisans/metadata bazında incelenip seçilir. Model/benchmark/deney kanıtı oluşmadan doğruluk veya öngörü başarısı iddiası yapılmaz.
**Sonuç:** Yeni yönün ilk teslimatı veri envanteri, adil held-out benchmark ve basit baseline'lardır; bağımsız deney ortağı prospektif iddia için sonraki aşamada gerekir. Ücretlendirme/alıcı kararı bilimsel sinyal görülene kadar açık bırakılır.

## ADR-030 — Sıfır atış yerine pilotla kalibre edilmiş bağlam transferi
**Tarih:** 2026-11-08
**Bağlam:** Sıfır atış görülmemiş-bağlam transferi Replogle içinde geçti, bağımsız Orion tekrarında başarısız oldu. Tanı: kaynak bağlamın ortalama profili hedefe taşınmıyor ve uygun ölçek bağlama göre çok değişiyor (oracle β 0,05–0,30). Aynı test setinde β değiştirmek test setine göre ayar olurdu.
**Karar:** Görev, gerçekçi bir laboratuvar akışına çevrildi: yeni hücre hattında küçük bir pilot (k=100) ölçülür; hedef ortalaması ve β yalnız pilottan öğrenilir; adil karşılaştırma "yalnız pilot ortalaması"dır. Yöntem açılmış verilerde (Replogle, Orion) geliştirildi, hiç açılmamış Tahoe-100M'de ön kayıtla bir kez sınandı ve 5/5 kuralı geçti (VALIDATION §14).
**Sonuç:** İlk bağımsız, ön kayıtlı pozitif sonuç; etki mütevazı (~%2 RMSE). Sıfır atış iddiası kurulmaz. Sonraki adımlar: zarar gören çiftler için sağlam tahmin (yeni geliştirme + yeni doğrulayıcı veri), genetik perturbasyon verisinde tekrar, laboratuvar ortağıyla prospektif pilot→tahmin testi.
