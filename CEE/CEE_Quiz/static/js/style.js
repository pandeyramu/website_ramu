
// ==================== ACCURATE TIMER CODE ====================
let endTime;
let timerInterval;
let currentUserName; // NEW: Store current user's name
let allowDirectSubmit = false;

const timerDisplay = document.getElementById('timer');
const quizForm = document.getElementById('quiz-form');
const startBtn = document.getElementById('start_btn');
const nameInput = document.querySelector('input[name="name"]');
const submitReviewPanel = document.getElementById('submit-review-panel');
const submitReviewBackdrop = document.getElementById('submit-review-backdrop');
const submitNowBtn = document.getElementById('submit-now-btn');
const closeReviewBtn = document.getElementById('close-review-btn');
const reviewTimeLeft = document.getElementById('review-time-left');
const reviewTotalQuestions = document.getElementById('review-total-questions');

// Get chapter ID for unique storage
const chapterId = "{{ chapter.id }}";

function buildUserStorageKey(rawName) {
    return rawName.trim().toLowerCase().replace(/[^a-z0-9]/g, '_');
}

function formatScientificText() {
    const targets = document.querySelectorAll('.question-block p strong, .option .option-text');
    targets.forEach((el) => {
        const raw = el.textContent || '';
        if (!raw || raw.includes('\\(') || raw.includes('\\)') || raw.includes('$$')) {
            return;
        }

        const formatted = raw.replace(/([A-Za-z])\^\s*(-?\d+)/g, '$1<sup>$2</sup>');
        if (formatted !== raw) {
            el.innerHTML = formatted;
        }
    });
}

function afterSubmit() {
    clearInterval(timerInterval);
    quizForm.classList.add("submitted");

    if (timerDisplay) {
        timerDisplay.style.display = 'block';
        timerDisplay.textContent = 'Calculating......';
        timerDisplay.style.color = '#ffffff';
        timerDisplay.style.backgroundColor = '#2c3e50';
        timerDisplay.style.padding = '8px 12px';
        timerDisplay.style.borderRadius = '8px';
    }
    
    // Clear timer state after successful submission
    if (currentUserName) {
        localStorage.removeItem(`quiz_${chapterId}_${currentUserName}_end_time`);
    }

    closeReviewModal();
}

function openReviewModal() {
    if (!submitReviewPanel) {
        return;
    }
    submitReviewPanel.hidden = false;
    submitReviewPanel.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
}

function closeReviewModal() {
    if (!submitReviewPanel) {
        return;
    }
    submitReviewPanel.hidden = true;
    submitReviewPanel.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
}

function updateTimer() {
    const now = Date.now();
    const timeLeft = Math.max(0, Math.floor((endTime - now) / 1000));
    
    let minutes = Math.floor(timeLeft / 60);
    let seconds = timeLeft % 60;
    
    minutes = minutes < 10 ? "0" + minutes : minutes;
    seconds = seconds < 10 ? "0" + seconds : seconds;
    
    timerDisplay.textContent = `Time Left : ${minutes}: ${seconds}`;
    
    if (timeLeft <= 60) {
        timerDisplay.style.color = timeLeft % 2 === 0 ? "#fd2109ff" : "#fff";
        timerDisplay.style.backgroundColor = timeLeft % 2 === 0 ? "#000" : "#e74c3c";
        timerDisplay.style.padding = "5px 10px";
        timerDisplay.style.borderRadius = "5px";
    }

    if (timeLeft <= 0) {
        clearInterval(timerInterval);
        alert("Time is up! Submitting your Answers......");
        allowDirectSubmit = true;
        afterSubmit();
        setTimeout(() => {
            quizForm.requestSubmit();  
        }, 100);
    }
    
    // Save end time to localStorage with user-specific key
    if (currentUserName) {
        localStorage.setItem(`quiz_${chapterId}_${currentUserName}_end_time`, endTime);
    }
}

