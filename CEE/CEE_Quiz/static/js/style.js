
// ==================== TIMER CODE ====================
let totalTime = 2700;
let timerInterval;

const timerDisplay = document.getElementById('timer');
const quizForm = document.getElementById('quiz-form');
const startBtn = document.getElementById('start_btn');
const nameInput = document.querySelector('input[name="name"]');

// Get chapter ID for unique storage
const chapterId = "{{ chapter.id }}";

function afterSubmit() {
    clearInterval(timerInterval);
    quizForm.classList.add("submitted");
    
    // Clear saved answers after successful submission
    localStorage.removeItem(`quiz_${chapterId}_answers`);
    localStorage.removeItem(`quiz_${chapterId}_save_time`);
    localStorage.removeItem(`quiz_${chapterId}_timer`);
    console.log('Quiz submitted - cleared all saved data');
}

function updateTimer() {
    let minutes = Math.floor(totalTime/60);
    let seconds = totalTime % 60;
    minutes = minutes < 10 ? "0" + minutes : minutes;
    seconds = seconds < 10 ? "0" + seconds : seconds;
    timerDisplay.textContent = `Time Left : ${minutes}: ${seconds}`;
    
    if (totalTime <= 60) {
        timerDisplay.style.color = totalTime % 2 === 0 ? "#fd2109ff" : "#fff";
        timerDisplay.style.backgroundColor = totalTime % 2 === 0 ? "#000" : "#e74c3c";
        timerDisplay.style.padding = "5px 10px";
        timerDisplay.style.borderRadius = "5px";
    }

    if (totalTime <= 0) {
        clearInterval(timerInterval);
        alert("Time is up! Submitting your Answers......");
        afterSubmit();
        setTimeout(() => {
            quizForm.requestSubmit();  
        }, 100);
    }

    totalTime--;
    
    // Save timer state to localStorage
    localStorage.setItem(`quiz_${chapterId}_timer`, totalTime);
}

function startQuiz(event) {
    event.preventDefault();
    if (!nameInput || nameInput.value.trim() === '') {
        alert('Please enter your name before starting the test!');
        nameInput.focus();
        return;
    }
    
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

    // Check if there's a saved timer state
    const savedTimer = localStorage.getItem(`quiz_${chapterId}_timer`);
    if (savedTimer && parseInt(savedTimer) > 0) {
        const resume = confirm(`You have a saved quiz in progress with ${Math.floor(savedTimer/60)} minutes remaining. Resume?`);
        if (resume) {
            totalTime = parseInt(savedTimer);
        } else {
            // Start fresh
            totalTime = 2700;
            localStorage.removeItem(`quiz_${chapterId}_answers`);
            localStorage.removeItem(`quiz_${chapterId}_timer`);
        }
    }

    updateTimer();
    timerInterval = setInterval(updateTimer, 1000);
}

if (startBtn) startBtn.addEventListener("click", startQuiz);

quizForm.addEventListener("submit", function() {
    afterSubmit();
});

// ==================== AUTO-SAVE ANSWERS ====================


// Load saved answers on page load
function loadSavedAnswers() {
    const savedAnswers = localStorage.getItem(`quiz_${chapterId}_answers`);
    if (savedAnswers) {
        try {
            const answers = JSON.parse(savedAnswers);
            console.log('Loading saved answers:', Object.keys(answers).length);
            
            let restoredCount = 0;
            // Restore radio button selections
            for (const [questionId, answer] of Object.entries(answers)) {
                const radio = document.querySelector(`input[name="q${questionId}"][value="${answer}"]`);
                if (radio) {
                    radio.checked = true;
                    restoredCount++;
                    // Visual feedback
                    const questionDiv = radio.closest('.question-container, .question, div[class*="question"]');
                    if (questionDiv) {
                        questionDiv.classList.add('answered');
                    }
                }
            }
            
            // Show recovery message
            if (restoredCount > 0) {
                showMessage(`✓ Recovered ${restoredCount} saved answers`, 'success');
            }
        } catch (e) {
            console.error('Error loading saved answers:', e);
        }
    }
}

