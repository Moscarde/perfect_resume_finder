document.addEventListener("DOMContentLoaded", function() {
    const eventSource = new EventSource('/status_updates');

    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        const statusMessages = document.getElementById('status-messages');

        if (data.event === 'status_done') {
            pClass = 'text-success';
        } else if (data.event === 'status_error') {
            pClass = 'text-danger';
        } else {
            pClass = '';
        }
        statusMessages.innerHTML += `<p class="${pClass}">${data.status}</p>`;

        if (data.event === 'status_done') {
            setTimeout(() => {
                location.reload();
            }, 3000);
        }
    };

    eventSource.onerror = function() {
        console.error("Erro ao conectar ao servidor.");
    };
});

document.getElementById('process-btn').addEventListener('click', function () {
    document.getElementById('process-btn').style.display = 'none';
    document.getElementById('spinner').style.display = 'block';
    const statusModal = new bootstrap.Modal(document.getElementById('statusModal'));
    statusModal.show();

    fetch('/process_database', {
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

// socket.on('status_update', function (data) {
//     const statusMessages = document.getElementById('status-messages');
//     statusMessages.innerHTML += `<p>${data.status}</p>`;
    
//     // Mostra o modal se não estiver visível
    
// });
// socket.on('status_error', function (data) {
//     const statusMessages = document.getElementById('status-messages');
//     statusMessages.innerHTML += `<p class="text-danger">${data.status}</p>`;
    
// });

// socket.on('status_done', function (data) {
//     const statusMessages = document.getElementById('status-messages');
//     statusMessages.innerHTML += `<p><strong>${data.status}</strong></p>`;

//     setTimeout(() => {
//         location.reload(); // Recarrega a página após 5 segundos
//     }, 3000);
// });
