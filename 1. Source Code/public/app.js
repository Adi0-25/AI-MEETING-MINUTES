document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const dashboardGrid = document.getElementById('dashboardGrid');
    const uploadZone = document.getElementById('uploadZone');
    const progressSection = document.getElementById('progressSection');
    const transcriptSection = document.getElementById('transcriptSection');
    const summarySection = document.getElementById('summarySection');
    
    const audioFileInput = document.getElementById('audioFile');
    const uploadArea = document.getElementById('uploadArea');
    const recordBtn = document.getElementById('recordBtn');
    const recordText = document.getElementById('recordText');
    const visualizer = document.getElementById('visualizer');
    
    const progressFill = document.getElementById('progressFill');
    const progressPhase = document.getElementById('progressPhase');
    const progressText = document.getElementById('progressText');
    
    const transcriptText = document.getElementById('transcriptText');
    const detectedLang = document.getElementById('detectedLang');
    const summaryContent = document.getElementById('summaryContent');
    const toastContainer = document.getElementById('toastContainer');
    
    const modelSize = document.getElementById('modelSize');
    const targetLang = document.getElementById('targetLang');
    
    let mediaRecorder = null;
    let audioChunks = [];
    let currentTranscription = null;
    let currentSummary = null;

    // EVENT LISTENERS
    uploadArea.addEventListener('dragover', (e) => { e.preventDefault(); uploadArea.classList.add('drag-over'); });
    uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('drag-over'));
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault(); uploadArea.classList.remove('drag-over');
        if (e.dataTransfer.files.length && e.dataTransfer.files[0].type.startsWith('audio/')) {
            processAudio(e.dataTransfer.files[0]);
        } else {
            showToast('Unsupported file type. Please upload audio.', 'error');
        }
    });

    uploadArea.addEventListener('click', (e) => {
        if (e.target.tagName.toLowerCase() !== 'label' && e.target.htmlFor !== 'audioFile') {
            audioFileInput.click();
        }
    });
    
    audioFileInput.addEventListener('change', (e) => {
        if (e.target.files.length) processAudio(e.target.files[0]);
    });

    recordBtn.addEventListener('click', toggleRecording);
    
    document.getElementById('newMeetingBtn').addEventListener('click', resetDashboard);
    document.getElementById('exportPdfBtn').addEventListener('click', exportToPDF);
    
    document.querySelectorAll('[data-copy]').forEach(btn => {
        btn.addEventListener('click', (e) => handleCopy(e.currentTarget));
    });

    // FUNCTIONS
    async function toggleRecording() {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
            recordBtn.classList.remove('recording');
            recordText.textContent = "Live Record Meeting";
            visualizer.classList.add('hidden');
        } else {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
                mediaRecorder.onstop = () => {
                    stream.getTracks().forEach(t => t.stop());
                    const file = new File([new Blob(audioChunks)], 'live_recording.webm', { type: 'audio/webm' });
                    processAudio(file);
                };
                mediaRecorder.start();
                recordBtn.classList.add('recording');
                recordText.textContent = "Stop Recording...";
                visualizer.classList.remove('hidden');
            } catch (err) {
                showToast('Microphone access denied.', 'error');
            }
        }
    }

    async function processAudio(file) {
        showProgressView();
        
        const fd = new FormData();
        fd.append('audio', file);
        fd.append('model', modelSize.value);

        try {
            updateProgress(15, 'Pipeline Connected', 'Booting Faster-Whisper ASR Engine...');
            const trRes = await fetch('/api/transcribe', { method: 'POST', body: fd });
            if (!trRes.ok) throw new Error((await trRes.json()).error || 'Transcription failed');
            
            const trData = await trRes.json();
            currentTranscription = trData;
            
            updateProgress(65, 'Transcription Complete', 'Running Qwen Semantic Summary...');
            const sumRes = await fetch('/api/summarize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: trData.text,
                    language: trData.language,
                    target_lang: targetLang.value
                })
            });
            
            if (!sumRes.ok) throw new Error((await sumRes.json()).error || 'Summarization failed');
            currentSummary = await sumRes.json();
            
            updateProgress(100, 'Intelligence Rendered', 'Finalizing layout...');
            setTimeout(() => showDashboard(trData, currentSummary), 800);
            
        } catch (err) {
            resetDashboard();
            showToast(err.message, 'error');
        }
    }

    function showProgressView() {
        uploadZone.classList.add('hidden');
        progressSection.classList.remove('hidden');
        transcriptSection.classList.add('hidden');
        summarySection.classList.add('hidden');
        updateProgress(0, 'Initializing', 'Preparing matrices...');
    }

    function updateProgress(percent, phase, text) {
        progressFill.style.width = percent + '%';
        progressPhase.textContent = phase;
        progressText.textContent = text;
    }

    function showDashboard(trData, sumData) {
        progressSection.classList.add('hidden');
        uploadZone.classList.add('hidden');
        
        // Morph Grid
        dashboardGrid.classList.remove('state-initial');
        dashboardGrid.classList.add('state-split');
        
        transcriptSection.classList.remove('hidden');
        summarySection.classList.remove('hidden');
        
        detectedLang.textContent = trData.original_audio_language ? trData.original_audio_language.toUpperCase() : 'EN';
        transcriptText.textContent = trData.text;
        
        summaryContent.innerHTML = sumData.professional_minutes ? marked.parse(sumData.professional_minutes) : '<p>Summary failed.</p>';
        showToast('Meeting intelligence extracted successfully.', 'success');
    }

    function resetDashboard() {
        dashboardGrid.classList.remove('state-split');
        dashboardGrid.classList.add('state-initial');
        uploadZone.classList.remove('hidden');
        progressSection.classList.add('hidden');
        transcriptSection.classList.add('hidden');
        summarySection.classList.add('hidden');
        audioFileInput.value = '';
    }

    function handleCopy(btn) {
        const targetId = btn.dataset.copy;
        const text = targetId === 'transcriptText' ? transcriptText.textContent : currentSummary?.professional_minutes;
        if (!text) return;
        
        navigator.clipboard.writeText(text).then(() => {
            showToast('Copied to clipboard', 'success');
        });
    }

    function exportToPDF() {
        if (!currentSummary) return showToast('No data to export', 'error');
        const d = new Date().toISOString().split('T')[0];
        const filename = `Minutes_${d}.pdf`;
        
        const html = `
            <div style="padding:40px; font-family:Helvetica; color:#000; background:#fff;">
                <h1 style="color:#000; border-bottom:1px solid #ccc;">Meeting Minutes (${d})</h1>
                ${marked.parse(currentSummary.professional_minutes)}
            </div>
        `;
        
        showToast('Generating PDF...', 'info');
        const btn = document.getElementById('exportPdfBtn');
        const originalText = btn.innerHTML;
        btn.innerHTML = 'Exporting...';
        btn.disabled = true;

        const opt = {
            margin: 0.5, 
            filename: filename,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2, useCORS: true, backgroundColor: '#ffffff' },
            jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
        };

        const container = document.createElement('div');
        container.innerHTML = html;

        html2pdf().set(opt).from(container).outputPdf('datauristring').then(async function(base64str) {
            try {
                const response = await fetch('/api/save_pdf', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        pdf_base64: base64str,
                        filename: filename
                    })
                });
                
                const result = await response.json();
                if (response.ok) {
                    showToast('PDF Saved directly to Project Folder!', 'success');
                } else {
                    showToast(result.error || 'Failed to save', 'error');
                }
            } catch (err) {
                showToast('Network error while saving', 'error');
            }
            btn.innerHTML = originalText;
            btn.disabled = false;
        }).catch(err => {
            console.error(err);
            showToast('Failed to generate PDF', 'error');
            btn.innerHTML = originalText;
            btn.disabled = false;
        });
    }

    function showToast(msg, type='info') {
        const t = document.createElement('div');
        t.style.cssText = `
            background: ${type==='error'?'#ef4444':'var(--neon-cyan)'};
            color: ${type==='error'?'#fff':'#000'};
            padding: 12px 24px; border-radius: 8px; font-weight: 500;
            margin-top: 10px; opacity: 0; transform: translateY(20px);
            transition: all 0.3s;
        `;
        t.textContent = msg;
        toastContainer.appendChild(t);
        
        requestAnimationFrame(() => { t.style.opacity=1; t.style.transform='translateY(0)'; });
        setTimeout(() => {
            t.style.opacity = 0;
            setTimeout(() => t.remove(), 300);
        }, 3000);
    }
});
