-- ═══════════════════════════════════════════════════════════
-- STAGING: stg_bank_customers
-- ═══════════════════════════════════════════════════════════
-- Ham veriyi standardize eder. Sütun isimleri, veri tipleri
-- ve temel filtreleme bu katmanda yapılır.
--
-- Kaynak: BigQuery raw_customers tablosu
-- ═══════════════════════════════════════════════════════════

with source as (
    select * from {{ source('raw', 'raw_customers') }}
),

cleaned as (
    select
        -- Tanımlayıcı
        cast(customer_id as string)             as customer_id,

        -- Sayısal değişkenler
        cast(credit_score as int64)             as credit_score,
        cast(age as int64)                      as age,
        cast(tenure as int64)                   as tenure,
        cast(balance as float64)                as balance,
        cast(products_number as int64)          as products_number,
        cast(estimated_salary as float64)       as estimated_salary,

        -- Kategorik değişkenler (standartlaştırılmış)
        initcap(trim(country))                  as country,
        initcap(trim(gender))                   as gender,

        -- Binary değişkenler
        cast(credit_card as int64)              as has_credit_card,
        cast(active_member as int64)            as is_active_member,

        -- Hedef değişken
        cast(churn as int64)                    as is_churned

    from source
    where customer_id is not null
)

select * from cleaned
