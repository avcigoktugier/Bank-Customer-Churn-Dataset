-- ═══════════════════════════════════════════════════════════
-- MARTS: rpt_churn_by_segment
-- ═══════════════════════════════════════════════════════════
-- Çoklu segment bazlı churn raporu. Risk skoru, yaş grubu,
-- engagement ve ürün sayısı kırılımlarında churn analizi.
-- ═══════════════════════════════════════════════════════════

with features as (
    select * from {{ ref('int_customer_features') }}
),

-- Risk segmentine göre
risk_segments as (
    select
        'Risk Segmenti' as segment_type,
        churn_risk_segment as segment_value,
        churn_risk_score as sort_order,
        count(*) as total_customers,
        sum(is_churned) as churned_customers,
        round(avg(cast(is_churned as float64)) * 100, 1) as churn_rate_pct,
        round(avg(balance), 0) as avg_balance,
        round(avg(age), 1) as avg_age
    from features
    group by churn_risk_segment, churn_risk_score
),

-- Yaş grubuna göre
age_segments as (
    select
        'Yaş Grubu' as segment_type,
        age_group as segment_value,
        case age_group
            when '18-25' then 1 when '26-35' then 2
            when '36-45' then 3 when '46-55' then 4
            when '56-65' then 5 else 6
        end as sort_order,
        count(*) as total_customers,
        sum(is_churned) as churned_customers,
        round(avg(cast(is_churned as float64)) * 100, 1) as churn_rate_pct,
        round(avg(balance), 0) as avg_balance,
        round(avg(age), 1) as avg_age
    from features
    group by age_group
),

-- Engagement segmentine göre
engagement_segments as (
    select
        'Engagement' as segment_type,
        engagement_segment as segment_value,
        engagement_score as sort_order,
        count(*) as total_customers,
        sum(is_churned) as churned_customers,
        round(avg(cast(is_churned as float64)) * 100, 1) as churn_rate_pct,
        round(avg(balance), 0) as avg_balance,
        round(avg(age), 1) as avg_age
    from features
    group by engagement_segment, engagement_score
),

-- Ürün sayısına göre
product_segments as (
    select
        'Ürün Sayısı' as segment_type,
        cast(products_number as string) as segment_value,
        products_number as sort_order,
        count(*) as total_customers,
        sum(is_churned) as churned_customers,
        round(avg(cast(is_churned as float64)) * 100, 1) as churn_rate_pct,
        round(avg(balance), 0) as avg_balance,
        round(avg(age), 1) as avg_age
    from features
    group by products_number
),

-- Bakiye segmentine göre
balance_segments as (
    select
        'Bakiye Segmenti' as segment_type,
        balance_segment as segment_value,
        case balance_segment
            when 'Sıfır' then 0 when 'Düşük' then 1
            when 'Orta' then 2 when 'Yüksek' then 3
            else 4
        end as sort_order,
        count(*) as total_customers,
        sum(is_churned) as churned_customers,
        round(avg(cast(is_churned as float64)) * 100, 1) as churn_rate_pct,
        round(avg(balance), 0) as avg_balance,
        round(avg(age), 1) as avg_age
    from features
    group by balance_segment
)

select * from risk_segments
union all
select * from age_segments
union all
select * from engagement_segments
union all
select * from product_segments
union all
select * from balance_segments
order by segment_type, sort_order
