document.addEventListener("DOMContentLoaded", () => {
  const getPasswordStrength = (password) => {
    let score = 0;
    if ((password || "").length >= 8) score += 1;
    if ((password || "").length >= 12) score += 1;
    if (/[A-Z]/.test(password || "")) score += 1;
    if (/[a-z]/.test(password || "")) score += 1;
    if (/\d/.test(password || "")) score += 1;
    if (/[^A-Za-z0-9]/.test(password || "")) score += 1;
    if (score <= 3) return "weak";
    if (score <= 4) return "medium";
    return "strong";
  };

  document.querySelectorAll("[data-password-meter]").forEach((form) => {
    const passwordInput =
      form.querySelector("input[name='password1']") ||
      form.querySelector("input[name='new_password1']");
    const meterBar = form.querySelector("[data-password-meter-bar]");
    const meterLabel = form.querySelector("[data-password-meter-label]");
    if (!passwordInput || !meterBar || !meterLabel) return;

    const labels = {
      weak: meterLabel.dataset.weak || "Yeu",
      medium: meterLabel.dataset.medium || "Trung binh",
      strong: meterLabel.dataset.strong || "Manh",
    };

    const renderStrength = () => {
      meterBar.classList.remove("is-weak", "is-medium", "is-strong");
      if (!passwordInput.value) {
        meterLabel.textContent = "-";
        return;
      }
      const strength = getPasswordStrength(passwordInput.value);
      meterBar.classList.add(`is-${strength}`);
      meterLabel.textContent = labels[strength];
    };

    passwordInput.addEventListener("input", renderStrength);
    renderStrength();
  });

  const panels = document.querySelectorAll(".panel, .card");
  panels.forEach((el, idx) => {
    el.classList.add("fade-up");
    el.style.animationDelay = `${Math.min(idx * 0.05, 0.35)}s`;
  });

  const isMobile = window.matchMedia("(max-width: 1080px)").matches;
  if (isMobile) {
    document.querySelectorAll(".menu a.active").forEach((link) => {
      link.scrollIntoView({ block: "nearest", inline: "nearest" });
    });
  }

  // Mobile sidebar (hamburger) toggle
  const layout = document.querySelector(".cms-layout");
  const sidebarToggle = document.querySelector("[data-sidebar-toggle]");
  const sidebarBackdrop = document.querySelector("[data-sidebar-backdrop]");
  const mobileMq = window.matchMedia("(max-width: 1080px)");

  const setSidebarOpen = (open) => {
    if (!layout) return;
    layout.classList.toggle("is-sidebar-open", !!open);
    document.body.classList.toggle("is-sidebar-open", !!open);
    if (sidebarToggle) sidebarToggle.setAttribute("aria-expanded", open ? "true" : "false");
  };

  if (layout && sidebarToggle && sidebarBackdrop) {
    sidebarToggle.addEventListener("click", () => {
      if (!mobileMq.matches) return;
      const open = !layout.classList.contains("is-sidebar-open");
      setSidebarOpen(open);
    });

    sidebarBackdrop.addEventListener("click", () => setSidebarOpen(false));

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") setSidebarOpen(false);
    });

    layout.querySelectorAll(".sidebar a").forEach((link) => {
      link.addEventListener("click", () => {
        if (mobileMq.matches) setSidebarOpen(false);
      });
    });

    if (typeof mobileMq.addEventListener === "function") {
      mobileMq.addEventListener("change", () => {
        setSidebarOpen(false);
      });
    } else if (typeof mobileMq.addListener === "function") {
      mobileMq.addListener(() => {
        setSidebarOpen(false);
      });
    }
  }

  document.querySelectorAll("input[type='file']").forEach((input) => {
    input.addEventListener("change", (event) => {
      const file = event.target.files && event.target.files[0];
      const preview = document.querySelector(`img[data-preview-for='${input.id}']`);
      if (!preview) return;
      if (!file || !file.type || !file.type.startsWith("image/")) return;

      preview.src = URL.createObjectURL(file);
      preview.classList.remove("is-hidden");
    });
  });

  // Better UX for long multi-select fields (e.g. San pham in Cua hang form)
  document.querySelectorAll("form select[multiple]").forEach((selectEl) => {
    if (!selectEl.id) return;

    const row = selectEl.closest(".form-row");
    if (!row) return;
    row.classList.add("multi-row");

    const box = document.createElement("div");
    box.className = "multi-select-box";
    box.innerHTML = `
      <div class="multi-select-tools">
        <input type="text" class="multi-search" placeholder="Tìm nhanh sản phẩm..." aria-label="Tìm nhanh sản phẩm">
        <div class="multi-actions">
          <button type="button" class="multi-btn" data-action="all">Chọn tất cả</button>
          <button type="button" class="multi-btn" data-action="clear">Bỏ chọn</button>
        </div>
      </div>
      <div class="multi-meta">Đã chọn <strong class="multi-count">0</strong> mục</div>
      <div class="multi-option-list" data-multi-list></div>
    `;

    selectEl.parentNode.insertBefore(box, selectEl);
    box.appendChild(selectEl);
    selectEl.classList.add("enhanced-multi");
    selectEl.hidden = true;

    const searchInput = box.querySelector(".multi-search");
    const countNode = box.querySelector(".multi-count");
    const optionList = box.querySelector("[data-multi-list]");

    const updateCount = () => {
      const count = Array.from(selectEl.options).filter((o) => o.selected).length;
      countNode.textContent = String(count);
    };

    const syncOptionUi = (option, checkbox, rowEl) => {
      checkbox.checked = !!option.selected;
      rowEl.classList.toggle("is-selected", !!option.selected);
    };

    Array.from(selectEl.options).forEach((opt) => {
      const rowEl = document.createElement("label");
      rowEl.className = "multi-option";
      rowEl.dataset.value = opt.value;
      rowEl.innerHTML = `
        <input type="checkbox" class="multi-option-check">
        <span class="multi-option-text"></span>
      `;
      const checkbox = rowEl.querySelector(".multi-option-check");
      const textNode = rowEl.querySelector(".multi-option-text");
      textNode.textContent = opt.text;
      checkbox.disabled = !!opt.disabled;
      syncOptionUi(opt, checkbox, rowEl);

      rowEl.addEventListener("click", (event) => {
        event.preventDefault();
        if (opt.disabled) return;
        opt.selected = !opt.selected;
        syncOptionUi(opt, checkbox, rowEl);
        updateCount();
        selectEl.dispatchEvent(new Event("change", { bubbles: true }));
      });

      optionList.appendChild(rowEl);
    });

    const filterOptions = (keyword) => {
      const q = (keyword || "").trim().toLowerCase();
      Array.from(optionList.querySelectorAll(".multi-option")).forEach((rowEl) => {
        const text = (rowEl.querySelector(".multi-option-text")?.textContent || "").toLowerCase();
        const visible = !q || text.includes(q);
        rowEl.hidden = !visible;
      });
      Array.from(selectEl.options).forEach((opt, idx) => {
        const rowEl = optionList.children[idx];
        const visible = !q || opt.text.toLowerCase().includes(q);
        if (rowEl) rowEl.hidden = !visible;
      });
    };

    box.querySelectorAll(".multi-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const action = btn.getAttribute("data-action");
        Array.from(selectEl.options).forEach((opt, idx) => {
          const rowEl = optionList.children[idx];
          const visible = rowEl ? !rowEl.hidden : true;
          if (!visible || opt.disabled) return;
          opt.selected = action === "all";
          const checkbox = rowEl?.querySelector(".multi-option-check");
          if (rowEl && checkbox) syncOptionUi(opt, checkbox, rowEl);
        });
        updateCount();
        selectEl.dispatchEvent(new Event("change", { bubbles: true }));
      });
    });

    searchInput.addEventListener("input", () => filterOptions(searchInput.value));
    selectEl.addEventListener("change", () => {
      Array.from(selectEl.options).forEach((opt, idx) => {
        const rowEl = optionList.children[idx];
        const checkbox = rowEl?.querySelector(".multi-option-check");
        if (rowEl && checkbox) syncOptionUi(opt, checkbox, rowEl);
      });
      updateCount();
    });
    updateCount();
  });

  // Custom dropdown (single select)
  document.querySelectorAll("[data-dropdown]").forEach((dd) => {
    const trigger = dd.querySelector(".dd-trigger");
    const menu = dd.querySelector(".dd-menu");
    const hiddenInput = dd.querySelector("input[type='hidden']");
    const items = dd.querySelectorAll(".dd-item");
    if (!trigger || !menu || !hiddenInput) return;

    const setLabel = (value) => {
      const active = Array.from(items).find((i) => i.dataset.value === value);
      if (active) {
        trigger.textContent = active.textContent;
      }
    };

    setLabel(hiddenInput.value || "");

    trigger.addEventListener("click", (event) => {
      event.preventDefault();
      dd.classList.toggle("open");
    });

    items.forEach((item) => {
      item.addEventListener("click", () => {
        const value = item.dataset.value || "";
        hiddenInput.value = value;
        setLabel(value);
        dd.classList.remove("open");
      });
    });

    document.addEventListener("click", (event) => {
      if (!dd.contains(event.target)) {
        dd.classList.remove("open");
      }
    });
  });

  // Checkbox filter dropdown with search
  document.querySelectorAll("[data-filter-dropdown]").forEach((dd) => {
    const trigger = dd.querySelector(".dd-trigger");
    const menu = dd.querySelector(".dd-menu");
    const searchInput = dd.querySelector("[data-dd-search]");
    const list = dd.querySelector("[data-dd-list]");
    if (!trigger || !menu || !list) return;

    const updateCount = () => {
      const checked = dd.querySelectorAll("input[type='checkbox']:checked").length;
      let countNode = dd.querySelector(".dd-count");
      if (checked > 0) {
        if (!countNode) {
          countNode = document.createElement("span");
          countNode.className = "dd-count";
          trigger.appendChild(countNode);
        }
        countNode.textContent = String(checked);
      } else if (countNode) {
        countNode.remove();
      }
    };

    trigger.addEventListener("click", (event) => {
      event.preventDefault();
      dd.classList.toggle("open");
      if (dd.classList.contains("open") && searchInput) {
        searchInput.focus();
      }
    });

    if (searchInput) {
      searchInput.addEventListener("input", () => {
        const q = (searchInput.value || "").trim().toLowerCase();
        list.querySelectorAll(".dd-option").forEach((opt) => {
          const text = opt.textContent.trim().toLowerCase();
          opt.style.display = !q || text.includes(q) ? "flex" : "none";
        });
      });
    }

    dd.querySelectorAll("input[type='checkbox']").forEach((cb) => {
      cb.addEventListener("change", updateCount);
    });

    document.addEventListener("click", (event) => {
      if (!dd.contains(event.target)) {
        dd.classList.remove("open");
      }
    });

    updateCount();
  });

  // Select all checkboxes helper
  document.querySelectorAll("[data-select-all]").forEach((master) => {
    const target = master.getAttribute("data-select-target");
    const items = document.querySelectorAll(`[data-select-item='${target}']`);
    master.addEventListener("change", () => {
      items.forEach((cb) => {
        cb.checked = master.checked;
      });
    });
  });

  // Global fixed horizontal scrollbar for wide tables
  const globalXBar = document.getElementById("global-xbar");
  if (globalXBar) {
    const globalXInner = globalXBar.querySelector(".global-xbar-inner");
    const baseXBarSize = 14;
    let activeTableWrap = null;
    let syncingFromWrap = false;
    let syncingFromBar = false;

    const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
    const readZoomScale = () => {
      const vvScale = window.visualViewport && Number(window.visualViewport.scale);
      if (Number.isFinite(vvScale) && vvScale > 0 && Math.abs(vvScale - 1) > 0.02) return vvScale;
      const dpr = window.devicePixelRatio || 1;
      return dpr;
    };
    const syncBarScale = () => {
      const zoomScale = clamp(readZoomScale(), 0.75, 2);
      globalXBar.style.setProperty("--xbar-size", `${Math.round(baseXBarSize * zoomScale)}px`);
    };

    const getTargets = () =>
      Array.from(document.querySelectorAll(".table-wrap, .user-table-wrap, .order-table-wrap")).filter(
        (el) => el && el.getClientRects().length > 0
      );

    const pickVisibleTarget = () => {
      const targets = getTargets();
      if (!targets.length) return null;
      const vh = window.innerHeight || document.documentElement.clientHeight;
      let best = null;
      let bestScore = -1;
      targets.forEach((el) => {
        const r = el.getBoundingClientRect();
        const visible = Math.max(0, Math.min(r.bottom, vh) - Math.max(r.top, 0));
        if (visible > bestScore) {
          bestScore = visible;
          best = el;
        }
      });
      return best || targets[0];
    };

    const syncBarGeometry = () => {
      const target = activeTableWrap || pickVisibleTarget();
      if (!target) return;
      const rect = target.getBoundingClientRect();
      const left = Math.max(8, rect.left + 10);
      const width = Math.max(160, rect.width - 20);
      globalXBar.style.left = `${left}px`;
      globalXBar.style.width = `${width}px`;
      globalXBar.style.top = "";
    };

    const syncFromWrap = () => {
      if (!activeTableWrap || !globalXInner) return;
      syncingFromWrap = true;
      globalXInner.style.width = `${activeTableWrap.scrollWidth}px`;
      const wrapMax = Math.max(1, activeTableWrap.scrollWidth - activeTableWrap.clientWidth);
      const barMax = Math.max(1, globalXBar.scrollWidth - globalXBar.clientWidth);
      const ratio = activeTableWrap.scrollLeft / wrapMax;
      globalXBar.scrollLeft = ratio * barMax;
      syncingFromWrap = false;
    };

    const refreshActive = () => {
      syncBarScale();
      if (!activeTableWrap || activeTableWrap.scrollWidth <= activeTableWrap.clientWidth + 2) {
        activeTableWrap = pickVisibleTarget();
      }
      if (!activeTableWrap) {
        globalXBar.hidden = true;
        return;
      }
      if (activeTableWrap.scrollWidth <= activeTableWrap.clientWidth + 1) {
        globalXBar.hidden = true;
        return;
      }
      syncBarGeometry();
      syncFromWrap();
      globalXBar.hidden = false;
    };

    document.querySelectorAll(".table-wrap, .user-table-wrap, .order-table-wrap").forEach((el) => {
      el.addEventListener("mouseenter", () => {
        activeTableWrap = el;
        refreshActive();
      });
      el.addEventListener("scroll", () => {
        if (!activeTableWrap) activeTableWrap = el;
        if (activeTableWrap !== el) return;
        if (syncingFromBar) return;
        syncFromWrap();
      });
    });

    globalXBar.addEventListener("scroll", () => {
      if (!activeTableWrap) return;
      if (syncingFromWrap) return;
      syncingFromBar = true;
      const barMax = Math.max(1, globalXBar.scrollWidth - globalXBar.clientWidth);
      const wrapMax = Math.max(1, activeTableWrap.scrollWidth - activeTableWrap.clientWidth);
      const ratio = globalXBar.scrollLeft / barMax;
      activeTableWrap.scrollLeft = ratio * wrapMax;
      syncingFromBar = false;
    });

    window.addEventListener("resize", refreshActive);
    window.addEventListener("scroll", refreshActive, { passive: true });
    if (window.visualViewport) {
      window.visualViewport.addEventListener("resize", refreshActive);
      window.visualViewport.addEventListener("scroll", refreshActive);
    }
    refreshActive();
  }

  // CuaHang coordinate picker integration (from store/home map click)
  const pickBtn = document.getElementById("btn-pick-coord");
  const inlineMapEl = document.getElementById("admin-coord-map");
  if (pickBtn || inlineMapEl) {
    const latInput = document.getElementById((pickBtn && pickBtn.dataset.latField) || "id_vi_do");
    const lonInput = document.getElementById((pickBtn && pickBtn.dataset.lonField) || "id_kinh_do");
    const sourceInput = document.getElementById((pickBtn && pickBtn.dataset.sourceField) || "id_coord_from_map");
    const searchInput = document.getElementById("admin-coord-search");
    const searchBtn = document.getElementById("admin-coord-search-btn");
    const statusEl = document.getElementById("admin-coord-status");

    if (latInput) {
      latInput.readOnly = true;
      latInput.title = "Tọa độ chỉ được lấy từ bản đồ.";
    }
    if (lonInput) {
      lonInput.readOnly = true;
      lonInput.title = "Tọa độ chỉ được lấy từ bản đồ.";
    }

    const setStatus = (msg, isOk = true) => {
      if (!statusEl) return;
      statusEl.textContent = msg;
      statusEl.style.color = isOk ? "" : "#b91c1c";
    };

    // Inline map in admin form
    if (inlineMapEl && window.L && latInput && lonInput && sourceInput) {
      const addressInput = document.getElementById("id_dia_chi");
      const initLat = Number(latInput.value);
      const initLon = Number(lonInput.value);
      const hasInit = Number.isFinite(initLat) && Number.isFinite(initLon);
      const map = L.map(inlineMapEl).setView(
        hasInit ? [initLat, initLon] : [10.7769, 106.7009],
        hasInit ? 17 : 13
      );

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
        referrerPolicy: "strict-origin-when-cross-origin",
        crossOrigin: true,
      }).addTo(map);

      let marker = null;
      const applyCoord = (lat, lon, msg = "Đã chọn tọa độ từ bản đồ.") => {
        if (!Number.isFinite(lat) || !Number.isFinite(lon)) return;
        if (!marker) {
          marker = L.marker([lat, lon]).addTo(map);
        } else {
          marker.setLatLng([lat, lon]);
        }
        latInput.value = lat.toFixed(6);
        lonInput.value = lon.toFixed(6);
        sourceInput.value = "map";
        setStatus(`${msg} (${lat.toFixed(6)}, ${lon.toFixed(6)})`, true);
      };

      if (hasInit) {
        marker = L.marker([initLat, initLon]).addTo(map);
        setStatus(`Tọa độ hiện tại: (${initLat.toFixed(6)}, ${initLon.toFixed(6)})`, true);
      } else {
        setStatus("Click lên bản đồ để chọn tọa độ.", true);
      }

      map.on("click", async (e) => {
        const lat = e.latlng.lat;
        const lon = e.latlng.lng;
        applyCoord(lat, lon, "Đã chọn tọa độ");
        try {
          const url = `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`;
          const res = await fetch(url, { headers: { Accept: "application/json" } });
          if (res.ok) {
            const data = await res.json();
            if (data && data.display_name) {
              setStatus(`${data.display_name} (${lat.toFixed(6)}, ${lon.toFixed(6)})`, true);
            }
          }
        } catch (_e) {
          // ignore reverse geocode failures
        }
      });

      const searchAddress = async (rawQuery, options = {}) => {
        const q = String(rawQuery ?? searchInput?.value ?? "").trim();
        if (!q) {
          if (!options.silent) setStatus("Vui lòng nhập địa chỉ để tìm.", false);
          return false;
        }
        if (!options.silent) setStatus("Đang tìm địa chỉ...", true);
        try {
          const url = `https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&countrycodes=vn&q=${encodeURIComponent(q)}`;
          const res = await fetch(url, { headers: { Accept: "application/json" } });
          const data = await res.json();
          const first = Array.isArray(data) ? data[0] : null;
          if (!first) {
            if (!options.silent) setStatus("Không tìm thấy địa chỉ phù hợp.", false);
            return false;
          }
          const lat = Number(first.lat);
          const lon = Number(first.lon);
          map.setView([lat, lon], 17);
          applyCoord(lat, lon, "Đã tìm và chọn tọa độ");
          if (searchInput && !options.fromSearchInput) searchInput.value = q;
          return true;
        } catch (_e) {
          if (!options.silent) setStatus("Không thể tìm địa chỉ lúc này.", false);
          return false;
        }
      };

      if (searchBtn && searchInput) {
        if (addressInput && addressInput.value.trim()) {
          searchInput.value = addressInput.value.trim();
        }
        searchBtn.addEventListener("click", () => searchAddress(undefined, { fromSearchInput: true }));
        searchInput.addEventListener("keydown", (event) => {
          if (event.key === "Enter") {
            event.preventDefault();
            searchAddress(undefined, { fromSearchInput: true });
          }
        });
      }

      if (addressInput) {
        let debouncedTimer = null;
        let lastAutoQuery = "";

        const triggerSearchFromAddress = (silent = false, force = false) => {
          const q = addressInput.value.trim();
          if (q.length < 5) return;
          if (!force && q === lastAutoQuery) return;
          lastAutoQuery = q;
          if (searchInput) searchInput.value = q;
          searchAddress(q, { silent });
        };

        addressInput.addEventListener("input", () => {
          // Đánh dấu cần lấy lại tọa độ nếu địa chỉ thay đổi.
          sourceInput.value = "";
          if (debouncedTimer) window.clearTimeout(debouncedTimer);
          debouncedTimer = window.setTimeout(() => triggerSearchFromAddress(true), 700);
        });

        addressInput.addEventListener("blur", () => {
          if (debouncedTimer) window.clearTimeout(debouncedTimer);
          triggerSearchFromAddress(false, true);
        });

        addressInput.addEventListener("keydown", (event) => {
          if (event.key === "Enter") {
            event.preventDefault();
            if (debouncedTimer) window.clearTimeout(debouncedTimer);
            triggerSearchFromAddress(false, true);
          }
        });
      }

      if (pickBtn) {
        pickBtn.addEventListener("click", (event) => {
          event.preventDefault();
          map.invalidateSize();
          inlineMapEl.scrollIntoView({ behavior: "smooth", block: "center" });
        });
      }

      setTimeout(() => map.invalidateSize(), 100);
      return;
    }

    const applyPickedCoord = (payload) => {
      if (!payload || payload.type !== "admin_coord_pick") return;
      if (!latInput || !lonInput || !sourceInput) return;

      const lat = Number(payload.lat);
      const lon = Number(payload.lon);
      if (!Number.isFinite(lat) || !Number.isFinite(lon)) return;

      latInput.value = lat.toFixed(6);
      lonInput.value = lon.toFixed(6);
      sourceInput.value = "map";
    };

    const consumePickedCoordFromStorage = () => {
      try {
        const saved = localStorage.getItem("admin_coord_pick");
        if (!saved) return;
        applyPickedCoord(JSON.parse(saved));
        localStorage.removeItem("admin_coord_pick");
      } catch (_e) {
        // ignore parse/storage errors
      }
    };

    window.addEventListener("message", (event) => {
      if (!event || !event.data) return;
      applyPickedCoord(event.data);
    });

    window.addEventListener("storage", (event) => {
      if (event.key === "admin_coord_pick") {
        consumePickedCoordFromStorage();
      }
    });
    window.addEventListener("focus", consumePickedCoordFromStorage);
    window.addEventListener("pageshow", consumePickedCoordFromStorage);
    consumePickedCoordFromStorage();
    // Fallback: some browsers/tabs miss storage/message delivery timing.
    const coordPoller = window.setInterval(consumePickedCoordFromStorage, 1200);
    window.addEventListener("beforeunload", () => window.clearInterval(coordPoller));

    if (!pickBtn) return;
    pickBtn.addEventListener("click", (event) => {
      event.preventDefault();
      const baseUrl = pickBtn.dataset.mapUrl || pickBtn.getAttribute("href") || "/";
      const url = new URL(baseUrl, window.location.origin);

      const addressInput = document.getElementById("id_dia_chi");
      const address = addressInput ? addressInput.value.trim() : "";
      if (address) {
        url.searchParams.set("q", address);
      }

      if (latInput && lonInput && latInput.value && lonInput.value) {
        // Keep current saved point as initial map center.
        url.searchParams.set("center_lat", latInput.value);
        url.searchParams.set("center_lon", lonInput.value);
      }

      // Keep opener so the map tab can send coordinates back to this form.
      const mapWindow = window.open(url.toString(), "_blank");
      if (!mapWindow) {
        window.alert("Trình duyệt đang chặn mở tab bản đồ. Hãy cho phép pop-up rồi thử lại.");
      }
    });
  }
});
