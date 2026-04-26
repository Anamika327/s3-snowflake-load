-- Ensure all key columns have no nulls
{% test no_nulls_in_key_columns(model, key_columns) %}

SELECT *
FROM {{ model }}
WHERE 1=0
{% for col in key_columns %}
    OR {{ col }} IS NULL
{% endfor %}

{% endtest %}
