-- Generate date dimension
{% macro date_spine(datepart, start_date, end_date) %}

    {% set begin_date = run_started_at.strptime('%Y-%m-%d', '%Y-%m-%d') if execute else none %}
    
    WITH date_spine AS (
        SELECT CAST(calendar_date AS DATE) AS date_day
        FROM (
            SELECT 
                '{{ start_date }}'::DATE + (interval '1 day' * seq4()) AS calendar_date
            FROM TABLE(GENERATOR(ROWCOUNT => 
                (('{{ end_date }}'::DATE - '{{ start_date }}'::DATE))
            ))
        )
    )
    
    SELECT date_day FROM date_spine

{% endmacro %}
