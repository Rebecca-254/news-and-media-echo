// Handle comment replies
document.addEventListener('DOMContentLoaded', function() {
    // Reply to comment functionality
    document.querySelectorAll('.reply-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const commentId = this.dataset.commentId;
            const commentForm = document.querySelector('#comment-form');
            const replyNotice = document.createElement('div');
            
            replyNotice.className = 'alert alert-info py-1 px-2 mb-2';
            replyNotice.innerHTML = `Replying to <strong>${this.dataset.authorName}</strong> 
                                    <button class="btn-close btn-close-white float-end" 
                                            style="font-size: 0.5rem;"></button>`;
            
            // Add cancel button
            replyNotice.querySelector('.btn-close').addEventListener('click', function() {
                commentForm.removeAttribute('data-parent-id');
                this.parentElement.remove();
            });
            
            // Check if there's already a reply notice
            const existingNotice = commentForm.querySelector('.alert');
            if (existingNotice) {
                existingNotice.replaceWith(replyNotice);
            } else {
                commentForm.prepend(replyNotice);
            }
            
            // Set parent ID in form
            commentForm.setAttribute('data-parent-id', commentId);
        });
    });
    
    // Newsletter form submission
    const newsletterForm = document.querySelector('#newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
                } else {
                    this.querySelector('.form-errors').innerHTML = 
                        `<div class="alert alert-danger">${data.errors.join('<br>')}</div>`;
                }
            });
        });
    }
});