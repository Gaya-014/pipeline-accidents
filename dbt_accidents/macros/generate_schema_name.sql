{# Par défaut dbt colle le nom du schéma de base au nom demandé (analytics_staging).
   Je veux des schémas propres : "staging" et "marts". #}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
