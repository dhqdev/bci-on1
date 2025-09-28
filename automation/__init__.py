# automation/__init__.py
# Módulo de automação

from .servopa_automation import (
    complete_servopa_automation,
    navigate_to_consorcio_selection,
    fill_grupo_and_search,
    select_first_client,
    navigate_to_lances
)

__all__ = [
    'complete_servopa_automation',
    'navigate_to_consorcio_selection', 
    'fill_grupo_and_search',
    'select_first_client',
    'navigate_to_lances'
]