function startQuiz(event) {
    event.preventDefault();
    if (!nameInput || nameInput.value.trim() === '') {
        alert('Please enter your name before starting the test!');
        nameInput.focus();
        return;
    }
    
    // Set current user name (sanitize to avoid key conflicts)
    currentUserName = buildUserStorageKey(nameInput.value);
    
    const hiddenNameInput = document.getElementById('hidden-name');
    if (hiddenNameInput) {
        hiddenNameInput.value = nameInput.value.trim();
    }
    
    const nameForm = document.getElementById('name-form');
    if (nameForm) {
        nameForm.style.display = "none";
    }
    
    startBtn.style.display = "none";
    quizForm.style.display = "block";
    timerDisplay.style.display = "block";

    // Check if there's a saved end time FOR THIS USER
    const savedEndTime = localStorage.getItem(`quiz_${chapterId}_${currentUserName}_end_time`);
    if (savedEndTime) {
        const savedEnd = parseInt(savedEndTime);
        const now = Date.now();
        const timeLeft = Math.floor((savedEnd - now) / 1000);
        
        if (timeLeft > 0) {
            const resume = confirm(`You have a saved quiz in progress with ${Math.floor(timeLeft/60)} minutes remaining. Resume?`);
            if (resume) {
                endTime = savedEnd;
            } else {
                // Start fresh - 45 minutes = 2700 seconds
                endTime = Date.now() + (2700 * 1000);
                localStorage.removeItem(`quiz_${chapterId}_${currentUserName}_end_time`);
            }
        } else {
            // Old test expired, start fresh
            endTime = Date.now() + (2700 * 1000);
            localStorage.removeItem(`quiz_${chapterId}_${currentUserName}_end_time`);
        }
    } else {
        // No saved test, start fresh
        endTime = Date.now() + (2700 * 1000);
    }

    updateTimer();
    timerInterval = setInterval(updateTimer, 1000);
}

function getAnsweredQuestionNumbers() {
    const answered = new Set();
    if (!quizForm) {
        return answered;
    }

    quizForm.querySelectorAll('input[type="radio"]:checked').forEach((radio) => {
        const block = radio.closest('.question-block');
        if (block) {
            const qNum = parseInt(block.dataset.questionNumber, 10);
            if (!Number.isNaN(qNum)) {
                answered.add(qNum);
            }
        }
    });
    return answered;
}

function renderSubmitReview() {
    if (!submitReviewPanel || !quizForm) {
        return;
    }

    const blocks = Array.from(quizForm.querySelectorAll('.question-block[data-question-number]'));
    const answeredSet = getAnsweredQuestionNumbers();
    const attempted = answeredSet.size;
    const total = blocks.length;
    const unattempted = Math.max(0, total - attempted);

    const attemptedCount = document.getElementById('attempted-count');
    const unattemptedCount = document.getElementById('unattempted-count');
    const linksContainer = document.getElementById('question-number-links');

    if (attemptedCount) {
        attemptedCount.textContent = String(attempted);
    }
    if (unattemptedCount) {
        unattemptedCount.textContent = String(unattempted);
    }
    if (reviewTotalQuestions) {
        reviewTotalQuestions.textContent = String(total);
    }
    if (reviewTimeLeft && timerDisplay) {
        reviewTimeLeft.textContent = timerDisplay.textContent || 'Time Left: --:--';
    }
    if (!linksContainer) {
        return;
    }

    const fragments = blocks.map((block) => {
        const qNum = parseInt(block.dataset.questionNumber, 10);
        const isAttempted = answeredSet.has(qNum);
        const cssClass = isAttempted ? 'q-link attempted' : 'q-link unattempted';
        return `<a href="#question-${qNum}" class="${cssClass}">Q${qNum}</a>`;
    });

    linksContainer.innerHTML = fragments.join('');
    openReviewModal();
}

function setupSubmitReviewActions() {
    if (!quizForm || !submitReviewPanel) {
        return;
    }

    quizForm.addEventListener('submit', function(event) {
        if (quizForm.classList.contains('submitted')) {
            return;
        }

        if (!allowDirectSubmit) {
            event.preventDefault();
            renderSubmitReview();
            return;
        }

        afterSubmit();
    });

    if (submitNowBtn) {
        submitNowBtn.addEventListener('click', function(event) {
            event.preventDefault();
            allowDirectSubmit = true;
            closeReviewModal();
            quizForm.requestSubmit();
        });
    }

    if (closeReviewBtn) {
        closeReviewBtn.addEventListener('click', function(event) {
            event.preventDefault();
            closeReviewModal();
        });
    }

    if (submitReviewBackdrop) {
        submitReviewBackdrop.addEventListener('click', closeReviewModal);
    }

    const linksContainer = document.getElementById('question-number-links');
    if (linksContainer) {
        linksContainer.addEventListener('click', function(event) {
            if (event.target.closest('a.q-link')) {
                closeReviewModal();
            }
        });
    }

    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && submitReviewPanel && !submitReviewPanel.hidden) {
            closeReviewModal();
        }
    });
}

