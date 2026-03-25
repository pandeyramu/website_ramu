let endTime;
let timerInterval;
let currentUserName;
let allowDirectSubmit = false;

const FULL_TEST_DURATION_SECONDS = 9000;
const timerDisplay = document.getElementById('full_test_timer');
const quizForm = document.getElementById('full-test-form');
const submitReviewPanel = document.getElementById('submit-review-panel');
const submitReviewBackdrop = document.getElementById('submit-review-backdrop');
const submitNowBtn = document.getElementById('submit-now-btn');
const closeReviewBtn = document.getElementById('close-review-btn');
const reviewTimeLeft = document.getElementById('review-time-left');

function buildUserStorageKey(rawName) {
    return rawName.trim().toLowerCase().replace(/[^a-z0-9]/g, '_');
}

function formatScientificText() {
    const targets = document.querySelectorAll('.question-block p strong, .option .option-text');
    targets.forEach((el) => {
        const raw = el.textContent || '';
        if (!raw) {
            return;
        }

        const formatted = raw.replace(/([A-Za-z])\^\s*(-?\d+)/g, '$1<sup>$2</sup>');
        if (formatted !== raw) {
            el.innerHTML = formatted;
        }
    });
}

function timerStorageKey() {
    return `full_test_${currentUserName}_end_time`;
}

function answerStorageKey() {
    return `full_test_${currentUserName}_answers`;
}

function afterSubmit() {
    clearInterval(timerInterval);
    if (quizForm) {
        quizForm.classList.add('submitted');
    }

    if (submitReviewPanel) {
        submitReviewPanel.hidden = true;
        submitReviewPanel.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }

    if (timerDisplay) {
        timerDisplay.style.display = 'block';
        timerDisplay.textContent = 'Calculating......';
        timerDisplay.style.color = '#ffffff';
        timerDisplay.style.backgroundColor = '#2c3e50';
        timerDisplay.style.padding = '8px 12px';
        timerDisplay.style.borderRadius = '8px';
    }

    if (currentUserName) {
        localStorage.removeItem(answerStorageKey());
        localStorage.removeItem(timerStorageKey());
    }
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

function saveAnswers() {
    if (!quizForm || !currentUserName || quizForm.classList.contains('submitted')) {
        return 0;
    }

    const answers = {};
    const checkedInputs = quizForm.querySelectorAll('input[type="radio"]:checked');
    checkedInputs.forEach((radio) => {
        const questionId = radio.name.replace('q', '');
        answers[questionId] = radio.value;
    });

    localStorage.setItem(answerStorageKey(), JSON.stringify(answers));
    return Object.keys(answers).length;
}

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
    const answerCount = count !== undefined ? count : quizForm.querySelectorAll('input[type="radio"]:checked').length;
    indicator.innerHTML = `Auto-saved ${answerCount} answers at ${savedTime}`;
    indicator.style.opacity = '1';

    setTimeout(() => {
        indicator.style.opacity = '0.4';
    }, 3000);
}

