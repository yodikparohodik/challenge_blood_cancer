Ниже — проверенные открытые источники размеченных микроскопических сканов крови с онкологическими проявлениями (лейкемии, множественная миелома, циркулирующие опухолевые клетки) + контрольные датасеты нормальных клеток.

## Онкогематология: размеченные датасеты

| Источник | Заболевание | Описание и объём | Разметка | Лицензия | Ссылка |
|---|---|---|---|---|---|
| **C-NMC 2019** (ISBI-челлендж) | Острый лимфобластный лейкоз (ALL) | ~10 661 изображение одиночных клеток [[4]] | Бинарная: злокачественные B-лимфобласты vs нормальные B-предшественники [[5]] | CC BY (TCIA) / условия Kaggle | TCIA [[5]], Kaggle [[4]] |
| **ALL image dataset** (Kaggle) | ALL | 3 256 изображений мазков периферической крови (PBS), 89 пациентов [[1]] | Benign vs malignant + 3 подтипа злокачественных клеток [[17]] | Условия Kaggle | kaggle.com/datasets/mehradaria/leukemia [[1]] |
| **Leukemia Classification** (Kaggle) | ALL | 15 135 изображений, 118 пациентов [[6]] | 2 класса: normal / ALL | Условия Kaggle | kaggle.com/datasets/andrewmvd/leukemia-classification [[6]] |
| **ALL-IDB** (v1/v2) | ALL | ALL-IDB1: 108 полей зрения (~39 000 элементов крови, лимфоциты помечены) [[7]]; ALL-IDB2: 260 одиночных клеток [[18]] | Маски/метки лимфоцитов для сегментации и классификации [[14]] | Бесплатно для исследований [[34]] | scotti.di.unimi.it/all [[7]]; зеркало IEEE DataPort [[16]] |
| **AML-Cytomorphology_LMU** (TCIA) | Острый миелоидный лейкоз (AML) | 18 365 экспертно размеченных одиночных клеток, 100 пациентов [[19]] | Экспертные классовые метки клеток | CC BY (стандарт TCIA) | cancerimagingarchive.net/collection/aml-cytomorphology_lmu [[19]] |
| **AML-Cytomorphology_MLL_Helmholtz** (TCIA) | AML | Мазки периферической крови, 13,3 ГБ [[21]] | Морфологическая разметка AML-клеток | CC BY (TCIA) | cancerimagingarchive.net/collection/aml-cytomorphology_mll_helmholtz [[21]] |
| **Multi-domain Leukemia Dataset** | ALL, AML, CLL, CML | Мультидоменный набор по 4 типам лейкозов [[25]] | Классовые метки типов лейкоза | См. arXiv | arXiv:2405.10803 [[25]] |
| **Leukemia PBF (sparse annotations, 2025)** | ALL/AML/CLL/CML/APML | 48 плёнок периферической крови: 18 ALL, 22 AML, 2 CLL, 4 CML, 2 APML [[33]] | Разреженные метки по плёнкам (weakly-supervised) | См. статью | arXiv:2504.02602 [[33]] |
| **MiMM_SBILab** (TCIA) | Множественная миелома (MM) | Микроскопия аспиратов костного мозга пациентов с MM [[49]] | Клеточные изображения MM | CC BY (TCIA) | cancerimagingarchive.net/collection/mimm_sbilab [[49]] |
| **SegPC-2021** | MM | Крупнейший публичный датасет сегментации плазматических клеток при MM [[52]] | Пиксельные маски ядра и цитоплазмы плазмоцитов [[48]] | Research use (челлендж) | репозиторий челленджа / ScienceDirect [[48]] |
| **PCMMD** (2025) | MM | >5 000 изображений плазматических и неплазматических клеток с клиническими данными пациентов [[47]] | Экспертные метки plasma / non-plasma [[51]] | CC BY (Nature Sci Data) | nature.com/articles/s41597-025-04459-1 [[47]]; репозиторий LabIA-UFBA [[50]] |
| **CTC-датасеты (циркулирующие опухолевые клетки)** | Метастатические солидные опухоли | Публичных наборов мало, в основном культуральные клеточные линии [[38]]; есть набор stained-изображений с bounding box [[37]] и FISH-изображения CTC для сегментации [[43]] | Bounding box / маски CTC | Различается по наборам | см. обзоры [[37]], [[43]] |

