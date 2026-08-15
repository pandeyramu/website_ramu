let endTime;
let timerInterval;
let currentUserName;
let allowDirectSubmit = false;
let currentTimeLeft = 9000;
let activeFlagPayload = null;
let submissionLocked = false;
let currentQuestionNumber = 1;
let questionBlockList = [];
const prevQuestionBtn = document.getElementById('prev-question-btn');
const nextQuestionBtn = document.getElementById('next-question-btn');
const quizNavCount = document.getElementById('quiz-nav-count');
const quizAnsweredCount = document.getElementById('quiz-answered-count');
const quizProgressFill = document.getElementById('quiz-progress-fill');
const questionJumpGrid = document.getElementById('question-jump-grid');

const FULL_TEST_DURATION_SECONDS = 9000;
const timerDisplay = document.getElementById('full_test_timer');
const quizForm = document.getElementById('full-test-form');
const submitReviewPanel = document.getElementById('submit-review-panel');
const submitReviewBackdrop = document.getElementById('submit-review-backdrop');
const submitNowBtn = document.getElementById('submit-now-btn');
const closeReviewBtn = document.getElementById('close-review-btn');
const reviewTimeLeft = document.getElementById('review-time-left');
const timeTakenInput = document.getElementById('time-taken-seconds');
const primarySubmitBtn = document.getElementById('submit-full-test-btn');

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
const exitUrl = document.body.dataset.exitUrl || '/';

function submittedAttemptStorageKey() {
    return `${storagePrefix()}_submitted_attempts_client`;
}

function getSubmittedAttempts() {
    return new Set(safeParseJSON(localStorage.getItem(submittedAttemptStorageKey()), []));
}

function markAttemptSubmittedClient() {
    if (!attemptReference) {
        return;
    }
    const submitted = getSubmittedAttempts();
    submitted.add(attemptReference);
    localStorage.setItem(submittedAttemptStorageKey(), JSON.stringify(Array.from(submitted)));
}

function isAttemptSubmittedClient() {
    return Boolean(attemptReference) && getSubmittedAttempts().has(attemptReference);
}

function redirectIfSubmittedAttempt() {
    if (!quizForm || quizForm.classList.contains('submitted') || !attemptReference || !isAttemptSubmittedClient()) {
        return false;
    }

    window.location.replace(exitUrl);
    clearAttemptStorage();
    return true;
}

function focusQuestionFromLink(linkElement) {
    const questionHash = linkElement?.getAttribute('href') || '';
    if (!questionHash.startsWith('#question-')) {
        return;
    }

    const questionElement = document.querySelector(questionHash);
    if (!questionElement) {
        return;
    }

    if (isActiveQuestionMode()) {
        const qNum = Number(questionElement.dataset.questionNumber);
        showQuestion(Number.isNaN(qNum) ? 1 : qNum);
        return;
    }

    const existingNotice = questionElement.querySelector('.question-jump-notice');
    existingNotice?.remove();

    questionElement.scrollIntoView({ behavior: 'smooth', block: 'center' });

    window.setTimeout(() => {
        questionElement.classList.add('question-focus-flash');

        const notice = document.createElement('div');
        notice.className = 'question-jump-notice';
        notice.setAttribute('role', 'status');
        notice.setAttribute('aria-live', 'polite');
        notice.textContent = `${linkElement.textContent || 'Question'} selected. Yes, this is the question.`;
        questionElement.appendChild(notice);

        window.setTimeout(() => {
            questionElement.classList.remove('question-focus-flash');
            notice.remove();
        }, 2800);
    }, 1000);
}

function buildUserStorageKey(rawName) {
    return rawName.trim().toLowerCase().replace(/[^a-z0-9]/g, '_');
}

function storagePrefix() {
    return quizContextKey;
}

function answerStorageKey() {
    return `${storagePrefix()}_${currentUserName}_${attemptReference}_answers`;
}

function timerStorageKey() {
    return `${storagePrefix()}_${currentUserName}_${attemptReference}_end_time`;
}

function saveTimeStorageKey() {
    return `${storagePrefix()}_${currentUserName}_${attemptReference}_save_time`;
}

function clearAttemptStorage() {
    if (!currentUserName) {
        return;
    }
    localStorage.removeItem(answerStorageKey());
    localStorage.removeItem(timerStorageKey());
    localStorage.removeItem(saveTimeStorageKey());
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
    document.body.classList.add('review-modal-open');
}

