"""
Script untuk menghasilkan 100+ ulasan realistis kuliner Indonesia
dengan pelabelan 5 aspek: Rasa, Porsi, Harga, Kemasan, Pelayanan.
Mencakup 4 outlet UMKM F&B dengan pola permasalahan operasional riil.
"""

import os
import random
import pandas as pd

RESTAURANTS_DATA = [
    {
        "name": "Ayam Geprek Sambal Korek Barokah",
        "menus": ["Paket Geprek Dada Sambal Korek", "Ayam Geprek Sambal Bawang", "Paket Kulit Ayam Crispy", "Nasi Ayam Geprek Keju Lumer"],
        "reviews": [
            # Mixed: Rasa bagus, Kemasan/Pelayanan jelek
            ("Ayamnya gurih renyah bumbunya mantap meresap, tapi kemasan mangkok tumpah kuah dan minyak sambal rembes ke kantong plastik. Driver nunggu 30 menit.", "positive", "neutral", "not_mentioned", "negative", "negative"),
            ("Rasa sambal koreknya nampol bikin nagih, ayam crispy bgt, sayangnya pas nyampe udah dingin anyep dan box kertas basah kuyup kena uap.", "positive", "not_mentioned", "not_mentioned", "negative", "not_mentioned"),
            ("Ayam geprek terenak di area ini bumbu medok, tapi sambalnya dikit banget ga cukup buat nasi seporsi. Tolong sendok jangan lupa dimasukin.", "positive", "negative", "not_mentioned", "not_mentioned", "negative"),
            ("Kulit ayamnya garing kriuk juara, porsi pas kenyang, cuma sausnya bocor kemana-mana di bungkus plastik. Kurang isolasi tutupnya.", "positive", "positive", "not_mentioned", "negative", "not_mentioned"),
            ("Bumbunya asin gurih nikmat, keju lumernya banyak. Tapi boxnya penyok pas diterima kurir, minyak sambal tembus ke dasar kardus.", "positive", "positive", "not_mentioned", "negative", "not_mentioned"),
            ("Daging ayam juicy ga kering, sambal korek pedas segar. Cuma pesanan salah, saya pesan sambal ijo dikasih sambal bawang.", "positive", "not_mentioned", "not_mentioned", "not_mentioned", "negative"),
            ("Ayam gepreknya agak keasinan hari ini, ga kayak biasanya. Sambal juga sedikit, harga 28rb jadi kerasa kemahalan.", "negative", "negative", "negative", "not_mentioned", "not_mentioned"),
            ("Lama banget proses di dapurnya, nunggu makanan 40 menit padahal antrean sepi. Pas datang ayam udah dingin.", "negative", "not_mentioned", "not_mentioned", "not_mentioned", "negative"),
            ("Mantap pol sambelnya pedes gila, ayam matang sempurna sampe ke tulang. Porsi nasi banyak, kemasan rapi ada segel.", "positive", "positive", "positive", "positive", "positive"),
            ("Ayamnya enak gurih, sambal pedes nendang. Tapi tutup sterofoam bolong kena uap panas ayam, tolong ganti thinwall.", "positive", "not_mentioned", "not_mentioned", "negative", "not_mentioned"),
            ("Rasa biasa aja bumbu kurang meresap, ayam terasa hambar di bagian dada. Porsi dikit, sambal cuma satu sendok teh.", "negative", "negative", "not_mentioned", "not_mentioned", "not_mentioned"),
            ("Packaging kacau balau, minyak sambal tumpah ngotorin plastik sama minuman. Padahal ayamnya sebenernya enak bgt.", "positive", "not_mentioned", "not_mentioned", "negative", "not_mentioned"),
            ("Porsi kuli kenyang seharian, harga murah meriah 20rb dapet ayam nasi sambal lalapan. Recommended buat anak kos!", "positive", "positive", "positive", "not_mentioned", "not_mentioned"),
            ("Sambal bawangnya sedap gila, ayamnya garing kriuk. Cuma lalapannya layu dan ada potongan daun kotor ga dicuci.", "positive", "not_mentioned", "not_mentioned", "not_mentioned", "negative"),
            ("Minta ekstra sambal di note aplikasi tapi ga dikasih sama sekali. Pelayanannya kurang teliti baca catatan orderan.", "not_mentioned", "not_mentioned", "not_mentioned", "not_mentioned", "negative"),
            ("Enak banget bumbu rempahnya kerasa, daging empuk. Packing plastik dobel rapi ga ada yang rembes. Puas!", "positive", "not_mentioned", "not_mentioned", "positive", "positive"),
            ("Ayamnya bau apek kayak minyak jelantah bekas goreng berkali-kali. Tenggorokan langsung gatal. Kecewa parah.", "negative", "not_mentioned", "negative", "not_mentioned", "not_mentioned"),
            ("Porsinya makin ciut ayamnya kecil banget seukuran burung puyuh. Padahal harganya udah naik jadi 25rb.", "not_mentioned", "negative", "negative", "not_mentioned", "not_mentioned"),
            ("Renyah kriuk bumbu pas ga keasinan. Pengiriman cepat dan kemasan rapi tersegel cable tie.", "positive", "not_mentioned", "positive", "positive", "positive"),
            ("Keasinan parah bumbunya hari ini, ga kemakan sama sekali. Tolong takaran garam diperhatikan koki.", "negative", "not_mentioned", "not_mentioned", "not_mentioned", "not_mentioned"),
            ("Packaging sangat aman pake mangkok paper bowl tebal dan ada solasi rapat. Ayam masih anget gurih enak.", "positive", "not_mentioned", "not_mentioned", "positive", "positive"),
            ("Rasa juara langganan keluarga, tapi hari ini sambalnya encer kebanyakan minyak. Porsi ayamnya standar.", "neutral", "neutral", "not_mentioned", "negative", "not_mentioned"),
            ("Harga murah rasa resto bintang lima, sambal korek mantul pedesnya pas di lidah. Selalu repeat order tiap minggu.", "positive", "positive", "positive", "not_mentioned", "positive"),
            ("Pelayan jutek pas ditanya soal pesanan takeaway, nunggunya lama banget hampir 45 menit. Makanan standar.", "neutral", "not_mentioned", "not_mentioned", "not_mentioned", "negative"),
            ("Ayam dingin alot kulitnya lemes kena uap. Sayang banget padahal racikan sambel koreknya enak seger.", "neutral", "not_mentioned", "not_mentioned", "negative", "not_mentioned")
        ]
    },
    {
        "name": "Kopi Susu Senja & Toast",
        "menus": ["Es Kopi Susu Gula Aren", "Toast Smoked Beef & Cheese", "Caramel Macchiato", "Roti Bakar Cokelat Keju"],
        "reviews": [
            ("Kopi susunya creamy pas kopinya wangi ga bikin asam lambung, toast renyah keju lumer. Kemasan cup tebal rapi.", "positive", "not_mentioned", "positive", "positive", "positive"),
            ("Gelas kopinya kecil banget es batunya penuh 80%, 2 kali sruput udah abis. Harga 28rb kemahalan buat porsi segini.", "neutral", "negative", "negative", "not_mentioned", "not_mentioned"),
            ("Toast smoked beefnya enak bgt gurih, tapi potongan dagingnya makin tipis dibanding bulan lalu. Shrinkflation ya?", "positive", "negative", "negative", "not_mentioned", "not_mentioned"),
            ("Kopi kemanisan parah sirup gulanya mendominasi ga kerasa kopinya sama sekali. Toastnya juga gosong pinggirannya.", "negative", "not_mentioned", "not_mentioned", "not_mentioned", "not_mentioned"),
            ("Packaging super aesthetic cup anti bocor dan ada seal tape rapi. Barista ramah senyum, pelayanan cepat 5 menit jadi.", "not_mentioned", "not_mentioned", "not_mentioned", "positive", "positive"),
            ("Roti bakarnya kering alot, cokelatnya dikit ga lumer. Harganya overprice banget untuk rasa standar warung kopi.", "negative", "negative", "negative", "not_mentioned", "not_mentioned"),
            ("Kopi terenak di komplek ini beneran berasa espresso premiumnya. Porsi pas, harga sangat terjangkau ada promo bundle.", "positive", "positive", "positive", "positive", "positive"),
            ("Pesan less sugar tapi dikasih manis banget kayak air gula. Driver nunggu 25 menit katanya antrean online numpuk.", "negative", "not_mentioned", "not_mentioned", "not_mentioned", "negative"),
            ("Kemasan cup bagus ga gampang tumpah di motor, toastnya dibungkus box karton tebal bersih.", "not_mentioned", "not_mentioned", "not_mentioned", "positive", "not_mentioned"),
            ("Rasa kopi lumayan enak, cuma es batunya kebanyakan bikin kopi jadi hambar setelah 10 menit perjalanan kurir.", "neutral", "negative", "not_mentioned", "not_mentioned", "not_mentioned"),
            ("Toast beef and egg juara sarapan, saus mentainya nagih gurih asam pas. Porsi mengenyangkan buat ganjal perut.", "positive", "positive", "positive", "not_mentioned", "positive"),
            ("Harganya mahal banget 35rb dapet segelas mini dan rasa kopi biasa aja ga ada spesialnya. Ga akan reorder lagi.", "negative", "negative", "negative", "not_mentioned", "not_mentioned"),
            ("Pelayanannya gercep satset, pesan 4 cup kopi dan 2 toast selesai dalam 7 menit. Semuanya hangat dan rapi.", "not_mentioned", "not_mentioned", "not_mentioned", "positive", "positive"),
            ("Pesenan salah, minta roti bakar coklat dikasih keju doang. Pas ditelepon respon kasir cuek ga ada solusi.", "not_mentioned", "not_mentioned", "not_mentioned", "not_mentioned", "negative"),
            ("Kopi susu gula aren terbaik, manisnya pas kopinya bold tapi lembut. Worth it setiap rupiahnya!", "positive", "not_mentioned", "positive", "not_mentioned", "positive"),
            ("Tutup cup kurang rapat pas diambil driver ada rembesan kopi basahin kantong kertas. Rasa kopi standar.", "neutral", "not_mentioned", "not_mentioned", "negative", "not_mentioned"),
            ("Porsi toast tebal daging melimpah saus keju tumpe-tumpe. Puas banget makan siang disini.", "positive", "positive", "positive", "not_mentioned", "positive"),
            ("Kopi asam bikin kembung, susunya kayak udah mau basi baunya agak asam aneh. Langsung saya buang.", "negative", "not_mentioned", "not_mentioned", "not_mentioned", "not_mentioned"),
            ("Harga bersahabat untuk tempat nongkrong senyaman ini, kopi enak dan toastnya renyah empuk.", "positive", "not_mentioned", "positive", "not_mentioned", "positive"),
            ("Lama bgt bikin kopinya padahal cuma pesan 1 es kopi susu, barista sibuk ngobrol sendiri.", "not_mentioned", "not_mentioned", "not_mentioned", "not_mentioned", "negative"),
            ("Packaging ramah lingkungan tanpa sedotan plastik tapi ada lid sippy cup praktis anti tumpah. Mantap!", "not_mentioned", "not_mentioned", "not_mentioned", "positive", "positive"),
            ("Ukuran cup menyusut dari yang biasa, harga tetap sama. Isinya dikit banget kebanyakan batu es.", "not_mentioned", "negative", "negative", "not_mentioned", "not_mentioned"),
            ("Kombinasi kopi dan toast beef keju lumer sempurna di lidah. Rasa bintang 5 harga kaki lima.", "positive", "positive", "positive", "not_mentioned", "positive"),
            ("Roti bakarnya gosong pahit, kejunya pelit cuma seupil. Kecewa banget sama kualitas dapurnya.", "negative", "negative", "negative", "not_mentioned", "not_mentioned"),
            ("Barista ramah dan informatif rekomendasiin beans yang ga asam. Pelayanan sangat memuaskan.", "not_mentioned", "not_mentioned", "not_mentioned", "not_mentioned", "positive")
        ]
    },
    {
        "name": "Bakso Rusuk Solo Pak Ndut",
        "menus": ["Bakso Rusuk Sapi Jumbo", "Mie Ayam Bakso Urat", "Bakso Halus Kuah Kaldu", "Pangsit Goreng Crispy"],
        "reviews": [
            ("Kuah kaldunya gurih ngaldu banget seger, rusuk sapinya empuk copot dari tulang, porsi jumbo kenyang pol!", "positive", "positive", "positive", "not_mentioned", "positive"),
            ("Lama banget pelayanannya, order mie ayam bakso nunggu 50 menit pas jam makan siang. Pelayan jutek ga ada senyum.", "not_mentioned", "not_mentioned", "not_mentioned", "not_mentioned", "negative"),
            ("Bakso uratnya kenyal daging kerasa asli bukan tepung, kuah bening sedap. Cuma kuahnya agak keasinan hari ini.", "positive", "positive", "not_mentioned", "not_mentioned", "not_mentioned"),
            ("Mangkok kertasnya penyok di jalan kuah bakso tumpah separuh ke kresek. Tolong ganti wadah yang lebih kokoh.", "neutral", "not_mentioned", "not_mentioned", "negative", "not_mentioned"),
            ("Porsi kuli beneran rusuknya gede banget daging tebel harga 42rb sangat worth it. Sambalnya pedas mantap.", "positive", "positive", "positive", "not_mentioned", "positive"),
            ("Kuah baksonya dingin pas dianter, lemak sapi udah beku di permukaan kuah jadi enek dimakan.", "negative", "not_mentioned", "not_mentioned", "negative", "not_mentioned"),
            ("Mie ayamnya manis pas bumbu ayam gurih melimpah, bakso halusnya lembut. Pelayanan ramah cepet saji.", "positive", "positive", "positive", "not_mentioned", "positive"),
            ("Pangsit gorengnya tengik bau minyak lama, baksonya ada bagian urat yang keras ga bisa dikunyah.", "negative", "not_mentioned", "negative", "not_mentioned", "not_mentioned"),
            ("Sambal dan saus dipisah rapi dalam klip kecil, kuah dibungkus plastik dobel anti jebol. Pengemasan top!", "not_mentioned", "not_mentioned", "not_mentioned", "positive", "positive"),
            ("Harga murah rasa juara, bakso rusuk terenak se-kota! Daging rusuknya empuk banget ga alot sama sekali.", "positive", "positive", "positive", "not_mentioned", "positive"),
            ("Antrean takeaway berantakan, pesanan saya dilewati 3 orang padahal udah bayar duluan. Kasir ga teliti.", "not_mentioned", "not_mentioned", "not_mentioned", "not_mentioned", "negative"),
            ("Kuah kaldu keasinan parah kebanyakan micin bikin haus seharian. Baksonya sebenernya enak tapi kuahnya bikin enek.", "negative", "not_mentioned", "not_mentioned", "not_mentioned", "not_mentioned"),
            ("Daging rusuknya tipis banyakan tulangnya doang, porsi bakso cuma dapet 3 biji kecil. Agak mengecewakan untuk harga 40rb.", "negative", "negative", "negative", "not_mentioned", "not_mentioned"),
            ("Pangsit goreng renyah kriuk gurih, bakso uratnya mantul. Pengemasan bersih dan steril rapi.", "positive", "not_mentioned", "positive", "positive", "positive"),
            ("Kuahnya tumpah basah kuyup boxnya jebol. Sayang bgt kurir bawa hati-hati tapi mangkok emang ga diisolasi.", "not_mentioned", "not_mentioned", "not_mentioned", "negative", "not_mentioned"),
            ("Citarasa khas Solo beneran autentik kuah bening gurih seger tanpa micin berlebihan. Recommended!", "positive", "positive", "positive", "not_mentioned", "positive"),
            ("Minta kuah dipisah dan tanpa daun bawang, tapi pas nyampe daun bawang seabrek dan kuah dicampur. Pelayan ga baca note.", "not_mentioned", "not_mentioned", "not_mentioned", "not_mentioned", "negative"),
            ("Bakso rusuk porsi raksasa mengenyangkan, harga bersahabat di kantong. Bakal jadi langganan tetap.", "positive", "positive", "positive", "not_mentioned", "positive"),
            ("Daging rusuk masih bau prengus sapi kurang bersih pas perebusan awal. Kuahnya hambar kurang bumbu.", "negative", "not_mentioned", "negative", "not_mentioned", "not_mentioned"),
            ("Pelayanannya sangat cekatan biarpun resto lagi rame pelanggan. Makanan datang dalam 10 menit panas-panas.", "positive", "not_mentioned", "not_mentioned", "positive", "positive"),
            ("Mangkok baksonya retak di bagian pinggir pas dibuka. Kuah netes kemana-mana ngotorin karpet meja.", "not_mentioned", "not_mentioned", "not_mentioned", "negative", "not_mentioned"),
            ("Porsi bakso banyak banget ngenyangin, daging sapi berasa pol ga pelit bumbu kuah. Mantap!", "positive", "positive", "positive", "not_mentioned", "positive"),
            ("Bumbu mie ayam terlalu manis kayak kolak, minyak ayamnya kebanyakan bikin mual di lidah.", "negative", "not_mentioned", "not_mentioned", "not_mentioned", "not_mentioned"),
            ("Alat makan sendok garpu ga dikasih padahal udah centang minta alat makan di aplikasi ojol. Repot makannya.", "not_mentioned", "not_mentioned", "not_mentioned", "negative", "negative"),
            ("Kuah gurih sedap daging rusuk lembut bgt lumer di mulut. Nilai 10/10 buat rasa dan porsi!", "positive", "positive", "positive", "not_mentioned", "positive")
        ]
    },
    {
        "name": "Bebek Goreng Madura Cak Roni",
        "menus": ["Bebek Goreng Bumbu Hitam", "Bebek Bakar Madu Pedas", "Nasi Bebek Kremes Gurih", "Bebek Rica Kemangi"],
        "reviews": [
            ("Bebek bumbu hitamnya juara dunia rempahnya medok gurih pedas sedap daging empuk ga amis sama sekali!", "positive", "positive", "positive", "not_mentioned", "positive"),
            ("Porsi bebek setengah ekor kenyang pol nasi pulen anget sambal mangga seger. Packaging rapi besek bambu bersih.", "positive", "positive", "positive", "positive", "positive"),
            ("Daging bebek empuk banget gampang lepas dari tulang, bumbu hitamnya meresap sampai ke serat daging terdalam.", "positive", "not_mentioned", "positive", "not_mentioned", "positive"),
            ("Sambal koreknya pedas nampol bumbu hitam gurih asin pas. Cuma nunggu driver agak lama 35 menit pas jam makan malam.", "positive", "not_mentioned", "not_mentioned", "not_mentioned", "negative"),
            ("Kemasan kardus tebal laminasi anti minyak ga ada bocor sama sekali, lalapan timun kemangi seger bersih.", "positive", "not_mentioned", "positive", "positive", "positive"),
            ("Bebeknya alot banget susah digigit kayak daging tua, bumbu hitamnya agak pahit gosong. Sangat kecewa.", "negative", "not_mentioned", "negative", "not_mentioned", "not_mentioned"),
            ("Harga 38rb dapet paket komplit bebek empuk nasi sambal lalapan kremesan melimpah, sangat worth it!", "positive", "positive", "positive", "not_mentioned", "positive"),
            ("Bumbu hitamnya sedikit banget cuma dapet 1 sendok makan padahal beli porsi bebek utuh. Pelit bgt.", "positive", "negative", "negative", "not_mentioned", "not_mentioned"),
            ("Kremesannya kriuk gurih ga berminyak, sambalnya pedas nendang bikin nambah nasi terus. Mantap Cak Roni!", "positive", "positive", "positive", "not_mentioned", "positive"),
            ("Bebek masih banyak bulu halus di bagian sayap dan paha, agak jijik makannya. Tolong proses pencabutan bulu diperbaiki.", "negative", "not_mentioned", "not_mentioned", "not_mentioned", "negative"),
            ("Pengemasan sangat higienis pake kotak bento sekat jadi sambal dan bebek ga campur aduk di jalan. Bagus!", "positive", "not_mentioned", "positive", "positive", "positive"),
            ("Pelayanan ramah bgt kasir cekatan, bebek siap dalam 8 menit masih panas ngepul pas diambil.", "not_mentioned", "not_mentioned", "not_mentioned", "positive", "positive"),
            ("Rasa rica kemanginya wangi sedap pedes nampol, porsi pas buat makan malam berdua. Selalu puas disini.", "positive", "positive", "positive", "not_mentioned", "positive"),
            ("Bebek bakar madunya manis gurih pas ga enek, bumbu olesan tebal. Pengiriman cepat dan rapi tersegel.", "positive", "positive", "positive", "positive", "positive"),
            ("Minyak bebeknya berlebihan basah kuyup di nasi sampai lembek. Bumbu hitam agak asin hari ini.", "neutral", "not_mentioned", "not_mentioned", "negative", "not_mentioned"),
            ("Porsi bebek jumbo daging tebal kulit krispi gurih. Sambal mangga mudanya seger pol ga ada obat!", "positive", "positive", "positive", "not_mentioned", "positive"),
            ("Driver ojol nunggu lama banget di resto hampir 40 menit karena bebek digoreng dadakan saat orderan masuk.", "positive", "not_mentioned", "not_mentioned", "not_mentioned", "negative"),
            ("Besek bambu pembungkusnya estetik dan rapi, makanan tetap hangat pas tiba di rumah. Rasa 10/10!", "positive", "positive", "positive", "positive", "positive"),
            ("Daging bebeknya amis bau bebek basah kurang rempah perebusan. Bumbu hitamnya ga bisa nutupin bau amisnya.", "negative", "not_mentioned", "negative", "not_mentioned", "not_mentioned"),
            ("Bebek goreng terenak di Jakarta Timur! Bumbu hitam autentik gurih rempah Madura asli bukan kaleng-kaleng.", "positive", "positive", "positive", "not_mentioned", "positive"),
            ("Sambalnya kurang pedes buat lidah pecinta pedas, tapi rasa bebeknya sendiri udah gurih empuk sedap.", "positive", "not_mentioned", "positive", "not_mentioned", "positive"),
            ("Porsi pas di perut, harga sebanding kualitas daging bebek premium. Pelayanan ramah bintang lima.", "positive", "positive", "positive", "not_mentioned", "positive"),
            ("Kemasan kertas minyak robek kena tulang bebek dan minyak tembus ke kantong kresek kurir.", "neutral", "not_mentioned", "not_mentioned", "negative", "not_mentioned"),
            ("Potongan bebeknya besar daging empuk gurih sampai ke serat dalam. Nasi bebek bumbu hitam nomor 1!", "positive", "positive", "positive", "not_mentioned", "positive"),
            ("Pesanan sambal mangga tidak dikirimkan padahal di struk tertulis jelas. Staf packing tolong lebih teliti.", "not_mentioned", "not_mentioned", "not_mentioned", "not_mentioned", "negative")
        ]
    }
]

rows = []
review_counter = 1

for resto in RESTAURANTS_DATA:
    r_name = resto["name"]
    menus = resto["menus"]
    for text, rasa, porsi, harga, kemasan, pelayanan in resto["reviews"]:
        menu = random.choice(menus)
        rows.append({
            "review_id": review_counter,
            "restaurant_name": r_name,
            "menu_item": menu,
            "review_text": text,
            "rasa": rasa,
            "porsi": porsi,
            "harga": harga,
            "kemasan": kemasan,
            "pelayanan": pelayanan
        })
        review_counter += 1

df = pd.DataFrame(rows)
output_path = "data/sample_reviews.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
df.to_csv(output_path, index=False)
print(f"Sukses membuat {len(df)} ulasan di {output_path} untuk {len(RESTAURANTS_DATA)} restoran!")
