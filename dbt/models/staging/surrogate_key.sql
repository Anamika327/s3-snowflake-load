-- Generate surrogate key using MD5 hash
{% macro surrogate_key(field_list) %}
    MD5(CONCAT(
        {% for field in field_list %}
            CAST({{ field }} AS VARCHAR),
            {% if not loop.last %}'||'{% endif %}
        {% endfor %}
    ))
{% endmacro %}
