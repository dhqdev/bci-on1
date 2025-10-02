// web/static/js/common.js
// Funções JavaScript compartilhadas

// Formata timestamp
function formatTimestamp(date = new Date()) {
    return date.toLocaleTimeString('pt-BR');
}

// Formata data
function formatDate(date = new Date()) {
    return date.toLocaleDateString('pt-BR');
}

// Mostra notificação toast
function showToast(message, type = 'info') {
    // Cria elemento toast se não existir
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999;';
        document.body.appendChild(toastContainer);
    }
    
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6'
    };
    
    const toast = document.createElement('div');
    toast.style.cssText = `
        background: ${colors[type] || colors.info};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        margin-bottom: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        animation: slideIn 0.3s ease-out;
        min-width: 250px;
    `;
    toast.textContent = message;
    
    toastContainer.appendChild(toast);
    
    // Remove após 3 segundos
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Adiciona estilos de animação
if (!document.getElementById('toast-animations')) {
    const style = document.createElement('style');
    style.id = 'toast-animations';
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// Valida email
function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Valida telefone
function validatePhone(phone) {
    return /^\d{10,13}$/.test(phone.replace(/\D/g, ''));
}

// Copia para clipboard
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('✅ Copiado para área de transferência!', 'success');
        return true;
    } catch (error) {
        showToast('❌ Erro ao copiar', 'error');
        return false;
    }
}

// Exporta tabela para CSV
function exportTableToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    if (!table) {
        showToast('❌ Tabela não encontrada', 'error');
        return;
    }
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    for (let row of rows) {
        let cols = row.querySelectorAll('td, th');
        let csvRow = [];
        for (let col of cols) {
            csvRow.push('"' + col.textContent + '"');
        }
        csv.push(csvRow.join(','));
    }
    
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
    
    showToast('✅ Arquivo exportado!', 'success');
}

// Confirma ação
function confirmAction(message) {
    return confirm(message);
}

// Loading overlay
function showLoading(message = 'Carregando...') {
    let overlay = document.getElementById('loading-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
        `;
        
        overlay.innerHTML = `
            <div style="background: white; padding: 30px; border-radius: 12px; text-align: center;">
                <div class="loading-spinner" style="margin: 0 auto 20px;"></div>
                <p style="margin: 0; font-size: 18px; color: #334155;">${message}</p>
            </div>
        `;
        
        document.body.appendChild(overlay);
    }
    overlay.style.display = 'flex';
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Formata número de telefone
function formatPhoneNumber(phone) {
    const cleaned = phone.replace(/\D/g, '');
    if (cleaned.length === 13) {
        return `+${cleaned.slice(0,2)} (${cleaned.slice(2,4)}) ${cleaned.slice(4,9)}-${cleaned.slice(9)}`;
    }
    return phone;
}

// Detecta tema escuro do sistema
function isDarkMode() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
}

// Log debug
function debugLog(...args) {
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.log('[DEBUG]', ...args);
    }
}

// Exporta funções globalmente
window.utils = {
    formatTimestamp,
    formatDate,
    showToast,
    validateEmail,
    validatePhone,
    copyToClipboard,
    exportTableToCSV,
    confirmAction,
    showLoading,
    hideLoading,
    debounce,
    formatPhoneNumber,
    isDarkMode,
    debugLog
};
