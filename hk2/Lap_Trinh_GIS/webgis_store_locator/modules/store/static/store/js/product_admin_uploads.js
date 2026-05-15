(function () {
  const previewBlocks = document.querySelectorAll("[data-product-image-preview]");
  if (!previewBlocks.length) return;

  previewBlocks.forEach(function (block) {
    const inputId = block.getAttribute("data-input-id");
    if (!inputId) return;

    const input = document.getElementById(inputId);
    if (!input) return;

    let selectedFiles = [];
    let objectUrls = [];

    function revokeUrls() {
      objectUrls.forEach(function (url) {
        URL.revokeObjectURL(url);
      });
      objectUrls = [];
    }

    function syncInputFiles() {
      const transfer = new DataTransfer();
      selectedFiles.forEach(function (file) {
        transfer.items.add(file);
      });
      input.files = transfer.files;
    }

    function renderEmpty() {
      block.style.display = "block";
      block.style.width = "auto";
      block.style.maxWidth = "none";
      block.innerHTML = '<div class="multi-image-empty">Chưa có ảnh nào được chọn.</div>';
    }

    function renderPreview() {
      revokeUrls();
      block.innerHTML = "";
      block.style.display = "flex";
      block.style.flexWrap = "wrap";
      block.style.gap = "10px";
      block.style.alignItems = "flex-start";
      block.style.width = "100%";
      block.style.maxWidth = "100%";

      if (!selectedFiles.length) {
        renderEmpty();
        return;
      }

      selectedFiles.forEach(function (file, index) {
        const card = document.createElement("div");
        card.className = "multi-image-card";
        card.style.width = "88px";
        card.style.height = "88px";
        card.style.minWidth = "88px";
        card.style.minHeight = "88px";
        card.style.maxWidth = "88px";
        card.style.maxHeight = "88px";
        card.style.position = "relative";
        card.style.overflow = "hidden";
        card.style.borderRadius = "12px";

        const image = document.createElement("img");
        const url = URL.createObjectURL(file);
        objectUrls.push(url);
        image.src = url;
        image.alt = file.name || ("Ảnh " + (index + 1));
        image.style.width = "88px";
        image.style.height = "88px";
        image.style.objectFit = "cover";
        image.style.display = "block";

        const removeBtn = document.createElement("button");
        removeBtn.type = "button";
        removeBtn.className = "multi-image-remove";
        removeBtn.setAttribute("aria-label", "Bỏ ảnh");
        removeBtn.textContent = "x";
        removeBtn.style.position = "absolute";
        removeBtn.style.top = "6px";
        removeBtn.style.right = "6px";
        removeBtn.addEventListener("click", function () {
          selectedFiles.splice(index, 1);
          syncInputFiles();
          renderPreview();
        });

        const badge = document.createElement("div");
        badge.className = "multi-image-badge";
        badge.textContent = index === 0 ? "Ảnh chính" : "Ảnh phụ";
        badge.style.position = "absolute";
        badge.style.left = "6px";
        badge.style.bottom = "6px";

        card.appendChild(image);
        card.appendChild(removeBtn);
        card.appendChild(badge);
        block.appendChild(card);
      });
    }

    input.addEventListener("change", function () {
      const incomingFiles = Array.from(input.files || []).filter(function (file) {
        return file && file.type && file.type.startsWith("image/");
      });

      incomingFiles.forEach(function (file) {
        const exists = selectedFiles.some(function (selectedFile) {
          return (
            selectedFile.name === file.name &&
            selectedFile.size === file.size &&
            selectedFile.lastModified === file.lastModified
          );
        });
        if (!exists) {
          selectedFiles.push(file);
        }
      });

      renderPreview();
    });

    renderEmpty();
  });
})();