function closeReviewModal() {
    if (!submitReviewPanel) {
        return;
    }
    if (submitReviewPanel.contains(document.activeElement)) {
        document.activeElement.blur();
    }
    submitReviewPanel.hidden = true;
    submitReviewPanel.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    document.body.classList.remove('review-modal-open');
}

function openFlagModal(payload) {
    if (!flagReviewPanel) {
        console.error('Flag review panel not found in DOM');
        return;
    }

    // production: debug log removed
    activeFlagPayload = payload;
    if (flagQuestionId) {
        flagQuestionId.textContent = String(payload.questionId);
    }
    if (flagQuestionPreview) {
        const shortText = payload.questionText.length > 180 ? `${payload.questionText.slice(0, 180)}...` : payload.questionText;
        flagQuestionPreview.textContent = shortText;
    }

    flagReviewPanel.hidden = false;
    flagReviewPanel.removeAttribute('hidden');
    flagReviewPanel.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    document.body.classList.add('review-modal-open');
    // production: debug log removed
}

function closeFlagModal() {
    if (!flagReviewPanel) {
        return;
    }

    if (flagReviewPanel.contains(document.activeElement)) {
        document.activeElement.blur();
    }

    flagReviewPanel.hidden = true;
    flagReviewPanel.setAttribute('aria-hidden', 'true');
    activeFlagPayload = null;
    document.body.style.overflow = '';
    document.body.classList.remove('review-modal-open');
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
        timerDisplay.textContent = 'Calculating...';
        timerDisplay.classList.remove('timer-safe', 'timer-warning', 'timer-critical');
        timerDisplay.classList.add('timer-done');
    }

    if (currentUserName) {
        localStorage.removeItem(answerStorageKey());
        localStorage.removeItem(timerStorageKey());
    }

    markAttemptSubmittedClient();

    closeReviewModal();
}

function lockSubmissionActions() {
    if (submissionLocked) {
        return;
    }
    submissionLocked = true;

    if (primarySubmitBtn) {
        primarySubmitBtn.disabled = true;
        primarySubmitBtn.textContent = 'Submitting...';
    }
    if (submitNowBtn) {
        submitNowBtn.disabled = true;
        submitNowBtn.textContent = 'Submitting...';
    }
}

function setupBackNavigationHandling() {
    if (!quizForm) {
        return;
    }

    if (quizForm.classList.contains('submitted')) {
        history.pushState({ resultGuard: true }, '', window.location.href);
        window.addEventListener('popstate', () => {
            clearAttemptStorage();
            window.location.replace(exitUrl);
        });
        return;
    }

    history.pushState({ quizGuard: true }, '', window.location.href);
    window.addEventListener('popstate', () => {
        const shouldLeave = window.confirm('Are you sure you want to leave this full test? Your attempt in progress will be lost.');
        if (shouldLeave) {
            clearAttemptStorage();
            window.location.replace(exitUrl);
            return;
        }
        history.pushState({ quizGuard: true }, '', window.location.href);
    });
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

    timerDisplay.textContent = `${hours}:${minutes}:${seconds}`;
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
    localStorage.setItem(saveTimeStorageKey(), new Date().toISOString());
    return Object.keys(answers).length;
}

function updateSaveIndicator(count) {
    let indicator = document.getElementById('save-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'save-indicator';
        indicator.setAttribute('role', 'status');
        indicator.setAttribute('aria-live', 'polite');
        document.body.appendChild(indicator);
    }

    if (indicator._hideTimer) {
        window.clearTimeout(indicator._hideTimer);
    }
    const savedTime = new Date().toLocaleTimeString();
    indicator.textContent = `Auto-saved ${count} answers at ${savedTime}`;
    indicator.classList.add('visible');
    indicator.classList.remove('hidden');
    indicator._hideTimer = window.setTimeout(() => {
        indicator.classList.remove('visible');
        indicator.classList.add('hidden');
    }, 2500);
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
        updateQuestionGridState();

       const targetButton = quizForm?.querySelector(
    `.flag-question-btn[data-question-number="${activeFlagPayload.questionNumber}"]`
);

if (targetButton) {
    targetButton.textContent = 'Reported';
    targetButton.disabled = true; 
    targetButton.style.pointerEvents = 'none';
    targetButton.classList.add('reported-btn'); 
    targetButton.setAttribute('aria-pressed', 'true');
}

quizForm
    ?.querySelector(`.question-block[data-question-number="${activeFlagPayload.questionNumber}"]`)
    ?.classList.add('flagged');
        alert('Review report sent. Thank you.');
        closeFlagModal();
    } catch (error) {
        alert(error.message || 'Could not send review report.');
    } finally {
        sendFlagBtn.disabled = false;
    }
}

