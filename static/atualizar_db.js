const socket = io();

document.getElementById('processar-btn').addEventListener('click', function () {
    document.getElementById('processar-btn').style.display = 'none';
    document.getElementById('spinner').style.display = 'block';
    const statusModal = new bootstrap.Modal(document.getElementById('statusModal'));
    statusModal.show();

    fetch('/processar_novos_dados', {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            console.log(data.status); // Mensagem de status no console
        })
        .catch(error => {
            console.error('Erro:', error);
            document.getElementById('spinner').style.display = 'none'; // Esconder o spinner
        });
});

socket.on('status_update', function (data) {
    const statusMessages = document.getElementById('status-messages');
    statusMessages.innerHTML += `<p>${data.status}</p>`;
    
    // Mostra o modal se não estiver visível
    
});
socket.on('status_error', function (data) {
    const statusMessages = document.getElementById('status-messages');
    statusMessages.innerHTML += `<p class="text-danger">${data.status}</p>`;
    
});

socket.on('status_done', function (data) {
    const statusMessages = document.getElementById('status-messages');
    statusMessages.innerHTML += `<p><strong>${data.status}</strong></p>`;

    setTimeout(() => {
        location.reload(); // Recarrega a página após 5 segundos
    }, 3000);
});
