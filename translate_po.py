import os
import re

translations = {
    # States
    "Cairo": "القاهرة", "Giza": "الجيزة", "Alexandria": "الإسكندرية", "Dakahlia": "الدقهلية",
    "Red Sea": "البحر الأحمر", "Beheira": "البحيرة", "Fayoum": "الفيوم", "Gharbia": "الغربية",
    "Ismailia": "الإسماعيلية", "Menofia": "المنوفية", "Minya": "المنيا", "Qalyubia": "القليوبية",
    "New Valley": "الوادي الجديد", "Suez": "السويس", "Aswan": "أسوان", "Assiut": "أسيوط",
    "Beni Suef": "بني سويف", "Port Said": "بورسعيد", "Damietta": "دمياط", "Sharkia": "الشرقية",
    "South Sinai": "جنوب سيناء", "Kafr El Sheikh": "كفر الشيخ", "Matrouh": "مطروح", 
    "Luxor": "الأقصر", "Qena": "قنا", "North Sinai": "شمال سيناء", "Sohag": "سوهاج",

    # Cities
    "15 May": "15 مايو", "Abaseya": "العباسية", "Abou El Feda": "أبو الفدا", "Abu Talat": "أبو تلات",
    "Aghouza": "العجوزة", "Ain Shams": "عين شمس", "Al Rehab": "الرحاب", "Almazah": "ألماظة",
    "Amiriya": "الأميرية", "Andalos": "الأندلس", "Azzam": "عزام", "Badr City": "مدينة بدر",
    "Basateen": "البساتين", "Bolkly": "بولكلي", "Borg El Arab": "برج العرب", "Boulaq": "بولاق",
    "Camp Caesar": "كامب شيزار", "Cleopatra": "كليوباترا", "Corniche": "الكورنيش", "Dar El Salam": "دار السلام",
    "Dokki": "الدقي", "Downtown Cairo": "وسط البلد", "El Haram": "الهرم", "El Hawamdeya": "الحوامدية",
    "El Katameya": "القطامية", "El Maadi": "المعادي", "El Marg": "المرج", "El Masara": "المعصرة",
    "El Mokattam": "المقطم", "El Moqattam": "المقطم", "El Nozha": "النزهة", "El Qobbah": "القبة",
    "El Rehab": "الرحاب", "El Rowad": "الرواد", "El Shaab": "الشعب", "El Shorouk": "الشروق",
    "El Tagamoaa El Khames": "التجمع الخامس", "El Tagamoaa El Tani": "التجمع الثاني",
    "El Tagamoaa El Talet": "التجمع الثالث", "El Tagamoaa El Awal": "التجمع الأول",
    "El Talbeya": "الطالبية", "El Zawya El Hamra": "الزاوية الحمراء", "Ezbet El Haggana": "عزبة الهجانة",
    "Faisal": "فيصل", "Garden City": "جاردن سيتي", "Giza Square": "ميدان الجيزة",
    "Hadaeq El Ahram": "حدائق الأهرام", "Hadaeq El Maadi": "حدائق المعادي", "Hadaeq El Qobbah": "حدائق القبة",
    "Haram": "الهرم", "Heliopolis": "مصر الجديدة", "Helwan": "حلوان", "Imbaba": "إمبابة",
    "Katameya": "القطامية", "Maadi": "المعادي", "Madinaty": "مدينتي", "Manial": "المنيل",
    "Manshiyat Naser": "منشية ناصر", "Matareya": "المطرية", "Mokattam": "المقطم", "Mohandeseen": "المهندسين",
    "Nasr City": "مدينة نصر", "New Cairo": "القاهرة الجديدة", "New Capital": "العاصمة الإدارية",
    "New Heliopolis": "هيليوبوليس الجديدة", "New Nuzha": "النزهة الجديدة", "Obour City": "مدينة العبور",
    "Qalyub": "قليوب", "Qasr El Nil": "قصر النيل", "Rod El Farag": "روض الفرج", "Sayeda Zeinab": "السيدة زينب",
    "Shoubra": "شبرا", "Shoubra El Kheima": "شبرا الخيمة", "Smart Village": "القرية الذكية",
    "Zamalek": "الزمالك", "Zeitoun": "الزيتون", "6th of October": "السادس من أكتوبر",
    "Abu Rawash": "أبو رواش", "Agouza": "العجوزة", "Al Ayayat": "العياط", "Al Badrashin": "البدرشين",
    "Al Haram": "الهرم", "Al Hawamdeya": "الحوامدية", "Al Wahat Al Baharia": "الواحات البحرية",
    "Awsim": "أوسيم", "Bulaq El Dakrour": "بولاق الدكرور", "El Ayyat": "العياط", "El Badrashin": "البدرشين",
    "El Omraniya": "العمرانية", "El Saff": "الصف", "El Wahat El Bahariya": "الواحات البحرية",
    "Kerdasa": "كرداسة", "Omrania": "العمرانية", "Ousim": "أوسيم", "Saf": "الصف", "Sheikh Zayed": "الشيخ زايد",
    # Alexandria
    "Abu Qir": "أبو قير", "Agami": "العجمي", "Al Amriya": "العامرية", "Al Attarin": "العطارين",
    "Al Dekheila": "الدخيلة", "Al Gomrok": "الجمرك", "Al Labban": "اللبان", "Al Manshiyah": "المنشية",
    "Al Montazah": "المنتزه", "Al Raml": "الرمل", "Amreya": "العامرية", "Anfoushi": "الأنفوشي",
    "Asafra": "العصافرة", "Attarine": "العطارين", "Bacchus": "باكوس", "Camp Caesar": "كامب شيزار",
    "Cleopatra": "كليوباترا", "Dekheila": "الدخيلة", "El Agami": "العجمي", "El Amriya": "العامرية",
    "El Attarin": "العطارين", "El Dekheila": "الدخيلة", "El Gomrok": "الجمرك", "El Labban": "اللبان",
    "El Manshiyah": "المنشية", "El Montazah": "المنتزه", "El Raml": "الرمل", "Fleming": "فلمينج",
    "Glim": "جليم", "Gomrok": "الجمرك", "Kafr Abdou": "كفر عبده", "Karmouz": "كرموز",
    "Kom El Dikka": "كوم الدكة", "Labban": "اللبان", "Louran": "لوران", "Maamoura": "المعمورة",
    "Mandara": "المندرة", "Miami": "ميامي", "Minyet El Bassal": "مينا البصل", "Moharam Bek": "محرم بك",
    "Montaza": "المنتزه", "Raml": "الرمل", "Roushdy": "رشدي", "San Stefano": "سان ستيفانو",
    "Shatby": "الشاطبي", "Sidi Beshr": "سيدي بشر", "Sidi Gaber": "سيدي جابر", "Smouha": "سموحة",
    "Sporting": "سبورتنج", "Stanley": "ستانلي", "Zezenia": "زيزينيا",
    # Dakahlia
    "Aga": "أجا", "Bani Ebeid": "بني عبيد", "Belqas": "بلقاس", "Dakarneh": "دكرنس", "Dekernes": "دكرنس",
    "El Gamaliya": "الجمالية", "El Kurdi": "الكردي", "El Manzala": "المنزلة", "El Matareya": "المطرية",
    "El Senbellawein": "السنبلاوين", "Gamalia": "الجمالية", "Gohina": "جهينة", "Kurdi": "الكردي",
    "Mahmoudia": "المحمودية", "Manzala": "المنزلة", "Matareya": "المطرية", "Mansoura": "المنصورة",
    "Minya El Nasr": "منية النصر", "Mit Ghamr": "ميت غمر", "Mit Salsil": "ميت سلسيل", "Nabaroh": "نبروه",
    "Senbellawein": "السنبلاوين", "Sherbin": "شربين", "Shorouk": "الشروق", "Talkha": "طلخا", "Zaqaziq": "الزقازيق",
    # Red Sea
    "Al Qusair": "القصير", "El Gouna": "الجونة", "El Qusair": "القصير", "Halayeb": "حلايب",
    "Hurghada": "الغردقة", "Marsa Alam": "مرسى علم", "Port Ghalib": "بورت غالب", "Ras Gharib": "رأس غارب",
    "Safaga": "سفاجا", "Shalateen": "شلاتين", "Soma Bay": "سوما باي",
    # Beheira
    "Abu El Matamir": "أبو المطامير", "Abu Hummus": "أبو حمص", "Badr": "بدر", "Damanhour": "دمنهور",
    "Edku": "إدكو", "El Delengat": "الدلنجات", "El Mahmoudiya": "المحمودية", "El Natroun": "وادي النطرون",
    "El Rahmaniya": "الرحمانية", "Hosh Essa": "حوش عيسى", "Itay El Barud": "إيتاي البارود",
    "Kafr El Dawwar": "كفر الدوار", "Kom Hamada": "كوم حمادة", "Nubariya": "النوبارية",
    "Rashid (Rosetta)": "رشيد", "Rosetta": "رشيد", "Shubrakhit": "شبراخيت", "Wadi El Natrun": "وادي النطرون",
    # Fayoum
    "Abshway": "إبشواي", "Etsa": "إطسا", "Fayoum": "الفيوم", "Itsa": "إطسا", "Senoress": "سنورس",
    "Sinnuris": "سنورس", "Tamiya": "طامية", "Yousef El Seddik": "يوسف الصديق",
    # Gharbia
    "Basyoun": "بسيون", "El Mahalla El Kubra": "المحلة الكبرى", "Kafr El Zayat": "كفر الزيات",
    "Kotour": "قطور", "Qutour": "قطور", "Samanoud": "سمنود", "Santa": "السنطة", "Tanta": "طنطا", "Zefta": "زفتى",
    # Ismailia
    "Abu Suwir": "أبو صوير", "El Qantara El Gharbiya": "القنطرة غرب", "El Qantara El Sharqiya": "القنطرة شرق",
    "Fayed": "فايد", "Ismailia": "الإسماعيلية", "Kasassine": "القصاصين", "Qantara Gharb": "القنطرة غرب",
    "Qantara Sharq": "القنطرة شرق", "Tall El Kebir": "التبل الكبير",
    # Menofia
    "Ashmoun": "أشمون", "Birket El Sab": "بركة السبع", "El Bagour": "الباجور", "El Shohada": "الشهداء",
    "Menouf": "منوف", "Quesna": "قويسنا", "Sadat City": "مدينة السادات", "Shibin El Kom": "شبين الكوم",
    "Tala": "تلا", "Tersa": "طرسيا",
    # Minya
    "Abu Qurqas": "أبو قرقاص", "Beni Mazar": "بني مزار", "Deir Mawas": "دير مواس", "El Idwa": "العدوة",
    "Maghagha": "مغاغة", "Mallawi": "ملوي", "Mataay": "مطاي", "Minya": "المنيا", "Samalut": "سمالوط",
    # Qalyubia
    "Abu Zaabal": "أبو زعبل", "Banha": "بنها", "El Kanater El Khayreya": "القناطر الخيرية",
    "El Khanka": "الخانكة", "El Obour": "العبور", "Kafr Shukr": "كفر شكر", "Khanka": "الخانكة",
    "Qanater Khayriya": "القناطر الخيرية", "Shibin El Qanater": "شبين القناطر", "Tukh": "طوخ",
    # New Valley
    "Balat": "بلاط", "Baris": "باريس", "Dakhla": "الداخلة", "El Dakhla": "الداخلة",
    "El Farafra": "الفرافرة", "El Kharga": "الخارجة", "Farafra": "الفرافرة", "Kharga": "الخارجة",
    "Mut": "موط", "Paris": "باريس",
    # Suez
    "Al Arbaeen": "الأربعين", "Al Ganayen": "الجناين", "Arbaeen": "الأربعين", "Ataqah": "عتاقة",
    "El Ganayen": "الجناين", "Suez": "السويس", "Zaitiyyah": "الزيتية",
    # Aswan
    "Abu Simbel": "أبو سمبل", "Aswan": "أسوان", "Daraw": "دراو", "Edfu": "إدفو",
    "Kalabsha": "كلابشة", "Kom Ombo": "كوم أمبو", "Nasr Al Nuba": "نصر النوبة", "Sebaiya": "السباعية",
    # Assiut
    "Abnub": "أبنوب", "Abu Tig": "أبو تيج", "Assiut": "أسيوط", "Badari": "البداري",
    "Dairut": "ديروط", "El Badari": "البداري", "El Fateh": "الفتح", "El Ghanayem": "الغنايم",
    "El Qusiya": "القوصية", "Manfalut": "منفلوط", "Sahel Selim": "ساحل سليم", "Sodfa": "صدفا",
    # Beni Suef
    "Al Fashn": "الفشن", "Al Wasta": "الواسطى", "Beni Suef": "بني سويف", "Biba": "ببا",
    "Ehnasia": "إهناسيا", "Ihnasiya": "إهناسيا", "Nasser": "ناصر", "Samasta": "سمسطا", "Wasta": "الواسطى",
    # Port Said
    "Al Dawahi": "الضواحي", "Al Manakh": "المناخ", "Al Zohour": "الزهور", "Bourfouad": "بورفؤاد",
    "Dawahy": "الضواحي", "East Port Said": "شرق بورسعيد", "El Dawahy": "الضواحي", "El Manakh": "المناخ",
    "El Sharq": "الشرق", "El Zohour": "الزهور", "Port Fouad": "بورفؤاد", "Port Said": "بورسعيد",
    "South Port Said": "جنوب بورسعيد", "Zohour": "الزهور",
    # Damietta
    "Damietta": "دمياط", "El Zarqa": "الزرقا", "ESirw": "السرو", "Faraskour": "فارسكور",
    "Kafr El Battikh": "كفر البطيخ", "Kafr Saad": "كفر سعد", "New Damietta": "دمياط الجديدة",
    "Ras El Bar": "رأس البر", "Zarkah": "الزرقا",
    # Sharkia
    "10th of Ramadan": "العاشر من رمضان", "Abu Hammad": "أبو حماد", "Abu Kebir": "أبو كبير",
    "Al Husseiniya": "الحسينية", "Al Qenayat": "القنايات", "Awlad Saqr": "أولاد صقر",
    "Belbeis": "بلبيس", "Diyarb Negm": "ديرب نجم", "El Ibrahimiya": "الإبراهيمية",
    "El Qurein": "القرين", "Faqous": "فاقوس", "Husseiniya": "الحسينية", "Ibrahimiya": "الإبراهيمية",
    "Kafr Saqr": "كفر صقر", "Mashtoul El Souq": "مشتول السوق", "Minya El Qamh": "منيا القمح",
    "Qenayat": "القنايات", "Qurein": "القرين", "Zagazig": "الزقازيق",
    # South Sinai
    "Abu Radis": "أبو رديس", "Abu Zenima": "أبو زنيمة", "Dahab": "دهب", "El Tor": "الطور",
    "Nuweiba": "نويبع", "Ras Sedr": "رأس سدر", "Ras Sudr": "رأس سدر", "Saint Catherine": "سانت كاترين",
    "Sharm El Sheikh": "شرم الشيخ", "Taba": "طابا", "Tor Sinai": "طور سيناء",
    # Kafr El Sheikh
    "Balteem": "بلطيم", "Bella": "بيلا", "Biyala": "بيلا", "Desouk": "دسوق", "Fouah": "فوه",
    "Hamoul": "الحامول", "Kafr El Sheikh": "كفر الشيخ", "Metobas": "مطوبس", "Motobas": "مطوبس",
    "Qallin": "قلين", "Riyadh": "الرياض", "Sidi Salem": "سيدي سالم", "Sporting": "سبورتنج",
    # Matrouh
    "Dabaa": "الضبعة", "El Alamein": "العلمين", "El Dabaa": "الضبعة", "El Hamam": "الحمام",
    "El Negaila": "النجيلة", "Marsa Matrouh": "مرسى مطروح", "Matrouh": "مطروح", "Negaila": "النجيلة",
    "Salum": "السلوم", "Sidi Barrani": "سيدي براني", "Siwa": "سيوة",
    # Luxor
    "Al Bayadiya": "البياضية", "Al Qarnah": "القرنة", "Al Tod": "الطود", "Armant": "أرمنت",
    "Esna": "إسنا", "Karnak": "الكرنك", "Luxor": "الأقصر", "Tiba": "طيبة",
    # Qena
    "Abu Tesht": "أبو تشت", "Deshna": "دشنا", "El Waqf": "الوقف", "Farshut": "فرشوط",
    "Nagaa Hammadi": "نجع حمادي", "Naqada": "نقادة", "Qena": "قنا", "Qift": "قفط", "Qous": "قوص",
    # North Sinai
    "Arish": "العريش", "Bir al-Abed": "بئر العبد", "El Arish": "العريش", "El Hasana": "الحسنة",
    "Hassana": "الحسنة", "Nakhl": "نخل", "Rafah": "رفح", "Sheikh Zuweid": "الشيخ زويد",
    # Sohag
    "Akhmim": "أخميم", "Al Balyana": "البلينا", "Awlad Toq Sharq": "أولاد طوق شرق", "Dar El Salam": "دار السلام",
    "El Maragha": "المراغة", "El Monsha": "المنشأة", "El Usayrat": "العسيرات", "Girga": "جرجا",
    "Juhayna": "جهينة", "Sakulta": "ساقلتة", "Sohag": "سوهاج", "Tahta": "طهطا", "Tima": "طما",
    
    # Defaults and ui
    "Select a State": "اختر المحافظة",
    "Select a City": "اختر المدينة",
    "Select a State first": "اختر المحافظة أولاً",
    "State / Governorate": "المحافظة",
    "City": "المدينة"
}

po_path = "locale/ar/LC_MESSAGES/django.po"

with open(po_path, 'r', encoding='utf-8') as f:
    po_content = f.read()

lines = po_content.splitlines()
out_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    out_lines.append(line)
    if line.startswith('msgid '):
        match = re.search(r'^msgid "(.*)"$', line)
        if match:
            msgid = match.group(1)
            if i + 1 < len(lines) and lines[i+1].startswith('msgstr ""'):
                if msgid in translations:
                    out_lines.append(f'msgstr "{translations[msgid]}"')
                    i += 2
                    continue
    i += 1

with open(po_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(out_lines) + '\n')
print("Successfully updated PO file.")
