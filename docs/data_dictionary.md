# Bank Customer Churn — Veri Sözlüğü (Data Dictionary)

## Veri Seti Özeti

| Özellik | Değer |
|---------|-------|
| Kaynak | Kaggle — Bank Customer Churn Prediction |
| Satır sayısı | 10,000 |
| Sütun sayısı | 12 |
| Eksik veri | 0 (hiç yok) |
| Duplike kayıt | 0 |
| Hedef değişken | churn (0/1) |
| Churn oranı | %20.4 (2,037 / 10,000) — dengesiz sınıf |
| Dosya boyutu | ~1.8 MB |

---

## Sütun Açıklamaları

### Tanımlayıcı Sütunlar (Analizden Çıkarılacak)

| Sütun | Veri Tipi | Açıklama | Not |
|-------|-----------|----------|-----|
| customer_id | int64 | Benzersiz müşteri kimliği (10,000 unique) | Join için sakla, modelden çıkar |

### Sayısal Değişkenler

| Sütun | Veri Tipi | Min | Ortalama | Medyan | Max | Std | Açıklama |
|-------|-----------|-----|----------|--------|-----|-----|----------|
| credit_score | int64 | 350 | 650.5 | 652 | 850 | 96.7 | Müşterinin kredi güvenilirlik skoru |
| age | int64 | 18 | 38.9 | 37 | 92 | 10.5 | Müşteri yaşı — churn ile en yüksek korelasyon (+0.285) |
| tenure | int64 | 0 | 5.0 | 5 | 10 | 2.9 | Bankadaki üyelik süresi (yıl) |
| balance | float64 | 0.0 | 76,485.9 | 97,198.5 | 250,898.1 | 62,397.4 | Hesap bakiyesi — %36.2 müşterinin bakiyesi sıfır |
| products_number | int64 | 1 | 1.5 | 1 | 4 | 0.6 | Kullanılan banka ürün sayısı |
| estimated_salary | float64 | 11.6 | 100,090.2 | 100,193.9 | 199,992.5 | 57,510.5 | Tahmini yıllık maaş — uniform dağılım, churn ile düşük korelasyon |

### Kategorik Değişkenler

| Sütun | Veri Tipi | Benzersiz Değer | Dağılım | Açıklama |
|-------|-----------|-----------------|---------|----------|
| country | object | 3 | France %50.1, Germany %25.1, Spain %24.8 | Müşterinin ülkesi |
| gender | object | 2 | Male %54.6, Female %45.4 | Cinsiyet |

### İkili (Binary) Değişkenler

| Sütun | Veri Tipi | 1 (Evet) | 0 (Hayır) | Açıklama |
|-------|-----------|----------|-----------|----------|
| credit_card | int64 | %70.6 | %29.4 | Kredi kartı var mı |
| active_member | int64 | %51.5 | %48.5 | Aktif üye mi |

### Hedef Değişken

| Sütun | Veri Tipi | 1 (Churn) | 0 (Kaldı) | Açıklama |
|-------|-----------|-----------|-----------|----------|
| churn | int64 | %20.4 (2,037) | %79.6 (7,963) | Müşteri bankayı terk etti mi |

---

## Anahtar Bulgular (EDA Özeti)

### En Güçlü Churn Sinyalleri

1. **Yaş (age):** Churn ile en güçlü korelasyon (+0.285). 46-55 yaş grubunda churn %50.6.
2. **Aktif üyelik (active_member):** Pasif üyelerde churn %26.9, aktif üyelerde %14.3.
3. **Bakiye (balance):** Pozitif korelasyon (+0.119). Bakiyesi olan müşterilerde churn %24.1.
4. **Ülke (country):** Almanya'da churn %32.4, Fransa ve İspanya'da ~%16.

### Dikkat Çekici Bulgular

- **Ürün paradoksu:** 3 ürün kullananların %82.7'si, 4 ürün kullananların %100'ü churn etmiş. En düşük churn 2 ürün kullananlarda (%7.6).
- **Cinsiyet farkı:** Kadın müşterilerde churn (%25.1) erkeklerden (%16.5) belirgin şekilde yüksek.
- **Kredi kartı etkisiz:** Kredi kartı sahipliği churn'ü neredeyse hiç etkilemiyor (%20.2 vs %20.8).
- **Maaş nötr:** Tahmini maaş neredeyse tamamen uniform dağılımlı ve churn ile korelasyonu yok (+0.012).
- **En riskli segment:** Almanya'daki 51-60 yaş arası pasif kadın müşteriler — churn oranı %85+ civarı.

### Multicollinearity Notu

- Balance ve products_number arasında negatif korelasyon (-0.304) mevcut.
- Diğer değişkenler arasında güçlü korelasyon yok — multicollinearity sorunu düşük.

---

## Feature Engineering Önerileri

| Yeni Değişken | Formül | Gerekçe |
|---------------|--------|---------|
| balance_salary_ratio | balance / estimated_salary | Bakiyenin gelire oranı |
| tenure_age_ratio | tenure / age | Müşteri sadakat göstergesi |
| is_zero_balance | balance == 0 | Sıfır bakiye flag'i |
| age_group | pd.cut(age, bins) | Yaş segmentasyonu |
| credit_score_cat | Low/Medium/High | Kredi skoru kategorisi |
| products_per_tenure | products_number / (tenure + 1) | Yıl başına ürün kullanımı |
| is_high_value | balance > median | Yüksek değerli müşteri flag'i |
