let endTime;
let timerInterval;
let currentUserName;
let allowDirectSubmit = false;
let currentTimeLeft = 9000;
let activeFlagPayload = null;

const FULL_TEST_DURATION_SECONDS = 9000;
const timerDisplay = document.getElementById('full_test_timer');
const quizForm = document.getElementById('full-test-form');
const submitReviewPanel = document.getElementById('submit-review-panel');
const submitReviewBackdrop = document.getElementById('submit-review-backdrop');
const submitNowBtn = document.getElementById('submit-now-btn');
const closeReviewBtn = document.getElementById('close-review-btn');
const reviewTimeLeft = document.getElementById('review-time-left');
const timeTakenInput = document.getElementById('time-taken-seconds');

const flagReviewPanel = document.getElementById('flag-review-panel');
const flagReviewBackdrop = document.getElementById('flag-review-backdrop');
const flagQuestionId = document.getElementById('flag-question-id');
const flagQuestionPreview = document.getElementById('flag-question-preview');
const flagReason = document.getElementById('flag-reason');
const sendFlagBtn = document.getElementById('send-flag-btn');
const closeFlagBtn = document.getElementById('close-flag-btn');

const quizContextKey = document.body.dataset.quizKey || 'full-test';
const watermarkText = document.body.dataset.watermark || '';
const attemptReference = document.body.dataset.attemptReference || '';
const topicName = document.body.dataset.topic || 'Full Test';

function buildUserStorageKey(rawName) {
    return rawName.trim().toLowerCase().replace(/[^a-z0-9]/g, '_');
}

function storagePrefix() {
    return quizContextKey;
}

function answerStorageKey() {
    return `${storagePrefix()}_${currentUserName}_answers`;
}

function timerStorageKey() {
    return `${storagePrefix()}_${currentUserName}_end_time`;
}

function reportStorageKey() {
    const reportScope = attemptReference || currentUserName || 'anonymous';
    return `${storagePrefix()}_${reportScope}_reported_questions`;
}

function safeParseJSON(rawValue, fallback) {
    try {
        return JSON.parse(rawValue);
    } catch (_error) {
        return fallback;
    }
}

function getReportedQuestions() {
    if (!currentUserName) {
        return new Set();
    }

    const stored = safeParseJSON(sessionStorage.getItem(reportStorageKey()), []);
    return new Set(Array.isArray(stored) ? stored.map((value) => Number(value)).filter((value) => !Number.isNaN(value)) : []);
}

function persistReportedQuestions(reportedSet) {
    if (!currentUserName) {
        return;
    }
    sessionStorage.setItem(reportStorageKey(), JSON.stringify(Array.from(reportedSet)));
}

function updateReportedCount() {
    const flaggedCount = document.getElementById('flagged-count');
    if (!flaggedCount) {
        return;
    }
    flaggedCount.textContent = String(getReportedQuestions().size);
}

function getCsrfToken() {
    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (csrfInput && csrfInput.value) {
        return csrfInput.value;
    }

    const match = document.cookie.match(/(^|;)\s*csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[2]) : '';
}

function renderWatermark() {
    const layer = document.getElementById('quiz-watermark');
    if (!layer) {
        return;
    }

    layer.innerHTML = '';
    if (!watermarkText.trim()) {
        return;
    }

    for (let index = 0; index < 18; index += 1) {
        const span = document.createElement('span');
        span.textContent = watermarkText;
        layer.appendChild(span);
    }
}

function applyTimerMood(timeLeft) {
    if (!timerDisplay) {
        return;
    }

    timerDisplay.classList.remove('timer-safe', 'timer-warning', 'timer-critical');
    if (timeLeft <= 60) {
        timerDisplay.classList.add('timer-critical');
    } else if (timeLeft <= 300) {
        timerDisplay.classList.add('timer-warning');
    } else {
        timerDisplay.classList.add('timer-safe');
    }
}

