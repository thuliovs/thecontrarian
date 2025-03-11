/**
 * logout.js - Script para garantir que o logout seja completo
 * 
 * Este script:
 * 1. Adiciona um evento de clique ao botão de logout
 * 2. Limpa cookies e armazenamento local relacionados à autenticação
 * 3. Redireciona para a página de logout do Django
 */

document.addEventListener('DOMContentLoaded', function() {
    // Encontrar todos os links de logout na página
    const logoutLinks = document.querySelectorAll('a[href*="logout"]');
    
    // Adicionar evento de clique a cada link de logout
    logoutLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            // Prevenir o comportamento padrão do link
            event.preventDefault();
            
            // URL original para onde o link iria redirecionar
            const logoutUrl = this.getAttribute('href');
            
            // Limpar cookies relacionados à sessão
            clearSessionCookies();
            
            // Limpar armazenamento local
            clearLocalStorage();
            
            // Redirecionar para a URL de logout após um pequeno atraso
            setTimeout(() => {
                window.location.href = logoutUrl;
            }, 100);
        });
    });
    
    // Função para limpar cookies relacionados à sessão
    function clearSessionCookies() {
        // Obter todos os cookies
        const cookies = document.cookie.split(';');
        
        // Para cada cookie, definir uma data de expiração no passado
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i];
            const eqPos = cookie.indexOf('=');
            const name = eqPos > -1 ? cookie.substr(0, eqPos).trim() : cookie.trim();
            
            // Excluir cookies relacionados à sessão
            if (name.includes('sessionid') || name.includes('csrftoken')) {
                document.cookie = name + '=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/';
            }
        }
    }
    
    // Função para limpar armazenamento local
    function clearLocalStorage() {
        // Remover itens específicos relacionados à autenticação
        localStorage.removeItem('user_authenticated');
        localStorage.removeItem('user_data');
        
        // Opcionalmente, limpar todo o armazenamento local
        // localStorage.clear();
    }
}); 