document.getElementById('toggle-dark-mode').addEventListener('click', function() {
    const body = document.body;
    const darkMode = body.classList.toggle('dark-mode');

    // Enviar a alteração para o servidor via POST usando fetch
    fetch('/set_dark_mode', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ dark_mode: darkMode })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erro na requisição');
        }
        return response.json();
    })
    .then(data => {
        console.log('Modo de cor alterado para: ' + data.mode);
    })
    .catch(error => {
        console.error('Erro ao alterar o modo de cor:', error);
    });
});