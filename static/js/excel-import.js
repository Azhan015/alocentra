// Universal excel import for rooms and faculty
let parsedData = [];
let currentImportType = ''; // 'rooms' or 'faculty'

document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('excelFile');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);

        const dropZone = document.getElementById('dropZone');
        if (dropZone) {
            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.style.background = 'rgba(108,99,255,0.1)';
            });
            dropZone.addEventListener('dragleave', (e) => {
                e.preventDefault();
                dropZone.style.background = 'rgba(108,99,255,0.05)';
            });
            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.style.background = 'rgba(108,99,255,0.05)';
                if (e.dataTransfer.files.length) {
                    fileInput.files = e.dataTransfer.files;
                    handleFileSelect({ target: fileInput });
                }
            });
        }
    }
});

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;

    currentImportType = window.location.pathname.includes('/faculty/') ? 'faculty' : 'rooms';

    const reader = new FileReader();
    reader.onload = function (e) {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array' });
        const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
        let rawData = XLSX.utils.sheet_to_json(firstSheet, { header: 1 });
        if (rawData.length < 2) {
            alert('File seems empty or missing headers.');
            return;
        }

        parsedData = [];
        const headers = rawData[0].map(h => String(h).toLowerCase().replace(/[^a-z0-9]/g, ''));

        for (let i = 1; i < rawData.length; i++) {
            const row = rawData[i];
            if (row.length === 0 || !row[0]) continue; // skip empty
            let rowObj = {};
            if (currentImportType === 'rooms') {
                const rIdx = headers.findIndex(h => h.includes('room'));
                const cIdx = headers.findIndex(h => h.includes('capacity'));
                if (rIdx > -1) rowObj.room_no = row[rIdx];
                if (cIdx > -1) rowObj.capacity = row[cIdx];
            } else if (currentImportType === 'faculty') {
                const nIdx = headers.findIndex(h => h.includes('name'));
                const dIdx = headers.findIndex(h => h.includes('designation'));
                const depIdx = headers.findIndex(h => h.includes('department'));
                const eIdx = headers.findIndex(h => h.includes('email'));
                if (nIdx > -1) rowObj.name = row[nIdx];
                if (dIdx > -1) rowObj.designation = row[dIdx];
                if (depIdx > -1) rowObj.department = row[depIdx];
                if (eIdx > -1) rowObj.email = row[eIdx];
            }
            parsedData.push(rowObj);
        }

        renderPreview();
    };
    reader.readAsArrayBuffer(file);
}

function renderPreview() {
    document.getElementById('importStep1').classList.add('d-none');
    document.getElementById('importStep2').classList.remove('d-none');
    document.getElementById('previewCount').innerText = parsedData.length;

    const tbody = document.getElementById('previewTbody');
    tbody.innerHTML = '';

    const previewData = parsedData.slice(0, 100);

    previewData.forEach(row => {
        const tr = document.createElement('tr');
        if (currentImportType === 'rooms') {
            tr.innerHTML = `<td>${row.room_no || ''}</td><td>${row.capacity || ''}</td>`;
        } else {
            tr.innerHTML = `<td>${row.name || ''}</td><td>${row.designation || ''}</td><td>${row.department || ''}</td><td>${row.email || ''}</td>`;
        }
        tbody.appendChild(tr);
    });
}

function resetImport() {
    document.getElementById('excelFile').value = '';
    parsedData = [];
    document.getElementById('importStep2').classList.add('d-none');
    document.getElementById('importStep1').classList.remove('d-none');
}

function confirmImportFaculty() {
    const url = currentImportType === 'rooms' ? '/rooms/import/confirm/' : '/faculty/import/confirm/';
    const bodyKey = currentImportType === 'rooms' ? 'rooms' : 'faculty';

    fetch(url, {
        method: 'POST',
        headers: { 'X-CSRFToken': CSRF_TOKEN, 'Content-Type': 'application/json' },
        body: JSON.stringify({ [bodyKey]: parsedData })
    })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert(data.message);
            }
        });
}
