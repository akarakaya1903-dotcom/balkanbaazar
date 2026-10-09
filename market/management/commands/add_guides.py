# -*- coding: utf-8 -*-
"""Arama motorlari icin rehber yazilari (Page olarak, Yardim sutununda). Tekrar calistirmak guvenlidir."""
from django.core.management.base import BaseCommand

from market.models import Page

GUIDES = [
    {
        "slug": "guvenli-alisveris-rehberi", "order": 10,
        "tr": ("Güvenli İkinci El Alışveriş Rehberi",
               "İkinci el alışverişte dolandırılmamak için şu adımları izle.\n\n"
               "1. Ürünü görmeden ön ödeme yapma. Kapora istenip ürün gösterilmiyorsa vazgeç.\n\n"
               "2. Halka açık, kalabalık bir yerde buluş. Mümkünse yanında biriyle git.\n\n"
               "3. Ürünü yerinde dene. Elektronikte açılıp çalıştığını, araçta belgelerini kontrol et.\n\n"
               "4. Çok ucuz fiyata şüpheyle yaklaş. Piyasanın çok altındaki fiyatlar çoğu zaman tuzaktır.\n\n"
               "5. Kimlik, banka kartı bilgisi ya da doğrulama kodu paylaşma. Hiçbir alıcı veya satıcının buna ihtiyacı yok.\n\n"
               "6. Yazışmayı site içinde tut. Şüpheli bir durumda ilan sayfasındaki \"Şikâyet et\" düğmesini kullan.\n\n"
               "Balkan Baazar'da bireysel ilan vermek ücretsizdir, komisyon yoktur."),
        "en": ("Safe Second-Hand Shopping Guide",
               "Follow these steps to avoid scams when buying second-hand.\n\n"
               "1. Never pay in advance without seeing the item. If a deposit is requested and the item is not shown, walk away.\n\n"
               "2. Meet in a busy public place. Bring someone with you if you can.\n\n"
               "3. Test the item on the spot. Check that electronics work and check a vehicle's documents.\n\n"
               "4. Be suspicious of prices far below the market. They are often a trap.\n\n"
               "5. Never share ID, bank card details or verification codes. No genuine buyer or seller needs them.\n\n"
               "6. Keep the conversation on the site. If something looks wrong, use the \"Report\" button on the listing.\n\n"
               "Posting a private ad on Balkan Baazar is free, with no commission."),
        "mk": ("Водич за безбедно купување половни работи",
               "Следи ги овие чекори за да не те измамат при купување половни работи.\n\n"
               "1. Не плаќај однапред ако не си го видел производот. Ако бараат капара, а не го покажуваат производот, откажи се.\n\n"
               "2. Сретни се на јавно и прометно место. Ако можеш, земи некого со тебе.\n\n"
               "3. Пробај го производот на лице место. Кај електрониката провери дали работи, а кај возилата провери ги документите.\n\n"
               "4. Биди внимателен кога цената е многу пониска од пазарната. Често е замка.\n\n"
               "5. Никогаш не споделувај лична карта, податоци од картичка или кодови за потврда. Ниту еден вистински купувач или продавач не ги бара.\n\n"
               "6. Разговарај преку сајтот. Ако нешто изгледа сомнително, користи го копчето „Пријави“ на огласот.\n\n"
               "Објавувањето оглас за физички лица на Balkan Baazar е бесплатно и без провизија."),
        "sq": ("Udhëzues për blerje të sigurt të përdorura",
               "Ndiq këto hapa që të mos mashtrohesh kur blen gjëra të përdorura.\n\n"
               "1. Mos paguaj paraprakisht pa e parë artikullin. Nëse kërkohet kapar dhe artikulli nuk të tregohet, hiq dorë.\n\n"
               "2. Takohu në një vend publik dhe me lëvizje. Nëse mundesh, merr dikë me vete.\n\n"
               "3. Provoje artikullin në vend. Te elektronika kontrollo nëse funksionon, te automjetet kontrollo dokumentet.\n\n"
               "4. Ji i kujdesshëm me çmimet shumë nën tregun. Shpesh janë lloj kurthi.\n\n"
               "5. Mos ndaj kurrë letërnjoftimin, të dhënat e kartës ose kodet e verifikimit. Asnjë blerës a shitës i vërtetë nuk i kërkon.\n\n"
               "6. Bisedo brenda faqes. Nëse diçka duket e dyshimtë, përdor butonin \"Raporto\" te shpallja.\n\n"
               "Publikimi i shpalljes private në Balkan Baazar është falas, pa komision."),
    },
    {
        "slug": "ikinci-el-araba-rehberi", "order": 11,
        "tr": ("İkinci El Araba Alırken Dikkat Edilecekler",
               "İkinci el araba almadan önce bu listeyi kontrol et.\n\n"
               "1. Belgeleri iste. Ruhsat sahibinin satıcı olduğundan ve şasi numarasının belgeyle araçtaki numaranın aynı olduğundan emin ol.\n\n"
               "2. Kilometreyi ve bakım geçmişini sor. Servis faturaları varsa incele.\n\n"
               "3. Test sürüşü yap. Motor sesi, vites, fren ve direksiyonu dene. Mümkünse güvendiğin bir ustaya göster.\n\n"
               "4. Araç üzerinde borç, ceza veya kısıtlama olup olmadığını yetkili kurumdan öğren.\n\n"
               "5. Fiyatı benzer ilanlarla karşılaştır. Aynı model, yıl ve kilometredeki ilanlara bak.\n\n"
               "6. Devri yazılı sözleşme ve resmi işlemle yap. Ödemeyi devir tamamlanmadan tam yapma.\n\n"
               "Balkan Baazar'da araç ilanlarını şehre ve fiyata göre filtreleyebilir, aramanı kaydedip yeni ilanlardan haberdar olabilirsin."),
        "en": ("Buying a Used Car: What to Check",
               "Go through this list before buying a used car.\n\n"
               "1. Ask for the documents. Make sure the registered owner is the seller and the chassis number on the papers matches the car.\n\n"
               "2. Ask about mileage and service history. Look at service invoices if there are any.\n\n"
               "3. Take a test drive. Check the engine sound, gearbox, brakes and steering. If possible, let a mechanic you trust inspect the car.\n\n"
               "4. Find out from the proper authority whether the car has debts, fines or restrictions.\n\n"
               "5. Compare the price with similar listings of the same model, year and mileage.\n\n"
               "6. Complete the transfer with a written contract and the official procedure. Do not pay in full before the transfer is done.\n\n"
               "On Balkan Baazar you can filter vehicle listings by city and price, and save a search to be notified about new ads."),
        "mk": ("Што да провериш кога купуваш половен автомобил",
               "Помини ја оваа листа пред да купиш половен автомобил.\n\n"
               "1. Побарај ги документите. Увери се дека сопственикот во сообраќајната дозвола е продавачот и дека бројот на шасијата се совпаѓа со возилото.\n\n"
               "2. Прашај за километражата и сервисната историја. Погледни ги сервисните фактури ако има.\n\n"
               "3. Направи пробна вожња. Провери го моторот, менувачот, сопирачките и воланот. Ако можеш, покажи го на мајстор од доверба.\n\n"
               "4. Дознај кај надлежната институција дали возилото има долгови, казни или ограничувања.\n\n"
               "5. Спореди ја цената со слични огласи за ист модел, година и километража.\n\n"
               "6. Преносот направи го со писмен договор и официјална постапка. Не плаќај целосно пред да заврши преносот.\n\n"
               "На Balkan Baazar огласите за возила можеш да ги филтрираш по град и цена и да зачуваш пребарување за да добиваш известувања за нови огласи."),
        "sq": ("Çfarë të kontrollosh kur blen një makinë të përdorur",
               "Kalo këtë listë para se të blesh një makinë të përdorur.\n\n"
               "1. Kërko dokumentet. Sigurohu që pronari në librezë është shitësi dhe që numri i shasisë përputhet me automjetin.\n\n"
               "2. Pyet për kilometrazhin dhe historikun e servisit. Shiko faturat e servisit nëse ka.\n\n"
               "3. Bëj një provë vozitjeje. Kontrollo zhurmën e motorit, marshet, frenat dhe timonin. Nëse mundesh, ia trego një mekaniku të besuar.\n\n"
               "4. Merr informacion nga institucioni përkatës nëse automjeti ka borxhe, gjoba ose kufizime.\n\n"
               "5. Krahaso çmimin me shpallje të ngjashme për të njëjtin model, vit dhe kilometrazh.\n\n"
               "6. Kryej transferimin me kontratë me shkrim dhe procedurë zyrtare. Mos paguaj plotësisht para se të përfundojë transferimi.\n\n"
               "Në Balkan Baazar mund t'i filtrosh shpalljet e automjeteve sipas qytetit dhe çmimit dhe të ruash një kërkim për të marrë njoftime për shpallje të reja."),
    },
    {
        "slug": "ilan-nasil-verilir", "order": 12,
        "tr": ("İyi Bir İlan Nasıl Verilir",
               "İlanın ne kadar iyi hazırlanırsa o kadar hızlı satılır.\n\n"
               "1. Başlığa marka, model ve yılı yaz. \"Satılık telefon\" yerine \"Samsung Galaxy S21, 128 GB\" yaz.\n\n"
               "2. Gün ışığında, temiz bir fonda net fotoğraflar çek. İlk fotoğraf vitrinindir, ürünü tam göster. Kusurları da çek.\n\n"
               "3. Açıklamada ürünün durumunu dürüstçe anlat: ne kadar kullanıldı, ne var ne yok, neden satılıyor.\n\n"
               "4. Gerçekçi bir fiyat yaz. Benzer ilanlara bak. Fiyatı kendi para biriminde (örneğin MKD) ya da Euro olarak girebilirsin.\n\n"
               "5. Telefon numaranı ekle ve mesajlara hızlı cevap ver.\n\n"
               "6. İlanın süresi dolunca \"İlanlarım\" sayfasından yenile.\n\n"
               "İlk ilanını vermek 2 dakika sürer. İlanlar yönetici onayından sonra yayına girer."),
        "en": ("How to Write a Good Ad",
               "The better your ad, the faster it sells.\n\n"
               "1. Put the brand, model and year in the title. Write \"Samsung Galaxy S21, 128 GB\" instead of \"Phone for sale\".\n\n"
               "2. Take sharp photos in daylight on a clean background. The first photo is your shop window, so show the whole item. Photograph flaws too.\n\n"
               "3. Describe the condition honestly: how long it was used, what is included, why you are selling.\n\n"
               "4. Set a realistic price. Look at similar ads. You can enter the price in your own currency (for example MKD) or in Euro.\n\n"
               "5. Add your phone number and reply to messages quickly.\n\n"
               "6. When your ad expires, renew it from the \"My ads\" page.\n\n"
               "Posting your first ad takes 2 minutes. Ads go live after an administrator approves them."),
        "mk": ("Како да објавиш добар оглас",
               "Колку подобро е подготвен огласот, толку побрзо се продава.\n\n"
               "1. Во насловот напиши марка, модел и година. Наместо „Се продава телефон“ напиши „Samsung Galaxy S21, 128 GB“.\n\n"
               "2. Сликај остри фотографии при дневна светлина на чиста позадина. Првата фотографија е излогот, затоа прикажи го целиот производ. Сликај ги и недостатоците.\n\n"
               "3. Во описот чесно опиши ја состојбата: колку се користел, што е во комплетот, зошто го продаваш.\n\n"
               "4. Постави реална цена. Погледни слични огласи. Цената можеш да ја внесеш во своја валута (на пример MKD) или во евра.\n\n"
               "5. Додај го телефонскиот број и одговарај брзо на пораките.\n\n"
               "6. Кога огласот ќе истече, обнови го од страницата „Мои огласи“.\n\n"
               "Првиот оглас го објавуваш за 2 минути. Огласите се објавуваат откако ќе ги одобри администратор."),
        "sq": ("Si të publikosh një shpallje të mirë",
               "Sa më mirë të jetë përgatitur shpallja, aq më shpejt shitet.\n\n"
               "1. Në titull shkruaj markën, modelin dhe vitin. Në vend të \"Shitet telefon\" shkruaj \"Samsung Galaxy S21, 128 GB\".\n\n"
               "2. Bëj foto të qarta në dritë dite dhe në sfond të pastër. Fotoja e parë është vitrina jote, ndaj trego të gjithë artikullin. Fotografo edhe të metat.\n\n"
               "3. Në përshkrim thuaj sinqerisht gjendjen: sa është përdorur, çfarë përfshihet, pse po e shet.\n\n"
               "4. Vendos një çmim realist. Shiko shpallje të ngjashme. Çmimin mund ta shkruash në monedhën tënde (p.sh. MKD) ose në euro.\n\n"
               "5. Shto numrin e telefonit dhe përgjigju shpejt mesazheve.\n\n"
               "6. Kur skadon shpallja, rinovoje nga faqja \"Shpalljet e mia\".\n\n"
               "Publikimi i shpalljes së parë zgjat 2 minuta. Shpalljet publikohen pasi t'i miratojë administratori."),
    },
]


class Command(BaseCommand):
    help = "Rehber yazilarini ekler/gunceller (Yardim sutunu)"

    def handle(self, *args, **options):
        for g in GUIDES:
            title, body = g["tr"]
            translations = {code: {"title": g[code][0], "body": g[code][1]} for code in ("en", "mk", "sq")}
            Page.objects.update_or_create(
                slug=g["slug"],
                defaults={"title": title, "body": body, "group": "f2", "order": g["order"],
                          "is_published": True, "translations": translations},
            )
            self.stdout.write(f"rehber: {g['slug']}")
