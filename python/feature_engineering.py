"""
Bank Customer Churn — Feature Engineering Scripti
===================================================
Temizlenmiş veriyi okur, yeni değişkenler türetir ve
BigQuery'ye yüklemeye hazır final veriyi oluşturur.

Kullanım:
    python feature_engineering.py

Girdi:  data/processed/bank_churn_cleaned.csv
Çıktı:  data/processed/bank_churn_features.csv
"""

import pandas as pd
import numpy as np
import os

# ─── Paths ───────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "bank_churn_cleaned.csv")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "bank_churn_features.csv")


def add_age_features(df: pd.DataFrame) -> pd.DataFrame:
    """Yaş bazlı yeni değişkenler."""
    print("   [1/6] Yaş değişkenleri...")
    
    # Yaş grupları
    bins = [0, 25, 35, 45, 55, 65, 100]
    labels = ["18-25", "26-35", "36-45", "46-55", "56-65", "65+"]
    df["age_group"] = pd.cut(df["age"], bins=bins, labels=labels).astype(str)
    
    # Tenure / Age oranı (müşteri sadakat göstergesi)
    df["tenure_age_ratio"] = (df["tenure"] / df["age"]).round(4)
    
    print(f"         → age_group: {df['age_group'].nunique()} kategori")
    print(f"         → tenure_age_ratio: ort={df['tenure_age_ratio'].mean():.4f}")
    
    return df


def add_balance_features(df: pd.DataFrame) -> pd.DataFrame:
    """Bakiye bazlı yeni değişkenler."""
    print("   [2/6] Bakiye değişkenleri...")
    
    # Sıfır bakiye flag'i
    df["is_zero_balance"] = (df["balance"] == 0).astype("int8")
    zero_pct = df["is_zero_balance"].mean() * 100
    
    # Bakiye / Maaş oranı
    df["balance_salary_ratio"] = (df["balance"] / df["estimated_salary"].replace(0, np.nan)).round(4)
    df["balance_salary_ratio"] = df["balance_salary_ratio"].fillna(0)
    
    # Yüksek bakiye flag'i (median üzeri)
    balance_median = df.loc[df["balance"] > 0, "balance"].median()
    df["is_high_balance"] = (df["balance"] > balance_median).astype("int8")
    
    # Bakiye segmenti
    df["balance_segment"] = pd.cut(
        df["balance"],
        bins=[-1, 0, 50000, 100000, 150000, 300000],
        labels=["Sıfır", "Düşük", "Orta", "Yüksek", "Çok Yüksek"]
    ).astype(str)
    
    print(f"         → is_zero_balance: %{zero_pct:.1f} sıfır bakiye")
    print(f"         → balance_salary_ratio: ort={df['balance_salary_ratio'].mean():.2f}")
    print(f"         → is_high_balance: %{df['is_high_balance'].mean()*100:.1f} yüksek bakiye")
    print(f"         → balance_segment: {df['balance_segment'].nunique()} segment")
    
    return df


def add_credit_features(df: pd.DataFrame) -> pd.DataFrame:
    """Kredi skoru bazlı yeni değişkenler."""
    print("   [3/6] Kredi skoru değişkenleri...")
    
    # Kredi skoru kategorisi
    bins = [0, 500, 600, 700, 800, 900]
    labels = ["Çok Düşük", "Düşük", "Orta", "İyi", "Mükemmel"]
    df["credit_score_cat"] = pd.cut(df["credit_score"], bins=bins, labels=labels).astype(str)
    
    print(f"         → credit_score_cat dağılımı:")
    for cat, cnt in df["credit_score_cat"].value_counts().sort_index().items():
        print(f"           {cat:12s}: {cnt:,}")
    
    return df


def add_product_features(df: pd.DataFrame) -> pd.DataFrame:
    """Ürün bazlı yeni değişkenler."""
    print("   [4/6] Ürün değişkenleri...")
    
    # Yıl başına ürün kullanımı
    df["products_per_tenure"] = (df["products_number"] / (df["tenure"] + 1)).round(4)
    
    # Çoklu ürün flag'i
    df["is_multi_product"] = (df["products_number"] >= 2).astype("int8")
    
    # Yüksek riskli ürün sayısı (3-4 ürün)
    df["is_high_risk_products"] = (df["products_number"] >= 3).astype("int8")
    
    print(f"         → products_per_tenure: ort={df['products_per_tenure'].mean():.3f}")
    print(f"         → is_multi_product: %{df['is_multi_product'].mean()*100:.1f}")
    print(f"         → is_high_risk_products: %{df['is_high_risk_products'].mean()*100:.1f}")
    
    return df