## Контроль: нормальные клетки крови (для обучения «норма vs опухоль»)

| Источник | Объём | Разметка | Лицензия | Ссылка |
|---|---|---|---|---|
| **PBC** (Peripheral Blood Cells) | 17 092 изображения, 8 классов нормальных клеток, 360×363 JPG [[61]] | Экспертная разметка патологов | CC BY 4.0 [[36]] | Mendeley Data snkd93bnjr [[61]] |
| **BloodMNIST** (MedMNIST) | Те же 17 092 изображения, стандартизированные (npz, 28×28…224) [[67]] | 8 классов | CC BY 4.0 (наследуется от PBC) | medmnist.com [[66]] |
| **Raabin-WBC** | ~40 000 лейкоцитов, 5 классов + артефакты [[59]] | Классы + координаты клеток | Free access [[58]] | raabindata.com [[65]] |
| **Large expert-annotated single-cell PB dataset (2025)** | >40 000 одиночных клеток — крупнейший публичный экспертный набор [[28]] | Экспертные классовые метки | CC BY (Nature Sci Data) | nature.com/articles/s41597-025-06223-x [[28]] |
| **TXL-PBC / BCCD-семейство** | 1 260 изображений, 18 143 bounding box (WBC/RBC/platelets) [[57]] | Детекционные рамки | См. репозиторий | arXiv:2407.13214 [[63]] |

## Практические замечания

1. **Оптимальные стартовые связки:** для «фото клетки → лейкоз/норма» берите **C-NMC 2019** (ALL) + **PBC/BloodMNIST** как контроль; для AML — **AML-Cytomorphology_LMU/Helmholtz**; для миеломы — **SegPC-2021/PCMMD**.
2. **ALL-IDB** мал, но идеален для валидации и сегментации лейкоцитов; **Kaggle-наборы** (3 256 и 15 135 изображений) — для предобучения классификатора.
3. **CTC-изображения** — самое слабое место: публичные наборы ограничены и в основном на клеточных линиях [[38]]; для солидных опухолей чаще используют не морфологию, а молекулярные профили CTC.
4. Обзор по датасетам для лейкозов с сравнением — PMC-обзор «Artificial intelligence and datasets for leukemia diagnosis» [[3]].
5. Код загрузки/аугментации — тот же, что в прошлом ответе (блок A: Albumentations для 2D-классификации); для TCIA-коллекций (AML, MiMM) данные уже в виде отдельных клеточных изображений, DICOM не нужен.

Если нужно, соберу готовый пайплайн «C-NMC + PBC → EfficientNet/ViT» с метриками и балансом классов или таблицу по подтипам ALL/AML (FAB/WHO-классы) из LMU/Helmholtz.


Вот несколько авторитетных источников с публично доступными размеченными наборами данных сканов мазков крови, включающими раковые (лейкозные) клетки и текстовыми описаниями/аннотациями:

## Крупные экспертно-размеченные датасеты (периферическая кровь)

### 1. MLL23 / Helmholtz Munich dataset (>40 000 клеток, 18 классов)
- **Что внутри:** >40 000 отдельных клеток из мазков периферической крови, размеченных экспертами-цитоморфологами Munich Leukemia Laboratory на 18 морфологических классов (миелобласты, промиелоциты, атипичные промиелоциты, нейтрофилы, эозинофилы, базофилы, моноциты, лимфоциты, атипичные/неопластические лимфоциты, волосатые клетки, нормобласты и др.). [pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC12606192/)
- **Где скачать:** Zenodo (DOI: 10.5281/zenodo.14277609). [pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC12606192/)
- **Описание и статья:** Scientific Data, 2025 — подробное описание сбора, окраски (Паппенгейм), сканирования (Metafer), контроля качества и схемы аннотаций. [pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC12606192/)

