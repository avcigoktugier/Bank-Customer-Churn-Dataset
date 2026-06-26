-- ═══════════════════════════════════════════════════════════
-- MARTS: fct_churn_analysis
-- ═══════════════════════════════════════════════════════════
-- Churn analizi için özet metrikler. Her müşterinin tüm
-- feature'ları ve hesaplanmış metrikleriyle birlikte
-- dashboard'lara doğrudan bağlanabilecek fact tablosu.
-- ═══════════════════════════════════════════════════════════

with features as (
    select * from {{ ref('int_customer_features') }}
),

-- Global ortalamalar (karşılaştırma için)
global_stats as (
    select
        avg(credit_score) as avg_credit_score,
        avg(age) as avg_age,
        avg(balance) as avg_balance,
        avg(estimated_salary) as avg_salary,
        avg(cast(is_churned as float64)) as overall_churn_rate
    from features
)

select
    f.customer_id,
    f.country,
    f.gender,
    f.age,
    f.age_group,
    f.tenure,
    f.credit_score,
    f.credit_score_category,
    f.balance,
    f.balance_segment,
    f.balance_salary_ratio,
    f.estimated_salary,
    f.products_number,
    f.products_per_tenure,
    f.has_credit_card,
    f.is_active_member,
    f.is_zero_balance,
    f.is_multi_product,
    f.is_high_risk_products,
    f.tenure_age_ratio,
    f.engagement_score,
    f.engagement_segment,
    f.churn_risk_score,
    f.churn_risk_segment,
    f.is_churned,

    -- Ortalamadan sapma
    round(f.credit_score - g.avg_credit_score, 2) as credit_score_vs_avg,
    round(f.age - g.avg_age, 2) as age_vs_avg,
    round(f.balance - g.avg_balance, 2) as balance_vs_avg,

    -- Churn olasılık tahmini (basit kural tabanlı)
    round(
        case
            when f.churn_risk_score >= 4 then 0.95
            when f.churn_risk_score = 3 then 0.70
            when f.churn_risk_score = 2 then 0.25
            when f.churn_risk_score = 1 then 0.12
            else 0.08
        end, 2
    ) as estimated_churn_probability

from features f
cross join global_stats g
