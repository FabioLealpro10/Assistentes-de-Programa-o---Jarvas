document.addEventListener('DOMContentLoaded', function () {
    const overlay = document.getElementById('loading-overlay');
    if (!overlay) return;

    const loadingText = overlay.querySelector('.loading-text');

    function showLoading(text) {
        if (text && loadingText) {
            loadingText.textContent = text;
        }
        overlay.classList.add('active');
    }

    function hideLoading() {
        overlay.classList.remove('active');
    }

    hideLoading();

    document.querySelectorAll('form').forEach(function (form) {
        form.addEventListener('submit', function () {
            if (form.classList.contains('chat-input-form')) {
                showLoading('JARVAS está pensando... <br> Tempo estimado: 1 a 5 minutos');
            } else {
                showLoading('Carregando...');
            }
        });
    });

    document.querySelectorAll('a[href]').forEach(function (link) {
        link.addEventListener('click', function (event) {
            const href = link.getAttribute('href');
            const target = link.getAttribute('target');

            if (!href || href.startsWith('#') || href.startsWith('javascript:')) {
                return;
            }

            if (target === '_blank') {
                return;
            }

            showLoading('Carregando...');
        });
    });

    window.addEventListener('pageshow', function (event) {
        if (event.persisted) {
            hideLoading();
        }
    });
});
