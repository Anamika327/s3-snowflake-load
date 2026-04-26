-- Logging macro for debugging
{% macro log_info(message) %}
    {% if execute %}
        {% do log(message, info=true) %}
    {% endif %}
{% endmacro %}
