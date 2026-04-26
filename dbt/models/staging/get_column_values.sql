-- Get unique column values for testing
{% macro get_column_values(table, column) %}

    {% set results = run_query("SELECT DISTINCT " ~ column ~ " FROM " ~ table) %}
    
    {% if execute %}
        {% set values = results.columns[0].values() %}
        {% for value in values %}
            {{ value }}
            {%- if not loop.last %}, {% endif %}
        {% endfor %}
    {% endif %}

{% endmacro %}
