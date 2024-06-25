document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const dragDropArea = document.getElementById('drag-drop-area');
    const resultContent = document.getElementById('result-content');
    const downloadBtn = document.getElementById('download-btn');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        await convertSQL(formData);
    });

    dragDropArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        dragDropArea.classList.add('dragover');
    });

    dragDropArea.addEventListener('dragleave', () => {
        dragDropArea.classList.remove('dragover');
    });

    dragDropArea.addEventListener('drop', async (e) => {
        e.preventDefault();
        dragDropArea.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file && file.name.endsWith('.sql')) {
            fileInput.files = e.dataTransfer.files;
            const formData = new FormData();
            formData.append('file', file);
            await convertSQL(formData);
        } else {
            alert('Please upload a .sql file');
        }
    });

    async function convertSQL(formData) {
        try {
            console.log('Sending conversion request');  // Debug log
            const response = await fetch('/convert', {
                method: 'POST',
                body: formData
            });

            console.log('Response status:', response.status);  // Debug log

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                downloadBtn.href = url;
                downloadBtn.download = 'converted_sql.sql';
                downloadBtn.style.display = 'inline-block';
                resultContent.textContent = 'Conversion successful! Click the download button to get your converted SQL file.';
            } else {
                const errorText = await response.text();
                resultContent.textContent = `Error: ${errorText}`;
                console.error('Conversion error:', errorText);  // Debug log
            }
        } catch (error) {
            resultContent.textContent = `Error: ${error.message}`;
            console.error('Fetch error:', error);  // Debug log
        }
    }
});