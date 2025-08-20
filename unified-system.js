// === 統合UI管理システム ===
const UIManager = {
    showGameUI() {
        log('Showing unified game UI...');
        const elements = {
            questionOverlay: document.getElementById('game-question-overlay'),
            headerTimer: document.getElementById('header-timer'),
            body: document.body
        };
        if (elements.questionOverlay) {
            elements.questionOverlay.classList.remove('hidden');
        }
        if (elements.headerTimer) {
            elements.headerTimer.classList.remove('hidden');
        }
        elements.body.classList.add('game-playing');
        this.updateAllStats();
    },
    hideGameUI() {
        const elements = {
            questionOverlay: document.getElementById('game-question-overlay'),
            choicesOverlay: document.getElementById('game-choices-overlay'),
            headerTimer: document.getElementById('header-timer'),
            body: document.body
        };
        if (elements.questionOverlay) {
            elements.questionOverlay.classList.add('hidden');
        }
        if (elements.choicesOverlay) {
            elements.choicesOverlay.classList.add('hidden');
        }
        if (elements.headerTimer) {
            elements.headerTimer.classList.add('hidden');
        }
        elements.body.classList.remove('game-playing');
    },
    updateTimer(timeValue, isWarning = false, isDanger = false) {
        const timerElements = [
            document.getElementById('header-timer'),
            document.getElementById('mobile-timer')
        ];
        timerElements.forEach(timer => {
            if (timer) {
                timer.textContent = timeValue;
                timer.classList.remove('warning', 'danger');
                if (isDanger) {
                    timer.classList.add('danger');
                } else if (isWarning) {
                    timer.classList.add('warning');
                }
            }
        });
    },
    updateAllStats() {
        const stats = {
            score: gameState.score,
            streak: gameState.streak,
            totalQuestions: gameState.totalQuestions,
            timer: gameState.timer
        };
        const scoreEl = document.getElementById('score');
        const streakEl = document.getElementById('streak');
        const totalQuestionsEl = document.getElementById('total-questions');
        if (scoreEl) scoreEl.textContent = stats.score;
        if (streakEl) streakEl.textContent = stats.streak;
        if (totalQuestionsEl) totalQuestionsEl.textContent = stats.totalQuestions;
        const mobileScore = document.getElementById('mobile-score');
        const mobileStreak = document.getElementById('mobile-streak');
        if (mobileScore) mobileScore.textContent = stats.score;
        if (mobileStreak) mobileStreak.textContent = stats.streak;
        const isWarning = stats.timer <= 10;
        const isDanger = stats.timer <= 5;
        this.updateTimer(stats.timer, isWarning, isDanger);
        if (gameState.speedRun.active) {
            this.updateSpeedRunStats();
        }
    },
    setButtonStates(config) {
        const buttons = {
            'show-answer': config.showAnswer || false,
            'game-btn-answer': config.showAnswer || false,
            'next-question': config.showNext || false,
            'game-btn-next': config.showNext || false,
            'end-game': config.showEnd !== false,
            'game-btn-end': config.showEnd !== false
        };
        Object.entries(buttons).forEach(([id, visible]) => {
            const btn = document.getElementById(id);
            if (btn) {
                if (visible) {
                    btn.classList.remove('hidden');
                    btn.disabled = false;
                } else {
                    btn.classList.add('hidden');
                }
            }
        });
    },
    updateSpeedRunStats() {
        const progressEl = document.getElementById('speedrun-progress');
        const remainingEl = document.getElementById('speedrun-remaining');
        const timerEl = document.getElementById('speedrun-timer');
        if (progressEl) {
            progressEl.textContent = `${gameState.speedRun.correctCount}/${gameState.speedRun.targetCount}`;
        }
        if (remainingEl) {
            const remaining = gameState.speedRun.targetCount - gameState.speedRun.correctCount;
            remainingEl.textContent = `残り: あと ${remaining} 問`;
        }
        if (timerEl && gameState.speedRun.startTime) {
            const end = gameState.speedRun.endTime || performance.now();
            const elapsed = (end - gameState.speedRun.startTime) / 1000;
            const minutes = Math.floor(elapsed / 60);
            const seconds = Math.floor(elapsed % 60);
            timerEl.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        }
    },
    updateQuestion(questionText, questionType, mode = 'normal') {
        const questionTextEl = document.getElementById('question-text');
        const questionTypeEl = document.getElementById('question-type');
        if (questionTextEl) questionTextEl.textContent = questionText;
        if (questionTypeEl) questionTypeEl.textContent = questionType;
        const gameQuestionText = document.getElementById('game-question-text');
        const gameQuestionType = document.getElementById('game-question-type');
        if (gameQuestionText) gameQuestionText.textContent = questionText;
        if (gameQuestionType) gameQuestionType.textContent = questionType;
        if (mode === 'registration') {
            this.updateRegistrationProgress();
        }
    },
    updateRegistrationProgress() {
        const progressEl = document.getElementById('question-progress');
        if (progressEl && gameState.registrationList) {
            const total = gameState.registrationList.length;
            const current = Math.min(gameState.registrationIndex + 1, total);
            progressEl.textContent = `問 ${current}／登録済み ${total} 件`;
        }
    }
};

