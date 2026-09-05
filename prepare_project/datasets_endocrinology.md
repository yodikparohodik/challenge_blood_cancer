Ниже — сводная таблица открытых источников, отсортированная по органам эндокринной системы (щитовидная железа → паращитовидные → надпочечники → гипофиз → поджелудочная/НЭО).

| Источник | Описание (орган / модальность) | Разметка для обучения | Лицензия | Ссылка | Объём | Направления исследований | Другие параметры |
|---|---|---|---|---|---|---|---|
| **TN5000** (Scientific Data, 2025) | Щитовидная железа, B-mode УЗИ; крупнейший открытый датасет с биопсийным подтверждением [[1]] | Да: маски узлов, класс benign/malignant, экспертные метки [[31]] | CC BY 4.0 [[101]] | Figshare 28455641 [[101]]; зеркала на Kaggle/HF [[109]] | 5 000 изображений [[31]] | Детекция, сегментация, классификация злокачественности | Золотой стандарт — биопсия [[102]] |
| **TN3K** | Щитовидная железа, УЗИ | Да: качественные маски узлов [[116]] | Open access, research/education [[111]] | GitHub TRFE-Net [[110]], HuggingFace [[116]] | 3 493 изображения, 2 421 пациент [[118]] | Сегментация узлов | Жёсткое train/test разбиение [[7]] |
| **
Ниже — сводная таблица открытых источников, отсортированная по органам эндокринной системы (щитовидная железа → паращитовидные → надпочечники → гипофиз → поджелудочная/НЭО).

| Источник | Описание (орган / модальность) | Разметка для обучения | Лицензия | Ссылка | Объём | Направления исследований | Другие параметры |
|---|---|---|---|---|---|---|---|
| **TN5000** (Scientific Data, 2025) | Щитовидная железа, B-mode УЗИ; крупнейший открытый датасет с биопсийным подтверждением [[1]] | Да: маски узлов, класс benign/malignant, экспертные метки [[31]] | CC BY 4.0 [[101]] | Figshare 28455641 [[101]]; зеркала на Kaggle/HF [[109]] | 5 000 изображений [[31]] | Детекция, сегментация, классификация злокачественности | Золотой стандарт — биопсия [[102]] |
| **TN3K** | Щитовидная железа, УЗИ | Да: качественные маски узлов [[116]] | Open access, research/education [[111]] | GitHub TRFE-Net [[110]], HuggingFace [[116]] | 3 493 изображения, 2 421 пациент [[118]] | Сегментация узлов | Жёсткое train/test разбиение [[7]] |
| **DDTI** (Колумбия, IDIME) | Щитовидная железа, УЗИ | Да: пиксельные маски + клинические описания [[15]] | Open access для науки [[4]] | Kaggle-зеркало [[4]] | 637 изображений [[6]] | Сегментация, классификация, TI-RADS-признаки | Один аппарат; в Kaggle-зеркале 99 случаев/134 изображения [[4]] |
| **TN-SCUI 2020** (MICCAI challenge) | Щитовидная железа, УЗИ | Да: маски + класс benign/malignant [[32]] | Research use, регистрация на челлендже | Zenodo 3715942 [[36]]; grand-challenge.org [[29]] | Train: 3 644 изображения (1 641 benign, 2 003 malignant) [[32]] | Сегментация + классификация | Есть лидерборд и эталонные решения |
| **Thyroid Ultrasound Cine-clip** (Stanford AIMI) | Щитовидная железа, УЗИ-видеоклипы | Да: сегментации радиологов, TI-RADS-дескрипторы, гистология [[152]] | Некоммерческая лицензия Stanford; коммерция — отдельно [[124]] | aimi.stanford.edu/datasets/thyroid-ultrasound-cine-clip [[119]] | 192 клипа, 167 пациентов с биопсией [[123]] | Сегментация, видео-анализ, TI-RADS | Биопсийное подтверждение [[125]] |
| **SegThy** (TUM) | Щитовидная железа и шея, УЗИ | Да: маски анатомии | CC BY [[9]] | cs.cit.tum.de/camp/segthy-dataset [[9]] | — | Сегментация железы/шеи | Подходит для анатомической локализации |
| **Figshare: thyroid nodules US + pathology** | Щитовидная железа, УЗИ | Да: диагноз, подтверждённый патоморфологией | CC BY 4.0 [[103]] | Figshare 26067475 [[103]] | — | Классификация с гистологическим «золотым стандартом» | Удобно для обучения «фото → диагноз» |
| **TCGA-THCA** | Щитовидная железа (карцинома), гистология WSI (H&E) + геномика | Слабая: диагноз, клинические и молекулярные данные (без пиксельных масок) | Open access (политика GDC/TCGA) | portal.gdc.cancer.gov/projects/TCGA-THCA [[94]]; TCIA [[93]] | 506 пациентов, ~500+ SVS-слайдов [[94]] | MIL-классификация слайдов, корреляция с геномикой, foundation-модели | Требует нарезки тайлов (OpenSlide/CLAM) |
| **PTC FNAC dataset** (IEEE DataPort) | Щитовидная железа, цитология (тонкоигольная аспирация) | Да: benign/malignant, готовые train/val/test [[49]] | Условия IEEE DataPort (research) | ieee-dataport.org/documents/papillary-thyroid-carcinoma-dataset [[49]] | — | Цитологическая классификация | Папиллярная карцинома |
| **Single-cell thyroid dataset** (2025) | Щитовидная железа, одиночные клетки | Да: экспертная разметка 3 419 клеток [[47]] | Open access (см. статью) | PMC12707618 [[47]] | 3 419 изображений клеток | Клеточная классификация | Редкий пример именно «клеточного» датасета |
| **Atlas Papanicolaou Society** | Щитовидная железа, цитология (FNA) | Нет (образовательный) | Образовательное использование | papsociety.org/image-atlas [[54]] | ~300 изображений | Обучение врачей, референс-изображения | Хорош для валидации/визуальной проверки |
| **Parathyroid US localization** (Mendeley) | Паращитовидные железы, УЗИ | Да: локализация нижних желёз [[154]] | Лицензия Mendeley Data (обычно CC BY 4.0) | data.mendeley.com/datasets/43fx6tx2xv [[154]] | Небольшой | Интраоперационная навигация, локализация | Публичных датасетов паращитовидных почти нет — это один из немногих |
| **ADRENAL-ACC-KI67-SEG** (TCIA) | Надпочечники, контрастная КТ | Да: 3D-сегментация опухоли + Ki-67 [[67]] | CC BY (стандарт TCIA) [[138]] | cancerimagingarchive.net/collection/adrenal-acc-ki67-seg [[66]] | 53 пациента с адренокортикальным раком [[67]] | Сегментация, прогноз пролиферации (Ki-67) | DICOM; есть зеркало на HuggingFace [[70]] |
| **Figshare Brain Tumor Dataset (Cheng)** | Гипофиз (в составе), CE-MRI T1 | Да: классовые метки (менингиома/глиома/аденома гипофиза) [[132]] | CC BY 4.0 [[129]] | figshare.com/articles/dataset/brain_tumor_dataset/1512427 [[129]] | 3 064 среза, 233 пациента (гипофиз — 930) [[132]] | Классификация опухолей мозга/гипофиза | Есть версия с масками — BRISC [[59]] |
| **Brain Tumor Classification MRI** (Kaggle) | Гипофиз (в составе), MRI | Да: 4 класса (глиома, менингиома, гипофиз, норма) [[58]] | Условия Kaggle (бесплатно для исследований) | kaggle.com/datasets/sartajbhuvaji/brain-tumor-classification-mri [[58]] | ~7 000 срезов | Классификация | Много готовых ноутбуков-бейзлайнов |
| **CTPRED-SUNITINIB-PANNET** (TCIA) | Поджелудочная, НЭО, КТ | Да: клинический ответ на сунитиниб [[84]] | CC BY (TCIA) [[138]] | cancerimagingarchive.net/collection/ctpred-sunitinib-pannet [[84]] | 11,85 ГБ DICOM [[84]] | Предикция ответа терапии при pNET | Редкий датасет именно НЭО |
| **pNETs CECT dataset** (2025) | Поджелудочная, НЭО, контрастная КТ | Да: аннотации под pNET [[85]] | См. статью/GitHub | arXiv:2501.17555 [[85]] | — | Сегментация/классификация pNET | Первый датасет, сфокусированный только на pNET |

