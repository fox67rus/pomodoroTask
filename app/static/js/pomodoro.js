document.addEventListener("DOMContentLoaded", () => {
    const root = document.querySelector("[data-pomodoro]");
    if (!root) {
        return;
    }

    const form = root.querySelector("[data-pomodoro-form]");
    const mode = root.querySelector("[data-mode]");
    const durationInput = root.querySelector("[data-duration]");
    const timeDisplay = root.querySelector("[data-time]");
    const statusDisplay = root.querySelector("[data-status]");
    const startButton = root.querySelector("[data-start]");
    const pauseButton = root.querySelector("[data-pause]");
    const resetButton = root.querySelector("[data-reset]");

    let remaining = Number(durationInput.value) * 60;
    let timerId = null;

    const render = () => {
        const minutes = String(Math.floor(remaining / 60)).padStart(2, "0");
        const seconds = String(remaining % 60).padStart(2, "0");
        timeDisplay.textContent = `${minutes}:${seconds}`;
    };

    const reset = () => {
        clearInterval(timerId);
        timerId = null;
        remaining = Number(durationInput.value) * 60;
        statusDisplay.textContent = "Готов к старту";
        render();
    };

    const complete = async () => {
        clearInterval(timerId);
        timerId = null;
        statusDisplay.textContent = "Сессия завершена и сохранена";
        const data = new FormData(form);
        await fetch("/pomodoro/sessions", {
            method: "POST",
            body: data,
            credentials: "same-origin",
        });
        try {
            new Audio("data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YQAAAAA=").play();
        } catch (_error) {
            // Browser autoplay settings can block sound; saving the session is more important.
        }
    };

    mode.addEventListener("change", () => {
        const minutes = mode.selectedOptions[0].dataset.minutes;
        durationInput.value = minutes;
        reset();
    });

    durationInput.addEventListener("change", reset);
    resetButton.addEventListener("click", reset);
    pauseButton.addEventListener("click", () => {
        clearInterval(timerId);
        timerId = null;
        statusDisplay.textContent = "Пауза";
    });
    startButton.addEventListener("click", () => {
        if (timerId) {
            return;
        }
        statusDisplay.textContent = "Фокус";
        timerId = setInterval(() => {
            remaining -= 1;
            render();
            if (remaining <= 0) {
                complete();
            }
        }, 1000);
    });

    render();
});
