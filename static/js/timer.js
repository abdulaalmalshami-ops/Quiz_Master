function initQuizTimer(timeLimitMinutes) {
    let timeRemaining = timeLimitMinutes * 60;
    const display = document.getElementById('time-display');
    const form = document.getElementById('quiz-form');

    function updateTimer() {
        const minutes = Math.floor(timeRemaining / 60);
        const seconds = timeRemaining % 60;

        display.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

        if (timeRemaining <= 0) {
            clearInterval(timerInterval);
            alert('Time is up! Submitting your answers.');
            form.submit();
        } else {
            timeRemaining--;
        }
    }

    updateTimer(); // Initial call
    const timerInterval = setInterval(updateTimer, 1000);
}
