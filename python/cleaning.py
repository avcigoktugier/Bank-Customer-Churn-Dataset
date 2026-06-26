"""
Bank Customer Churn — Veri Temizleme Scripti
=============================================
Ham veriyi okur, temizler ve analize hazır hale getirir.

Kullanım:
    python cleaning.py

Girdi:  data/raw/Bank_Customer_Churn_Prediction.csv
Çıktı:  data/processed/bank_churn_cleaned.csv
"""

import pandas as pd
import numpy as np
import os
import sys

# ─── Paths ───────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "Bank_Customer_Churn_Prediction.csv")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
OUTPUT_PATH = os.path.join(PROCESSED_DIR, "bank_churn_cleaned.csv")


def load_data(path: str) -> pd.DataFrame:
    """Ham veriyi oku ve ilk kontrolleri yap."""
    print("=" * 60)
    print("1. VERİ YÜKLEME")
    print("=" * 60)
    
    df = pd.read_csv(path)
    print(f"   Satır: {df.shape[0]:,}  |  Sütun: {df.shape[1]}")
    print(f"   Bellek: {df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    return df


def check_quality(df: pd.DataFrame) -> pd.DataFrame:
    """Veri kalite kontrolü: eksik veri, duplike, aykırı değer tespiti."""
    print("\n" + "=" * 60)
    print("2. VERİ KALİTE KONTROLÜ")
    print("=" * 60)
    
    # Eksik veri
    missing = df.isnull().sum()
    total_missing = missing.sum()
    print(f"\n   Eksik veri: {'Yok ✓' if total_missing == 0 else total_missing}")
    if total_missing > 0:
        print(missing[missing > 0])
    
    # Duplike kayıt
    dupes = df.duplicated().sum()
    id_dupes = df["customer_id"].duplicated().sum()
    print(f"   Tam duplike: {dupes}")
    print(f"   Duplike customer_id: {id_dupes}")
    
    if dupes > 0:
        print(f"   → {dupes} duplike satır siliniyor...")
        df = df.drop_duplicates().reset_index(drop=True)
    
    if id_dupes > 0:
        print(f"   → {id_dupes} duplike customer_id siliniyor (ilk kayıt korunuyor)...")
        df = df.drop_duplicates(subset=["customer_id"], keep="first").reset_index(drop=True)
    
    # Aykırı değer tespiti (IQR yöntemi)
    print("\n   Aykırı değer tespiti (IQR):")
    numerical_cols = ["credit_score", "age", "tenure", "balance", "estimated_salary"]
    for col in numerical_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        outliers = ((df[col] < lower) | (df[col] > upper)).sum()
        pct = outliers / len(df) * 100
        status = "⚠" if pct > 5 else "✓"
        print(f"   {status} {col:22s} → {outliers:4d} aykırı ({pct:.1f}%)")
    
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Veri temizleme: tip dönüşümleri, standardizasyon."""
    print("\n" + "=" * 60)
    print("3. VERİ TEMİZLEME")
    print("=" * 60)
    
    # ── Gereksiz sütunları kaldır ─────────────────────────
    # customer_id'yi index olarak sakla ama analiz sütunlarından çıkar
    print("\n   Sütun temizliği:")
    print("   → customer_id index olarak korunuyor")
    
    # ── Kategorik değişkenleri standartlaştır ──────────────
    print("   → country ve gender değerleri kontrol ediliyor...")
    df["country"] = df["country"].str.strip().str.title()
    df["gender"] = df["gender"].str.strip().str.title()
    
    # Beklenmeyen değer kontrolü
    expected_countries = {"France", "Germany", "Spain"}
    expected_genders = {"Male", "Female"}
    
    actual_countries = set(df["country"].unique())
    actual_genders = set(df["gender"].unique())
    
    if actual_countries != expected_countries:
        unexpected = actual_countries - expected_countries
        print(f"   ⚠ Beklenmeyen country değerleri: {unexpected}")
    else:
        print(f"   ✓ country: {sorted(actual_countries)}")
    
    if actual_genders != expected_genders:
        unexpected = actual_genders - expected_genders
        print(f"   ⚠ Beklenmeyen gender değerleri: {unexpected}")
    else:
        print(f"   ✓ gender: {sorted(actual_genders)}")
    
    # ── Veri tipi optimizasyonu ────────────────────────────
    print("\n   Veri tipi optimizasyonu:")
    
    # Binary sütunları int8'e
    binary_cols = ["credit_card", "active_member", "churn"]
    for col in binary_cols:
        df[col] = df[col].astype("int8")
        print(f"   → {col}: int8")
    
    # products_number → int8
    df["products_number"] = df["products_number"].astype("int8")
    print(f"   → products_number: int8")
    
    # tenure → int8
    df["tenure"] = df["tenure"].astype("int8")
    print(f"   → tenure: int8")
    
    # category tipine çevir
    df["country"] = df["country"].astype("category")
    df["gender"] = df["gender"].astype("category")
    print(f"   → country, gender: category")
    
    mem_after = df.memory_usage(deep=True).sum() / 1024
    print(f"\n   Optimizasyon sonrası bellek: {mem_after:.1f} KB")
    
    return df


def validate_cleaned(df: pd.DataFrame) -> bool:
    """Temizlenmiş verinin doğrulaması."""
    print("\n" + "=" * 60)
    print("4. DOĞRULAMA")
    print("=" * 60)
    
    checks = []
    
    # Satır sayısı kontrolü
    row_ok = len(df) > 0
    checks.append(row_ok)
    print(f"   {'✓' if row_ok else '✗'} Satır sayısı: {len(df):,}")
    
    # Eksik veri kontrolü
    null_ok = df.isnull().sum().sum() == 0
    checks.append(null_ok)
    print(f"   {'✓' if null_ok else '✗'} Eksik veri yok")
    
    # Hedef değişken kontrolü
    churn_vals = set(df["churn"].unique())
    churn_ok = churn_vals == {0, 1}
    checks.append(churn_ok)
    print(f"   {'✓' if churn_ok else '✗'} churn değerleri: {churn_vals}")
    
    # Aralık kontrolleri
    age_ok = df["age"].between(0, 120).all()
    checks.append(age_ok)
    print(f"   {'✓' if age_ok else '✗'} age aralığı: {df['age'].min()}-{df['age'].max()}")
    
    cs_ok = df["credit_score"].between(300, 900).all()
    checks.append(cs_ok)
    print(f"   {'✓' if cs_ok else '✗'} credit_score aralığı: {df['credit_score'].min()}-{df['credit_score'].max()}")
    
    tenure_ok = df["tenure"].between(0, 15).all()
    checks.append(tenure_ok)
    print(f"   {'✓' if tenure_ok else '✗'} tenure aralığı: {df['tenure'].min()}-{df['tenure'].max()}")
    
    bal_ok = (df["balance"] >= 0).all()
    checks.append(bal_ok)
    print(f"   {'✓' if bal_ok else '✗'} balance >= 0")
    
    all_ok = all(checks)
    print(f"\n   {'✅ Tüm doğrulamalar geçti!' if all_ok else '❌ Bazı kontroller başarısız!'}")
    
    return all_ok


def main():
    """Ana pipeline: yükle → kontrol et → temizle → doğrula → kaydet."""
    print("\n🏦 Bank Customer Churn — Veri Temizleme Pipeline'ı")
    print("─" * 60)
    
    # 1. Yükle
    df = load_data(RAW_PATH)
    
    # 2. Kalite kontrolü
    df = check_quality(df)
    
    # 3. Temizle
    df = clean_data(df)
    
    # 4. Doğrula
    is_valid = validate_cleaned(df)
    
    if not is_valid:
        print("\n❌ Doğrulama başarısız — dosya kaydedilmedi!")
        sys.exit(1)
    
    # 5. Kaydet
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    
    print("\n" + "=" * 60)
    print("5. KAYIT")
    print("=" * 60)
    print(f"   ✓ Temiz veri kaydedildi: {OUTPUT_PATH}")
    print(f"   Satır: {df.shape[0]:,}  |  Sütun: {df.shape[1]}")
    
    # Özet
    print("\n" + "=" * 60)
    print("ÖZET")
    print("=" * 60)
    churn_rate = df["churn"].mean() * 100
    print(f"   Toplam müşteri : {len(df):,}")
    print(f"   Churn oranı    : %{churn_rate:.1f}")
    print(f"   Ülkeler        : {sorted(df['country'].unique())}")
    print(f"   Yaş aralığı    : {df['age'].min()} - {df['age'].max()}")
    print(f"\n✅ Temizleme pipeline'ı başarıyla tamamlandı!\n")


if __name__ == "__main__":
    main()
