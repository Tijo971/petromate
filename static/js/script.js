function showError(el, message= "This field is required!"){
    el.classList.add("is-invalid");
    feedback = el.nextElementSibling
    if(feedback?.classList.contains("invalid-feedback")){
        feedback.textContent = message
    }
    el.focus()
}

function showSelect2Error(el, message= "This field is required!"){
    const select2Container = el.nextElementSibling;
    if (select2Container && select2Container.classList.contains('select2')) {
        const selection = select2Container.querySelector('.select2-selection');
        if (selection) {
            selection.classList.add('is-invalid');
        }
    }
    feedback = select2Container.nextElementSibling;
    if (feedback.classList.contains("invalid-feedback")){
        feedback.style.display = "block";
        feedback.textContent = message
    }
    el.focus()
}

function resetErrors(form){
    form.querySelectorAll(".is-invalid").forEach(el => el.classList.remove("is-invalid"));
    form.querySelectorAll(".invalid-feedback").forEach(el => el.textContent = "");
}

function isValidEmail(email) {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return pattern.test(email);
}


// Function to get CSRF token from cookie (Django default)
function getCSRFToken() {
    let cookieValue = null;
    const name = 'csrftoken';
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function fetchData(url, method = 'GET', data = null) {
    const options = {
        method, 
        headers: { 
            'Content-Type': 'application/json', 
        } 
    };
    if (method === 'POST') options.headers["X-CSRFToken"] = getCSRFToken() // CSRF token header 
    if (method === 'POST' && data) options.body = JSON.stringify(data);

    const response = await fetch(url, options);
    if (!response.ok) throw new Error('Network error: ' + response.status);
    return await response.json();
}


function confirmDelete() {
    url = this.dataset.url
    action = this.dataset.action || "delete"

    if(url) {
        Swal.fire({
            title: 'Are you sure?',
            text: `Do you want to ${action}?`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: `Yes, ${action} it!`,
            cancelButtonText: 'Cancel'
        }).then((result) => {
            if (result.isConfirmed) {
                // ✅ Action if confirmed (example: submit form or redirect)

                // Send POST request
                fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()  // CSRF token header
                    },
                    // body: JSON.stringify(data),
                    credentials: 'same-origin'  // Include cookies
                })
                .then(response => response.json())  // Parse JSON response
                .then(data => {
                    location.reload()
                })
                .catch((error) => {
                    console.error('Error:', `${error}`);
                    showMessage('error', `${error}`)
                });
            }
        })
    }
}

function showMessage(type, message, title = null) {
    const swalTitle = title || (type.charAt(0).toUpperCase() + type.slice(1));
    Swal.fire({
        icon: type,
        title: swalTitle,
        text: message,
        showConfirmButton: true
    });
}

function showFormProcessing(form, show= true){
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        // Disable the button to prevent multiple clicks
        submitBtn.disabled = show;
        spinner =  `<span class="spinner-border spinner-border-sm ms-1" role="status" aria-hidden="true"></span>`;

        if(show){
            submitBtn.innerHTML = `${submitBtn.innerHTML} ${spinner}`;
        } else {
            submitBtn.querySelector("span").remove();
        }
    }
}

function onlyNumbers(e = null) {
    // Remove non-digit characters
    this.value = this.value?.replace(/\D/g, '');
}

function charsOnly(e = null) {
    // Remove digits
    this.value = this.value?.replace(/[^A-Za-z.\s]/g, '');
}

function max4Digits(e = null) {
    this.value = this.value?.replace(/\D/g, '').slice(0, 4);
}

function max10Digits(e = null) {
    this.value = this.value?.replace(/\D/g, '').slice(0, 10);
}

// scroll vertical
$('.search-table').DataTable({
    scrollY: '265px',
    scrollCollapse: true,
    paging: false,
    info: false, 
    scrollX: true,
    language: {
        searchPlaceholder: 'Search...',
        sSearch: '',
    },
});
// scroll vertical