-- ═══════════════════════════════════════════════════════════
-- MARTS: dim_customers
-- ═══════════════════════════════════════════════════════════
-- Müşteri dimension tablosu. Dashboard'larda filtre ve
-- drill-down için kullanılacak ana referans tablo.
-- ═══════════════════════════════════════════════════════════

with features as (
    select * from {{ ref('int_customer_features') }}
)

select
    customer_id,
    country,
    gender,
    age,
    age_group,
    tenure,
    credit_score,
    credit_score_category,
    balance,
    balance_segment,
    is_zero_balance,
    estimated_salary,
    products_number,
    is_multi_product,
    has_credit_card,
    is_active_member,
    engagement_score,
    engagement_segment,
    churn_risk_score,
    churn_risk_segment,
    is_churned

from features
