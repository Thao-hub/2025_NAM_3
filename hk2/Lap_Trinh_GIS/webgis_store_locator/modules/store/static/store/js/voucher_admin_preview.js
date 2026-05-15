(function () {
  function formatCurrency(value) {
    const amount = Number.isFinite(value) ? Math.max(0, Math.round(value)) : 0;
    return `${amount.toLocaleString("vi-VN")} đ`;
  }

  function initVoucherPreview() {
    const card = document.querySelector("[data-voucher-preview]");
    const discountTypeField = document.getElementById("id_loai_giam");
    const discountValueField = document.getElementById("id_gia_tri_giam");
    const minimumOrderField = document.getElementById("id_gia_tri_don_hang_toi_thieu");
    const maxDiscountField = document.getElementById("id_giam_toi_da");
    const codeField = document.getElementById("id_ma_code");
    const activeField = document.getElementById("id_dang_ap_dung");
    const sampleInput = document.getElementById("voucherPreviewSampleInput");

    if (!card || !discountTypeField || !discountValueField || !minimumOrderField) {
      return;
    }

    const subtotalEl = document.getElementById("voucherPreviewSubtotal");
    const discountEl = document.getElementById("voucherPreviewDiscount");
    const totalEl = document.getElementById("voucherPreviewTotal");
    const hintEl = document.getElementById("voucherPreviewHint");

    function updatePreview() {
      const sampleOrder = Number(
        sampleInput && sampleInput.value !== ""
          ? sampleInput.value
          : (card.dataset.sampleOrder || 200000)
      );
      const discountType = discountTypeField.value || "fixed";
      const discountValue = Number(discountValueField.value || 0);
      const minimumOrder = Number(minimumOrderField.value || 0);
      const maxDiscount = Number(maxDiscountField && maxDiscountField.value ? maxDiscountField.value : 0);
      const code = (codeField && codeField.value ? codeField.value.trim().toUpperCase() : "");
      const isActive = !activeField || activeField.checked;

      let discount = 0;
      let hint = "Nhập mã, loại giảm, giá trị giảm và điều kiện tối thiểu để xem kết quả ngay.";

      if (!Number.isFinite(sampleOrder) || sampleOrder < 0) {
        hint = "Số tiền mẫu phải là số hợp lệ từ 0 trở lên.";
      } else if (!isActive) {
        hint = "Voucher đang ở trạng thái tạm khóa nên khách hàng sẽ chưa dùng được.";
      } else if (minimumOrder > sampleOrder) {
        hint = `Đơn mẫu chưa đủ điều kiện vì cần tối thiểu ${formatCurrency(minimumOrder)}.`;
      } else if (discountValue <= 0) {
        hint = "Giá trị giảm cần lớn hơn 0 để tính được preview.";
      } else if (discountType === "percent") {
        discount = sampleOrder * (discountValue / 100);
        if (maxDiscount > 0) {
          discount = Math.min(discount, maxDiscount);
          hint = `Voucher ${code || "(chưa nhập mã)"} giảm ${discountValue}% và chặn tối đa ${formatCurrency(maxDiscount)}.`;
        } else {
          hint = `Voucher ${code || "(chưa nhập mã)"} giảm ${discountValue}% trên đơn mẫu.`;
        }
      } else {
        discount = discountValue;
        hint = `Voucher ${code || "(chưa nhập mã)"} giảm trực tiếp ${formatCurrency(discountValue)}.`;
      }

      discount = Math.min(discount, sampleOrder);
      subtotalEl.textContent = formatCurrency(sampleOrder);
      discountEl.textContent = formatCurrency(discount);
      totalEl.textContent = formatCurrency(sampleOrder - discount);
      hintEl.textContent = hint;
    }

      [
      discountTypeField,
      discountValueField,
      minimumOrderField,
      maxDiscountField,
      codeField,
      activeField,
      sampleInput,
    ].forEach(function (field) {
      if (!field) return;
      field.addEventListener("input", updatePreview);
      field.addEventListener("change", updatePreview);
    });

    updatePreview();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initVoucherPreview);
  } else {
    initVoucherPreview();
  }
})();
