(function () {
  "use strict";

  const root = document.getElementById("miniCalendar");
  if (!root) return;

  const grid = document.getElementById("mcGrid");
  const titleEl = document.getElementById("mcTitle");
  const dayDetail = document.getElementById("mcDayDetail");
  const viewButtons = root.querySelectorAll(".mc-view-btn");
  const prevBtn = document.getElementById("mcPrev");
  const nextBtn = document.getElementById("mcNext");
  const todayBtn = document.getElementById("mcToday");

  const MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
  ];
  const DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  let events = [];
  try {
    events = JSON.parse(root.dataset.events || "[]");
  } catch (e) {
    events = [];
  }

  // Group events by ISO date string ("YYYY-MM-DD") for quick lookup.
  const eventsByDate = {};
  events.forEach((ev) => {
    if (!eventsByDate[ev.date]) eventsByDate[ev.date] = [];
    eventsByDate[ev.date].push(ev);
  });

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  let view = "week"; // "week" | "month" | "year"
  let anchor = new Date(today); // date used to compute the visible range

  function isoDate(d) {
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${y}-${m}-${day}`;
  }

  function isSameDay(a, b) {
    return a.getFullYear() === b.getFullYear() &&
      a.getMonth() === b.getMonth() &&
      a.getDate() === b.getDate();
  }

  function categoryClass(category) {
    return "category-" + String(category).toLowerCase().replace(/\s+/g, "-");
  }

  function startOfWeek(d) {
    const result = new Date(d);
    result.setDate(result.getDate() - result.getDay());
    return result;
  }

  function renderDayDetail(dateObj) {
    const key = isoDate(dateObj);
    const dayEvents = eventsByDate[key] || [];
    if (dayEvents.length === 0) {
      dayDetail.classList.add("d-none");
      dayDetail.innerHTML = "";
      return;
    }
    const heading = dateObj.toLocaleDateString(undefined, {
      weekday: "long", month: "long", day: "numeric", year: "numeric",
    });
    let html = `<h6 class="mb-2">${heading}</h6><ul class="list-unstyled mb-0">`;
    dayEvents.forEach((ev) => {
      html += `<li class="mb-1"><span class="badge category-badge ${categoryClass(ev.category)}">${ev.category}</span> ${escapeHtml(ev.title)}</li>`;
    });
    html += "</ul>";
    dayDetail.innerHTML = html;
    dayDetail.classList.remove("d-none");
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  function makeDayCell(dateObj, opts) {
    opts = opts || {};
    const cell = document.createElement("div");
    cell.className = "mc-day";
    if (opts.otherMonth) cell.classList.add("mc-day-other-month");
    if (isSameDay(dateObj, today)) cell.classList.add("mc-day-today");

    const num = document.createElement("div");
    num.className = "mc-day-num";
    num.textContent = dateObj.getDate();
    cell.appendChild(num);

    const key = isoDate(dateObj);
    const dayEvents = eventsByDate[key] || [];
    if (dayEvents.length > 0) {
      const dots = document.createElement("div");
      dots.className = "mc-dots";
      dayEvents.slice(0, 4).forEach((ev) => {
        const dot = document.createElement("span");
        dot.className = "mc-dot " + categoryClass(ev.category);
        dot.title = ev.title;
        dots.appendChild(dot);
      });
      cell.appendChild(dots);

      if (opts.showLabels) {
        const labelWrap = document.createElement("div");
        labelWrap.className = "mc-labels";
        dayEvents.slice(0, 3).forEach((ev) => {
          const label = document.createElement("div");
          label.className = "mc-label " + categoryClass(ev.category);
          label.textContent = ev.title;
          labelWrap.appendChild(label);
        });
        if (dayEvents.length > 3) {
          const more = document.createElement("div");
          more.className = "mc-label-more";
          more.textContent = `+${dayEvents.length - 3} more`;
          labelWrap.appendChild(more);
        }
        cell.appendChild(labelWrap);
      }
    }

    cell.addEventListener("click", () => renderDayDetail(dateObj));
    return cell;
  }

  function renderWeek() {
    grid.className = "mc-grid mc-grid-week";
    grid.innerHTML = "";
    const start = startOfWeek(anchor);
    const end = new Date(start);
    end.setDate(end.getDate() + 6);
    titleEl.textContent = `Week of ${MONTH_NAMES[start.getMonth()]} ${start.getDate()} – ${MONTH_NAMES[end.getMonth()]} ${end.getDate()}, ${end.getFullYear()}`;

    for (let i = 0; i < 7; i++) {
      const d = new Date(start);
      d.setDate(start.getDate() + i);
      const col = document.createElement("div");
      col.className = "mc-week-col";
      const heading = document.createElement("div");
      heading.className = "mc-week-heading";
      heading.textContent = DAY_NAMES[i];
      col.appendChild(heading);
      col.appendChild(makeDayCell(d, { showLabels: true }));
      grid.appendChild(col);
    }
  }

  function renderMonth() {
    grid.className = "mc-grid mc-grid-month";
    grid.innerHTML = "";
    const year = anchor.getFullYear();
    const month = anchor.getMonth();
    titleEl.textContent = `${MONTH_NAMES[month]} ${year}`;

    DAY_NAMES.forEach((name) => {
      const heading = document.createElement("div");
      heading.className = "mc-week-heading";
      heading.textContent = name;
      grid.appendChild(heading);
    });

    const firstOfMonth = new Date(year, month, 1);
    const gridStart = startOfWeek(firstOfMonth);
    for (let i = 0; i < 42; i++) {
      const d = new Date(gridStart);
      d.setDate(gridStart.getDate() + i);
      grid.appendChild(makeDayCell(d, { otherMonth: d.getMonth() !== month }));
    }
  }

  function renderYear() {
    grid.className = "mc-grid mc-grid-year";
    grid.innerHTML = "";
    const year = anchor.getFullYear();
    titleEl.textContent = `${year}`;

    for (let m = 0; m < 12; m++) {
      const monthWrap = document.createElement("div");
      monthWrap.className = "mc-mini-month";

      const heading = document.createElement("div");
      heading.className = "mc-mini-month-heading";
      heading.textContent = MONTH_NAMES[m];
      heading.addEventListener("click", () => {
        anchor = new Date(year, m, 1);
        view = "month";
        setActiveViewButton();
        render();
      });
      monthWrap.appendChild(heading);

      const miniGrid = document.createElement("div");
      miniGrid.className = "mc-mini-grid";
      const firstOfMonth = new Date(year, m, 1);
      const gridStart = startOfWeek(firstOfMonth);
      for (let i = 0; i < 42; i++) {
        const d = new Date(gridStart);
        d.setDate(gridStart.getDate() + i);
        const cell = document.createElement("div");
        cell.className = "mc-mini-day";
        if (d.getMonth() !== m) cell.classList.add("mc-mini-day-other-month");
        if (isSameDay(d, today)) cell.classList.add("mc-mini-day-today");
        if (eventsByDate[isoDate(d)]) cell.classList.add("mc-mini-day-has-event");
        cell.textContent = d.getDate();
        cell.addEventListener("click", () => renderDayDetail(d));
        miniGrid.appendChild(cell);
      }
      monthWrap.appendChild(miniGrid);
      grid.appendChild(monthWrap);
    }
  }

  function render() {
    dayDetail.classList.add("d-none");
    dayDetail.innerHTML = "";
    if (view === "week") renderWeek();
    else if (view === "month") renderMonth();
    else renderYear();
  }

  function setActiveViewButton() {
    viewButtons.forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.view === view);
    });
  }

  viewButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      view = btn.dataset.view;
      setActiveViewButton();
      render();
    });
  });

  prevBtn.addEventListener("click", () => {
    if (view === "week") anchor.setDate(anchor.getDate() - 7);
    else if (view === "month") anchor.setMonth(anchor.getMonth() - 1);
    else anchor.setFullYear(anchor.getFullYear() - 1);
    render();
  });

  nextBtn.addEventListener("click", () => {
    if (view === "week") anchor.setDate(anchor.getDate() + 7);
    else if (view === "month") anchor.setMonth(anchor.getMonth() + 1);
    else anchor.setFullYear(anchor.getFullYear() + 1);
    render();
  });

  todayBtn.addEventListener("click", () => {
    anchor = new Date(today);
    render();
  });

  render();
})();
