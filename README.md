# Balkan Baazar — hibrit Balkan pazaryeri (Django)

Üsküp (Skopje) merkezli, sekiz Balkan ülkesine hizmet eden iki yapılı pazaryeri:

1. **İkinci El** — sahibinden.com mantığında bireysel ilanlar (kategori → alt kategori,
   durum, elden teslim/kargo, şehir, fiyat filtreleri).
2. **Mağazalar** — trendyol mantığında kurumsal satış (mağaza sayfaları, ürünler,
   puan, ücretsiz kargo, doğrulanmış mağaza rozeti).

Ülkeler: 🇲🇰 Kuzey Makedonya · 🇦🇱 Arnavutluk · 🇽🇰 Kosova · 🇷🇸 Sırbistan ·
🇲🇪 Karadağ · 🇧🇦 Bosna-Hersek · 🇧🇬 Bulgaristan · 🇬🇷 Yunanistan

Diller (10): Makedonca, Arnavutça, Sırpça, Boşnakça, Hırvatça, Karadağca, Bulgarca,
Yunanca + Türkçe + İngilizce.

Para birimleri: MKD, ALL, RSD, BAM ve EUR (Kosova, Karadağ, Bulgaristan, Yunanistan).
Fiyatlar veritabanında EUR tutulur, seçili ülkenin kuruyla gösterilir.

---

