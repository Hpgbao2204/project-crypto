// Main JavaScript for the Secure Document System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Policy editor functionality
    setupPolicyEditor();

    // File upload preview
    setupFileUploadPreview();
});

function setupPolicyEditor() {
    const policyInput = document.getElementById('policy');
    const attributeTags = document.querySelectorAll('.attribute-tag');
    const operatorButtons = document.querySelectorAll('.operator-btn');
    
    if (!policyInput) return;

    // Add attribute to policy when clicked
    attributeTags.forEach(tag => {
        tag.addEventListener('click', function() {
            const attribute = this.getAttribute('data-attribute');
            addToPolicy(attribute);
        });
    });

    // Add operator to policy when clicked
    operatorButtons.forEach(button => {
        button.addEventListener('click', function() {
            const operator = this.getAttribute('data-operator');
            addToPolicy(` ${operator} `);
        });
    });

    function addToPolicy(text) {
        if (policyInput.selectionStart || policyInput.selectionStart === 0) {
            const startPos = policyInput.selectionStart;
            const endPos = policyInput.selectionEnd;
            policyInput.value = policyInput.value.substring(0, startPos) + text + policyInput.value.substring(endPos, policyInput.value.length);
            policyInput.focus();
            policyInput.selectionStart = startPos + text.length;
            policyInput.selectionEnd = startPos + text.length;
        } else {
            policyInput.value += text;
        }
    }
}

function setupFileUploadPreview() {
    const fileInput = document.querySelector('input[type="file"]');
    const previewContainer = document.getElementById('file-preview');
    
    if (!fileInput || !previewContainer) return;

    fileInput.addEventListener('change', function() {
        previewContainer.innerHTML = '';
        
        if (this.files && this.files[0]) {
            const file = this.files[0];
            const fileInfo = document.createElement('div');
            fileInfo.className = 'mt-3 p-3 border rounded';
            
            // Display file information
            fileInfo.innerHTML = `
                <h5><i class="fas fa-file me-2"></i>${file.name}</h5>
                <p class="mb-1"><strong>Type:</strong> ${file.type || 'Unknown'}</p>
                <p class="mb-1"><strong>Size:</strong> ${formatFileSize(file.size)}</p>
                <p class="mb-0"><strong>Last Modified:</strong> ${new Date(file.lastModified).toLocaleString()}</p>
            `;
            
            previewContainer.appendChild(fileInfo);
            
            // If it's an image, show preview
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.className = 'img-fluid mt-3 border rounded';
                    img.style.maxHeight = '300px';
                    previewContainer.appendChild(img);
                }
                reader.readAsDataURL(file);
            }
        }
    });
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Confirm delete
function confirmDelete(formId) {
    if (confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
        document.getElementById(formId).submit();
    }
    return false;
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        alert('Copied to clipboard!');
    }, function(err) {
        console.error('Could not copy text: ', err);
    });
}