function updateTimeTakenField() {
    if (!timeTakenInput) {
        return;
    }
    const elapsed = Math.max(0, FULL_TEST_DURATION_SECONDS - currentTimeLeft);
    timeTakenInput.value = String(elapsed);
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

function openFlagModal(payload) {
    if (!flagReviewPanel) {
        return;
    }

    activeFlagPayload = payload;
    if (flagQuestionId) {
        flagQuestionId.textContent = String(payload.questionId);
    }
    if (flagQuestionPreview) {
        const shortText = payload.questionText.length > 180 ? `${payload.questionText.slice(0, 180)}...` : payload.questionText;
        flagQuestionPreview.textContent = shortText;
    }

    flagReviewPanel.hidden = false;
    flagReviewPanel.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
}

function closeFlagModal() {
    if (!flagReviewPanel) {
        return;
    }

    flagReviewPanel.hidden = true;
    flagReviewPanel.setAttribute('aria-hidden', 'true');
    activeFlagPayload = null;
    document.body.style.overflow = '';
}

function afterSubmit() {
    if (!quizForm) {
        return;
    }

    clearInterval(timerInterval);
    quizForm.classList.add('submitted');
    updateTimeTakenField();

    if (timerDisplay) {
        timerDisplay.style.display = 'block';
        timerDisplay.textContent = 'Calculating......';
        timerDisplay.classList.remove('timer-safe', 'timer-warning', 'timer-critical');
        timerDisplay.classList.add('timer-done');
    }

    if (currentUserName) {
        localStorage.removeItem(answerStorageKey());
        localStorage.removeItem(timerStorageKey());
    }

    closeReviewModal();
}

function updateTimer() {
    if (!timerDisplay) {
        return;
    }

    const now = Date.now();
    const timeLeft = Math.max(0, Math.floor((endTime - now) / 1000));
    currentTimeLeft = timeLeft;

    const hours = String(Math.floor(timeLeft / 3600)).padStart(2, '0');
    const minutes = String(Math.floor((timeLeft % 3600) / 60)).padStart(2, '0');
    const seconds = String(timeLeft % 60).padStart(2, '0');

    timerDisplay.textContent = `Time Left: ${hours}:${minutes}:${seconds}`;
    applyTimerMood(timeLeft);

    if (currentUserName) {
        localStorage.setItem(timerStorageKey(), String(endTime));
    }

    if (timeLeft <= 0 && quizForm) {
        clearInterval(timerInterval);
        allowDirectSubmit = true;
        afterSubmit();
        setTimeout(() => quizForm.requestSubmit(), 100);
    }
}

function getAnsweredQuestionNumbers() {
    const answered = new Set();
    if (!quizForm) {
        return answered;
    }

    quizForm.querySelectorAll('input[type="radio"]:checked').forEach((radio) => {
        const block = radio.closest('.question-block');
        if (!block) {
            return;
        }
        const qNum = Number(block.dataset.questionNumber);
        if (!Number.isNaN(qNum)) {
            answered.add(qNum);
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
    const reportedSet = getReportedQuestions();
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
    updateReportedCount();

    if (reviewTimeLeft && timerDisplay) {
        reviewTimeLeft.textContent = timerDisplay.textContent || 'Time Left: --:--:--';
    }
    if (!linksContainer) {
        return;
    }

    linksContainer.innerHTML = blocks.map((block) => {
        const qNum = Number(block.dataset.questionNumber);
        const qId = Number(block.dataset.questionId);
        const isAttempted = answeredSet.has(qNum);
        const isReported = reportedSet.has(qId);
        const cssClass = isReported ? `q-link flagged ${isAttempted ? 'attempted' : 'unattempted'}` : (isAttempted ? 'q-link attempted' : 'q-link unattempted');
        return `<a href="#question-${qNum}" class="${cssClass}">Q${qNum}</a>`;
    }).join('');

    openReviewModal();
}

function saveAnswers() {
    if (!quizForm || !currentUserName || quizForm.classList.contains('submitted')) {
        return 0;
    }

    const answers = {};
    quizForm.querySelectorAll('input[type="radio"]:checked').forEach((radio) => {
        answers[radio.name.replace('q', '')] = radio.value;
    });

    localStorage.setItem(answerStorageKey(), JSON.stringify(answers));
    localStorage.setItem(`${storagePrefix()}_${currentUserName}_save_time`, new Date().toISOString());
    return Object.keys(answers).length;
}

function updateSaveIndicator(count) {
    let indicator = document.getElementById('save-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'save-indicator';
        indicator.style.cssText = 'position: fixed; bottom: 20px; right: 20px; background: #4CAF50; color: white; padding: 10px 20px; border-radius: 5px; font-size: 14px; z-index: 9999; box-shadow: 0 2px 5px rgba(0,0,0,0.3); transition: opacity 0.3s; font-family: Arial, sans-serif;';
        document.body.appendChild(indicator);
    }

    const savedTime = new Date().toLocaleTimeString();
    indicator.innerHTML = `Auto-saved ${count} answers at ${savedTime}`;
    indicator.style.opacity = '1';
    setTimeout(() => {
        indicator.style.opacity = '0.4';
    }, 3000);
}

async function sendQuestionReport() {
    if (!activeFlagPayload || !flagReason) {
        return;
    }

    const payload = {
        name: document.getElementById('hidden-name')?.value || '',
        attempt_reference: attemptReference,
        topic: topicName,
        reason: flagReason.value,
        question_id: activeFlagPayload.questionId,
        question_text: activeFlagPayload.questionText,
    };

    sendFlagBtn.disabled = true;
    try {
        const response = await fetch('/report-question/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify(payload),
            credentials: 'same-origin',
        });

        const contentType = response.headers.get('content-type') || '';
        const bodyText = await response.text();
        let result = null;
        if (contentType.includes('application/json')) {
            result = safeParseJSON(bodyText, null);
        }

        if (!result) {
            const fallbackMessage = bodyText.includes('<!DOCTYPE')
                ? 'Server returned HTML instead of JSON (likely CSRF or server error).'
                : 'Unexpected server response while sending review report.';
            throw new Error(fallbackMessage);
        }

        if (!response.ok || !result.ok) {
            throw new Error(result.message || 'Unable to send review report.');
        }

        const reported = getReportedQuestions();
        reported.add(activeFlagPayload.questionId);
        persistReportedQuestions(reported);
        updateReportedCount();

        const targetButton = quizForm?.querySelector(`.flag-question-btn[data-question-number="${activeFlagPayload.questionNumber}"]`);
        targetButton?.setAttribute('aria-pressed', 'true');
        if (targetButton) {
            targetButton.textContent = 'Reported';
        }
        quizForm?.querySelector(`.question-block[data-question-number="${activeFlagPayload.questionNumber}"]`)?.classList.add('flagged');

        alert('Review report sent. Thank you.');
        closeFlagModal();
    } catch (error) {
        alert(error.message || 'Could not send review report.');
    } finally {
        sendFlagBtn.disabled = false;
    }
}

function setupSubmitReviewActions() {
    if (!quizForm) {
        return;
    }

    if (!submitReviewPanel) {
        allowDirectSubmit = true;
        return;
    }

    quizForm.addEventListener('submit', (event) => {
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

    submitNowBtn?.addEventListener('click', (event) => {
        event.preventDefault();
        if (!window.confirm('Submit this full test now? You will not be able to change your answers after submission.')) {
            return;
        }
        allowDirectSubmit = true;
        closeReviewModal();
        quizForm.requestSubmit();
    });

    closeReviewBtn?.addEventListener('click', (event) => {
        event.preventDefault();
        closeReviewModal();
    });

    submitReviewBackdrop?.addEventListener('click', closeReviewModal);
    flagReviewBackdrop?.addEventListener('click', closeFlagModal);
    closeFlagBtn?.addEventListener('click', closeFlagModal);
    sendFlagBtn?.addEventListener('click', sendQuestionReport);

    const linksContainer = document.getElementById('question-number-links');
    linksContainer?.addEventListener('click', (event) => {
        if (event.target.closest('a.q-link')) {
            closeReviewModal();
        }
    });

    document.addEventListener('click', (event) => {
        const flagButton = event.target.closest('.flag-question-btn');
        if (!flagButton || !quizForm || quizForm.classList.contains('submitted')) {
            return;
        }

        const questionBlock = flagButton.closest('.question-block');
        if (!questionBlock) {
            return;
        }

        const questionNumber = Number(questionBlock.dataset.questionNumber);
        const questionId = Number(questionBlock.dataset.questionId);
        const questionText = questionBlock.dataset.questionText || '';
        if (Number.isNaN(questionNumber) || Number.isNaN(questionId) || !questionText) {
            alert('Question details missing. Please refresh and try again.');
            return;
        }

        openFlagModal({ questionNumber, questionId, questionText });
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            if (submitReviewPanel && !submitReviewPanel.hidden) {
                closeReviewModal();
            }
            if (flagReviewPanel && !flagReviewPanel.hidden) {
                closeFlagModal();
            }
        }
    });
}

function setupNonCopyProtection() {
    if (!quizForm || quizForm.classList.contains('submitted')) {
        return;
    }

    const blockCopy = (event) => {
        if (event.target.closest('.question-block')) {
            event.preventDefault();
        }
    };

    document.addEventListener('copy', blockCopy);
    document.addEventListener('cut', blockCopy);
    document.addEventListener('contextmenu', blockCopy);
}

function initializeTimerForActiveTest() {
    if (!quizForm || quizForm.classList.contains('submitted')) {
        return;
    }

    const rawName = document.getElementById('hidden-name')?.value || '';
    if (!rawName.trim()) {
        return;
    }

    currentUserName = buildUserStorageKey(rawName);
    const savedEndTime = localStorage.getItem(timerStorageKey());

    if (savedEndTime) {
        const parsed = Number(savedEndTime);
        if (!Number.isNaN(parsed) && parsed > Date.now()) {
            endTime = parsed;
        } else {
            endTime = Date.now() + (FULL_TEST_DURATION_SECONDS * 1000);
            localStorage.removeItem(timerStorageKey());
        }
    } else {
        endTime = Date.now() + (FULL_TEST_DURATION_SECONDS * 1000);
    }

    updateTimer();
    timerInterval = setInterval(updateTimer, 1000);
}

function pingKeepalive() {
    fetch('/keepalive/', {
        method: 'GET',
        credentials: 'same-origin',
    }).catch(() => {
        // Keepalive failures are non-critical.
    });
}

document.addEventListener('change', (event) => {
    if (!quizForm) {
        return;
    }

    if (event.target.matches('input[type="radio"][name^="q"]')) {
        const count = saveAnswers();
        if (count > 0) {
            updateSaveIndicator(count);
        }

        const questionBlock = event.target.closest('.question-block');
        if (questionBlock) {
            questionBlock.querySelectorAll('.option').forEach((label) => label.classList.remove('selected'));
            event.target.closest('.option')?.classList.add('selected');
        }
    }
});

window.addEventListener('beforeunload', (event) => {
    if (!quizForm || quizForm.classList.contains('submitted')) {
        return;
    }

    const count = saveAnswers();
    if (count > 0) {
        event.preventDefault();
        event.returnValue = 'You have in-progress answers. Are you sure you want to leave?';
    }
});

document.addEventListener('DOMContentLoaded', () => {
    renderWatermark();
    setupNonCopyProtection();

    const rawName = document.getElementById('hidden-name')?.value || '';
    if (rawName.trim()) {
        currentUserName = buildUserStorageKey(rawName);
    }

    if (quizForm && quizForm.classList.contains('submitted') && timerDisplay) {
        timerDisplay.remove();
    }

    closeReviewModal();
    closeFlagModal();
    initializeTimerForActiveTest();
    setupSubmitReviewActions();

    if (quizForm) {
        quizForm.querySelectorAll('.flag-question-btn').forEach((button) => {
            const questionBlock = button.closest('.question-block');
            const questionId = Number(questionBlock?.dataset.questionId);
            if (getReportedQuestions().has(questionId)) {
                button.textContent = 'Reported';
                button.setAttribute('aria-pressed', 'true');
                button.closest('.question-block')?.classList.add('flagged');
            }
        });
    }

    updateReportedCount();

    setInterval(() => {
        const count = saveAnswers();
        if (count > 0) {
            updateSaveIndicator(count);
        }
    }, 30000);

    const hasActiveQuiz = quizForm && !quizForm.classList.contains('submitted');
    if (hasActiveQuiz) {
        pingKeepalive();
        setInterval(pingKeepalive, 900000);
    }
});
