from django.core.management.base import BaseCommand

from market.models import Page

PAGES = [
 [
  "hakkimizda",
  "Hakkımızda",
  "f1",
  1,
  "Balkan Baazar, Balkanların yeni pazaryeridir. Kuzey Makedonya, Arnavutluk, Kosova, Sırbistan, Karadağ, Bosna-Hersek, Bulgaristan ve Yunanistan'daki mağaza ürünlerini ve bireysel ikinci el ilanlarını tek platformda buluşturur.\n\nPlatform, [[company]] tarafından işletilir. Amacımız bölgedeki alıcıları ve satıcıları güvenli, sade ve çok dilli bir ortamda bir araya getirmektir.\n\nMağazalar ürünlerini panelden yönetir, bireysel kullanıcılar ücretsiz ikinci el ilan verebilir. Alıcılar ve satıcılar site içi mesajlaşma ile iletişime geçer.\n\nAdres: [[address]]\nE-posta: [[email]]"
 ],
 [
  "iletisim",
  "İletişim",
  "f1",
  2,
  "Soruların, önerilerin ve şikâyetlerin için bize ulaşabilirsin.\n\nİşletme: [[company]]\nAdres: [[address]]\nE-posta: [[email]]\nTelefon: [[phone]]\n\nBir ilanla ilgili sorun bildirmek için ilan sayfasındaki \"Şikâyet et\" düğmesini kullanabilirsin. Kişisel verilerinle ilgili talepler için e-posta ile yazman yeterli."
 ],
 [
  "gizlilik-politikasi",
  "Gizlilik Politikası",
  "f2",
  1,
  "Son güncelleme: 5 Ekim 2026\n\n1. Veri sorumlusu\nBu politika, Balkan Baazar (balkanbaazar.com) platformunu işleten [[company]] (\"biz\") tarafından kişisel verilerinin nasıl işlendiğini açıklar. İletişim: [[email]], [[address]].\n\n2. Topladığımız veriler\n- Hesap bilgileri: kullanıcı adı, ad ve soyad, e-posta adresi, şifre (şifreler okunamaz biçimde saklanır). Google ile giriş yaparsan Google'dan ad ve doğrulanmış e-posta adresini alırız.\n- İlan ve mağaza içeriği: başlık, açıklama, fiyat, fotoğraf, video, telefon numarası, şehir.\n- Mesajlar: kullanıcılar arasındaki yazışmalar.\n- Sipariş bilgileri: teslimat adı, adresi ve telefonu.\n- Teknik veriler: IP adresi, tarayıcı bilgisi ve sunucu kayıtları; güvenlik ve hata ayıklama amacıyla.\n- Çerezler ve anonim ziyaretçi sayacı (bkz. Çerez Politikası).\n\n3. İşleme amaçları\nHesabını oluşturmak ve yönetmek, ilanlarını yayınlamak, alıcı ve satıcıyı iletişime geçirmek, siparişleri yürütmek, bildirim e-postaları göndermek, dolandırıcılığı ve kötüye kullanımı önlemek, siteyi geliştirmek ve yasal yükümlülükleri yerine getirmek.\n\n4. Paylaşım\nVerilerini satmayız. İlanında yazdığın bilgiler (başlık, açıklama, fotoğraf, telefon numarası) sitede herkese görünür. Siparişte teslimat bilgilerin ilgili satıcıyla paylaşılır. Altyapı hizmetleri (barındırma, e-posta gönderimi, Google ile giriş) için hizmet sağlayıcıları kullanırız. Yasal bir talep olursa yetkili makamlarla paylaşabiliriz.\n\n5. Saklama\nVerilerini hesabın açık olduğu sürece ve yasal yükümlülükler gerektirdiği süre boyunca saklarız. Hesabını sildirdiğinde kişisel verilerin silinir veya anonimleştirilir; yasal olarak saklanması gerekenler hariç.\n\n6. Haklarının kullanımı\nVerilerine erişme, düzeltme, silme, işlenmesine itiraz etme ve verilerinin kopyasını isteme hakkın vardır. Talepler için [[email]] adresine yaz. Başvurunu makul süre içinde yanıtlarız.\n\n7. Çocuklar\nPlatform 18 yaşından küçükler için tasarlanmamıştır.\n\n8. Güvenlik\nVerilerini korumak için HTTPS, şifre özetleme ve erişim kontrolleri kullanırız. Hiçbir sistem tamamen risksiz değildir.\n\n9. Değişiklikler\nBu politikayı güncelleyebiliriz. Güncel hâli bu sayfada yayınlanır.\n\nEnglish summary\nWe collect account details, listing content, messages, order delivery details and technical logs to run the marketplace, prevent abuse and send notifications. We do not sell your data. Your listing details are public. You can request access, correction or deletion of your data by writing to [[email]]. Operator: [[company]], [[address]]."
 ],
 [
  "kullanim-kosullari",
  "Kullanım Koşulları",
  "f2",
  2,
  "Son güncelleme: 5 Ekim 2026\n\n1. Kabul\nBalkan Baazar'ı kullanarak bu koşulları kabul etmiş olursun. Platformu [[company]] işletir.\n\n2. Hesap\nDoğru bilgi vermekle ve hesabının güvenliğinden sorumlusun. Hesabını başkasına devretmemelisin. 18 yaşından küçükler platformu kullanamaz.\n\n3. Platformun rolü\nBalkan Baazar bir pazaryeri ve ilan platformudur. Mağaza satıcıları ve bireysel ilan verenler satışı kendi adlarına yapar. Biz ürünlerin sahibi veya satıcısı değiliz; ilanların doğruluğunu, ürünlerin kalitesini veya alıcı ile satıcı arasındaki işlemlerin sonucunu garanti etmeyiz.\n\n4. İlan kuralları\nİlanların doğru, güncel ve sana ait olmalıdır. Şunlar yasaktır: yasa dışı veya çalıntı ürünler, sahte/taklit ürünler, silah ve patlayıcılar, uyuşturucu, canlı hayvan ticaretinde yasa dışı faaliyet, yetişkin içeriği, dolandırıcılık amaçlı veya yanıltıcı ilanlar, başkalarının fotoğraf ve içeriğini izinsiz kullanmak, nefret söylemi ve hakaret. Aynı ürünü tekrar tekrar ilan etmek veya spam yapmak yasaktır.\n\n5. İçerik ve lisans\nYüklediğin içeriklerin sorumluluğu sana aittir. İçeriğini platformda göstermemiz, saklamamız ve tanıtım amacıyla (örneğin ilan paylaşımlarında) kullanmamız için bize geri alınabilir, dünya çapında, ücretsiz bir kullanım izni verirsin.\n\n6. Ödeme ve teslimat\nŞu an platform üzerinden online kart ödemesi alınmamaktadır. Mağaza siparişlerinde ödeme, teslimat sırasında (kapıda) yapılır. Bireysel ilanlarda ödeme ve teslimat alıcı ile satıcı arasında kararlaştırılır. Güvenliğin için ürünü görmeden ön ödeme yapmamanı öneririz.\n\n7. Şikâyet ve kaldırma\nKurallara aykırı gördüğün ilanları \"Şikâyet et\" düğmesiyle bildirebilirsin. Kuralları ihlal eden ilanları kaldırma ve hesapları geçici veya kalıcı olarak kapatma hakkımız saklıdır. Bireysel ilanlar belirli bir süre sonra otomatik yayından kalkabilir.\n\n8. Sorumluluğun sınırı\nPlatform \"olduğu gibi\" sunulur. Yasaların izin verdiği ölçüde, kullanıcılar arasındaki işlemlerden, dolaylı zararlardan veya hizmet kesintilerinden doğan zararlardan sorumlu değiliz.\n\n9. Fikri mülkiyet\nBalkan Baazar adı, logosu ve yazılımı [[company]] veya lisans verenlerine aittir. İzinsiz kopyalanamaz.\n\n10. Değişiklikler ve uygulanacak hukuk\nKoşulları güncelleyebiliriz. Güncel hâli bu sayfada yayınlanır. Bu koşullara Kuzey Makedonya hukuku uygulanır; uyuşmazlıklarda Üsküp mahkemeleri yetkilidir.\n\n11. İletişim\n[[company]], [[address]], [[email]]\n\nEnglish summary\nBalkan Baazar is a marketplace and classifieds platform operated by [[company]]. Sellers and individual advertisers are responsible for their listings. Prohibited items (illegal, stolen, counterfeit, weapons, drugs, adult content, scams) are not allowed and we may remove listings or close accounts. No online card payments are taken at the moment; shop orders are paid on delivery. Contact: [[email]]."
 ],
 [
  "iade-ve-iptal",
  "İade ve İptal",
  "f2",
  3,
  "Son güncelleme: 5 Ekim 2026\n\nMağaza siparişleri\n- Ödeme: Şu an siparişler kapıda ödeme ile yapılır. Teslimat sırasında ürünü kontrol etmeni öneririz.\n- İptal: Siparişin satıcı tarafından kargoya verilmesinden önce iptal talebi iletebilirsin. Talebini sipariş bilgilerinle [[email]] adresine yaz ya da satıcıyla site içi mesajlaşmadan iletişime geç.\n- İade: Ürünü teslim aldıktan sonra 14 gün içinde, kullanılmamış ve orijinal ambalajında olması koşuluyla iade talebi iletebilirsin. Ürün hasarlı, eksik veya ilanda anlatılandan farklı geldiyse bu süre ve koşullardan bağımsız olarak talebini hemen bildir.\n- İade kargo bedeli: Ürün hatalı veya yanlış gönderildiyse satıcı karşılar; diğer durumlarda satıcının koşulları geçerlidir ve ürün sayfasında belirtilir.\n- İade sonrası: Ürün satıcıya ulaşıp kontrol edildikten sonra ödediğin tutar iade edilir. Kapıda ödemede iade, anlaşılan yöntemle (örneğin banka havalesi) yapılır.\n\nBireysel ikinci el ilanlar\nBireyler arasındaki satışlar bu platform üzerinden yürütülen bir mağaza satışı değildir; iade ve cayma hakkı otomatik olarak geçerli değildir. Ürünü satın almadan önce görmeni ve satıcıyla koşulları yazılı olarak netleştirmeni öneririz.\n\nYasal haklar\nBu sayfadaki koşullar, tüketici mevzuatından doğan yasal haklarını sınırlamaz.\n\nTalepler için: [[company]], [[email]], [[address]]\n\nEnglish summary\nShop orders are currently paid on delivery. You may request cancellation before the order is shipped and a return within 14 days of delivery if the item is unused and in its original packaging; damaged or wrong items should be reported immediately. Private second-hand listings are deals between individuals and carry no automatic return right. Contact: [[email]]."
 ],
 [
  "cerez-politikasi",
  "Çerez Politikası",
  "f2",
  4,
  "Son güncelleme: 5 Ekim 2026\n\nÇerez, tarayıcında saklanan küçük bir metin dosyasıdır. Balkan Baazar şunları kullanır:\n\n- Oturum çerezi: giriş yapmış kalmanı sağlar.\n- Güvenlik çerezi (CSRF): formların güvenle gönderilmesini sağlar.\n- Tercih çerezleri: seçtiğin ülke ve dili hatırlar.\n- Ziyaretçi sayacı çerezi: siteyi günde kaç kişinin ziyaret ettiğini, kimliğini belirlemeden anonim olarak saymak için 24 saat geçerli bir çerez bırakır.\n- Çerez bildirimi tercihin tarayıcının yerel depolamasında saklanır.\n\nGoogle ile giriş yaparsan Google kendi çerezlerini kullanabilir; bunlar Google'ın politikalarına tabidir.\n\nÇerezleri tarayıcı ayarlarından silebilir veya engelleyebilirsin; bu durumda giriş yapma gibi bazı özellikler çalışmayabilir.\n\nSorular için: [[email]]"
 ]
]


class Command(BaseCommand):
    help = "Taslak yasal ve kurumsal sayfalari ekler. Var olan sayfalara dokunmaz (--force ile ustune yazar)."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Var olan sayfalarin icerigini taslakla degistir")

    def handle(self, *args, **options):
        for slug, title, group, order, body in PAGES:
            page, created = Page.objects.get_or_create(
                slug=slug, defaults={"title": title, "body": body, "group": group, "order": order, "is_published": True})
            if created:
                self.stdout.write(self.style.SUCCESS(f"eklendi: {slug}"))
            elif options["force"]:
                page.title, page.body, page.group, page.order = title, body, group, order
                page.save()
                self.stdout.write(f"guncellendi: {slug}")
            else:
                self.stdout.write(f"var (atlandi): {slug}")