### 2. AML-Cytomorphology_LMU (TCIA) — ~18 365 клеток, ОМЛ и контроль
- **Что внутри:** 18 365 экспертно-размеченных изображений отдельных клеток из мазков периферической крови: 100 пациентов с острым миелоидным лейкозом (ОМЛ) и 100 без гематологических злокачественных заболеваний. Классификация по стандартной морфологической схеме. [cancerimagingarchive](https://www.cancerimagingarchive.net/collection/aml-cytomorphology_lmu/)
- **Где скачать:** The Cancer Imaging Archive (TCIA), коллекция [AML-Cytomorphology_LMU](https://www.cancerimagingarchive.net/collection/aml-cytomorphology_lmu/). [cancerimagingarchive](https://www.cancerimagingarchive.net/collection/aml-cytomorphology_lmu/)
- **Форматы:** TIFF (изображения), DAT/ZIP (аннотации), TXT (сокращения классов). [cancerimagingarchive](https://www.cancerimagingarchive.net/collection/aml-cytomorphology_lmu/)
- **Статья-источник:** Matek et al., Nature Machine Intelligence, 2019. [cancerimagingarchive](https://www.cancerimagingarchive.net/collection/aml-cytomorphology_lmu/)

### 3. C-NMC 2019 (ISBI 2019 ALL Challenge) — нормальные vs лейкозные B-лимфобласты
- **Что внутри:** Набор для классификации нормальных прекурсоров B-лимфоидной линии и лейкозных B-лимфобластов (ALL). В сумме >15 000 изображений клеток (обучающая + тестовые фазы), с метками «норма/рак». [cancerimagingarchive](https://www.cancerimagingarchive.net/wp-content/uploads/CNMC_readme.pdf)
- **Где скачать:** TCIA, коллекция [C-NMC 2019](https://www.cancerimagingarchive.net/collection/c-nmc-2019/). [cancerimagingarchive](https://www.cancerimagingarchive.net/collection/c-nmc-2019/)
- **Форматы:** Изображения (BMP/PDF), метки (CSV), README с описанием. [cancerimagingarchive](https://www.cancerimagingarchive.net/collection/c-nmc-2019/)
- **Контекст:** Использовался в конкурсе IEEE ISBI 2019 по классификации клеток при B-ОЛЛ. [cancerimagingarchive](https://www.cancerimagingarchive.net/collection/c-nmc-2019/)

## Дополнительные наборы и обзоры

- **AML-Cytomorphology_MLL_Helmholtz** (TCIA) — морфологический датасет белых клеток при четырёх генетических подтипах ОМЛ и контроле. [cancerimagingarchive](https://www.cancerimagingarchive.net/collection/aml-cytomorphology_mll_helmholtz/)
- **Bone-Marrow-Cytomorphology_MLL_Helmholtz_Fraunhofer** (TCIA) — экспертно-размеченные изображения цитологии костного мозга при гематологических злокачественных заболеваниях (если интересны также костномозговые препараты). [cancerimagingarchive](https://www.cancerimagingarchive.net/collection/bone-marrow-cytomorphology_mll_helmholtz_fraunhofer/)
- **Обзор датасетов для диагностики лейкоза:** статья 2025 г. в PMC с детальным анализом публичных бенчмарков и ссылками на наборы (включая вышеупомянутые). [pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC12681519/)

## Как выбирать
- Если нужны **множественные типы клеток и богатая морфологическая таксономия** — берите MLL23 (Zenodo). [pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC12606192/)
- Если фокус на **ОМЛ и сопоставление с нормой** — AML-Cytomorphology_LMU (TCIA). [cancerimagingarchive](https://www.cancerimagingarchive.net/collection/aml-cytomorphology_lmu/)
- Если нужна задача **бинарной классификации «норма vs лейкоз» (ALL)** — C-NMC 2019 (TCIA). [cancerimagingarchive](https://www.cancerimagingarchive.net/collection/c-nmc-2019/)


Distinguishing cell types in peripheral blood smears is critical for differential diagnosis of blood diseases, such as leukemia subtypes. Machine learning can assist physicians in automating cell classification. Still, the generalizability of deep neural networks remains challenging, particularly concerning domain shifts emerging from variations in, e.g., patient cohorts, staining protocols, scanning procedures, and image resolution. We introduce a large, publicly available, fully annotated peripheral blood dataset comprising over 40,000 single-cell images classified into 18 classes by cytomorphology experts.

In the group of lymphoid cells, there are mature ‘typical lymphocytes’ (number of single-cell images = 5,532) and atypical lymphocytes like plasma cells (1,658), large granular lymphocytes (1,849), reactive lymphocytes (33), hairy cells (3,265) and other neoplastic lymphocytes (180), as well as smudge cells (988). In comparison, the group of myeloid cells is divided into mature cells like band neutrophil granulocytes (687), segmented neutrophil granulocytes (7,170), eosinophil granulocytes (2,448), basophil granulocytes (616), monocytes (2510), and immature cells like myeloblasts (8,606), metamyelocytes (483), promyelocytes (745), myelocytes (747), and atypical promyelocytes (2,033). Lastly, normoblasts (2071) are also present in the dataset. The cell types occur with specific frequencies in the peripheral blood in healthy and pathological patients.

| Набор                                          | Тип материала (кровь/костный мозг) | Число изображений                           | Классы                                                   | Формат                                                            | Прямая ссылка на скачивание                                                                  | Лицензия                                       | DOI/статья                                                                         | Примеры классов (конкретные названия)                                                                                                                                                    |
| ---------------------------------------------- | ---------------------------------- | ------------------------------------------- | -------------------------------------------------------- | ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ---------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| MLL23 (Helmholtz / Munich Leukemia Laboratory) | Периферическая кровь               | >40 000 одиночных клеток                    | 18 морфологических классов                               | ZIP-архивы по классам (изображения клеток)                        | https://zenodo.org/records/14277609                                                          | Open (Zenodo; данные открыты для исследований) | Scientific Data, 2025 (статья описывает набор MLL23) zenodo+1                      | myeloblast, promyelocyte, promyelocyte_atypical, neutrophil, eosinophil, basophil, monocyte, lymphocyte, lymphocyte_atypical, lymphocyte_neoplastic, hairy_cell, normoblast и др. zenodo |
| AML-Cytomorphology_LMU (TCIA)                  | Периферическая кровь               | 18 365 клеток                               | Стандартная цитоморфологическая схема для ОМЛ + контроль | TIFF (изображения), DAT/ZIP (аннотации), TXT (сокращения классов) | https://www.cancerimagingarchive.net/collection/aml-cytomorphology_lmu/ (IBM Aspera Connect) | CC BY 3.0 (TCIA; требуется цитирование)        | Matek et al., Nature Machine Intelligence, 2019; DOI: 10.7937/tcia.2019.36f5o9ld   | Классы по стандартной схеме цитоморфологии (миелоидные/лимфоидные линии, бласты и зрелые формы); сокращения перечислены в abbreviations.txt                                              |
| C-NMC 2019 (ISBI 2019 ALL Challenge)           | Периферическая кровь (мазки)       | 10 661 обучающих клеток (+ тестовые наборы) | 2 класса: ALL (рак) vs норма                             | BMP (изображения), CSV (метки), PDF (README)                      | https://www.cancerimagingarchive.net/collection/c-nmc-2019/ (IBM Aspera Connect)             | CC BY 3.0 (TCIA; требуется цитирование)        | Gupta et al., Medical Engineering & Physics, 2022; DOI: 10.7937/tcia.2019.dc64i46r | ALL (cancer, B-lymphoblast), Normal (B-lymphoid precursor)                                                                                                                               |


Ниже — источники, где **одновременно** есть: (1) фото мазков/клеток, (2) сегментация/разметка раковых (или патологических) клеток, и (3) текстовое описание (классы, метаданные, протокол).

## 1) AML-Cytomorphology_MLL_Helmholtz (TCIA) — ОМЛ, 4 генетических подтипа + контроль
- **Фото:** 81 214 изображений клеток (TIFF), 189 пациентов. [wiki.cancerimagingarchive](https://wiki.cancerimagingarchive.net/pages/viewpage.action?pageId=145753815)
- **Сегментация/разметка:** автоматическая детекция клеток на Metafer с порогом сегментации; далее отбор и сканирование отдельных WBC в 40x; аннотации по классам и пациенту. [wiki.cancerimagingarchive](https://wiki.cancerimagingarchive.net/pages/viewpage.action?pageId=145753815)
- **Текстовое описание:** подробное описание на странице TCIA (WHO 2022 классификация, 4 подтипа APL/NPM1/CBFB::MYH11/RUNX1::RUNX1T1, метаданные возраста/пола/анализов крови в .csv/.xls). [wiki.cancerimagingarchive](https://wiki.cancerimagingarchive.net/pages/viewpage.action?pageId=145753815)
- **Ссылка:** https://wiki.cancerimagingarchive.net/pages/viewpage.action?pageId=145753815 (доступ к данным через TCIA/Aspera). [wiki.cancerimagingarchive](https://wiki.cancerimagingarchive.net/pages/viewpage.action?pageId=145753815)

## 2) AML-Cytomorphology_LMU (TCIA) — ОМЛ, 18 365 клеток
- **Фото:** 18 365 одиночных клеток (TIFF).   
- **Сегментация/разметка:** экспертные аннотации классов для каждой клетки (повторные аннотации для оценки согласованности); файл `annotations.dat`.   
- **Текстовое описание:** `abbreviations.txt` (классы), README/статья Matek et al., Nat Mach Intell 2019 с описанием протокола и классов.   
- **Ссылка:** https://www.cancerimagingarchive.net/collection/aml-cytomorphology_lmu/ 

## 3) C-NMC 2019 (ISBI 2019 ALL Challenge) — ОЛЛ, «рак vs норма»
- **Фото:** 10 661 обучающих изображений клеток (BMP).   
- **Сегментация/разметка:** метки «ALL (cancer) / Normal» в CSV; изображения уже сегментированы на уровне отдельных клеток.   
- **Текстовое описание:** CNMC_readme.pdf и статья Gupta et al., Med Eng Phys 2022 (описание набора, классов, задачи).   
- **Ссылка:** https://www.cancerimagingarchive.net/collection/c-nmc-2019/ 

## 4) MLL23 (Zenodo) — периферическая кровь, 18 классов
- **Фото:** >40 000 одиночных клеток (ZIP по классам).   
- **Сегментация/разметка:** каждая папка/файл соответствует классу; аннотации встроены в структуру набора.   
- **Текстовое описание:** страница Zenodo и статья Scientific Data (2025) с описанием классов, окраски, сканирования и доменных сдвигов.   
- **Ссылка:** https://zenodo.org/records/14277609 

## 5) ALL_IDB1 / ALL_IDB2 — ОЛЛ, координаты поражённых клеток + маски
- **Фото:** ALL_IDB1 — 108 изображений мазков; ALL_IDB2 — 260 вырезок 257×257. [pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC12681519/table/tbl0002/)
- **Сегментация/разметка:** файлы координат (.xyc) с центрами поражённых лимфоцитов; по ним строятся бинарные маски для сегментации. [ijirt](https://ijirt.org/publishedpaper/IJIRT181047_PAPER.pdf)
- **Текстовое описание:** описания в статьях и таблицах обзоров (классы L1/L2/L3 B-ALL, протокол). [pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC12681519/table/tbl0002/)
- **Ссылка (обзор/таблица):** https://pmc.ncbi.nlm.nih.gov/articles/PMC12681519/table/tbl0002/ [pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC12681519/table/tbl0002/)

Если нужно, могу собрать минимальный «пакет» из 2–3 наборов, где лучше всего выражены все три компонента (фото + явная сегментация + развёрнутое текстовое описание) и дать прямые ссылки на файлы масок/аннотаций.

Вот минимальный «пакет» из трёх наборов, где одновременно хорошо выражены **фото**, **явная сегментация/разметка раковых клеток** и **развёрнутое текстовое описание**. Для каждого — прямые ссылки на файлы аннотаций/масок.

| Набор | Фото | Сегментация/разметка раковых клеток | Текстовое описание (классы, протокол, метаданные) | Прямые ссылки на аннотации/маски |
|---|---|---|---|---|
| **AML-Cytomorphology_MLL_Helmholtz** (TCIA) — 4 генетических подтипа ОМЛ + контроль | 81 214 изображений клеток (TIFF), 189 пациентов.  | Автоматическая детекция/сегментация клеток на Metafer; отбор и сканирование отдельных WBC; аннотации по классам и пациенту.  | WHO 2022 классификация, 4 подтипа (APL/NPM1/CBFB::MYH11/RUNX1::RUNX1T1), метаданные (возраст, пол, анализы крови) в .csv/.xls.  | Коллекция TCIA: https://wiki.cancerimagingarchive.net/pages/viewpage.action?pageId=145753815 (доступ через TCIA/Aspera; в составе — файлы аннотаций и метаданных).  |
| **C-NMC 2019** (ISBI 2019 ALL Challenge) — ОЛЛ, бинарная задача | 10 661 обучающих изображений клеток (BMP).  | Метки «ALL (cancer) / Normal» в CSV; изображения уже сегментированы на уровне отдельных клеток.  | CNMC_readme.pdf и статья Gupta et al., Med Eng Phys 2022 (описание набора, классов, задачи).  | TCIA: https://www.cancerimagingarchive.net/collection/c-nmc-2019/ (пакет ~10.44 ГБ, IBM Aspera Connect; внутри — BMP + CSV-метки).  |
| **ALL-IDB1** (Acute Lymphoblastic Leukemia Image Database) — ОЛЛ | 108 изображений мазков (JPG 2592×1944), ~39 000 элементов крови.  [scotti.di.unimi](https://scotti.di.unimi.it/all/) | Файлы `.xyc` с координатами центроидов бластов; по ним строятся бинарные маски для сегментации.  [ieee-dataport](https://ieee-dataport.org/documents/all-idb-acute-lymphoblastic-leukaemia-international-database) | Подробное описание на сайте проекта (FAB-классы L1/L2/L3, правила именования ImXXX_Y.jpg, метрики оценки).  [scotti.di.unimi](https://scotti.di.unimi.it/all/) | Официальный сайт: https://scotti.di.unimi.it/all/ (запрос доступа по email; аннотации — файлы `ImXXX_Y.xyc` в папке `xyc/`).  [scotti.di.unimi](https://scotti.di.unimi.it/all/)<br>IEEE DataPort (описание/инструкции): https://ieee-dataport.org/documents/all-idb-acute-lymphoblastic-leukaemia-international-database  [ieee-dataport](https://ieee-dataport.org/documents/all-idb-acute-lymphoblastic-leukaemia-international-database) |

### Почему именно эти три
- **AML-Cytomorphology_MLL_Helmholtz** — максимальный объём, явная сегментация клеток, богатые метаданные и текстовое описание подтипов ОМЛ.   
- **C-NMC 2019** — чистая бинарная задача «рак vs норма», готовые CSV-метки и развёрнутый README/статья.   
- **ALL-IDB1** — классический набор с координатами бластов (.xyc), по которым легко получить маски, и очень детальное текстовое описание протокола и классов. [scotti.di.unimi](https://scotti.di.unimi.it/all/)

Если нужно, могу дать пошаговый рецепт: как из `.xyc` (ALL-IDB1) сделать бинарные маски и как сопоставить CSV-метки C-NMC с изображениями для быстрой загрузки в пайплайн обучения.


