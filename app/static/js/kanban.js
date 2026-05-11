document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".kanban-column").forEach((column) => {
        new Sortable(column, {
            group: "tasks",
            animation: 150,
            ghostClass: "sortable-ghost",
            onAdd: saveTaskPosition,
            onUpdate: saveTaskPosition,
        });
    });
});

function saveTaskPosition(event) {
    const card = event.item;
    const column = event.to;
    const placeholder = column.querySelector(".empty-column");
    if (placeholder) {
        placeholder.remove();
    }

    const formData = new FormData();
    formData.append("status", column.dataset.status);
    formData.append("position", event.newIndex + 1);

    fetch(`/tasks/${card.dataset.taskId}/status`, {
        method: "POST",
        body: formData,
        credentials: "same-origin",
    });
}
