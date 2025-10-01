# utils/config.py
# Configurações globais do sistema

import os

# Configurações do Servopa
SERVOPA_CONFIG = {
    'LOGIN_URL': "https://www.consorcioservopa.com.br/vendas/login",
    'DASHBOARD_URL': "https://www.consorcioservopa.com.br/vendas/dashboard", 
    'PAINEL_URL': "https://www.consorcioservopa.com.br/vendas/painel",
    'LANCES_URL': "https://www.consorcioservopa.com.br/vendas/lances",
    'LOGIN': os.getenv("SERVOPA_LOGIN", "26.350.659/0001-61"),
    'SENHA': os.getenv("SERVOPA_SENHA", "43418")
}

# Configurações do Todoist
TODOIST_CONFIG = {
    'LOGIN_URL': "https://app.todoist.com/auth/login",
    'EMAIL': "oscarifn6@gmail.com",
    'PASSWORD': "spfctri12",
    'PROJECT_NAME': "Lances Servopa Outubro Dia 8",
    'TASK_PATTERN': r'(\d+) - dia \d+'
}

# Configurações gerais
GENERAL_CONFIG = {
    'TIMEOUT': 20,
    'HEADLESS': False,
    'DELAYS': {
        'NATURAL_TYPING': 0.1,
        'BETWEEN_ACTIONS': 1,
        'PAGE_LOAD': 3,
        'LOGIN_WAIT': 10
    }
}

# Configurações da interface
UI_CONFIG = {
    'WINDOW_SIZE': '900x700',
    'COLORS': {
        'primary': '#3498db',
        'success': '#2ecc71', 
        'warning': '#f39c12',
        'danger': '#e74c3c',
        'dark': '#2c3e50',
        'light': '#ecf0f1',
        'secondary': '#95a5a6'
    }
}