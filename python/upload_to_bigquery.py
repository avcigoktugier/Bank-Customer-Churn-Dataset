"""
Bank Customer Churn — BigQuery'ye Yükleme Scripti
===================================================
Temizlenmiş ve feature engineering yapılmış veriyi
Google BigQuery veri ambarına yükler.

Ön Koşullar:
    1. Google Cloud hesabı ve proje oluşturulmuş olmalı
    2. BigQuery API etkinleştirilmiş olmalı
    3. Service account JSON key'i indirilmiş olmalı
    4. pip install google-cloud-bigquery pandas-gbq

Kullanım:
    python upload_to_bigquery.py

Ortam Değişkenleri:
    GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
    GCP_PROJECT_ID=your-project-id
"""

import pandas as pd
import os
import sys

# ─── Yapılandırma ────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Google Cloud ayarları — KENDİ BİLGİLERİNLE GÜNCELLE
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "your-gcp-project-id")
BQ_DATASET = "bank_churn"

# Yüklenecek tablolar
TABLES = {
    "raw_customers": os.path.join(PROJECT_ROOT, "data", "raw", "Bank_Customer_Churn_Prediction.csv"),
    "cleaned_customers": os.path.join(PROJECT_ROOT, "data", "processed", "bank_churn_cleaned.csv"),
    "featured_customers": os.path.join(PROJECT_ROOT, "data", "processed", "bank_churn_features.csv"),
}


def check_prerequisites():
    """Ön koşulları kontrol et."""
    print("=" * 60)
    print("1. ÖN KOŞUL KONTROLÜ")
    print("=" * 60)
    
    # google-cloud-bigquery kurulu mu?
    try:
        from google.cloud import bigquery
        print("   ✓ google-cloud-bigquery kurulu")
    except ImportError:
        print("   ✗ google-cloud-bigquery kurulu değil!")
        print("     → pip install google-cloud-bigquery pandas-gbq")
        return False
    
    # Credentials
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if creds_path and os.path.exists(creds_path):
        print(f"   ✓ Credentials: {creds_path}")
    else:
        print("   ⚠ GOOGLE_APPLICATION_CREDENTIALS ayarlanmamış")
        print("     → export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json")
        print("     → Veya gcloud auth application-default login kullanın")
    
    # Project ID
    if GCP_PROJECT_ID == "your-gcp-project-id":
        print("   ⚠ GCP_PROJECT_ID güncellenmemiş!")
        print("     → Bu scriptteki GCP_PROJECT_ID değerini veya")
        print("       export GCP_PROJECT_ID=your-project-id yapın")
        return False
    else:
        print(f"   ✓ Project ID: {GCP_PROJECT_ID}")
    
    return True


def create_dataset(client):
    """BigQuery dataset oluştur (yoksa)."""
    from google.cloud import bigquery
    
    dataset_ref = f"{GCP_PROJECT_ID}.{BQ_DATASET}"
    
    try:
        client.get_dataset(dataset_ref)
        print(f"   ✓ Dataset zaten var: {dataset_ref}")
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"  # veya "EU"
        dataset.description = "Bank Customer Churn Analysis — Bitirme Projesi"
        client.create_dataset(dataset)
        print(f"   ✓ Dataset oluşturuldu: {dataset_ref}")


def upload_table(client, table_name: str, csv_path: str):
    """CSV dosyasını BigQuery'ye yükle."""
    from google.cloud import bigquery
    
    if not os.path.exists(csv_path):
        print(f"   ✗ Dosya bulunamadı: {csv_path}")
        return False
    
    # CSV oku
    df = pd.read_csv(csv_path)
    table_ref = f"{GCP_PROJECT_ID}.{BQ_DATASET}.{table_name}"
    
    # Yükleme ayarları
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Üzerine yaz
        autodetect=True,
    )
    
    try:
        job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
        job.result()  # Tamamlanmasını bekle
        
        table = client.get_table(table_ref)
        print(f"   ✓ {table_name}: {table.num_rows:,} satır yüklendi → {table_ref}")
        return True
    except Exception as e:
        print(f"   ✗ {table_name} yüklenemedi: {e}")
        return False


def verify_upload(client):
    """Yüklenen tabloları doğrula."""
    print("\n" + "=" * 60)
    print("4. DOĞRULAMA SORGULARI")
    print("=" * 60)
    
    queries = {
        "Toplam müşteri": f"SELECT COUNT(*) as cnt FROM `{GCP_PROJECT_ID}.{BQ_DATASET}.raw_customers`",
        "Churn oranı": f"SELECT ROUND(AVG(churn) * 100, 1) as churn_pct FROM `{GCP_PROJECT_ID}.{BQ_DATASET}.cleaned_customers`",
        "Feature sayısı": f"SELECT COUNT(*) as col_cnt FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = 'featured_customers' AND table_schema = '{BQ_DATASET}'",
    }
    
    for label, query in queries.items():
        try:
            result = client.query(query).result()
            for row in result:
                val = list(row.values())[0]
                print(f"   ✓ {label}: {val}")
        except Exception as e:
            print(f"   ✗ {label}: {e}")


def main():
    print("\n☁️  Bank Customer Churn — BigQuery Yükleme Pipeline'ı")
    print("─" * 60)
    
    # 1. Ön koşul kontrolü
    if not check_prerequisites():
        print("\n❌ Ön koşullar sağlanmadı. Yukarıdaki adımları tamamlayın.")
        sys.exit(1)
    
    # 2. Client oluştur
    from google.cloud import bigquery
    client = bigquery.Client(project=GCP_PROJECT_ID)
    
    # 3. Dataset oluştur
    print("\n" + "=" * 60)
    print("2. DATASET OLUŞTURMA")
    print("=" * 60)
    create_dataset(client)
    
    # 4. Tabloları yükle
    print("\n" + "=" * 60)
    print("3. TABLO YÜKLEME")
    print("=" * 60)
    
    success_count = 0
    for table_name, csv_path in TABLES.items():
        if upload_table(client, table_name, csv_path):
            success_count += 1
    
    print(f"\n   {success_count}/{len(TABLES)} tablo başarıyla yüklendi")
    
    # 5. Doğrula
    if success_count > 0:
        verify_upload(client)
    
    print(f"\n✅ BigQuery yükleme pipeline'ı tamamlandı!\n")


if __name__ == "__main__":
    main()