**Дополнительно (агрегаторы и замечания):**
- Каталог открытых УЗИ-датасетов с фильтром по лицензии и анатомии: **Ultrasound Open Access Datasets** [[8]].
- Курируемый список медицинских датасетов (в т.ч. DDTI, TN3K, TG3K): GitHub **openmedlab/Awesome-Medical-Dataset** [[21]].
- Большинство коллекций TCIA распространяются под CC BY 4.0 с требованием цитирования [[138]]; данные TCGA/GDC открыты, но требуют соблюдения политики использования и цитирования.
- Слабое место эндокринологии — **паращитовидные железы**: публичных размеченных датасетов практически нет [[154]]; по гипофизу и надпочечникам данные есть в основном как «подкласс» в более крупных коллекциях.
- Для задач «фото → диагноз» по щитовидной железе оптимальная связка: **TN5000/TN3K** (УЗИ с биопсией) + fine-tune EfficientNet/ConvNeXt/ViT или УЗИ-foundation-модель; для гистологии — **TCGA-THCA** + foundation-модели патологии (UNI/CONCH/H-Optimus-0) с MIL.

Соберу недостающие детали по каждому датасету (классы, форматы, объёмы), затем дам полное раскрытие с кодом.

<function>
<invoke name="web_search">
<parameter name="queries">["TN5000 thyroid dataset figshare classes benign malignant annotation format", "TN3K dataset 1815 training 1678 test images size github", "DDTI thyroid database clinical descriptions echogenicity calcification margin", "TN-SCUI 2020 training dataset 3644 images masks format zenodo", "SegThy dataset ultrasound thyroid neck segmentation size"]</parameter=
</invoke>
<invoke name="web_search">
<parameter name="queries">["papillary thyroid carcinoma dataset IEEE DataPort FNAC images number", "Adrenal-ACC-Ki67-Seg TCIA patients clinical data", "CTPRED-SUNITINIB-PANNET sunitinib pancreatic neuroendocrine tumor patients", "pNET dataset arXiv 2501.17555 cases segmentation annotation", "Mendeley dataset ultrasound localization inferior parathyroid", "single-cell thyroid cancer image dataset 3419 images classes"]</parameter=
</invoke>
</function_calls>

