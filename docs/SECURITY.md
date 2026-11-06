# Güvenlik ve Uyum — Topiome

> Bu doküman hukuki tavsiye değildir. Üretim öncesi KVKK/GDPR danışmanı ve siber güvenlik uzmanı ile gözden geçirilmelidir.

## 1. Tehdit modeli (özet)

| Varlık | Tehdit | Kontrol |
|---|---|---|
| Hasta/araştırma verisi | Yetkisiz erişim, sızıntı | org izolasyonu, şifreleme, signed URL, audit |
| Hesap | Credential stuffing, phishing | Argon2id, rate limit, MFA (yakında), oturum süresi |
| API | IDOR, yetki yükseltme | her istekte org/rol kontrolü, testler |
| Dosya yükleme | Zararlı dosya, zip bomb | boyut limiti, MIME, ClamAV, ayrıştırma izolasyonu |
| Pipeline | Kötü niyetli parametre, kaynak tüketimi | whitelist, timeout, memory limit, sandbox worker |
| Rapor | Yanlış iddia, veri sızıntısı | şablon kontrolü, RUO, paylaşım token'ı |
| Tedarik zinciri | Bağımlılık saldırısı | lockfile, Dependabot, imzalı image |

## 2. Kimlik ve erişim

- Şifre: Argon2id, minimum 10 karakter; breached-password kontrolü henüz yok (Faz 2).
- Oturum: httpOnly, Secure, SameSite=Lax; 7 gün; logout'ta iptal.
- Roller: owner, admin, analyst, viewer.
- MFA: Faz 2 (TOTP).
- SSO/SAML: kurumsal plan (Faz 3).
- API anahtarı: `topiome_live_...`, yalnızca bir kez gösterilir, hash saklanır, scope'lu.

## 3. Veri koruma

- Transit: TLS 1.2+; HSTS.
- Rest: disk şifreleme (cloud sağlayıcı) + uygulama seviyesinde hassas alan şifrelemesi (Faz 2).
- Yedek: şifreli, ayrı hesap/bölge, 30 gün.
- Log: PII/PHI maskelenir; dosya içeriği loglanmaz.
- Ortamlar: dev/staging/prod ayrı; prod verisi dev'e kopyalanmaz.

## 4. KVKK / GDPR

- Rol: veri işleyen (processor) / veri sorumlusu (controller) sözleşmeleri.
- Hukuki dayanak: araştırma faaliyeti; kurumun etik kurul onayı kullanıcı sorumluluğunda.
- Veri ikametgahı: AB (Frankfurt) varsayılan; Türkiye için ayrı bölge opsiyonu.
- Alt işleyiciler: AWS/Hetzner, Stripe, e-posta sağlayıcısı; liste yayınlanır.
- Veri sahibi hakları: erişim, düzeltme, silme, taşınabilirlik; 30 gün yanıt.
- DPA (Data Processing Agreement) şablonu: `docs/legal/` (oluşturulacak).
- Kayıt: işleme envanteri (ROPA), veri ihlali müdahale planı.

## 5. Audit log

Kaydedilen olaylar:
- login/logout/failed login
- org/user/role değişikliği
- sample upload/download/delete
- run start/finish/fail
- report generate/download/share
- API key create/revoke
- billing değişikliği

Alanlar: `id, org_id, actor_id, action, resource_type, resource_id, ip, user_agent, metadata, created_at`.
Saklama: 24 ay (kurumsal planla artırılabilir). Değiştirilemez (append-only).

## 6. Uygulama güvenliği

- OWASP ASVS L2 hedefi.
- Girdi doğrulama: Pydantic/Zod; dosya adları sanitize.
- SQL: ORM/parametreli; raw SQL yasak (istisna review).
- XSS: React escape + CSP; `dangerouslySetInnerHTML` yasak.
- CSRF: SameSite + Origin kontrolü.
- SSRF: dış URL getirme yok (Faz 1).
- Rate limit: giriş IP + e-posta başına 15 dk / 10, IP başına 50 başarısız deneme (`429` + `Retry-After`); register/upload için henüz yok. Sayaç süreç içidir; çok worker'da ters proxy/WAF gerekir.
- Hata mesajları: iç detay sızdırmaz; `trace_id` verir.
- Bağımlılık: `npm audit`, `pip-audit`, Dependabot.

## 7. Altyapı

- Docker image: non-root, read-only root fs (mümkünse), minimal base.
- Secret: environment/secret manager; image içine gömülmez.
- Ağ: DB dışarı açık değil; yalnızca internal network. (Kuyruk şu an Postgres tabanlı; Redis yok.)
- Yedek/restore testi: aylık.
- Loglama: JSON, merkezi; 90 gün sıcak, 1 yıl arşiv.
- İzleme: uptime, 5xx, queue depth, disk, yavaş sorgu.

## 8. Olay müdahale

1. Tespit → 2. Sınıflandırma (P1–P4) → 3. Kontainment → 4. Delil koruma → 5. Düzeltme → 6. Bildirim (72 saat GDPR) → 7. Post-mortem.

İletişim: güvenlik@topiome.com (kurulacak). P1 için 24 saat içinde ilk bildirim.

## 9. RUO ve klinik sınır

- Ürün klinik karar desteği değildir; böyle pazarlanamaz.
- Kullanıcı sözleşmesinde açık RUO maddesi.
- Klinik kullanım ancak ayrı ürün, ayrı validasyon, ISO 13485/IVDR süreci ile.
- Rapor ve UI'da kalıcı uyarı; kaldırılamaz.

## 10. Yayın öncesi güvenlik kontrolü

- [ ] Secret taraması (gitleaks)
- [ ] Bağımlılık zafiyet taraması
- [x] Auth/IDOR testleri (org izolasyonu, rol kontrolü, rate limit, üretim ayar kapıları)
- [x] Yükleme limitleri, arşiv path traversal ve format testleri
- [x] Güvenli cookie + HSTS + `nosniff` + frame/referrer/permissions başlıkları; [ ] CSP
- [ ] Audit log kapsamı (altyapı var, kapsam genişletilecek)
- [ ] Yedek restore testi
- [ ] DPA/KVKK metinleri
- [ ] Penetrasyon testi (Faz 2)