## Kurulum

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py makemigrations market
python manage.py migrate
python manage.py seed --reset   # 8 ülke, kategoriler, mağazalar, ~5.000 ilan
python manage.py createsuperuser
python manage.py runserver
```

Açılış: http://127.0.0.1:8000/ — yönetim: http://127.0.0.1:8000/admin/

Tek satırda kurulum için: `bash setup.sh`

## Sayfalar

| Yol | İçerik |
|---|---|
| `/` | Ana sayfa, 8 ülkeli banner, kategoriler, öne çıkan mağazalar |
| `/ilanlar/?mode=used` | İkinci el listeleme + filtreler |
| `/ilanlar/?mode=shop` | Mağaza ürünleri listeleme |
| `/ilan/<id>/<slug>/` | İlan / ürün detayı |
| `/magazalar/` | Mağaza dizini |
| `/magaza/<slug>/` | Mağaza vitrini |
| `/paketler/` | Mağaza paketleri |
| `/ayar/ulke/<KOD>/`, `/ayar/dil/<kod>/` | Ülke / dil değiştirme (session) |
| `/uyelik/kayit/` · `/uyelik/giris/` · `/uyelik/cikis/` | Üyelik |
| `/magaza-basvuru/` | Mağaza başvuru formu |
| `/panel/` | Satıcı paneli — özet |
| `/panel/urunler/` · `/panel/urun/yeni/` · `/panel/urun/<id>/` | Ürün yönetimi (kapak + galeri görseli) |
| `/panel/magaza/` · `/panel/odeme/` | Mağaza ayarları (logo dahil), paket ve ödeme |
| `/yonetim/` | **Site sahibi yönetim paneli** (sadece `is_staff`) |
| `/ilanlarim/` · `/ilanlarim/yeni/` | Bireysel (ikinci el) ilan verme |
| `/sepet/` · `/odeme/` · `/siparislerim/` | Sepet ve ödeme (mağaza ürünleri) |
| `/mesajlar/` · `/mesaj/<id>/` | Mesajlaşma |

## Ürün görselleri

Satıcı panelinde ürün formunda artık:
- **Kapak görseli** — `Listing.image`, formun üstünde önizlemeyle.
- **Galeri** — `ListingImage` modeli, ürün başına sınırsız ek fotoğraf; panelde 3 boş
  yuvayla açılır, doldukça `formset` otomatik büyür, mevcut görseller silinebilir.
- Mağaza ayarlarında **logo** (`Shop.logo`) — mağaza kartlarında ve panelde ilk harf
  yerine logo gösterilir.

Görseller `MEDIA_ROOT` altında saklanır; `DEBUG=1` iken Django kendisi sunar,
üretimde nginx/S3 gibi bir depoya yönlendirilmeli.

## İlan öne çıkarma (ücretli vitrin)

Sahibinden'in asıl gelir modeli olan "vitrin" özelliği: ilan/ürün sahibi kendi
ilanını `/vitrin/<id>/` üzerinden 3/7/30 günlüğüne öne çıkarabilir (fiyatlar
`config/settings.py` içinde `BOOST_PACKAGES`'ta tanımlı, kolayca değiştirilir).

- Ödeme, sepet-ödemede kurulan aynı Stripe Checkout akışını kullanır — anahtar
  tanımlıysa gerçek ödeme sayfasına gider, tanımlı değilse demo akışla anında uygulanır.
- Satın alma onaylanınca `Listing.featured_until` uzatılır (üst üste satın alma
  süreleri toplanır, mevcut vitrin süresi bitmeden yeni paket alınırsa üstüne eklenir).
- Öne çıkan ilanlar hem ana sayfada hem `/ilanlar/` ve `/magazalar/` filtrelenmiş
  listelerinde **otomatik olarak en üstte** çıkar (veritabanı seviyesinde sıralama,
  ayrı bir arka plan görevi gerekmez — süre dolunca kendiliğinden sıradan listeye döner).
  Kartlarda ve ilan detayında sarı "★ Öne Çıkan" rozetiyle işaretlenir.
- İlan sahibi butonu: `/ilanlarim/` (bireysel ilan) ve satıcı panelindeki
  `/panel/urunler/` (mağaza ürünü) listelerinde her satırda "★ Öne çıkar" bağlantısı var.

Django admin → **Boosts**'ta tüm satın alımları (durum, tutar, ödeme zamanı) görebilirsin.

## Varyant + stok sistemi

Mağaza ürünlerinde artık gerçek stok takibi var:

- Ürün formunda **"Stoğu takip et"** açılırsa `stock` adedi tükeninceye kadar satışa
  açık kalır; kapalıysa (varsayılan) sınırsız kabul edilir — mevcut demo veriler bozulmaz.
- **Seçenekler (beden/renk)** — aynı formda, ürün başına birden fazla varyant
  eklenebilir (`ListingVariant`: ad, fiyat farkı, kendi stoğu). Varyantı olan bir
  üründe "Sepete ekle" önce seçenek seçmeyi zorunlu kılar.
- Sepete eklerken ve ödeme onaylanırken stok **iki kez** doğrulanır (ekleme anında
  ve ödeme anında) — yarış durumunda stok tükenmişse kullanıcı uyarılır.
- Ödeme onaylanınca stok gerçekten düşer; sipariş iptal edilirse stok geri eklenir.

## Favoriler

`/favorilerim/` — hem ilan/ürün hem mağaza favorilere eklenebilir. İlan/ürün
kartlarında ve detay sayfasında kalp simgesiyle işaretlenir. Üst bardaki ♡ simgesi
favoriler sayfasına götürür.

## Değerlendirme ve yorum

Sadece **gerçekten satın alınmış** ürünler için yorum yapılabilir — `Review`,
`OrderItem`'a bire bir bağlı, sahte yorum yazılamaz. Alıcı `/siparislerim/`'de
ödenmiş bir sipariş kalemi için "Değerlendir" bağlantısını görür, 1–5 yıldız ve
yorum bırakır. Ürün detayında gerçek yorum varsa ortalama puan ve yorum sayısı
gösterilir (yoksa demo veriden gelen puan görünmeye devam eder).

## Kupon kodu

Ödeme sayfasında kupon kodu alanı var. `Coupon` modeli admin'den yönetilir:
yüzde ya da sabit tutar indirimi, tek mağazaya veya tüm platforma geçerli,
son kullanma tarihi, azami kullanım sayısı. Stripe ile ödemede indirim tek
kalem olarak ("Sepet — kupon uygulandı") gönderilir.

## Kargo takibi ve iptal

Çoklu satıcılı sepetlerde her sipariş kalemi **kendi kargosuyla** ilerler
(bir siparişte iki farklı mağazadan ürün olabilir, her biri ayrı kargolanır):

- Satıcı panelinde yeni **"Gelen siparişler"** sayfası (`/panel/siparisler/`) —
  her kalem için kargo firması + takip numarası girip "Kargoya ver" diyebiliyor.
  Bu işlem alıcıya e-posta gönderir.
- Alıcı `/siparislerim/`'de her kalemin durumunu (hazırlanıyor / kargoya verildi
  + takip no) görür.
- Sipariş henüz kargoya verilmediyse alıcı **iptal edebilir** — stok otomatik
  geri eklenir, her iki tarafa da e-posta gider.

## E-posta bildirimleri

`market/emails.py` merkezi bir bildirim modülü — her olayda ilgili kişiye kısa,
iki dilli (TR + EN) bir e-posta gider:

| Olay | Kime |
|---|---|
| Mağaza başvurusu gönderildi | Başvuran + (tanımlıysa) `STAFF_NOTIFY_EMAILS` |
| Başvuru onaylandı / reddedildi | Başvuran |
| Yeni mesaj | Sohbetteki diğer kişi |
| Sipariş ödendi | Alıcı + siparişteki her mağazanın sahibi |
| Sipariş kalemi kargoya verildi | Alıcı |
| Sipariş iptal edildi | Alıcı + ilgili mağaza sahipleri |

**Varsayılan olarak** `EMAIL_BACKEND` konsol backend'idir — e-postalar gerçekten
gönderilmez, çalıştırdığın terminale yazılır. Bu sayede proje SMTP kurmadan da
sorunsuz çalışır ve bildirimleri terminalde görebilirsin.

**Gerçek gönderim için** (örnek: Gmail SMTP veya herhangi bir sağlayıcı):
```bash
export EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
export EMAIL_HOST=smtp.example.com
export EMAIL_PORT=587
export EMAIL_HOST_USER=posta@ornekdomain.com
export EMAIL_HOST_PASSWORD=xxxx
export DEFAULT_FROM_EMAIL="Balkan Baazar <no-reply@ornekdomain.com>"
export STAFF_NOTIFY_EMAILS=sen@ornekdomain.com,ekip@ornekdomain.com
```
Bir gönderim başarısız olursa (örneğin SMTP çöktüyse) hata sadece loglanır,
kullanıcının işlemi (mesaj gönderme, sipariş verme vb.) engellenmez.

## Bireysel ilan verme

`/ilanlarim/` — giriş yapan herkes kendi ikinci el ilanını verebilir: sahibinden.com
mantığında kategori/alt kategori, fiyat, şehir, durum (sıfır/ikinci el), teslimat,
telefon, açıklama, kapak görseli ve galeri. İlan otomatik olarak kullanıcının o an
seçili ülkesine ve `owner` alanına bağlanır; `/ilanlarim/` sayfasında düzenlenip silinebilir.

## Sepet ve ödeme (Stripe)

Yalnızca **mağaza ürünleri** (`mode=shop`) sepete eklenebilir — ikinci el ilanlar
telefon/mesajla iletişime dayanıyor. Sepet oturuma (session) kaydedilir; ürün
kartlarındaki 🛒 simgesiyle veya ürün detayındaki "Sepete ekle" ile eklenir.

`/odeme/` teslimat bilgisini alır ve **Stripe Checkout**'a yönlendirir — kart
bilgisi hiçbir zaman bu sunucuya dokunmaz, Stripe'ın kendi güvenli (PCI uyumlu)
sayfasında toplanır. Ödeme tamamlanınca Stripe hem başarı sayfasına yönlendirir
hem de (tanımlıysa) bir webhook gönderir; ikisi de siparişi `paid` yapar, bu yüzden
kullanıcı sekmeyi kapatsa bile webhook siparişi işaretler.

**Test için** (ücretsiz Stripe test hesabı):
1. https://dashboard.stripe.com adresinde ücretsiz hesap aç, **Test mode**'a geç.
2. Developers → API keys'ten `pk_test_...` ve `sk_test_...` anahtarlarını al.
3. Ortam değişkeni olarak tanımla:
   ```bash
   export STRIPE_PUBLIC_KEY=pk_test_xxx
   export STRIPE_SECRET_KEY=sk_test_xxx
   export SITE_URL=http://127.0.0.1:8000
   ```
4. Ödeme sayfasında test kartı kullan: **4242 4242 4242 4242**, herhangi bir
   gelecek tarih, herhangi bir CVC.
5. (Opsiyonel, webhook için) `stripe listen --forward-to 127.0.0.1:8000/odeme/webhook/`
   çalıştır, verdiği `whsec_...` değerini `STRIPE_WEBHOOK_SECRET` olarak tanımla.

**Anahtar tanımlanmazsa** site otomatik olarak demo akışa düşer: ödeme sayfasında
kart formu yerine bir uyarı gösterilir, "Ödemeyi tamamla" butonuna basınca sipariş
Stripe'a hiç gitmeden doğrudan `paid` işaretlenir — yani proje anahtarsız da
sorunsuz çalışmaya devam eder, sadece gerçek tahsilat yapmaz.

Alıcı `/siparislerim/`'de, sen `/yonetim/` panelinde ve Django admin → Orders'ta
tüm siparişleri (Stripe oturum kimliği ve ödeme zamanı dahil) görürsün.

## Mesajlaşma

Bir ilanın/ürünün altındaki "Mesaj gönder" butonu, alıcı ile satıcı (mağaza sahibi
ya da bireysel ilan sahibi) arasında bir `Conversation` açar ya da var olanı bulur.
`/mesajlar/` gelen kutusu son mesaj önizlemesi ve okunmamış sayısıyla listeler;
`/mesaj/<id>/` sohbet balonlarıyla mesajlaşma ekranıdır. Üst menüdeki ✉ simgesi
okunmamış mesaj sayısını rozet olarak gösterir.

## Üyelik ve mağaza akışı

1. Ziyaretçi `/uyelik/kayit/` üzerinden hesap açar (giriş otomatik yapılır).
2. `/magaza-basvuru/` formunu doldurur: mağaza adı, ülke, şehir, kategori, yetkili,
   telefon, vergi numarası, web sitesi, açıklama. Başvuru `ShopApplication` olarak kaydedilir.
3. Yönetici, admin'de başvuruyu seçip **"Secili basvurulari onayla ve magazayi ac"**
   işlemini çalıştırır. Bu, `Shop` kaydını oluşturur, sahibini başvuru sahibi yapar
   ve saati başlatır (ilk 3 ay ücretsiz).
4. Onaydan sonra kullanıcı `/panel/` adresinde kendi panelini görür: özet istatistikler,
   ürün listesi, ürün ekleme/düzenleme/silme, mağaza ayarları, paket durumu.

Panel yalnızca `Shop.owner == request.user` olan mağazanın ürünlerini gösterir ve
düzenletir; başkasının ürününe erişim 404 döner.

## Mağaza fiyatlandırması

`Shop.monthly_fee_eur` açılış tarihine göre otomatik hesaplar:

- 0–3. ay → **ücretsiz**
- 4–9. ay → **9 € / ay**
- 10. aydan sonra → **29 € / ay**

Değerler `config/settings.py` içindeki `SHOP_PLAN_*` ayarlarından değiştirilir.

## Site sahibi yönetim paneli (/yonetim/)

Django'nun teknik admin ekranı yerine, markaya uygun **ayrı, sade bir panel**:

- **Genel bakış** — bekleyen başvuru, toplam mağaza/ilan/kullanıcı sayısı, son başvurular
  ve son açılan mağazalar; tek tıkla onay.
- **Mağaza başvuruları** — beklemede / onaylandı / reddedildi sekmeleri, arama.
  Onayla butonu `ShopApplication.approve()` metodunu çağırır (mağazayı açar, ücretsiz
  3 ayı başlatır). Reddet, açılır bir kutuda dahili not alır.
- **Mağazalar** — ülkeye göre filtre, arama, tek tıkla doğrulama rozeti aç/kapat,
  paketi elle değiştirme (ücretsiz / 9 € / 29 €).
- **İlan & ürünler** — moda/ülkeye göre filtre, yayından kaldır/yayına al, sil.
- **Ülkeler & kurlar** — sekiz ülkenin kurunu (1 € = X) tek formdan güncelle.

Erişim `is_staff=True` kullanıcılarla sınırlı: `createsuperuser` ile açılan hesap
otomatik `is_staff`'tır. Üst menüdeki hesap açılır listesinde **Yönetim** bağlantısı
sadece staff kullanıcıya görünür ve bekleyen başvuru sayısını rozet olarak gösterir.
Teknik/nadir işler için (kategori düzenleme, kullanıcı silme vb.) `/admin/` hâlâ
duruyor ve panelin menüsünden "Gelişmiş / Django admin" ile erişilebiliyor.

## Ana sayfa banner'ı (v2)

Ana sayfa artık paylaştığın referans tasarıma yakın bir görünümde:

- **Logo lockup**: alışveriş çantası + "B" rozeti, lacivert/turkuaz iki tonlu
  "BalkanBaazar" yazısı, altında gri alt başlık.
- **Başlık + açıklama**: gradyan renkli iki satırlık başlık, açıklama metni —
  tamamı `market/i18n.py` sözlüğünden geldiği için on dilin hepsinde çalışır.
- **İki CTA butonu**: dolgulu lacivert "Alışverişe başla" ve turuncu çerçeveli
  "Mağazanı aç".
- **Harita + bayrak pin'leri**: gerçek coğrafi sınırlar yerine, sitenin geri
  kalanıyla tutarlı soyut bir "blob" şekil üzerine 8 ülkenin SVG bayrağı konum
  iğnesi (pin) olarak yerleştirildi; üstüne gelince ülke adı balonu çıkar,
  tıklayınca o ülkeye geçer.
- **İmza yazısı**: sağ altta el yazısı fontuyla (Google Fonts "Caveat") kısa bir slogan.
- **Kategori şeridi**: banner'ın altına taşan, yuvarlak köşeli beyaz bir kart
  içinde ikon + etiket şeklinde 12 kategori kısayolu, en sonda "Daha Fazlası".

**Bilinçli bir seçim**: referanstaki gerçek fotoğraf (Mostar Köprüsü vb.)
telif nedeniyle kullanılmadı; yerine dağ/nehir motifini SVG gradyanlarla
çizdim, böylece hem lisans sorunu olmuyor hem de sitenin geri kalanındaki
düz/vektörel tasarım diliyle tutarlı kalıyor. İstersen kendi çektiğin/satın
aldığın bir fotoğrafı `.hero2-bg` arkasına `background-image` olarak
eklemek de mümkün — `static/css/app.css` içindeki `.hero2` kuralına bakabilirsin.

Eski banner (`_banner.html`, güneş motifli) hâlâ dosyada duruyor, kullanılmıyor;
istersen silinebilir ya da başka bir sayfada tekrar kullanılabilir.

## Ana ekran banner'ı (eski)

`templates/market/_banner.html` — sekiz ülkeyi temsil eden görsel şerit. Bayraklar emoji
değil, `templates/market/_flag.html` içinde SVG olarak çizildi; her işletim sisteminde
aynı görünür ve panelde, para birimi şeridinde, ülke menüsünde de kullanılır.
Banner'daki tüm metinler `market/i18n.py` sözlüğünden gelir, ülke adları
`Country.display_name(lang)` ile çevrilir — yani on dilin hepsinde çalışır.

## Kategori şeridi

`templates/market/_catnav.html` — ana kategori üstüne gelince alt kategorileri açan
mega menü, kategori başına seçili ülkedeki ilan/mağaza sayısı ve doğrudan alt kategori
bağlantıları. Hem `/ilanlar/` hem `/magazalar/` sayfasında aynı bileşen kullanılır.

## Renkler

Tek bir ülkenin bayrak rengine yaslanmamak için kırmızı kullanılmadı.
Palet Adriyatik laciverti (`--deep #0D2A3A`), deniz yeşili (`--sea #10707E`),
kehribar (`--amber #E4A13B`) ve kum (`--bg #F6F5F1`) üzerine kurulu.
`static/css/app.css` başındaki değişkenlerden topluca değiştirilebilir.
Koyu tema ve mobil uyumluluk hazır.

