# Bank Customer Churn Prediction — Bitirme Projesi

## Proje Hakkında

Bu proje, bir bankanın müşteri kaybını (churn) analiz ederek hangi müşterilerin bankayı terk etme eğiliminde olduğunu tespit etmeyi ve bu kayıpları önleyecek aksiyonlar önermeyi amaçlar.

**Veri Seti:** [Kaggle — Bank Customer Churn Prediction](https://www.kaggle.com/datasets/gauravtopre/bank-customer-churn-dataset)

## Pipeline Mimarisi

```
Kaggle (CSV) → Fivetran → BigQuery (raw) → Python (EDA & Cleaning)
                                              ↓
                                    BigQuery (cleaned) → dbt (modeling)
                                              ↓
                                    Looker Studio + Power BI (dashboards)
```

## Kullanılan Araçlar

| Araç | Kullanım Amacı |
|------|----------------|
| **Fivetran** | Veri entegrasyonu ve otomatik taşıma |
| **Zapier** | Otomasyon ve bildirim |
| **Python** | EDA, veri temizleme, feature engineering |
| **BigQuery** | Veri ambarı, SQL sorguları |
| **dbt** | Veri modelleme, test, dokümantasyon |
| **GitHub** | Versiyon kontrolü |
| **Looker Studio** | Dashboard ve görselleştirme |
| **Power BI** | Raporlama ve interaktif analiz |

## Klasör Yapısı

```
bank-churn-project/
├── README.md
├── .gitignore
├── data/
│   └── raw/                        # Ham veri (CSV)
├── notebooks/
│   └── eda_analysis.ipynb          # Keşifsel veri analizi
├── python/
│   ├── cleaning.py                 # Veri temizleme
│   ├── feature_engineering.py      # Yeni değişken türetme
│   └── upload_to_bigquery.py       # BigQuery'ye yükleme
├── dbt/
│   └── bank_churn/
│       ├── models/
│       │   ├── staging/            # Ham veri standardizasyonu
│       │   ├── intermediate/       # İş mantığı katmanı
│       │   └── marts/              # Dashboard-ready tablolar
│       └── tests/
├── dashboards/
│   └── screenshots/
├── docs/
│   └── data_dictionary.md
└── presentation/
```

## Temel Bulgular

- **Churn oranı:** %20.4 (10,000 müşteriden 2,037'si)
- **En güçlü sinyal:** Yaş — 46-55 yaş grubunda churn %50.6
- **Ülke etkisi:** Almanya'da churn %32.4, diğer ülkelerin 2 katı
- **Ürün paradoksu:** 3-4 ürün kullananlarda churn %83-100
- **Aktif üyelik:** Pasif üyelerde churn %26.9, aktif olanlarda %14.3

## Kurulum

```bash
pip install pandas numpy matplotlib seaborn google-cloud-bigquery
```

## Ekip

- [İsim] — Data Analyst
