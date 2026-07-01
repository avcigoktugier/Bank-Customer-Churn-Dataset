-- ═══════════════════════════════════════════════════════════
-- INTERMEDIATE: int_customer_features
-- ═══════════════════════════════════════════════════════════
-- İş mantığı katmanı. Feature engineering, segmentasyon
-- ve türetilmiş değişkenler burada oluşturulur.
--
-- Kaynak: stg_bank_customers
-- ═══════════════════════════════════════════════════════════

with customers as (
    select * from {{ ref('stg_bank_customers') }}
),

featured as (
    select
        -- ─── Orijinal sütunlar ───────────────────────────
        customer_id,
        credit_score,
        country,
        gender,
        age,
        tenure,
        balance,
        products_number,
        has_credit_card,
        is_active_member,
        estimated_salary,
        is_churned,

        -- ─── Yaş segmentasyonu ───────────────────────────
        case
            when age between 18 and 25 then '18-25'
            when age between 26 and 35 then '26-35'
            when age between 36 and 45 then '36-45'
            when age between 46 and 55 then '46-55'
            when age between 56 and 65 then '56-65'
            else '65+'
        end as age_group,

        -- ─── Bakiye değişkenleri ─────────────────────────
        case when balance = 0 then 1 else 0 end as is_zero_balance,

        case
            when balance = 0 then 'Sıfır'
            when balance < 50000 then 'Düşük'
            when balance < 100000 then 'Orta'
            when balance < 150000 then 'Yüksek'
            else 'Çok Yüksek'
        end as balance_segment,

        round(
            safe_divide(balance, estimated_salary), 4
        ) as balance_salary_ratio,

        -- ─── Kredi skoru segmenti ────────────────────────
        case
            when credit_score < 500 then 'Çok Düşük'
            when credit_score < 600 then 'Düşük'
            when credit_score < 700 then 'Orta'
            when credit_score < 800 then 'İyi'
            else 'Mükemmel'
        end as credit_score_category,

        -- ─── Ürün değişkenleri ───────────────────────────
        round(
            safe_divide(products_number, tenure + 1), 4
        ) as products_per_tenure,

        case when products_number >= 2 then 1 else 0 end as is_multi_product,
        case when products_number >= 3 then 1 else 0 end as is_high_risk_products,

        -- ─── Tenure / Age oranı ──────────────────────────
        round(
            safe_divide(tenure, age), 4
        ) as tenure_age_ratio,

        -- ─── Engagement skoru (0-3) ──────────────────────
        (is_active_member + has_credit_card +
            case when balance > 0 then 1 else 0 end
        ) as engagement_score,

        -- ─── Bileşik risk skoru (0-5) ────────────────────
        (
            case when age >= 45 then 1 else 0 end +
            case when is_active_member = 0 then 1 else 0 end +
            case when products_number >= 3 then 1 else 0 end +
            case when country = 'Germany' then 1 else 0 end +
            case when balance = 0 then 1 else 0 end
        ) as churn_risk_score

    from customers
),

with_segments as (
    select
        *,

        -- Engagement segmenti
        case engagement_score
            when 0 then 'Çok Düşük'
            when 1 then 'Düşük'
            when 2 then 'Orta'
            when 3 then 'Yüksek'
        end as engagement_segment,

        -- Risk segmenti
        case
            when churn_risk_score <= 0 then 'Çok Düşük'
            when churn_risk_score = 1 then 'Düşük'
            when churn_risk_score = 2 then 'Orta'
            when churn_risk_score = 3 then 'Yüksek'
            when churn_risk_score = 4 then 'Çok Yüksek'
            when churn_risk_score >= 5 then 'Kritik'
        end as churn_risk_segment

    from featured
)

select * from with_segments