def add_engagement_features(df: pd.DataFrame) -> pd.DataFrame:
    """Müşteri bağlılık/etkileşim skorları."""
    print("   [5/6] Etkileşim değişkenleri...")
    
    # Engagement skoru (aktif üyelik + kredi kartı + bakiye varlığı)
    df["engagement_score"] = (
        df["active_member"] + 
        df["credit_card"] + 
        (df["balance"] > 0).astype(int)
    ).astype("int8")
    
    # Engagement segmenti
    engagement_map = {0: "Çok Düşük", 1: "Düşük", 2: "Orta", 3: "Yüksek"}
    df["engagement_segment"] = df["engagement_score"].map(engagement_map)
    
    print(f"         → engagement_score dağılımı:")
    for score, cnt in df["engagement_score"].value_counts().sort_index().items():
        churn_rate = df[df["engagement_score"] == score]["churn"].mean() * 100
        print(f"           {engagement_map[score]:12s} (skor={score}): {cnt:,} müşteri → churn %{churn_rate:.1f}")
    
    return df


def add_risk_features(df: pd.DataFrame) -> pd.DataFrame:
    """Bileşik risk skoru."""
    print("   [6/6] Risk skoru...")
    
    # Risk faktörleri (her biri 0 veya 1)
    df["risk_age"] = (df["age"] >= 45).astype(int)
    df["risk_inactive"] = (df["active_member"] == 0).astype(int)
    df["risk_products"] = (df["products_number"] >= 3).astype(int)
    df["risk_germany"] = (df["country"] == "Germany").astype(int)
    df["risk_zero_balance"] = df["is_zero_balance"]
    
    # Toplam risk skoru (0-5)
    df["churn_risk_score"] = (
        df["risk_age"] + 
        df["risk_inactive"] + 
        df["risk_products"] + 
        df["risk_germany"] +
        df["risk_zero_balance"]
    ).astype("int8")
    
    # Yardımcı risk sütunlarını sil
    df.drop(columns=["risk_age", "risk_inactive", "risk_products", 
                      "risk_germany", "risk_zero_balance"], inplace=True)
    
    # Risk segmenti
    risk_map = {0: "Çok Düşük", 1: "Düşük", 2: "Orta", 3: "Yüksek", 4: "Çok Yüksek", 5: "Kritik"}
    df["churn_risk_segment"] = df["churn_risk_score"].map(risk_map)
    
    print(f"         → churn_risk_score dağılımı:")
    for score in sorted(df["churn_risk_score"].unique()):
        cnt = (df["churn_risk_score"] == score).sum()
        churn_rate = df[df["churn_risk_score"] == score]["churn"].mean() * 100
        label = risk_map.get(score, "?")
        print(f"           {label:12s} (skor={score}): {cnt:,} müşteri → gerçek churn %{churn_rate:.1f}")
    
    return df


def validate_features(df: pd.DataFrame) -> None:
    """Yeni değişkenlerin doğrulaması."""
    print("\n" + "=" * 60)
    print("DOĞRULAMA")
    print("=" * 60)
    
    null_cols = df.columns[df.isnull().any()].tolist()
    if null_cols:
        print(f"   ⚠ Null değer içeren sütunlar: {null_cols}")
    else:
        print("   ✓ Hiçbir sütunda null değer yok")
    
    inf_cols = [col for col in df.select_dtypes(include=[np.number]).columns 
                if np.isinf(df[col]).any()]
    if inf_cols:
        print(f"   ⚠ Sonsuz değer içeren sütunlar: {inf_cols}")
    else:
        print("   ✓ Hiçbir sütunda sonsuz değer yok")
    
    print(f"   ✓ Final boyut: {df.shape[0]:,} satır × {df.shape[1]} sütun")


def main():
    print("\n🔧 Bank Customer Churn — Feature Engineering Pipeline'ı")
    print("─" * 60)
    
    # Yükle
    print(f"\n   Girdi: {INPUT_PATH}")
    df = pd.read_csv(INPUT_PATH)
    print(f"   Yüklendi: {df.shape[0]:,} satır × {df.shape[1]} sütun")
    original_cols = df.shape[1]
    
    # Feature Engineering
    print("\n" + "=" * 60)
    print("FEATURE ENGINEERING")
    print("=" * 60)
    
    df = add_age_features(df)
    df = add_balance_features(df)
    df = add_credit_features(df)
    df = add_product_features(df)
    df = add_engagement_features(df)
    df = add_risk_features(df)
    
    # Doğrula
    validate_features(df)
    
    # Yeni eklenen sütunları listele
    new_cols = df.shape[1] - original_cols
    print(f"\n   📊 {new_cols} yeni değişken eklendi:")
    added = list(df.columns[original_cols:])
    for col in added:
        print(f"      + {col}")
    
    # Kaydet
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\n   ✓ Kaydedildi: {OUTPUT_PATH}")
    print(f"   Final: {df.shape[0]:,} satır × {df.shape[1]} sütun")
    print(f"\n✅ Feature engineering pipeline'ı başarıyla tamamlandı!\n")


if __name__ == "__main__":
    main()