## Yapı

```
balkanbaazar/
├── config/            # settings, urls, wsgi, asgi
├── market/            # models, views, admin, i18n, seed komutu
│   ├── models.py      # Country, City, Category, Shop, Listing
│   ├── i18n.py        # 10 dilin arayüz metinleri
│   └── management/commands/seed.py
├── templates/         # base + market şablonları
├── static/css/app.css # tüm tasarım
└── manage.py
```

## Üretime alırken

- `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS` ortam değişkenleri.
- SQLite yerine PostgreSQL: `config/settings.py` içindeki örnek blok.
- `python manage.py collectstatic`, arkada gunicorn + nginx.
- Ürün görselleri için `Listing`'e `ImageField` eklenebilir (Pillow zaten kurulu).

## Sonraki adımlar (henüz yok)

Vasıta/emlak için kategoriye özel yapılandırılmış alanlar (km, yıl, m², oda
sayısı vb.), kupon/vitrin satın alımlarının staff panelinden yönetimi, gerçek
zamanlı mesajlaşma, görsel yeniden boyutlandırma/optimizasyon, gerçek kur
servisi, arama motoru (Elasticsearch/Postgres full-text), gettext'e geçiş
(`.po`), SEO (meta etiket, sitemap, structured data), performans (önbellekleme),
KVKK/GDPR uyum metinleri, mobil API.
