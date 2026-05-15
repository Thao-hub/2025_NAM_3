document.addEventListener("DOMContentLoaded", () => {
  const getMessage = (field) => {
    const v = field.validity || {};
    if (v.valueMissing) {
      if (field.type === "checkbox" || field.type === "radio") return "Vui lòng chọn mục này.";
      return "Vui lòng điền vào trường này.";
    }
    if (v.typeMismatch) {
      if (field.type === "email") return "Vui lòng nhập đúng định dạng email.";
      if (field.type === "url") return "Vui lòng nhập đúng định dạng liên kết.";
    }
    if (v.tooShort) return `Vui lòng nhập ít nhất ${field.minLength} ký tự.`;
    if (v.tooLong) return `Vui lòng nhập tối đa ${field.maxLength} ký tự.`;
    if (v.patternMismatch) return "Giá trị nhập vào chưa đúng định dạng.";
    if (v.rangeUnderflow) return `Giá trị phải lớn hơn hoặc bằng ${field.min}.`;
    if (v.rangeOverflow) return `Giá trị phải nhỏ hơn hoặc bằng ${field.max}.`;
    if (v.stepMismatch) return "Giá trị nhập vào chưa đúng bước hợp lệ.";
    return field.validationMessage || "Giá trị không hợp lệ.";
  };

  const getFeedbackEl = (field) => {
    let feedback = field.parentElement?.querySelector(`.invalid-feedback[data-for="${field.id || field.name}"]`);
    if (feedback) return feedback;

    feedback = document.createElement("div");
    feedback.className = "invalid-feedback";
    feedback.dataset.for = field.id || field.name || "field";

    if (field.parentElement) {
      field.parentElement.appendChild(feedback);
    } else {
      field.insertAdjacentElement("afterend", feedback);
    }
    return feedback;
  };

  const showError = (field) => {
    const msg = getMessage(field);
    field.classList.add("is-invalid");
    field.style.borderColor = "#dc3545";
    const feedback = getFeedbackEl(field);
    feedback.textContent = msg;
    feedback.style.display = "block";
    feedback.style.color = "#dc3545";
    feedback.style.marginTop = "6px";
    feedback.style.fontSize = "0.875rem";
  };

  const clearError = (field) => {
    field.setCustomValidity("");
    field.classList.remove("is-invalid");
    field.style.borderColor = "";
    const feedback = field.parentElement?.querySelector(`.invalid-feedback[data-for="${field.id || field.name}"]`);
    if (feedback) feedback.style.display = "none";
  };

  const inputsSelector = "input, select, textarea";
  document.querySelectorAll("form").forEach((form) => {
    if (form.dataset.nativeValidation === "true") return;
    form.setAttribute("novalidate", "novalidate");

    const fields = Array.from(form.querySelectorAll(inputsSelector)).filter((el) => {
      const t = (el.type || "").toLowerCase();
      return !["hidden", "submit", "button", "reset"].includes(t);
    });

    fields.forEach((field) => {
      field.addEventListener(
        "invalid",
        (event) => {
          event.preventDefault();
          showError(field);
        },
        true
      );
      field.addEventListener("input", () => {
        if (field.checkValidity()) clearError(field);
      });
      field.addEventListener("change", () => {
        if (field.checkValidity()) clearError(field);
      });
    });

    form.addEventListener("submit", (event) => {
      let firstInvalid = null;
      fields.forEach((field) => {
        if (!field.checkValidity()) {
          if (!firstInvalid) firstInvalid = field;
          showError(field);
        } else {
          clearError(field);
        }
      });
      if (firstInvalid) {
        event.preventDefault();
        firstInvalid.focus();
      }
    });
  });
});
