{# Par défaut, dbt préfixe le schéma personnalisé par celui de la cible (analytics_staging).
   Cette surcharge utilise directement les noms "staging" et "marts". #}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
