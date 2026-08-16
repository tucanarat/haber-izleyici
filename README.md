# 📰 Haber İzleyici

RSS kaynaklarını otomatik tarayan, anahtar kelimelere göre işaretleyen ve
GitHub Pages üzerinde canlı bir panelde gösteren basit bir araç.

## Nasıl çalışıyor?

1. `config.yaml` içindeki RSS kaynakları periyodik olarak taranır (varsayılan: her 10 dakikada bir).
2. Her haberin başlığı/özeti, `config.yaml` içindeki anahtar kelimelerle karşılaştırılır.
3. Sonuçlar `data/news.json` dosyasına yazılır ve GitHub'a otomatik commit'lenir.
4. `index.html`, bu JSON dosyasını okuyup tarayıcıda canlı bir panel olarak gösterir.

Bilgisayarının açık olmasına gerek yok — her şey GitHub'ın sunucularında (GitHub Actions) çalışır.

## Kurulum (ilk seferde)

### 1. Repoyu GitHub'a yükle
Bu klasördeki dosyaları kendi GitHub reponda (örn. `haber-izleyici`) yayınla:

```bash
cd haber-izleyici
git init
git add .
git commit -m "İlk kurulum"
git branch -M main
git remote add origin https://github.com/KULLANICI_ADIN/haber-izleyici.git
git push -u origin main
```

### 2. GitHub Actions için yazma izni ver
- Repo sayfasında **Settings → Actions → General** yoluna git.
- "Workflow permissions" bölümünden **"Read and write permissions"** seçeneğini işaretle ve kaydet.
- (Bu izin olmadan bot, güncellenen haberleri repoya commit'leyemez.)

### 3. GitHub Pages'i aç
- **Settings → Pages** yoluna git.
- "Source" olarak **"Deploy from a branch"** seç, branch olarak **main**, klasör olarak **/ (root)** seç, kaydet.
- Birkaç dakika sonra panelin şu adreste yayında olacak:
  `https://KULLANICI_ADIN.github.io/haber-izleyici/`

### 4. İlk taramayı manuel tetikle (opsiyonel, hemen görmek istersen)
- Repo sayfasında **Actions** sekmesine git.
- "Haber Tarama" workflow'unu seç → **"Run workflow"** butonuna bas.
- Birkaç saniye içinde `data/news.json` güncellenecek ve panelde haberler görünecek.

Bundan sonra sistem otomatik olarak 10 dakikada bir kendini güncelleyecek.

## Ayarları değiştirme

`config.yaml` dosyasını düzenle:

```yaml
sources:
  - name: "Kaynak Adı"
    url: "https://ornek.com/rss"

keywords:
  - "takip etmek istediğin kelime"
  - "başka bir kelime"
```

- Yeni bir kaynak eklemek için `sources` listesine RSS linkini ekle.
- `keywords` listesini boş bırakırsan **tüm haberler** gösterilir (filtre uygulanmaz),
  ancak eşleşenler yine de panelde kırmızı çerçeveyle vurgulanmaz.
- Değişiklikleri kaydedip GitHub'a push ettiğinde bir sonraki otomatik taramadan itibaren geçerli olur.

## Tarama sıklığını değiştirme

`.github/workflows/fetch.yml` dosyasındaki şu satırı düzenle:

```yaml
- cron: "*/10 * * * *"   # her 10 dakikada bir
```

Örnekler:
- `*/5 * * * *` → her 5 dakikada bir
- `*/30 * * * *` → her 30 dakikada bir

Not: GitHub Actions'ın ücretsiz planında dakikalık kotan var; çok sık tarama
(örneğin 1 dakikada bir) uzun vadede kotanı hızlı tüketebilir. 5-10 dakika
aralığı günlük haber takibi için yeterlidir.

## DHA (Demirören Haber Ajansı) hakkında not

DHA'nın herkese açık, ücretsiz bir RSS beslemesi yok — abonelik karşılığında
size özel şifreli bir RSS URL'si veriyorlar. Aboneliğiniz varsa, o özel URL'yi
`config.yaml` içindeki `sources` listesine aynı formatta ekleyebilirsiniz.

## Yerel makinede test etme

```bash
pip install -r requirements.txt
python fetch_news.py
```

Bu komut `data/news.json` dosyasını günceller. Ardından `index.html`'i
tarayıcıda açarak (veya basit bir yerel sunucuyla) sonucu görebilirsin:

```bash
python -m http.server 8000
# tarayıcıda: http://localhost:8000
```