function initializeTimerForActiveQuiz() {
    if (!quizForm || quizForm.style.display === 'none' || quizForm.classList.contains('submitted')) {
        return;
    }

    const hiddenNameInput = document.getElementById('hidden-name');
    const rawName = hiddenNameInput ? hiddenNameInput.value : '';
    if (!rawName || !rawName.trim()) {
        return;
    }

    currentUserName = buildUserStorageKey(rawName);

    const savedEndTime = localStorage.getItem(`quiz_${chapterId}_${currentUserName}_end_time`);
    if (savedEndTime) {
        const savedEnd = parseInt(savedEndTime);
        const now = Date.now();
        const timeLeft = Math.floor((savedEnd - now) / 1000);

        if (timeLeft > 0) {
            endTime = savedEnd;
        } else {
            endTime = Date.now() + (2700 * 1000);
            localStorage.removeItem(`quiz_${chapterId}_${currentUserName}_end_time`);
        }
    } else {
        endTime = Date.now() + (2700 * 1000);
    }

    updateTimer();
    timerInterval = setInterval(updateTimer, 1000);
}

document.addEventListener('change', function(e) {
    if (e.target.type === 'radio' && e.target.name.startsWith('q') && currentUserName) {
        const count = saveAnswers();
        updateSaveIndicator(count);

        // Visual feedback
        const questionDiv = e.target.closest('.question-container, .question, div[class*="question"]');
        if (questionDiv) {
            questionDiv.classList.add('answered');
        }
    }
});

// Save answers to localStorage
function saveAnswers() {
    if (!currentUserName) return 0;

    const form = document.querySelector('form#quiz-form');
    if (!form) return 0;

    const answers = {};
    const radioInputs = form.querySelectorAll('input[type="radio"]:checked');

    radioInputs.forEach(radio => {
        const questionId = radio.name.replace('q', '');
        answers[questionId] = radio.value;
    });

    localStorage.setItem(`quiz_${chapterId}_${currentUserName}_answers`, JSON.stringify(answers));
    localStorage.setItem(`quiz_${chapterId}_${currentUserName}_save_time`, new Date().toISOString());
    return Object.keys(answers).length;
}

// Auto-save every 30 seconds
setInterval(function() {
    if (quizForm && quizForm.style.display !== 'none' && !quizForm.classList.contains('submitted') && currentUserName) {
        const count = saveAnswers();
        if (count > 0) {
            updateSaveIndicator(count);
        }
    }
}, 30000);

// Save before page unload
window.addEventListener('beforeunload', function(e) {
    if (quizForm && quizForm.style.display !== 'none' && !quizForm.classList.contains('submitted') && currentUserName) {
        const count = saveAnswers();
        if (count > 0) {
            e.preventDefault();
            e.returnValue = 'You have unsaved progress. Are you sure you want to leave?';
        }
    }
});

// Save indicator
function updateSaveIndicator(count) {
    let indicator = document.getElementById('save-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'save-indicator';
        indicator.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #4CAF50;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 14px;
            z-index: 9999;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            transition: opacity 0.3s;
            font-family: Arial, sans-serif;
        `;
        document.body.appendChild(indicator);
    }

    const savedTime = new Date().toLocaleTimeString();
    const answerCount = count !== undefined ? count : document.querySelectorAll('input[type="radio"]:checked').length;
    indicator.innerHTML = `Auto-saved ${answerCount} answers at ${savedTime}`;
    indicator.style.opacity = '1';

    setTimeout(() => {
        indicator.style.opacity = '0.4';
    }, 3000);
}

// Also load on DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
    formatScientificText();
    if (window.MathJax && typeof window.MathJax.typesetPromise === 'function') {
        window.MathJax.typesetPromise();
    }

    if (quizForm && quizForm.classList.contains('submitted') && timerDisplay) {
        timerDisplay.remove();
    }

    closeReviewModal();

    if (quizForm && quizForm.style.display !== 'none') {
        initializeTimerForActiveQuiz();
    }

    setupSubmitReviewActions();
});

// ==================== KEEPALIVE FOR DATABASE ====================

// Keepalive should run only while an active quiz is visible.
function pingKeepalive() {
    fetch('/keepalive/', {
        method: 'GET',
        credentials: 'same-origin'
    }).catch(() => {
        // Keepalive failures are non-critical; ignore noisy console errors.
    });
}

const hasActiveQuiz = quizForm && quizForm.style.display !== 'none' && !quizForm.classList.contains('submitted');
if (hasActiveQuiz) {
    pingKeepalive();
    setInterval(pingKeepalive, 900000); // 15 minutes
}
