document.querySelectorAll('form[data-confirmacion]').forEach((formulario) => {
    formulario.addEventListener('submit', (evento) => {
        if (!window.confirm(formulario.dataset.confirmacion)) {
            evento.preventDefault();
        }
    });
});
