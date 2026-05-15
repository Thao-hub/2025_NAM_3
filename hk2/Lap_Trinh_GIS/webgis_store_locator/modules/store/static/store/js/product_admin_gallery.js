(function () {
  const manager = document.querySelector("[data-product-gallery-manager]");
  if (!manager) return;

  const container = manager.querySelector("[data-gallery-sortable]");
  if (!container) return;

  let dragItem = null;

  function refreshOrderInputs() {
    Array.from(container.querySelectorAll("[data-gallery-item]")).forEach(function (item, index) {
      const orderInput = item.querySelector("[data-gallery-order]");
      const badge = item.querySelector("[data-gallery-order-badge]");
      if (orderInput) orderInput.value = String(index + 1);
      if (badge) badge.textContent = "Thứ tự " + (index + 1);
    });
  }

  function toggleDelete(item) {
    const deleteInput = item.querySelector("[data-gallery-delete]");
    const button = item.querySelector("[data-gallery-delete-toggle]");
    if (!deleteInput || !button) return;
    const imageId = item.dataset.imageId || "";
    const deleting = deleteInput.value === imageId;
    deleteInput.value = deleting ? "" : imageId;
    item.style.opacity = deleting ? "1" : ".45";
    item.style.borderColor = deleting ? "rgba(15,23,42,.08)" : "rgba(239,68,68,.45)";
    button.textContent = deleting ? "Xóa ảnh" : "Giữ lại";
  }

  container.querySelectorAll("[data-gallery-item]").forEach(function (item) {
    item.addEventListener("dragstart", function () {
      dragItem = item;
      item.style.opacity = ".5";
    });

    item.addEventListener("dragend", function () {
      item.style.opacity = item.querySelector("[data-gallery-delete]").value ? ".45" : "1";
      dragItem = null;
      refreshOrderInputs();
    });

    item.addEventListener("dragover", function (event) {
      event.preventDefault();
      if (!dragItem || dragItem === item) return;
      const rect = item.getBoundingClientRect();
      const before = event.clientY < rect.top + rect.height / 2;
      container.insertBefore(dragItem, before ? item : item.nextSibling);
    });

    const deleteButton = item.querySelector("[data-gallery-delete-toggle]");
    if (deleteButton) {
      deleteButton.addEventListener("click", function () {
        toggleDelete(item);
      });
    }
  });

  refreshOrderInputs();
})();
