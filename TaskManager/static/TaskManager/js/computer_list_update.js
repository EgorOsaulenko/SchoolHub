// Auto-update status for computer list
(function() {
    const meta = document.getElementById('computer-list-meta');
    if (!meta) return;

    const hasPermissionMS = meta.dataset.hasPermission === 'true';
    const apiUrl = meta.dataset.apiUrl;

    function updateStatus() {
        fetch(apiUrl)
            .then(response => response.json())
            .then(data => {
                data.computers.forEach(comp => {
                    const container = document.getElementById(`status-container-${comp.id}`);
                    if (!container) return;

                    let html = '';
                    if (comp.session) {
                        html += `<div class="alert alert-info py-2 mb-3"><small class="d-block text-muted">Гравець:</small><strong>${comp.session.user}</strong><hr class="my-1"><small>Тариф: ${comp.session.tariff}</small><br><small>Початок: ${comp.session.start_time}</small></div>`;
                        if (hasPermissionMS) {
                            html += `<a href="/schedule/session/stop/${comp.session.id}/" class="btn btn-danger w-100 mt-auto">Завершити сесію</a>`;
                        }
                    } else {
                        const badgeClass = comp.status === 'FR' ? 'text-bg-success' : 'text-bg-danger';
                        html += `<div class="mb-3"><span class="badge rounded-pill ${badgeClass} px-3 py-2">${comp.status_display}</span></div>`;
                        if (comp.status === 'FR') {
                            if (hasPermissionMS) {
                                html += `<a href="/schedule/session/start/${comp.id}/" class="btn btn-primary w-100 mt-auto">Відкрити сесію</a>`;
                            } else {
                                html += `<a href="/schedule/booking/${comp.id}/" class="btn btn-success w-100 mt-auto">Забронювати</a>`;
                            }
                        }
                    }
                    container.innerHTML = html;
                });
            })
            .catch(() => {});
    }

    updateStatus();
    setInterval(updateStatus, 5000);
})();
