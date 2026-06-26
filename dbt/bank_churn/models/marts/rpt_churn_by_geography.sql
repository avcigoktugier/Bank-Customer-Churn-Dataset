-- ═══════════════════════════════════════════════════════════
-- MARTS: rpt_churn_by_geography
-- ═══════════════════════════════════════════════════════════
-- Ülke bazlı churn raporu. Looker Studio ve Power BI'da
-- coğrafi analiz dashboard'u için kullanılacak.
-- ═══════════════════════════════════════════════════════════

with features as (
    select * from {{ ref('int_customer_features') }}
)

select
    country,
    gender,

    -- Müşteri sayıları
    count(*) as total_customers,
    sum(is_churned) as churned_customers,
    count(*) - sum(is_churned) as retained_customers,

    -- Churn oranları
    round(avg(cast(is_churned as float64)) * 100, 1) as churn_rate_pct,
    round((1 - avg(cast(is_churned as float64))) * 100, 1) as retention_rate_pct,

    -- Ortalama metrikler
    round(avg(age), 1) as avg_age,
    round(avg(credit_score), 0) as avg_credit_score,
    round(avg(balance), 0) as avg_balance,
    round(avg(estimated_salary), 0) as avg_salary,
    round(avg(products_number), 2) as avg_products,
    round(avg(tenure), 1) as avg_tenure,

    -- Segment dağılımları
    round(avg(cast(is_active_member as float64)) * 100, 1) as active_member_pct,
    round(avg(cast(has_credit_card as float64)) * 100, 1) as credit_card_pct,
    round(avg(cast(is_zero_balance as float64)) * 100, 1) as zero_balance_pct,

    -- Risk dağılımı
    round(avg(churn_risk_score), 2) as avg_risk_score

from features
group by country, gender
order by churn_rate_pct desc
