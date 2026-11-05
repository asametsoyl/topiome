# Topiome

**Spatial disease atlas platform — Research Use Only.**

Topiome, spatial transcriptomics verisini hücre kompozisyonu, mekânsal bölgeler ve ilaç hedefi kanıtlarıyla birlikte paylaşılabilir bir doku atlasına dönüştürür.

> Eski ad: Glio-Cartography (GBM odaklı, Teknofest). Yeni ürün: hastalıktan bağımsız çekirdek + doğrulanmış hastalık paketleri.

## Neden

- Tekrarlanabilir dekonvolüsyon ve spatial domain analizi
- Hastalığa özgü marker, bölge ve hedef tanımları
- Spot bazında belirsizlik ve kalibrasyon
- Yayına hazır, sınırlamaları açık rapor

## İlk hastalık paketleri

Meme · Kolorektal · Akciğer · Melanom · Prostat · Glioblastoma

## Teknoloji

Next.js 16 · React 19 · TypeScript · Tailwind 4 · FastAPI · SQLAlchemy 2 · Python 3.12 · PostgreSQL · Redis/RQ (prod) · S3

## Kurulum

```bash
# Gereksinimler: Node >= 22, uv, Docker (opsiyonel)
bash scripts/setup.sh
npm run dev
```

- Web: http://localhost:3000
- API: http://localhost:8000/docs
- Demo: `demo@topiome.com` / `demo1234`

## Dokümantasyon

| Dosya | İçerik |
|---|---|
| [`AGENTS.md`](AGENTS.md) | AI ajanları ve geliştiriciler için giriş noktası |
| [`docs/STATUS.md`](docs/STATUS.md) | Yapılanlar, sıradakiler, oturum kaydı |
| [`docs/PRODUCT.md`](docs/PRODUCT.md) | Vizyon, kullanıcı, fiyatlandırma |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Mimari ve veri akışı |
| [`docs/VALIDATION.md`](docs/VALIDATION.md) | Doğruluk stratejisi ve benchmark eşikleri |
| [`docs/DISEASE_PACKS.md`](docs/DISEASE_PACKS.md) | Hastalık paketi şeması |
| [`docs/DATA.md`](docs/DATA.md) | Veri formatları ve gizlilik |
| [`docs/SECURITY.md`](docs/SECURITY.md) | KVKK/GDPR ve güvenlik |
| [`docs/BUSINESS.md`](docs/BUSINESS.md) | Şirketleşme ve iş modeli |
| [`docs/BRAND.md`](docs/BRAND.md) | Marka ve görsel kimlik |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Fazlar |
| [`docs/DECISIONS.md`](docs/DECISIONS.md) | ADR'ler |
| [`docs/API.md`](docs/API.md) | REST API |

## RUO uyarısı

> **For Research Use Only.** Topiome is not intended for diagnosis, prognosis, treatment selection, or clinical decision-making. Results are computational inferences from research data and must be independently validated.

## Lisans

Proprietary. Tüm hakları saklıdır. Marka ve kod, şirket kuruluşu tamamlanana kadar kuruculara aittir.