// Save answers to localStorage
function saveAnswers() {
    const form = document.querySelector('form#quiz-form');
    if (!form) return 0;
    
    const answers = {};
    const radioInputs = form.querySelectorAll('input[type="radio"]:checked');
    
    radioInputs.forEach(radio => {
        const name = radio.name; // e.g., "q123"
        const questionId = name.replace('q', '');
        answers[questionId] = radio.value;
    });
    
    localStorage.setItem(`quiz_${chapterId}_answers`, JSON.stringify(answers));
    localStorage.setItem(`quiz_${chapterId}_save_time`, new Date().toISOString());
    
    console.log('Auto-saved:', Object.keys(answers).length, 'answers');
    return Object.keys(answers).length;
}

// Auto-save every 30 seconds
let autoSaveInterval = setInterval(function() {
    if (quizForm && quizForm.style.display !== 'none') {
        const count = saveAnswers();
        updateSaveIndicator(count);
    }
}, 30000); // 30 seconds

// Save on every answer selection
document.addEventListener('change', function(e) {
    if (e.target.type === 'radio' && e.target.name.startsWith('q')) {
        saveAnswers();
        updateSaveIndicator();
        
        // Visual feedback
        const questionDiv = e.target.closest('.question-container, .question, div[class*="question"]');
        if (questionDiv) {
            questionDiv.classList.add('answered');
        }
    }
});

// Save before page unload
window.addEventListener('beforeunload', function(e) {
    if (quizForm && quizForm.style.display !== 'none' && !quizForm.classList.contains('submitted')) {
        saveAnswers();
        // Optional: warn user about leaving
        e.preventDefault();
        e.returnValue = 'You have unsaved progress. Are you sure you want to leave?';
    }
});

// ==================== SAVE INDICATOR ====================

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
    indicator.innerHTML = `💾 Auto-saved ${answerCount} answers at ${savedTime}`;
    indicator.style.opacity = '1';
    
    // Fade out after 3 seconds
    setTimeout(() => {
        indicator.style.opacity = '0.4';
    }, 3000);
}

function showMessage(msg, type) {
    const messageDiv = document.createElement('div');
    messageDiv.style.cssText = `
        position: fixed;
        top: 80px;
        left: 50%;
        transform: translateX(-50%);
        background: ${type === 'success' ? '#4CAF50' : '#ff9800'};
        color: white;
        padding: 15px 30px;
        border-radius: 5px;
        font-size: 16px;
        z-index: 10000;
        box-shadow: 0 3px 10px rgba(0,0,0,0.3);
        font-family: Arial, sans-serif;
        font-weight: bold;
    `;
    messageDiv.textContent = msg;
    document.body.appendChild(messageDiv);
    
    setTimeout(() => {
        messageDiv.style.transition = 'opacity 0.5s';
        messageDiv.style.opacity = '0';
        setTimeout(() => messageDiv.remove(), 500);
    }, 5000);
}

// Load saved answers when form becomes visible
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.target === quizForm && quizForm.style.display === 'block') {
            setTimeout(loadSavedAnswers, 100);
        }
    });
});

if (quizForm) {
    observer.observe(quizForm, { attributes: true, attributeFilter: ['style'] });
}

// Also load on DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
    if (quizForm && quizForm.style.display !== 'none') {
        loadSavedAnswers();
    }
});

// ==================== KEEPALIVE FOR DATABASE ====================

console.log('Starting keepalive pings...');

setInterval(function() {
    fetch('/keepalive/', {
        method: 'GET',
        credentials: 'same-origin'
    })
    .then(response => {
        if (response.ok) {
            console.log('Keepalive successful:', new Date().toLocaleTimeString());
        } else {
            console.warn('Keepalive failed:', response.status);
        }
    })
    .catch(err => {
        console.error('Keepalive error:', err);
    });
}, 300000); // 5 minutes

// Ping on user activity
let lastActivity = Date.now();
document.addEventListener('click', function() {
    const now = Date.now();
    if (now - lastActivity > 240000) { // 4 minutes
        fetch('/keepalive/', { method: 'GET', credentials: 'same-origin' });
        lastActivity = now;
    }
});