function updateTimer() {
    if (!timerDisplay) {
        return;
    }

    const now = Date.now();
    const timeLeft = Math.max(0, Math.floor((endTime - now) / 1000));
    const hours = String(Math.floor(timeLeft / 3600)).padStart(2, '0');
    const minutes = String(Math.floor((timeLeft % 3600) / 60)).padStart(2, '0');
    const seconds = String(timeLeft % 60).padStart(2, '0');

    timerDisplay.textContent = `Time Left: ${hours}:${minutes}:${seconds}`;

    if (timeLeft <= 60) {
        timerDisplay.style.color = timeLeft % 2 === 0 ? '#fd2109ff' : '#fff';
        timerDisplay.style.backgroundColor = timeLeft % 2 === 0 ? '#000' : '#e74c3c';
        timerDisplay.style.padding = '5px 10px';
        timerDisplay.style.borderRadius = '5px';
    }

    if (currentUserName) {
        localStorage.setItem(timerStorageKey(), String(endTime));
    }

    if (timeLeft <= 0 && quizForm) {
        clearInterval(timerInterval);
        allowDirectSubmit = true;
        afterSubmit();
        setTimeout(() => {
            quizForm.requestSubmit();
        }, 100);
    }
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
    if (!linksContainer) {
        return;
    }

    if (reviewTimeLeft && timerDisplay) {
        reviewTimeLeft.textContent = timerDisplay.textContent || 'Time Left: --:--:--';
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

    quizForm.addEventListener('submit', function (event) {
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
        submitNowBtn.addEventListener('click', function (event) {
            event.preventDefault();
            allowDirectSubmit = true;
            closeReviewModal();
            quizForm.requestSubmit();
        });
    }

    if (closeReviewBtn) {
        closeReviewBtn.addEventListener('click', function (event) {
            event.preventDefault();
            closeReviewModal();
        });
    }

    if (submitReviewBackdrop) {
        submitReviewBackdrop.addEventListener('click', closeReviewModal);
    }

    const linksContainer = document.getElementById('question-number-links');
    if (linksContainer) {
        linksContainer.addEventListener('click', function (event) {
            if (event.target.closest('a.q-link')) {
                closeReviewModal();
            }
        });
    }

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && submitReviewPanel && !submitReviewPanel.hidden) {
            closeReviewModal();
        }
    });
}

function initializeTimerForActiveTest() {
    if (!quizForm || quizForm.classList.contains('submitted')) {
        return;
    }

    const hiddenNameInput = document.getElementById('hidden-name');
    const rawName = hiddenNameInput ? hiddenNameInput.value : '';
    if (!rawName || !rawName.trim()) {
        return;
    }

    currentUserName = buildUserStorageKey(rawName);
    const savedEndTime = localStorage.getItem(timerStorageKey());
    const now = Date.now();

    if (savedEndTime) {
        const parsed = parseInt(savedEndTime, 10);
        if (!Number.isNaN(parsed) && parsed > now) {
            endTime = parsed;
        } else {
            endTime = now + FULL_TEST_DURATION_SECONDS * 1000;
            localStorage.removeItem(answerStorageKey());
            localStorage.removeItem(timerStorageKey());
        }
    } else {
        endTime = now + FULL_TEST_DURATION_SECONDS * 1000;
    }

    updateTimer();
    timerInterval = setInterval(updateTimer, 1000);
}

function pingKeepalive() {
    fetch('/keepalive/', {
        method: 'GET',
        credentials: 'same-origin'
    }).catch(() => {
        // Keepalive failures are non-critical.
    });
}

document.addEventListener('change', function (event) {
    if (!quizForm) {
        return;
    }

    if (event.target.matches('input[type="radio"][name^="q"]')) {
        const questionBlock = event.target.closest('.question-block');
        if (questionBlock) {
            questionBlock.querySelectorAll('.option').forEach((label) => label.classList.remove('selected'));
            event.target.closest('.option')?.classList.add('selected');
        }
        const count = saveAnswers();
        updateSaveIndicator(count);
    }
});

window.addEventListener('beforeunload', function (event) {
    if (!quizForm || quizForm.classList.contains('submitted')) {
        return;
    }

    const count = saveAnswers();
    if (count > 0) {
        event.preventDefault();
        event.returnValue = 'You have in-progress answers. Are you sure you want to leave?';
    }
});

document.addEventListener('DOMContentLoaded', function () {
    formatScientificText();

    if (!quizForm) {
        return;
    }

    closeReviewModal();

    if (quizForm.classList.contains('submitted') && timerDisplay) {
        timerDisplay.remove();
    }

    initializeTimerForActiveTest();
    setupSubmitReviewActions();

    setInterval(function () {
        const count = saveAnswers();
        if (count > 0) {
            updateSaveIndicator(count);
        }
    }, 30000);

    if (!quizForm.classList.contains('submitted')) {
        pingKeepalive();
        setInterval(pingKeepalive, 900000);
    }
});
