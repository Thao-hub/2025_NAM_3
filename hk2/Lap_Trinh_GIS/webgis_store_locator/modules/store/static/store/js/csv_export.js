(function () {
  function escapeCsvCell(value) {
    if (value === null || value === undefined) {
      return '""';
    }

    let text = String(value);

    // Prevent Excel from interpreting cells as formulas when users open CSV files.
    if (/^[=+\-@]/.test(text)) {
      text = "'" + text;
    }

    text = text.replace(/"/g, '""');
    return '"' + text + '"';
  }

  function normalizeRow(record, columns) {
    return columns.map(function (column) {
      return escapeCsvCell(record[column.key]);
    });
  }

  function buildFilename(prefix, activeBrand) {
    const stamp = new Date().toISOString().replace(/[:.]/g, "-");
    const brand = String(activeBrand || "all")
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9_-]+/g, "-")
      .replace(/^-+|-+$/g, "") || "all";
    return prefix + "_" + brand + "_" + stamp + ".csv";
  }

  function exportCsv(options) {
    const items = Array.isArray(options.items) ? options.items : [];
    const columns = Array.isArray(options.columns) ? options.columns : [];

    if (!items.length || !columns.length) {
      return false;
    }

    const lines = [];
    lines.push(columns.map(function (column) { return escapeCsvCell(column.label); }).join(","));

    for (const item of items) {
      lines.push(normalizeRow(item, columns).join(","));
    }

    const csvParts = ["\ufeff", lines.join("\r\n")];
    const blob = new Blob(csvParts, { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");

    anchor.href = url;
    anchor.download = options.filename || buildFilename("export", options.activeBrand);
    anchor.rel = "noopener";
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();

    window.setTimeout(function () {
      URL.revokeObjectURL(url);
    }, 1000);

    return true;
  }

  window.StoreCsvExporter = {
    buildFilename: buildFilename,
    exportCsv: exportCsv,
  };
})();
