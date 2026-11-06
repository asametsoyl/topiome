# Dağıtım — Topiome

> Tek sunucuda Docker Compose ile üretim kurulumu. Bulut sağlayıcı kararı (STATUS D4) bekliyor; bu kurulum Hetzner / AWS EC2 / herhangi bir Linux VM'de aynıdır.

## Bileşenler

| Servis | İmaj | Görev |
|---|---|---|
| `db` | `postgres:16-alpine` | Metadata, audit log, sonuç payload'ları |
| `api` | `infra/docker/api.Dockerfile` | FastAPI (2 uvicorn worker); açılışta Alembic migration (Postgres advisory lock ile) |
| `worker` | aynı imaj, `python -m app.worker` | Kuyruktaki run'ları çalıştırır (`QUEUE_MODE=worker`); birden fazla worker güvenle çalışır |
| `web` | `infra/docker/web.Dockerfile` | Next.js standalone sunucu; `/api/*` isteklerini iç ağdaki `api`'ye yönlendirir |

Yalnızca `web` dışarı açılır. `api` iç ağdadır; bu yüzden Next.js'in ilettiği `X-Forwarded-For` başlığına güvenilir (audit log IP'leri ve giriş sınırlaması için). API'yi doğrudan internete açmayın.

Kuyruk Postgres tabanlıdır; **Redis/RQ servisi gerekmez**. API `queued` run kaydı açar, worker atomik olarak sahiplenir.

## Kurulum

```bash
cp infra/.env.production.example infra/.env.production   # SECRET_KEY, POSTGRES_PASSWORD, APP_URL doldur
export TOPIOME_GIT_COMMIT=$(git rev-parse HEAD)
docker compose -f infra/docker-compose.yml --env-file infra/.env.production up -d --build
```

TLS için önüne Caddy / Traefik / bulut yük dengeleyici koyun (`web:3000`'e yönlendirin). `APP_URL` HTTPS adresi olmalı; çerezler üretimde `Secure` işaretlidir.

### exFAT geliştirme diskinden build

Bu repo macOS'ta exFAT diskte tutuluyorsa iki sorun çıkar:

1. macOS her dosyanın yanına `._*` AppleDouble dosyası yazar; Docker BuildKit bunların xattr'ını okuyamaz (`operation not permitted`).
2. Kaynak dosyalar 0700 izinli olabilir. Dockerfile'lar `COPY --chown=topiome:topiome` kullanır; bu düzeltilmiştir.

Çözüm: build'i temiz bir kopyadan yapın (veya `.dockerignore`'a rağmen kalan `._*` dosyalarını silin):

```bash
rsync -a --exclude node_modules --exclude .venv --exclude .next --exclude .git \
  --exclude '._*' --exclude '__pycache__' --exclude '*.db*' \
  ./ /tmp/topiome-build/
cd /tmp/topiome-build
docker compose -f infra/docker-compose.yml --env-file infra/.env.production up -d --build
```

CI/Linux sunucuda normal checkout ile doğrudan build edilir.

## Doğrulama

```bash
docker compose -f infra/docker-compose.yml --env-file infra/.env.production ps
curl -fsS http://localhost:3000/api/v1/health   # WEB_PORT farklıysa ona göre
```

Beklenen: `db`, `api`, `web` healthy; `worker` up (healthcheck kapalı). `/api/v1/health` `{"status":"ok","db":true,"storage":true,...}` döner.

Üretim stack'i 2026-11-06'da gerçekten build edilip çalıştırıldı: dört konteyner healthy, web proxy üzerinden kayıt → proje → sentetik örnek → queued run → worker → succeeded → sonuç → HTML rapor akışı geçti. Üretimde demo login 404 döner.

## Güvenlik kapıları

API, `APP_ENV=production` iken şu durumlarda **açılmayı reddeder** (`Settings.production_problems`):

- `SECRET_KEY` varsayılan ya da 32 karakterden kısa,
- `DATABASE_URL` SQLite,
- `ALLOW_DEMO_LOGIN=true`,
- `QUEUE_MODE` geçersiz.

Giriş denemeleri sınırlıdır: aynı IP + e-posta için 15 dakikada 10, IP başına 50 başarısız deneme (`429` + `Retry-After`). Sınır süreç başınadır; ters proxy'de de oran sınırı önerilir.

## Run kuyruğu

- `QUEUE_MODE=inline` (geliştirme): run, isteği yanıtlayan API sürecinde çalışır. API yeniden başlarsa yarım kalan run'lar açılışta `interrupted` olarak kapatılır.
- `QUEUE_MODE=worker` (üretim): API yalnızca `queued` kaydı açar; worker atomik `queued → running` geçişiyle sahiplenir. `RUN_TIMEOUT_HOURS` (varsayılan 6) aşılan `running` run'lar worker açılışında `interrupted` olur.

## Yedekleme

- Postgres: `docker compose exec db pg_dump -U topiome topiome | gzip > backup-$(date +%F).sql.gz` (günlük, 30 gün sakla).
- Depolama (`storage` volume): yüklenen ham dosyalar + `results.json` / `report.html`. Volume'u günlük anlık görüntüyle yedekleyin.

## Güncelleme

```bash
git pull && export TOPIOME_GIT_COMMIT=$(git rev-parse HEAD)
docker compose -f infra/docker-compose.yml --env-file infra/.env.production up -d --build
```

Migration'lar API açılışında otomatik çalışır. Geri dönüş: önceki imaj etiketine dönün; veri şeması geri alınacaksa `docker compose exec api python -m app.migrate downgrade <rev>`.

## Referans verisi ve modeller

Paketlerle gelen referans imzaları (`packages/disease-packs/references/`) ve eğitilmiş modeller (`packages/disease-packs/models/`) imaja kopyalanır; her run bunların SHA-256'sını provenance'a yazar. Model eğitimi PyTorch gerektirir ama üretim imajı gerektirmez (çıkarım NumPy).
