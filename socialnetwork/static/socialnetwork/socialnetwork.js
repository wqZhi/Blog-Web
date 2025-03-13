"use strict";

let currentStreamType = 'global';

function initStream() {
    const pageNameElement = document.getElementById('id_page_name');
    if (pageNameElement && pageNameElement.textContent.includes('Follower')) {
        currentStreamType = 'follower';
    }
    refreshPosts();
    setInterval(refreshPosts, 5000);
}

function getStreamURL() {
    if (currentStreamType === 'global') {
        return document.getElementById('global-stream-url').dataset.url;
    } else {
        return document.getElementById('follower-stream-url').dataset.url;
    }
}

function sanitize(s) {
    if (s == null) return '';
    return s.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
}

function refreshPosts() {
    const url = getStreamURL();

    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
        })
        .then(posts => updatePostsList(posts))
        .catch(error => {
            console.error('Error:', error);
            displayError('Failed to load posts');
        });
}


function updatePostsList(posts) {
    const postList = document.getElementById('post-list');
    const existingPostElements = new Map();
    
    // Map existing post elements by ID
    Array.from(postList.children).forEach(child => {
        const postId = child.dataset.postId;
        existingPostElements.set(postId, child);
    });
    
    const sortedPosts = posts.sort((a, b) => 
        new Date(b.timestamp) - new Date(a.timestamp)
    );
    
    // Keep track of processed posts to maintain order
    const processedPosts = new Set();
    
    // First update existing posts in place
    sortedPosts.forEach(post => {
        const postId = String(post.id);
        const existingElement = existingPostElements.get(postId);
        
        if (existingElement) {
            updateExistingPost(existingElement, post);
            processedPosts.add(postId);
        }
    });
    
    // Then add new posts and reposition existing ones
    let currentElement = postList.firstChild;
    for (const post of sortedPosts) {
        const postId = String(post.id);
        const existingElement = existingPostElements.get(postId);
        
        if (existingElement) {
            // Move existing element to the correct position
            if (currentElement !== existingElement) {
                postList.insertBefore(existingElement, currentElement);
            } else {
                currentElement = currentElement.nextSibling;
            }
        } else {
            // Create and insert new element
            const newElement = createPostElement(post);
            postList.insertBefore(newElement, currentElement);
        }
    }
}



function updateExistingPost(existingElement, newPostData) {
    // Update post text if changed
    const textSpan = existingElement.querySelector(`#id_post_text_${newPostData.id}`);
    if (textSpan) textSpan.textContent = sanitize(newPostData.text);

    // Update timestamp if changed
    const timeSpan = existingElement.querySelector(`#id_post_date_time_${newPostData.id}`);
    if (timeSpan) timeSpan.textContent = formatDateTime(newPostData.timestamp);

    // Update comments without removing existing elements
    const commentsContainer = existingElement.querySelector(`#comments-${newPostData.id}`);
    if (commentsContainer) {
        updateCommentsContainer(commentsContainer, newPostData.comments);
    }
}

function updateCommentsContainer(container, comments) {
    // Map existing comment elements by ID
    const existingComments = new Map();
    Array.from(container.children).forEach(child => {
        const commentId = child.id.replace('id_comment_div_', '');
        existingComments.set(commentId, child);
    });

    // Track processed comments
    const processedComments = new Set();

    // First update existing comments
    comments.forEach(comment => {
        const commentId = String(comment.id);
        const existingComment = existingComments.get(commentId);

        if (existingComment) {
            // Update existing comment text and timestamp
            const textSpan = existingComment.querySelector(`#id_comment_text_${commentId}`);
            if (textSpan) textSpan.textContent = sanitize(comment.text);

            const timeSpan = existingComment.querySelector(`#id_comment_date_time_${commentId}`);
            if (timeSpan) timeSpan.textContent = formatDateTime(comment.timestamp);

            processedComments.add(commentId);
        }
    });

    // Then add new comments (at the end)
    comments.forEach(comment => {
        const commentId = String(comment.id);
        if (!processedComments.has(commentId)) {
            const commentHTML = createCommentHtml(comment);
            // Use insertAdjacentHTML to avoid removing existing elements
            container.insertAdjacentHTML('beforeend', commentHTML);
        }
    });
}


