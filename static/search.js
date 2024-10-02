document.getElementById('search-form').addEventListener('submit', function (event) {
    event.preventDefault(); // Evita o reload da página

    const formData = new FormData(this);

    fetch('/search', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            const resultsTable = document.getElementById('results-table');
            resultsTable.innerHTML = ''; // Limpa os resultados anteriores

            if (data.length > 0) {
                console.log(data)
                data.forEach(item => {
                    const row = document.createElement('tr');

                    const linkedinCell = document.createElement('td');
                    linkedinCell.innerHTML = '<a href="' + item.linkedin_url + '" target="_blank">' + item.name + '</a>';
                    row.appendChild(linkedinCell);

                    const emailCell = document.createElement('td');
                    emailCell.textContent = item.email;
                    row.appendChild(emailCell);

                    const desiredRoleCell = document.createElement('td');
                    desiredRoleCell.textContent = item.desired_role;
                    row.appendChild(desiredRoleCell);

                    const countryCell = document.createElement('td');
                    countryCell.textContent = item.contry; // Corrigido para 'country'
                    row.appendChild(countryCell);

                    const englishLevelCell = document.createElement('td');
                    englishLevelCell.textContent = item.english_level;
                    row.appendChild(englishLevelCell);

                    const resumeUrlCell = document.createElement('td');
                    resumeUrlCell.innerHTML = '<a href="' + item.resume_url + '" target="_blank">View resume</a>';
                    row.appendChild(resumeUrlCell);

                    resultsTable.appendChild(row);
                });
            } else {
                const row = document.createElement('tr');
                const cell = document.createElement('td');
                cell.colSpan = 4; 
                cell.textContent = 'No results found.';
                row.appendChild(cell);
                resultsTable.appendChild(row);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
        });
});

document.querySelectorAll('.check-btn').forEach(checkBtn => {
    checkBtn.addEventListener('change', function () {
        const inputField = document.getElementById('termo-input');
        let currentValue = inputField.value.split(', ');

        if (this.checked) {
            currentValue.push(this.value);
        } else {
            currentValue = currentValue.filter(value => value !== this.value);
        }

        inputField.value = currentValue.join(', ');
    });
});