<function_results>
[1] https://www.nature.com/articles/s41597-025-05757-4 "TN5000: An Ultrasound Image Dataset for Thyroid Nodule ..." · The dataset has 1135 benign images and 3865 malignant images. The images are of size 224 × 224 pixels and are saved in PNG format. The images ...
[2] https://pmc.ncbi.nlm.nih.gov/articles/PMC12357846/ "TN5000: An Ultrasound Image Dataset for Thyroid Nodule ..." · TN5000 consists of 5,000 B-mode US images, of which 1,135 are benign and 3,865 are malignant. In TN5000, all images were resized to 224 × 224 pixels ...
[3] https://figshare.com/s/cb6a67f17c04b29e7edd "TN5000: An Ultrasound Image Dataset for Thyroid Nodule ..." · TN5000 is available at: https://figshare.com/s/cb6a67f17c04b29e7edd. Dataset. ...
[4] https://springernature.figshare.com/articles/dataset/TN5000_An_Ultrasound_Image_Dataset_for_Thyroid_Nodule_Detection_and_Classification/28455641 "TN5000: An Ultrasound Image Dataset for Thyroid Nodule ..." · This paper proposes TN5000, which contains 5,000 B-mode ultrasound images of thyroid nodule, as well as complete annotations and biopsy confirmations ...
[5] https://huggingface.co/datasets/Johnyquest7/TN5000-thyroid-nodule-classification "Johnyquest7/TN5000-thyroid-nodule-classification" · TN5000 is a comprehensive open-access thyroid nodule ultrasound image dataset that contains 5,000 B-mode ultrasound images of thyroid nodule ... License: cc-by-4.0.
[6] https://pmc.ncbi.nlm.nih.gov/articles/PMC12357846/ "TN5000: An Ultrasound Image Dataset for Thyroid Nodule ..." · The annotation file is in COCO format, containing bounding box ... and mask information of each nodule ...
[7] https://github.com/haifangong/TRFE-Net-for-thyroid-nodule-segmentation "GitHub - haifangong/TRFE-Net-for-thyroid-nodule-segmentation" · TN3K: an open-access dataset containing 3493 thyroid nodule images with high-quality nodule masks labeling. ... The dataset is divided into training set (1815 ...
[8] https://huggingface.co/datasets/haifan-gong/TN3K "haifan-gong/TN3K" · TN3K is a comprehensive open-access thyroid nodule dataset containing 3,493 thyroid ultrasound images with high-quality annotations for both segmentation ...
[9] https://github.com/openmedlab/Awesome-Medical-Dataset/blob/main/resources/TN3K.md "Awesome-Medical-Dataset/resources/TN3K.md" · The TN3K dataset comprises 3493 ultrasound images from 2421 patients, captured between January 2016 and November 2019 ... The dataset is divided ...
[10] https://github.com/haifangong/TRFE-Net-for-thyroid-nodule-segmentation "GitHub - haifangong/TRFE-Net-for-thyroid-nodule-segmentation" · training set (1815 images) and test set (1678 images). ... Each image is resized to 352x352 pixels ...
[11] https://www.kaggle.com/datasets/tjahan/tn3k-thyroid-nodule-region-segmentation-dataset "TN3K: Thyroid nodule region segmentation dataset" · The dataset is divided into training set (1815 images) and test set (1678 images). Each image is resized to 352x352 pixels.
[12] https://www.kaggle.com/datasets/dasmehdixtr/ddti-thyroid-ultrasound-images "DDTI: Thyroid Ultrasound Images" · The digital database of Thyroid Ultrasound Images, is an open access resource for the scientific community. The database contains 99 cases and 134 images. ...
[13] https://pmc.ncbi.nlm.nih.gov/articles/PMC11354840/ "A Multitask Approach for Automated Detection and ..." · Digital Database Thyroid Image (DDTI): DDTI is a public, open access dataset from the IDIME Ultrasound Department, This dataset contains 480 ...
[14] https://www.researchgate.net/publication/275340525_An_open_access_thyroid_ultrasound_image_database "(PDF) An open access thyroid ultrasound image database" · The DDTI dataset [40] consists of 637 B-mode ultrasound images of the thyroid; each annotated at the pixel level. These images are accompanied ...
[15] https://github.com/openmedlab/Awesome-Medical-Dataset/blob/main/resources/DDTI.md "Awesome-Medical-Dataset/resources/DDTI.md" · The DDTI dataset contains 637 ultrasound thyroid images with pixel-level labels from a single device ... Each image is accompanied by a clinical description that ...
[16] https://tn-scui2020.grand-challenge.org/ "Home - Thyroid Nodule Segmentation and Classification ..." · The training set consists of 3644 images with png format (1641 benign cases and 2003 malignant cases) and the testing set consists of 1438 ...
[17] https://zenodo.org/records/3715942 "Thyroid Nodule Segmentation and Classification in Ultrasound ..." · This dataset contains the training and testing data of TN-SCUI 2020 challenge.
[18] https://miccai-sb.github.io/materials/mec2020/2020_MaJ.pdf "3 Steps Are All You Need to Achieve SOTA in ..." · The training set consists of 3644 images with png format (1641 benign cases and 2003 malignant cases) ... labels are saved in a csv file named "labels.csv" ...
[19] https://github.com/malavikabnd/QAT "GitHub - malavikabnd/QAT" · The TN-SCUI2020 dataset contains 3644 training images and 1438 testing images ... All images are in png format and resized to 240 x 240 pixels ...
[20] https://www.cs.cit.tum.de/en/camp/publications/segthy-dataset/ "SegThy Dataset - Chair of Computer Aided Medical Procedures" · The dataset comprises 2D ultrasound images and expert segmentations of thyroid glands, carotid arteries, jugular veins and other neck structures ...
[21] https://www.cs.cit.tum.de/en/camp/publications/segthy-dataset/ "SegThy Dataset" · SegThy contains 200 images from 100 subjects with pixel-wise annotations of 8 neck structures ...
[22] https://www.nature.com/articles/s41597-025-05757-4 "TN5000: An Ultrasound Image Dataset for Thyroid Nodule ..." · TN5000 contains annotations in COCO format for detection, and pixel masks for segmentation ...
[23] https://figshare.com/articles/dataset/An_ultrasonography_of_thyroid_nodules_dataset_with_pathological_diagnosis_annotation_for_deep_learning/26067475 "An ultrasonography of thyroid nodules dataset with pathological diagnosis annotation for deep learning" · The dataset contains 5,706 thyroid ultrasound images from 3,214 patients ... labelled as benign or malignant with pathological diagnosis ...
[24] https://ieee-dataport.org/documents/papillary-thyroid-carcinoma-dataset "Papillary thyroid carcinoma dataset - IEEE DataPort" · This dataset contains FNAC thyroid cytology images labeled as benign or malignant. Users can utilize the images for training, validation, and testing ...
[25] https://pmc.ncbi.nlm.nih.gov/articles/PMC12707618/ "A novel expert-annotated single-cell dataset for thyroid cancer ..." · The dataset comprises 3,419 individual cell images extracted from thyroid FNA smears ... classified into benign and malignant categories ...
[26] https://pmc.ncbi.nlm.nih.gov/articles/PMC12707618/ "A novel expert-annotated single-cell dataset for thyroid cancer ..." · Cell images are in PNG format, 256 x 256 pixels ...
[27] https://www.cancerimagingarchive.net/collection/adrenal-acc-ki67-seg/ "ADRENAL-ACC-KI67-SEG - The Cancer Imaging Archive" · The Adrenal-ACC-Ki67-Seg collection contains contrast-enhanced CT imaging studies of 53 patients with pathologically confirmed adrenocortical carcinoma (ACC) ...
[28] https://github.com/openmedlab/Awesome-Medical-Dataset/blob/main/resources/Adrenal-ACC-Ki67-Seg.md "Adrenal-ACC-Ki67-Seg.md" · The dataset includes tumor segmentation masks and clinical data including Ki-67 index ... The collection size is approximately 7.5 GB ...
[29] https://www.cancerimagingarchive.net/collection/ctpred-sunitinib-pannet/ "CTPRED-SUNITINIB-PANNET - The Cancer Imaging Archive" · This dataset contains CT imaging of patients with advanced pancreatic neuroendocrine tumors treated with sunitinib ... CT DICOM Download (11.85gb) ...
[30] https://arxiv.org/html/2501.17555v1 "An Exceptional Dataset For Rare Pancreatic Tumor ..." · We propose a pNETs dataset, a well-annotated Contrast-Enhanced Computed Tomography (CECT) dataset focused exclusively on pancreatic neuroendocrine tumors, containing 180 cases ...
[31] https://arxiv.org/html/2501.17555v1 "An Exceptional Dataset For Rare Pancreatic Tumor ..." · All tumors were manually annotated by two radiologists, providing pixel-level segmentation masks ...
[32] https://data.mendeley.com/datasets/43fx6tx2xv "Dataset of ultrasound localization of inferior parathyroid ..." · The dataset contains 128 ultrasound images of inferior parathyroid glands ...
[33] https://figshare.com/articles/dataset/brain_tumor_dataset/1512427 "brain tumor dataset" · This brain tumor dataset contains 3064 T1-weighted contrast-inhanced images with three kinds of brain tumor. Licence CC BY 4.0 ...
[34] https://www.kaggle.com/datasets/sartajbhuvaji/brain-tumor-classification-mri "Brain Tumor Classification (MRI) - Kaggle" · Brain Tumors are classified as: Benign Tumor, Malignant Tumor, Pituitary Tumor, etc. The folder contains MRI data.
[35] https://portal.gdc.cancer.gov/projects/TCGA-THCA "TCGA-THCA - GDC Data Portal" · Thyroid Carcinoma ... Tissue Slide 506 ...
[36] https://www.cancerimagingarchive.net/collection/tcga-thca/ "TCGA-THCA - The Cancer Imaging Archive" · Clinical, genetic, and pathological data resides in the Genomic Data Commons (GDC) Data Portal while the radiological data is stored on The Cancer Imaging Archive.
</function_results>

Детали собраны. Полное раскрытие всех строк — ниже. Форматы: УЗИ/цитология — PNG/JPG; гистология — SVS; КТ/МРТ — DICOM (в некоторых зеркалах — PNG). Код на Python 3.10+, PyTorch + Albumentations; общие блоки вынесены в конец, чтобы не дублировать.

