/**
 * responsive.js - Script para melhorar a responsividade do site
 * 
 * Este script:
 * 1. Fecha automaticamente o menu móvel após clicar em um item
 * 2. Ajusta elementos baseado no tamanho da tela
 * 3. Adiciona comportamentos de toque específicos para dispositivos móveis
 */

document.addEventListener('DOMContentLoaded', function() {
    // Referência ao botão de toggler e ao container do navbar
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    // Fechar automaticamente o menu móvel após clicar em qualquer link
    document.querySelectorAll('.navbar-nav .nav-item a').forEach(item => {
        item.addEventListener('click', () => {
            if (window.innerWidth < 992 && navbarCollapse.classList.contains('show')) {
                // Usar API do Bootstrap para fechar o menu
                const bsCollapse = new bootstrap.Collapse(navbarCollapse);
                bsCollapse.hide();
            }
        });
    });
    
    // Ajustar elementos baseados no tamanho da tela
    function adjustElementsForScreenSize() {
        const isMobile = window.innerWidth < 768;
        
        // Ajustar formulários para visibilidade no móvel
        document.querySelectorAll('.form-layout').forEach(form => {
            if (isMobile) {
                form.style.position = 'relative';
                form.style.top = 'auto';
                form.style.left = 'auto';
                form.style.transform = 'none';
                form.style.margin = '30px auto';
            } else {
                form.style.position = '';
                form.style.top = '';
                form.style.left = '';
                form.style.transform = '';
                form.style.margin = '';
            }
        });
    }
    
    // Executar os ajustes no carregamento da página
    adjustElementsForScreenSize();
    
    // Executar os ajustes quando a janela for redimensionada
    window.addEventListener('resize', adjustElementsForScreenSize);
}); 