// === 統合選択肢管理システム ===
const ChoiceManager = {
    showChoices(choices, mode = 'reverse') {
        const questionOverlay = document.getElementById('game-question-overlay');
        const choicesOverlay = document.getElementById('game-choices-overlay');
        const grid = document.getElementById('game-choices-grid');
        if (!choicesOverlay || !grid) {
            log('Choice overlay elements not found');
            return;
        }
        if (questionOverlay) {
            questionOverlay.classList.add('hidden');
        }
        grid.innerHTML = '';
        choices.forEach((choice, index) => {
            const button = document.createElement('button');
            button.className = 'choice-btn';
            button.textContent = choice.name;
            button.onclick = () => this.handleChoiceClick(choice, button, mode);
            grid.appendChild(button);
        });
        choicesOverlay.classList.remove('hidden');
        UIManager.setButtonStates({
            showAnswer: false,
            showNext: false,
            showEnd: true
        });
        log(`Choices displayed: ${choices.length} options`);
    },
    hideChoices() {
        const choicesOverlay = document.getElementById('game-choices-overlay');
        const questionOverlay = document.getElementById('game-question-overlay');
        if (choicesOverlay) {
            choicesOverlay.classList.add('hidden');
        }
        if (questionOverlay && gameState.isPlaying) {
            questionOverlay.classList.remove('hidden');
        }
    },
    handleChoiceClick(selectedChoice, button, mode) {
        try {
            document.querySelectorAll('.choice-btn').forEach(btn => {
                btn.disabled = true;
                btn.style.pointerEvents = 'none';
            });
            if (mode === 'reverse') {
                this.handleReverseChoice(selectedChoice, button);
            } else {
                log(`Choice selected in ${mode} mode: ${selectedChoice.name}`);
            }
        } catch (error) {
            log('Error handling choice click: ' + error.message);
        }
    },
    handleReverseChoice(selectedChoice, button) {
        const isCorrect = selectedChoice.name === gameState.currentQuestion.name;
        gameState.timerExpired = true;
        stopTimer();
        if (isCorrect) {
            const timeBonus = Math.max(0, gameState.timer * 2);
            const baseScore = 100;
            const streakBonus = gameState.streak * 10;
            const totalScore = baseScore + timeBonus + streakBonus;
            gameState.score += totalScore;
            gameState.streak++;
            log(`Correct answer! Score: ${totalScore}`);
        } else {
            gameState.streak = 0;
            log('Incorrect answer');
        }
        this.showAnswerFeedback(selectedChoice.name, isCorrect);
        UIManager.updateAllStats();
    },
    showAnswerFeedback(selectedName, isCorrect) {
        const correctName = gameState.currentQuestion?.name;
        document.querySelectorAll('.choice-btn').forEach(btn => {
            if (btn.textContent === correctName) {
                btn.classList.add('correct');
            } else if (selectedName && btn.textContent === selectedName) {
                btn.classList.add('incorrect');
            }
        });
        MessageManager.showFeedback(selectedName, isCorrect, correctName);
        UIManager.setButtonStates({
            showAnswer: false,
            showNext: true,
            showEnd: true
        });
        this.hideChoices();
    },
    generateMultipleChoices() {
        try {
            const correct = gameState.currentQuestion;
            const allOptions = [
                ...facilityQuestions,
                ...intersectionQuestions,
                ...gameState.customProblems.filter(p => p.type !== 'street')
            ];
            const incorrectOptions = allOptions.filter(q => q.name !== correct.name);
            const shuffled = incorrectOptions.sort(() => 0.5 - Math.random());
            const choices = [correct, ...shuffled.slice(0, 3)];
            return choices.sort(() => 0.5 - Math.random());
        } catch (error) {
            log('Error generating choices: ' + error.message);
            return [gameState.currentQuestion];
        }
    }
};

// === 統合メッセージ管理システム ===
const MessageManager = {
    show(message, type = 'info', duration = 5000) {
        const className = `${type}-message`;
        const sidebar = document.querySelector('.sidebar');
        if (!sidebar) return;
        const messageDiv = document.createElement('div');
        messageDiv.className = className;
        messageDiv.textContent = message;
        sidebar.insertBefore(messageDiv, sidebar.firstChild);
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, duration);
    },
    showWarning(message) { this.show(message, 'warning'); },
    showSuccess(message) { this.show(message, 'success'); },
    showError(message) { this.show(message, 'error'); },
    showInfo(message) { this.show(message, 'info'); },
    showFeedback(selectedName, isCorrect, correctName) {
        const existing = document.getElementById('reverse-feedback-popup');
        if (existing) existing.remove();
        const popup = document.createElement('div');
        popup.id = 'reverse-feedback-popup';
        popup.style.cssText = `position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(45,45,45,0.95); padding: 1.5rem; border-radius: 12px; z-index: 2000; color: white; text-align: center; backdrop-filter: blur(10px); min-width: 280px; max-width: 90vw;`;
        popup.innerHTML = `
            <div style="font-size: 1.25rem; font-weight: bold; margin-bottom: 1rem;">
                ${isCorrect ? '✅ 正解！' : '❌ 不正解'}
            </div>
            <div>あなたの選択: <strong>${selectedName}</strong></div>
            ${isCorrect ? '' : `<div style="margin-top: 0.5rem;">正解: <strong style="color: #4CAF50;">${correctName}</strong></div>`}
        `;
        document.body.appendChild(popup);
        setTimeout(() => {
            if (popup.parentNode) {
                popup.parentNode.removeChild(popup);
            }
        }, 3000);
    }
};