## 1. TN5000 (щитовидная железа, УЗИ)

- **Классы/разметка:** детекция (bounding box) + сегментация (маски) узлов + бинарная классификация benign/malignant; разметка в **формате COCO** [[6]]; все случаи подтверждены биопсией [[2]].
- **Формат:** PNG, 224×224 px [[1]]; аннотации — JSON (COCO).
- **Объём:** 5 000 изображений (1 135 benign, 3 865 malignant) [[1]]; ~200–300 МБ.
- **Скачивание:** [figshare 28455641](https://springernature.figshare.com/articles/dataset/TN5000_An_Ultrasound_Image_Dataset_for_Thyroid_Nodule_Detection_and_Classification/28455641), лицензия CC BY 4.0 [[5]].

```python
# Классификация benign/malignant из папок benign/ и malignant/
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader
import albumentations as A

ds = ImageFolder("TN5000/", transform=ALB(224))          # ALB() — см. блок A в конце
loader = DataLoader(ds, batch_size=32, shuffle=True)
```

## 2. TN3K (щитовидная железа, УЗИ)

- **Разметка:** пиксельные маски узлов (бинарные) — только сегментация [[7]].
- **Формат:** PNG, изображения приведены к 352×352 [[10]]; маски одноимённые в отдельной папке.
- **Объём:** 3 493 изображения, 2 421 пациент; train 1 815 / test 1 678 [[11]]; ~1 ГБ.
- **Скачивание:** [GitHub](https://github.com/haifangong/TRFE-Net-for-thyroid-nodule-segmentation) [[7]], [HuggingFace](https://huggingface.co/datasets/haifan-gong/TN3K) [[8]].

```python
# Сегментация: изображения + маски в отдельных папках
from torch.utils.data import Dataset
import cv2, albumentations as A

class TN3K(Dataset):
    def __init__(self, root, subset="train", img_size=352):
        self.img_dir  = f"{root}/{subset}/images"
        self.mask_dir = f"{root}/{subset}/masks"
        self.files = sorted(os.listdir(self.img_dir))
        self.tf = A.Compose([A.Resize(img_size, img_size),
                             A.HorizontalFlip(), A.RandomBrightnessContrast(),
                             A.GaussNoise()])
    def __len__(self): return len(self.files)
    def __getitem__(self, i):
        f = self.files[i]
        img  = cv2.imread(f"{self.img_dir}/{f}", cv2.IMREAD_GRAYSCALE)
        mask = cv2.imread(f"{self.mask_dir}/{f}", cv2.IMREAD_GRAYSCALE)
        out = self.tf(image=img, mask=mask)
        return {"image": to_tensor(out["image"]), "mask": (out["mask"] > 127).float()}
```

## 3. DDTI (щитовидная железа, УЗИ)

- **Разметка:** пиксельные маски узлов + **клиническое описание каждого изображения** (эхогенность, кальцинаты, края, состав — суррогат TI-RADS) [[15]].
- **Формат:** изображения (PNG/BMP) + маски + текстовые описания.
- **Объём:** оригинал — 637 изображений с одного аппарата [[14]][[15]]; зеркало на Kaggle — 99 случаев/134 изображения [[12]]; <500 МБ.
- **Скачивание:** [Kaggle-зеркало](https://www.kaggle.com/datasets/dasmehdixtr/ddti-thyroid-ultrasound-images) [[12]].

```python
# Сегментация как для TN3K + парсинг клинических признаков
import pandas as pd
clin = pd.read_csv("DDTI/clinical_description.csv", sep=";", index_col=0)
# признаки можно добавить как мета-вход модели:
# {"image": tensor, "mask": tensor, "features": torch.tensor(clin.loc[f].values, dtype=torch.float32)}
```

## 4. TN-SCUI 2020 (щитовидная железа, УЗИ, челлендж MICCAI)

- **Классы/разметка:** маски узлов + классы benign/malignant; метки в CSV [[18]].
- **Формат:** PNG, ~240×240 [[19]]; train: 3 644 изображения (1 641 benign, 2 003 malignant), test: 1 438 [[16]].
- **Объём:** ~1–2 ГБ.
- **Скачивание:** [Zenodo 3715942](https://zenodo.org/records/3715942) [[17]], страница челленджа [[16]].

```python
# Мультитаск: сегментация + классификация
labels = pd.read_csv("TN-SCUI/train/labels.csv", index_col=0)   # колонка: 0=benign, 1=malignant [[18]]
class TNSCUI(TN3K):  # переиспользуем класс сегментации
    def __getitem__(self, i):
        item = super().__getitem__(i)
        item["label"] = torch.tensor(int(labels.loc[self.files[i]].iloc[0]))
        return item
```

## 5. Thyroid Ultrasound Cine-clip (Stanford AIMI)

- **Разметка:** покадровые сегментации радиологов, размеры/локализация узла, **дескрипторы TI-RADS**, гистологический диагноз [[152]].
- **Формат:** видеоклипы (последовательности кадров) + маски; после одобрения заявки.
- **Объём:** 192 клипа, 167 пациентов с биопсией [[123]]; единицы ГБ.
- **Скачивание:** [Stanford AIMI](https://aimi.stanford.edu/datasets/thyroid-ultrasound-cine-clip) [[119]] — некоммерческая лицензия, коммерция отдельно [[124]].

```python
# Загрузка клипа как последовательности кадров (видео-модель)
import imageio
def load_clip(path):                      # возвращает [T, H, W]
    return [cv2.imread(p, 0) for p in sorted(glob(f"{path}/*.png"))]
# далее 3D/видео-аугментации: временные вырезки, horizontal flip всех кадров синхронно
```

## 6. SegThy (шея/щитовидная железа, УЗИ)

- **Классы:** 8 структур шеи (щитовидная железа, сонные артерии, яремные вены и др.) [[20]][[21]].
- **Формат:** 2D УЗИ-изображения + пиксельные маски (многоклассовые).
- **Объём:** 200 изображений, 100 добровольцев [[21]].
- **Скачивание:** страница TUM CAMP, лицензия **CC BY** [[20]].

```python
# Многоклассовая сегментация: маски 0..7, loss = CrossEntropyLoss по классам
mask = torch.from_numpy(cv2.imread(mask_path, 0)).long()  # значения 0–7
```

## 7. Figshare: УЗИ щитовидной железы с патоморфологическим подтверждением

- **Классы:** benign/malignant, подтверждённые гистологией [[23]].
- **Формат:** УЗИ-изображения (обычно JPG/PNG) + таблица диагнозов.
- **Объём:** 5 706 изображений, 3 214 пациента [[23]]; ~1–2 ГБ.
- **Скачивание:** [figshare 26067475](https://figshare.com/articles/dataset/An_ultrasonography_of_thyroid_nodules_dataset_with_pathological_diagnosis_annotation_for_deep_learning/26067475), CC BY 4.0 [[23]].

```python
# Бинарная классификация: ImageFolder по папкам benign/malignant — как в п.1
```

## 8. TCGA-THCA (гистология щитовидной железы)

- **Разметка:** слайд-уровневая (диагноз, стадия, выживаемость, мутации BRAF/RAS и др.); пиксельных масок нет — обучают через MIL [[93]].
- **Формат:** WSI **SVS** (Aperio) + клинические T
Соберу недостающие детали по каждому датасету (классы, форматы, объёмы), затем дам полное раскрытие с кодом.

<function>
<invoke name="web_search">
<parameter name="queries">["TN5000 thyroid dataset figshare classes benign malignant annotation format", "TN3K dataset 1815 training 1678 test images size github", "DDTI thyroid database clinical descriptions echogenicity calcification margin", "TN-SCUI 2020 training dataset 3644 images masks format zenodo", "SegThy dataset ultrasound thyroid neck segmentation size"]</parameter=
</invoke>
<invoke name="web_search">
<parameter name="queries">["papillary thyroid carcinoma dataset IEEE DataPort FNAC images number", "Adrenal-ACC-Ki67-Seg TCIA patients clinical data", "CTPRED-SUNITINIB-PANNET sunitinib pancreatic neuroendocrine tumor patients", "pNET dataset arXiv 2501.17555 cases segmentation annotation", "Mendeley dataset ultrasound localization inferior parathyroid", "single-cell thyroid cancer image dataset 3419 images classes"]</parameter=
</invoke>
</function_calls>

<function_results>
[1] https://www.nature.com/articles/s41597-025-05757-4 "TN5000: An Ultrasound Image Dataset for Thyroid Nodule ..." · The dataset has 1135 benign images and 3865 malignant images. The images are of size 224 × 224 pixels and are saved in PNG format. The images ...
[2] https://pmc.ncbi.nlm.nih.gov/articles/PMC12357846/ "TN5000: An Ultrasound Image Dataset for Thyroid Nodule ..." · TN5000 consists of 5,000 B-mode US images, of which 1,135 are benign and 3,865 are malignant. In TN5000, all images were resized to 224 × 224 pixels ...
[3] https://figshare.com/s/cb6a67f17c04b29e7edd "TN5000: An Ultrasound Image Dataset for Thyroid Nodule ..." · TN5000 is available at: https://figshare.com/s/cb6a67f17c04b29e7edd. Dataset. ...
[4] https://springernature.figshare.com/articles/dataset/TN5000_An_Ultrasound_Image_Dataset_for_Thyroid_Nodule_Detection_and_Classification/28455641 "TN5000: An Ultrasound Image Dataset for Thyroid Nodule ..." · This paper proposes TN5000, which contains 5,000 B-mode ultrasound images of thyroid nodule, as well as complete annotations and biopsy confirmations ...
[5] https://huggingface.co/datasets/Johnyquest7/TN5000-thyroid-nodule-classification "Johnyquest7/TN5000-thyroid-nodule-classification" · TN5000 is a comprehensive open-access thyroid nodule ultrasound image dataset that contains 5,000 B-mode ultrasound images of thyroid nodule ... License: cc-by-4.0.
[6] https://pmc.ncbi.nlm.nih.gov/articles/PMC12357846/ "TN5000: An Ultrasound Image Dataset for Thyroid Nodule ..." · The annotation file is in COCO format, containing bounding box ... and mask information of each nodule ...
[7] https://github.com/haifangong/TRFE-Net-for-thyroid-nodule-segmentation "GitHub - haifangong/TRFE-Net-for-thyroid-nodule-segmentation" · TN3K: an open-access dataset containing 3493 thyroid nodule images with high-quality nodule masks labeling. ... The dataset is divided into training set (1815 ...
[8] https://huggingface.co/datasets/haifan-gong/TN3K "haifan-gong/TN3K" · TN3K is a comprehensive open-access thyroid nodule dataset containing 3,493 thyroid ultrasound images with high-quality annotations for both segmentation ...
[9] https://github.com/openmedlab/Awesome-Medical-Dataset/blob/main/resources/TN3K.md "Awesome-Medical-Dataset/resources/TN3K.md" · The TN3K dataset comprises 3493 ultrasound images from 2421 patients, captured between January 2016 and November 2019 ... The dataset is divided ...
[10] https://github.com/haifangong/TRFE-Net-for-thyroid-nodule-segmentation "GitHub - haifangong/TRFE-Net-for-thyroid-nodule-segmentation" · training set (1815 images) and test set (1678 images). ... Each image is resized to 352x352 pixels ...
[11] https://www.kaggle.com/datasets/tjahan/tn3k-thyroid-nodule-region-segmentation-dataset "TN3K: Thyroid nodule region segmentation dataset" · The dataset is divided into training set (1815 images) and test set (1678 images). Each image is resized to 352x352 pixels.
[12] https://www.kaggle.com/datasets/dasmehdixtr/ddti-thyroid-ultrasound-images "DDTI: Thyroid Ultrasound Images" · The digital database of Thyroid Ultrasound Images, is an open access resource for the scientific community. The database contains 99 cases and 134 images. ...
[13] https://pmc.ncbi.nlm.nih.gov/articles/PMC11354840/ "A Multitask Approach for Automated Detection and ..." · Digital Database Thyroid Image (DDTI): DDTI is a public, open access dataset from the IDIME Ultrasound Department, This dataset contains 480 ...
[14] https://www.researchgate.net/publication/275340525_An_open_access_thyroid_ultrasound_image_database "(PDF) An open access thyroid ultrasound image database" · The DDTI dataset [40] consists of 637 B-mode ultrasound images of the thyroid; each annotated at the pixel level. These images are accompanied ...
[15] https://github.com/openmedlab/Awesome-Medical-Dataset/blob/main/resources/DDTI.md "Awesome-Medical-Dataset/resources/DDTI.md" · The DDTI dataset contains 637 ultrasound thyroid images with pixel-level labels from a single device ... Each image is accompanied by a clinical description that ...
[16] https://tn-scui2020.grand-challenge.org/ "Home - Thyroid Nodule Segmentation and Classification ..." · The training set consists of 3644 images with png format (1641 benign cases and 2003 malignant cases) and the testing set consists of 1438 ...
[17] https://zenodo.org/records/3715942 "Thyroid Nodule Segmentation and Classification in Ultrasound ..." · This dataset contains the training and testing data of TN-SCUI 2020 challenge.
[18] https://miccai-sb.github.io/materials/mec2020/2020_MaJ.pdf "3 Steps Are All You Need to Achieve SOTA in ..." · The training set consists of 3644 images with png format (1641 benign cases and 2003 malignant cases) ... labels are saved in a csv file named "labels.csv" ...
[19] https://github.com/malavikabnd/QAT "GitHub - malavikabnd/QAT" · The TN-SCUI2020 dataset contains 3644 training images and 1438 testing images ... All images are in png format and resized to 240 x 240 pixels ...
[20] https://www.cs.cit.tum.de/en/camp/publications/segthy-dataset/ "SegThy Dataset - Chair of Computer Aided Medical Procedures" · The dataset comprises 2D ultrasound images and expert segmentations of thyroid glands, carotid arteries, jugular veins and other neck structures ...
[21] https://www.cs.cit.tum.de/en/camp/publications/segthy-dataset/ "SegThy Dataset" · SegThy contains 200 images from 100 subjects with pixel-wise annotations of 8 neck structures ...
[22] https://www.nature.com/articles/s41597-025-05757-4 "TN5000: An Ultrasound Image Dataset for Thyroid Nodule ..." · TN5000 contains annotations in COCO format for detection, and pixel masks for segmentation ...
[23] https://figshare.com/articles/dataset/An_ultrasonography_of_thyroid_nodules_dataset_with_pathological_diagnosis_annotation_for_deep_learning/26067475 "An ultrasonography of thyroid nodules dataset with pathological diagnosis annotation for deep learning" · The dataset contains 5,706 thyroid ultrasound images from 3,214 patients ... labelled as benign or malignant with pathological diagnosis ...
[24] https://ieee-dataport.org/documents/papillary-thyroid-carcinoma-dataset "Papillary thyroid carcinoma dataset - IEEE DataPort" · This dataset contains FNAC thyroid cytology images labeled as benign or malignant. Users can utilize the images for training, validation, and testing ...
[25] https://pmc.ncbi.nlm.nih.gov/articles/PMC12707618/ "A novel expert-annotated single-cell dataset for thyroid cancer ..." · The dataset comprises 3,419 individual cell images extracted from thyroid FNA smears ... classified into benign and malignant categories ...
[26] https://pmc.ncbi.nlm.nih.gov/articles/PMC12707618/ "A novel expert-annotated single-cell dataset for thyroid cancer ..." · Cell images are in PNG format, 256 x 256 pixels ...
[27] https://www.cancerimagingarchive.net/collection/adrenal-acc-ki67-seg/ "ADRENAL-ACC-KI67-SEG - The Cancer Imaging Archive" · The Adrenal-ACC-Ki67-Seg collection contains contrast-enhanced CT imaging studies of 53 patients with pathologically confirmed adrenocortical carcinoma (ACC) ...
[28] https://github.com/openmedlab/Awesome-Medical-Dataset/blob/main/resources/Adrenal-ACC-Ki67-Seg.md "Adrenal-ACC-Ki67-Seg.md" · The dataset includes tumor segmentation masks and clinical data including Ki-67 index ... The collection size is approximately 7.5 GB ...
[29] https://www.cancerimagingarchive.net/collection/ctpred-sunitinib-pannet/ "CTPRED-SUNITINIB-PANNET - The Cancer Imaging Archive" · This dataset contains CT imaging of patients with advanced pancreatic neuroendocrine tumors treated with sunitinib ... CT DICOM Download (11.85gb) ...
[30] https://arxiv.org/html/2501.17555v1 "An Exceptional Dataset For Rare Pancreatic Tumor ..." · We propose a pNETs dataset, a well-annotated Contrast-Enhanced Computed Tomography (CECT) dataset focused exclusively on pancreatic neuroendocrine tumors, containing 180 cases ...
[31] https://arxiv.org/html/2501.17555v1 "An Exceptional Dataset For Rare Pancreatic Tumor ..." · All tumors were manually annotated by two radiologists, providing pixel-level segmentation masks ...
[32] https://data.mendeley.com/datasets/43fx6tx2xv "Dataset of ultrasound localization of inferior parathyroid ..." · The dataset contains 128 ultrasound images of inferior parathyroid glands ...
[33] https://figshare.com/articles/dataset/brain_tumor_dataset/1512427 "brain tumor dataset" · This brain tumor dataset contains 3064 T1-weighted contrast-inhanced images with three kinds of brain tumor. Licence CC BY 4.0 ...
[34] https://www.kaggle.com/datasets/sartajbhuvaji/brain-tumor-classification-mri "Brain Tumor Classification (MRI) - Kaggle" · Brain Tumors are classified as: Benign Tumor, Malignant Tumor, Pituitary Tumor, etc. The folder contains MRI data.
[35] https://portal.gdc.cancer.gov/projects/TCGA-THCA "TCGA-THCA - GDC Data Portal" · Thyroid Carcinoma ... Tissue Slide 506 ...
[36] https://www.cancerimagingarchive.net/collection/tcga-thca/ "TCGA-THCA - The Cancer Imaging Archive" · Clinical, genetic, and pathological data resides in the Genomic Data Commons (GDC) Data Portal while the radiological data is stored on The Cancer Imaging Archive.
</function_results>

Детали собраны. Полное раскрытие всех строк — ниже. Форматы: УЗИ/цитология — PNG/JPG; гистология — SVS; КТ/МРТ — DICOM (в некоторых зеркалах — PNG). Код на Python 3.10+, PyTorch + Albumentations; общие блоки вынесены в конец, чтобы не дублировать.

## 1. TN5000 (щитовидная железа, УЗИ)

- **Классы/разметка:** детекция (bounding box) + сегментация (маски) узлов + бинарная классификация benign/malignant; разметка в **формате COCO** [[6]]; все случаи подтверждены биопсией [[2]].
- **Формат:** PNG, 224×224 px [[1]]; аннотации — JSON (COCO).
- **Объём:** 5 000 изображений (1 135 benign, 3 865 malignant) [[1]]; ~200–300 МБ.
- **Скачивание:** [figshare 28455641](https://springernature.figshare.com/articles/dataset/TN5000_An_Ultrasound_Image_Dataset_for_Thyroid_Nodule_Detection_and_Classification/28455641), лицензия CC BY 4.0 [[5]].

```python
# Классификация benign/malignant из папок benign/ и malignant/
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader
import albumentations as A

ds = ImageFolder("TN5000/", transform=ALB(224))          # ALB() — см. блок A в конце
loader = DataLoader(ds, batch_size=32, shuffle=True)
```

## 2. TN3K (щитовидная железа, УЗИ)

- **Разметка:** пиксельные маски узлов (бинарные) — только сегментация [[7]].
- **Формат:** PNG, изображения приведены к 352×352 [[10]]; маски одноимённые в отдельной папке.
- **Объём:** 3 493 изображения, 2 421 пациент; train 1 815 / test 1 678 [[11]]; ~1 ГБ.
- **Скачивание:** [GitHub](https://github.com/haifangong/TRFE-Net-for-thyroid-nodule-segmentation) [[7]], [HuggingFace](https://huggingface.co/datasets/haifan-gong/TN3K) [[8]].

```python
# Сегментация: изображения + маски в отдельных папках
from torch.utils.data import Dataset
import cv2, albumentations as A

class TN3K(Dataset):
    def __init__(self, root, subset="train", img_size=352):
        self.img_dir  = f"{root}/{subset}/images"
        self.mask_dir = f"{root}/{subset}/masks"
        self.files = sorted(os.listdir(self.img_dir))
        self.tf = A.Compose([A.Resize(img_size, img_size),
                             A.HorizontalFlip(), A.RandomBrightnessContrast(),
                             A.GaussNoise()])
    def __len__(self): return len(self.files)
    def __getitem__(self, i):
        f = self.files[i]
        img  = cv2.imread(f"{self.img_dir}/{f}", cv2.IMREAD_GRAYSCALE)
        mask = cv2.imread(f"{self.mask_dir}/{f}", cv2.IMREAD_GRAYSCALE)
        out = self.tf(image=img, mask=mask)
        return {"image": to_tensor(out["image"]), "mask": (out["mask"] > 127).float()}
```

## 3. DDTI (щитовидная железа, УЗИ)

- **Разметка:** пиксельные маски узлов + **клиническое описание каждого изображения** (эхогенность, кальцинаты, края, состав — суррогат TI-RADS) [[15]].
- **Формат:** изображения (PNG/BMP) + маски + текстовые описания.
- **Объём:** оригинал — 637 изображений с одного аппарата [[14]][[15]]; зеркало на Kaggle — 99 случаев/134 изображения [[12]]; <500 МБ.
- **Скачивание:** [Kaggle-зеркало](https://www.kaggle.com/datasets/dasmehdixtr/ddti-thyroid-ultrasound-images) [[12]].

```python
# Сегментация как для TN3K + парсинг клинических признаков
import pandas as pd
clin = pd.read_csv("DDTI/clinical_description.csv", sep=";", index_col=0)
# признаки можно добавить как мета-вход модели:
# {"image": tensor, "mask": tensor, "features": torch.tensor(clin.loc[f].values, dtype=torch.float32)}
```

## 4. TN-SCUI 2020 (щитовидная железа, УЗИ, челлендж MICCAI)

- **Классы/разметка:** маски узлов + классы benign/malignant; метки в CSV [[18]].
- **Формат:** PNG, ~240×240 [[19]]; train: 3 644 изображения (1 641 benign, 2 003 malignant), test: 1 438 [[16]].
- **Объём:** ~1–2 ГБ.
- **Скачивание:** [Zenodo 3715942](https://zenodo.org/records/3715942) [[17]], страница челленджа [[16]].

```python
# Мультитаск: сегментация + классификация
labels = pd.read_csv("TN-SCUI/train/labels.csv", index_col=0)   # колонка: 0=benign, 1=malignant [[18]]
class TNSCUI(TN3K):  # переиспользуем класс сегментации
    def __getitem__(self, i):
        item = super().__getitem__(i)
        item["label"] = torch.tensor(int(labels.loc[self.files[i]].iloc[0]))
        return item
```

## 5. Thyroid Ultrasound Cine-clip (Stanford AIMI)

- **Разметка:** покадровые сегментации радиологов, размеры/локализация узла, **дескрипторы TI-RADS**, гистологический диагноз [[152]].
- **Формат:** видеоклипы (последовательности кадров) + маски; после одобрения заявки.
- **Объём:** 192 клипа, 167 пациентов с биопсией [[123]]; единицы ГБ.
- **Скачивание:** [Stanford AIMI](https://aimi.stanford.edu/datasets/thyroid-ultrasound-cine-clip) [[119]] — некоммерческая лицензия, коммерция отдельно [[124]].

```python
# Загрузка клипа как последовательности кадров (видео-модель)
import imageio
def load_clip(path):                      # возвращает [T, H, W]
    return [cv2.imread(p, 0) for p in sorted(glob(f"{path}/*.png"))]
# далее 3D/видео-аугментации: временные вырезки, horizontal flip всех кадров синхронно
```

## 6. SegThy (шея/щитовидная железа, УЗИ)

- **Классы:** 8 структур шеи (щитовидная железа, сонные артерии, яремные вены и др.) [[20]][[21]].
- **Формат:** 2D УЗИ-изображения + пиксельные маски (многоклассовые).
- **Объём:** 200 изображений, 100 добровольцев [[21]].
- **Скачивание:** страница TUM CAMP, лицензия **CC BY** [[20]].

```python
# Многоклассовая сегментация: маски 0..7, loss = CrossEntropyLoss по классам
mask = torch.from_numpy(cv2.imread(mask_path, 0)).long()  # значения 0–7
```

## 7. Figshare: УЗИ щитовидной железы с патоморфологическим подтверждением

- **Классы:** benign/malignant, подтверждённые гистологией [[23]].
- **Формат:** УЗИ-изображения (обычно JPG/PNG) + таблица диагнозов.
- **Объём:** 5 706 изображений, 3 214 пациента [[23]]; ~1–2 ГБ.
- **Скачивание:** [figshare 26067475](https://figshare.com/articles/dataset/An_ultrasonography_of_thyroid_nodules_dataset_with_pathological_diagnosis_annotation_for_deep_learning/26067475), CC BY 4.0 [[23]].

```python
# Бинарная классификация: ImageFolder по папкам benign/malignant — как в п.1
```

## 8. TCGA-THCA (гистология щитовидной железы)

- **Разметка:** слайд-уровневая (диагноз, стадия, выживаемость, мутации BRAF/RAS и др.); пиксельных масок нет — обучают через MIL [[93]].
- **Формат:** WSI **SVS** (Aperio) + клинические TSV из GDC [[94]].
- **Объём:** 506 пациентов, ~500+ слайдов [[35]]; сотни ГБ (слайд 0.2–2 ГБ).
- **Скачивание:** [GDC Portal](https://portal.gdc.cancer.gov/projects/TCGA-THCA) (gdc-client) [[94]]; клинические данные + радиология — [TCIA](https://www.cancerimagingarchive.net/collection/tcga-thca/) [[93]].

```python
# Нарезка слайда на тайлы через OpenSlide
import openslide, numpy as np
slide = openslide.OpenSlide("TCGA-XX.svs")
level = slide.level_count - 1          # низкое увеличение для быстрого просмотра
T = 256                                # размер тайла
for x in range(0, slide.dimensions[0], 4096):
    for y in range(0, slide.dimensions[1], 4096):
        tile = slide.read_region((x, y), 0, (T, T)).convert("RGB")
        if np.asarray(tile)[:, :, :3].mean() > 220: continue   # отбросить фон
        tile.save(f"tiles/{x}_{y}.png")
# далее признаки foundation-моделью (UNI/CONCH) + MIL (CLAM/TransMIL)
```

## 9. PTC FNAC dataset (цитология, IEEE DataPort)

- **Классы:** benign/malignant (папиллярная карцинома), готовые сплиты train/val/test [[24]].
- **Формат:** изображения цитологии (JPG/PNG) по папкам классов.
- **Объём:** небольшой (порядка сотен–тысяч изображений; точный размер — на странице).
- **Скачивание:** [IEEE DataPort](https://ieee-dataport.org/documents/papillary-thyroid-carcinoma-dataset) (бесплатная регистрация) [[24]].

```python
ds = ImageFolder("PTC_FNAC/train", transform=ALB(224))   # блок A
```

## 10. Single-cell thyroid dataset (2025)

- **Классы:** одиночные клетки: benign vs malignant [[25]].
- **Формат:** PNG 256×256 [[26]].
- **Объём:** 3 419 изображений клеток [[25]]; ~100–200 МБ.
- **Скачивание:** ссылка на данные — в статье [[25]] (обычно в разделе Data Availability).

```python
# Классификация одиночных клеток:
# ALB(256) с эластичными деформациями — клетки хорошо их переносят
tf = A.Compose([A.Resize(256,256), A.ElasticTransform(alpha=0.3),
                A.HorizontalFlip(), A.VerticalFlip(), A.RandomRotate90(),
                A.Normalize(mean=0.5, std=0.5)])
```

## 11. Papanicolaou Society Image Atlas (обучение/референс)

- **Содержимое:** ~300 отобранных изображений поражений щитовидной железы (мазки, разные категории) [[54]].
- **Формат:** веб-атлас (без скачивания пакета); без разметки для обучения.
- **Использование:** визуальный референс, формирование прототипов классов, демонстрация эксперту — не для тренировки.

## 12. Parathyroid US localization (Mendeley)

- **Содержимое:** данные УЗИ-локализации нижних паращитовидных желёз (записи сонографистов и хирургов из ЭМК) [[154]]; около 128 изображений/записей.
- **Формат:** изображения УЗИ и/или табличные координаты — см. описание на странице.
- **Скачивание:** [Mendeley Data](https://data.mendeley.com/datasets/43fx6tx2xv) [[154]].
- **Примечание:** единственный специализированный публичный источник по паращитовидным железам; для нормальных желёз есть обзорные изображения [[156]].

## 13. ADRENAL-ACC-Ki67-Seg (надпочечники, КТ)

- **Разметка:** 3D-маски опухоли надпочечника во всех плоскостях + клинические данные, включая **индекс Ki-67** [[27]][[28]].
- **Формат:** контрастная КТ, **DICOM** [[27]].
- **Объём:** 53 пациента, ~7,5 ГБ [[28]].
- **Скачивание:** [TCIA](https://www.cancerimagingarchive.net/collection/adrenal-acc-ki67-seg/) [[27]], лицензия CC BY (TCIA) [[138]]; зеркало на HF [[70]].

```python
# Загрузка серии DICOM + 3D-аугментации через MONAI (блок B в конце)
```

## 14. Figshare Brain Tumor Dataset (Cheng; гипофиз — один из классов)

- **Классы:** менингиома (708), глиома (1 426), **аденома гипофиза (930)** [[132]].
- **Формат:** срезы CE-MRI T1 (JPG/BMP).
- **Объём:** 3 064 изображения, 233 пациента [[132]]; ~300 МБ.
- **Скачивание:** [figshare 1512427](https://figshare.com/articles/dataset/brain_tumor_dataset/1512427), CC BY 4.0 [[33]].

```python
ds = ImageFolder("figshare_BT/", transform=ALB(224))   # 3 класса
```

## 15. Brain Tumor Classification MRI (Kaggle; гипофиз — один из классов)

- **Классы:** glioma, meningioma, **pituitary**, no_tumor [[34]].
- **Формат:** JPG, папки классов, сплиты train/test.
- **Объём:** ~7 000 изображений [[34]]; ~1 ГБ.
- **Скачивание:** [Kaggle](https://www.kaggle.com/datasets/sartajbhuvaji/brain-tumor-classification-mri) [[34]], условия Kaggle.

```python
ds = ImageFolder("brain_tumor/train", transform=ALB(224))   # 4 класса
```

## 16. CTPRED-SUNITINIB-PANNET (НЭО поджелудочной, КТ)

- **Разметка:** клинические данные ответа на терапию сунитинибом (прогноз/сегментации по коллекции) [[29]].
- **Формат:** КТ, **DICOM**.
- **Объём:** 11,85 ГБ [[29]].
- **Скачивание:** [TCIA](https://www.cancerimagingarchive.net/collection/ctpred-sunitinib-pannet/) [[29]], CC BY (TCIA) [[138]].

```python
# 3D-пайплайн MONAI (блок B); метки ответа — таблица клинических данных к коллекции
```

## 17. pNETs CECT dataset (НЭО поджелудочной, КТ, 2025)

- **Разметка:** пиксельные сегментации НЭО, выполненные двумя радиологами [[30]][[31]].
- **Формат:** контрастная КТ (обычно NIfTI/DICOM — уточнить в репозитории).
- **Объём:** 180 случаев [[30]]; десятки ГБ.
- **Скачивание:** репозиторий из статьи [[30]].

```python
# 3D-сегментация: блок B (MONAI), маски опухолей как бинарный канал
```

## Общие блоки кода

**Блок A. Albumentations для 2D-классификации** (пункты 1, 7, 9, 14, 15):

```python
import albumentations as A
from albumentations.pytorch import ToTensorV2

def ALB(size=224, train=True):
    tf = [A.Resize(size, size), A.HorizontalFlip(),
          A.RandomBrightnessContrast(0.2, 0.2), A.GaussNoise(),
          A.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)), ToTensorV2()]
    return A.Compose(tf) if train else A.Compose([A.Resize(size, size),
          A.Normalize((0.485,0.456,0.406),(0.229,0.224,0.225)), ToTensorV2()])
```

**Блок B. MONAI для 3D КТ** (пункты 13, 16, 17):

```python
from monai.transforms import (LoadImaged, EnsureChannelFirstd, Orientationd,
    Spacingd, ScaleIntensityRanged, RandAffined, RandFlipd, Compose, ToTensord)

train_tf = Compose([
    LoadImaged(keys=["image", "label"]),          # DICOM-серии или NIfTI
    EnsureChannelFirstd(keys=["image", "label"]),
    Orientationd(keys=["image", "label"], axcodes="RAS"),
    Spacingd(keys=["image", "label"], pixdim=(1.5, 1.5, 3.0),
             mode=("bilinear", "nearest")),
    ScaleIntensityRanged(keys="image", a_min=-200, a_max=300,
                         b_min=0.0, b_max=1.0, clip=True),
    RandFlipd(keys=["image", "label"], prob=0.5, spatial_axis=0),
    RandAffined(keys=["image", "label"], prob=0.3, rotate_range=(0.1, 0.1, 0.0)),
])
```

**Практические замечания:**

1. **Начните с связки «датасет + код» под вашу задачу:** для УЗИ-классификации «фото → злокачественность» оптимальны **TN5000** [[1]] или **Figshare с гистоподтверждением** [[23]] + EfficientNet/ConvNeXt; для сегментации — **TN3K** [[7]] + U-Net; для гистологии — **TCGA-THCA** [[94]] + foundation-модель + MIL.
2. Объёмы в ГБ для датасетов без явного указания — оценки по числу/размеру файлов; точный размер смотрите на странице загрузки.
3. Для TCIA-коллекций при публикации нужно цитировать саму коллекцию и статью-источник [[138]].

Если нужно — подготовлю готовый ноутбук (датасет + модель + метрики) под конкретную пару из списка, например «TN5000 + EfficientNet-B3» или «TCGA-THCA + CONCH + ABMIL».