function createPostElement(post) {
    const div = document.createElement('div');
    div.className = 'post-box';
    div.id = `id_post_div_${post.id}`;
    div.dataset.postId = post.id;
    
    div.innerHTML = `
        <p>
            <a href="/profile/${sanitize(post.author.username)}" 
               id="id_post_profile_${post.id}">
                ${sanitize(post.author.first_name)} ${sanitize(post.author.last_name)}
            </a>
            <span id="id_post_date_time_${post.id}">${formatDateTime(post.timestamp)}</span>:
            <span id="id_post_text_${post.id}">${sanitize(post.text)}</span>
        </p>
        <div class="comments" id="comments-${post.id}">
            ${post.comments.map(comment => createCommentHtml(comment)).join('')}
        </div>
        <form class="comment-form" data-post-id="${post.id}">
            <input type="text" 
                   id="id_comment_input_text_${post.id}" 
                   placeholder="Write a comment..." 
                   name="comment_text">
            <button type="submit" id="id_comment_button_${post.id}">Comment</button>
        </form>
    `;
    
    return div;
}

function addNewPost(post) {
    const postList = document.getElementById('post-list');
    if (!document.getElementById(`id_post_div_${post.id}`)) {
        const postElement = createPostElement(post);
        postList.insertBefore(postElement, postList.firstChild);
    }
}

function updatePostComments(post) {
    const commentsDiv = document.getElementById(`comments-${post.id}`);
    if (commentsDiv) {
        commentsDiv.innerHTML = post.comments.map(comment => createCommentHtml(comment)).join('');
    }
}

function createCommentHtml(comment) {
    return `
        <div class="comment" id="id_comment_div_${comment.id}">
            <p style="margin-left: 20px;">
                <a href="/profile/${sanitize(comment.author.username)}" 
                   id="id_comment_profile_${comment.id}">
                    ${sanitize(comment.author.first_name)} ${sanitize(comment.author.last_name)}
                </a>:
                <span id="id_comment_text_${comment.id}">${sanitize(comment.text)}</span>
                (<span id="id_comment_date_time_${comment.id}">${formatDateTime(comment.timestamp)}</span>)
            </p>
        </div>
    `;
}

function formatDateTime(date) {
    const d = new Date(date);
    if (isNaN(d.getTime())) {
        return 'Invalid Date';
    }
    const options = { 
        month: 'numeric',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    };
    return d.toLocaleString('en-US', options).replace(/, /, ' ');
}

function displayError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

function getCSRFToken() {
    const cookieMatch = document.cookie.match(/csrftoken=([\w-]+)/);
    return cookieMatch ? cookieMatch[1] : "unknown";
}


document.addEventListener('DOMContentLoaded', function() {
  
    const postForm = document.getElementById('post-form');
    if (postForm) {
        postForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new URLSearchParams(new FormData(this));

            fetch(this.action, {
                method: 'POST',
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: formData
            })
            .then(response => response.json())
            .then(post => {
                addNewPost(post);
                this.querySelector('textarea').value = '';
            })
            .catch(error => console.error('Error:', error));
        });
    }

    document.getElementById('post-list').addEventListener('submit', function(e) {
        if (e.target.classList.contains('comment-form')) {
            e.preventDefault();
            const form = e.target;
            const postId = form.dataset.postId;
            const commentText = form.querySelector('input[name="comment_text"]').value;

            if (!commentText.trim()) {
                displayError('Comment cannot be empty');
                return;
            }

            const formData = new URLSearchParams();
            formData.append('comment_text', commentText);
            formData.append('post_id', postId);

            const addCommentUrl = document.getElementById('add-comment-url').dataset.url;
            fetch(addCommentUrl, {
                method: 'POST',
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: formData
            })
            .then(response => {
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                return response.json();
            })
            .then(comment => {
                if (comment.error) {
                    displayError(comment.error);
                } else {
                    const commentsDiv = document.getElementById(`comments-${postId}`);
                    const commentHTML = createCommentHtml(comment);
                    commentsDiv.insertAdjacentHTML('beforeend', commentHTML);
                    form.reset();
                }
            })
            .catch(error => console.error('Error:', error));
        }
    });

    initStream();
});