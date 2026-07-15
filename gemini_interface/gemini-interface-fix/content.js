(function() {
    'use strict';

    function restaurarInterfaz() {
        // Buscar botones que el sistema haya dejado deshabilitados por error
        const botones = document.querySelectorAll('button[disabled]');
        
        botones.forEach(boton => {
            // Si el texto del botón o su entorno sugiere que es para ejecutar/run
            const texto = boton.innerText.toLowerCase();
            if (texto.includes('run') || texto.includes('ejecutar') || texto.includes('clear')) {
                boton.removeAttribute('disabled');
                boton.style.pointerEvents = 'auto';
                boton.style.cursor = 'pointer';
            }
        });
    }

    // Ejecuta la revisión continuamente cada 2000 milisegundos (2 segundos)
    setInterval(restaurarInterfaz, 2000);
    console.log("[Gemini Extension] Vigilante de botones activado.");
})();