function setupFlagModalActions() {
    if (!flagReviewPanel) {
        return;
    }

    flagReviewBackdrop?.addEventListener('click', closeFlagModal);
    closeFlagBtn?.addEventListener('click', (event) => {
        event.preventDefault();
        closeFlagModal();
    });
    sendFlagBtn?.addEventListener('click', (event) => {
        event.preventDefault();
        sendQuestionReport();
    });
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
        if (quizForm.classList.contains('submitted') || submissionLocked) {
            event.preventDefault();
            return;
        }

        if (!allowDirectSubmit) {
            event.preventDefault();
            renderSubmitReview();
            return;
        }

        lockSubmissionActions();
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

    const linksContainer = document.getElementById('question-number-links');
    linksContainer?.addEventListener('click', (event) => {
        const linkElement = event.target.closest('a.q-link');
        if (linkElement) {
            event.preventDefault();
            event.stopPropagation();
            closeReviewModal();
            window.setTimeout(() => focusQuestionFromLink(linkElement), 50);
        }
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

function setupFlagButtonListeners() {
    // production: debug log removed
    document.addEventListener('click', (event) => {
        const flagButton = event.target.closest('.flag-question-btn');
        if (!flagButton) {
            return;
        }

        // production: debug log removed
        event.preventDefault();
        event.stopPropagation();

        const questionBlock = flagButton.closest('.question-block');
        if (!questionBlock) {
            console.error('Question block not found');
            return;
        }

        const questionNumber = Number(questionBlock.dataset.questionNumber);
        const questionId = Number(questionBlock.dataset.questionId);
        const questionText = questionBlock.dataset.questionText || '';
        // production: debug log removed
        
        if (Number.isNaN(questionNumber) || Number.isNaN(questionId) || !questionText) {
            alert('Question details missing. Please refresh and try again.');
            return;
        }

        if (!flagReviewPanel) {
            console.error('Flag review panel not found');
            return;
        }

        openFlagModal({ questionNumber, questionId, questionText });
    }, true);
    // production: debug log removed
}

function isActiveQuestionMode() {
    return Boolean(quizForm && !quizForm.classList.contains('submitted') && questionBlockList.length > 1);
}

function collectQuestionBlocks() {
    questionBlockList = quizForm ? Array.from(quizForm.querySelectorAll('.question-block[data-question-number]')) : [];
}

function typeSetQuestionBlock(block) {
    if (block && window.MathJax && typeof window.MathJax.typesetPromise === 'function') {
        window.MathJax.typesetPromise([block]).catch(() => {});
    }
}

function showQuestion(number) {
    const target = Number(number);
    if (!isActiveQuestionMode() || Number.isNaN(target)) {
        return;
    }
    const clamped = Math.min(Math.max(target, 1), questionBlockList.length);
    currentQuestionNumber = clamped;

    questionBlockList.forEach((block) => {
        block.classList.toggle('active', Number(block.dataset.questionNumber) === clamped);
    });

    if (quizNavCount) {
        quizNavCount.textContent = `${clamped} of ${questionBlockList.length}`;
    }
    updateQuizProgress();
    updateQuestionGridState();
    typeSetQuestionBlock(questionBlockList[clamped - 1]);

    if (currentUserName) {
        localStorage.setItem(`${storagePrefix()}_${currentUserName}_${attemptReference}_current_question`, String(clamped));
    }

    if (prevQuestionBtn) {
        prevQuestionBtn.disabled = clamped <= 1;
    }
    if (nextQuestionBtn) {
        nextQuestionBtn.disabled = clamped >= questionBlockList.length;
    }

    const activeBlock = questionBlockList[clamped - 1];
    if (activeBlock) {
        activeBlock.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function getAnsweredCount() {
    if (!quizForm) {
        return 0;
    }
    return quizForm.querySelectorAll('input[type="radio"]:checked').length;
}

function updateQuizProgress() {
    const total = questionBlockList.length || 1;
    const answered = getAnsweredCount();

    if (quizAnsweredCount) {
        quizAnsweredCount.textContent = `${answered} answered`;
    }
    if (quizProgressFill) {
        const pct = Math.min(100, Math.round((answered / total) * 100));
        quizProgressFill.style.width = `${pct}%`;
    }
}

function buildQuestionGrid() {
    if (!questionJumpGrid) {
        return;
    }
    questionJumpGrid.innerHTML = '';
    questionBlockList.forEach((block) => {
        const qNum = Number(block.dataset.questionNumber);
        const button = document.createElement('button');
        button.type = 'button';
        button.dataset.questionNumber = String(qNum);
        button.textContent = String(qNum);
        button.setAttribute('aria-label', `Go to question ${qNum}`);
        button.addEventListener('click', () => {
            showQuestion(qNum);
        });
        questionJumpGrid.appendChild(button);
    });
}

function updateQuestionGridState() {
    if (!questionJumpGrid) {
        return;
    }
    const reportedSet = getReportedQuestions();
    questionBlockList.forEach((block) => {
        const qNum = Number(block.dataset.questionNumber);
        const button = questionJumpGrid.querySelector(`button[data-question-number="${qNum}"]`);
        if (!button) {
            return;
        }
        const qId = Number(block.dataset.questionId);
        const isAnswered = Boolean(block.querySelector('input[type="radio"]:checked'));
        const isFlagged = reportedSet.has(qId);
        button.classList.remove('qj-answered', 'qj-flagged', 'qj-current');
        if (qNum === currentQuestionNumber) {
            button.classList.add('qj-current');
            const gridRect = questionJumpGrid.getBoundingClientRect();
            const buttonRect = button.getBoundingClientRect();
            if (buttonRect.top < gridRect.top) {
                questionJumpGrid.scrollTop += (buttonRect.top - gridRect.top) - 4;
            } else if (buttonRect.bottom > gridRect.bottom) {
                questionJumpGrid.scrollTop += (buttonRect.bottom - gridRect.bottom) + 4;
            }
        }
        if (isAnswered) {
            button.classList.add('qj-answered');
        }
        if (isFlagged) {
            button.classList.add('qj-flagged');
        }
    });
}

function setupActiveQuestionMode() {
    collectQuestionBlocks();
    if (!isActiveQuestionMode()) {
        return;
    }

    quizForm.classList.add('active-question-mode');
    buildQuestionGrid();

    const savedNumber = Number(localStorage.getItem(`${storagePrefix()}_${currentUserName}_${attemptReference}_current_question`) || '1');
    showQuestion(Number.isNaN(savedNumber) ? 1 : savedNumber);

    prevQuestionBtn?.addEventListener('click', () => {
        showQuestion(currentQuestionNumber - 1);
    });
    nextQuestionBtn?.addEventListener('click', () => {
        showQuestion(currentQuestionNumber + 1);
    });
    updateQuizProgress();
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
            updateQuestionGridState();
            updateQuizProgress();
        }

        if (isActiveQuestionMode() && currentQuestionNumber < questionBlockList.length) {
            window.setTimeout(() => {
                showQuestion(currentQuestionNumber + 1);
            }, 350);
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

    if (redirectIfSubmittedAttempt()) {
        return;
    }

    closeReviewModal();
    closeFlagModal();
    setupBackNavigationHandling();
    initializeTimerForActiveTest();
    setupSubmitReviewActions();
    setupFlagModalActions();
    setupFlagButtonListeners();
    setupActiveQuestionMode();

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

    const quizTopBar = document.getElementById('quiz-topbar');
    if (quizTopBar) {
        const currentScrollY = () => window.scrollY || document.documentElement.scrollTop || document.body.scrollTop || 0;
        const updateCompactState = () => {
            quizTopBar.classList.toggle('quiz-topbar--compact', currentScrollY() > 200);
        };
        window.addEventListener('scroll', updateCompactState, { capture: true, passive: true });
        document.addEventListener('scroll', updateCompactState, { capture: true, passive: true });
        window.setTimeout(updateCompactState, 500);
    }
});

window.addEventListener('pageshow', (event) => {
    if (event.persisted) {
        redirectIfSubmittedAttempt();
    }
});
