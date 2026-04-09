document.addEventListener('DOMContentLoaded', function(){
  // update status via AJAX (admin)
  const statusForm = document.getElementById('status-form');
  if(statusForm){
    statusForm.addEventListener('submit', function(e){
      e.preventDefault();
      const form = e.target;
      const pk = form.dataset.pk;
      const data = new FormData(form);
      fetch(`/api/complaint/${pk}/update-status/`, {
        method: 'POST',
        body: data,
        headers: { 'X-CSRFToken': getCookie('csrftoken') }
      }).then(r=>r.json()).then(resp=>{
        if(resp.ok){
          const badge = document.getElementById('status-badge');
          badge.textContent = resp.status;
          alert('Status updated');
        } else {
          alert('Error: ' + (resp.error || 'unknown'));
        }
      })
    })
  }

  // CSRF helper
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // file preview on submit page
  const fileInput = document.getElementById('id_attachment');
  if(fileInput){
    fileInput.addEventListener('change', function(){
      const p = document.getElementById('file-preview');
      p.innerHTML = '';
      const f = this.files[0];
      if(!f) return;
      if(f.type.startsWith('image/')){
        const img = document.createElement('img');
        img.src = URL.createObjectURL(f);
        img.style.maxWidth = '200px';
        img.classList.add('img-thumbnail');
        p.appendChild(img);
      } else {
        p.innerHTML = `<span class="badge bg-secondary">${f.name}</span>`;
      }
    })
  }
});
