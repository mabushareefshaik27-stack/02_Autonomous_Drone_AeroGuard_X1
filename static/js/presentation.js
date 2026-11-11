/**
 * AeroGuard-X1 Interactive Slide Deck Controller.
 * Manages slide transitions, keyboard shortcuts, speaker notes, and presentation timer.
 */

let currentSlide = 0;
let totalSlides = 0;
let timerSeconds = 0;
let timerInterval = null;

document.addEventListener("DOMContentLoaded", () => {
  const slides = document.querySelectorAll(".slide");
  totalSlides = slides.length;

  showSlide(0);
  startTimer();
  setupKeyboardControls();
  buildOverviewGrid();

  // Button Listeners
  document.getElementById("btnPrev").addEventListener("click", prevSlide);
  document.getElementById("btnNext").addEventListener("click", nextSlide);
  document.getElementById("btnNotes").addEventListener("click", toggleNotes);
  document.getElementById("btnOverview").addEventListener("click", toggleOverview);
  document.getElementById("btnFullscreen").addEventListener("click", toggleFullscreen);
  document.getElementById("btnCloseOverview").addEventListener("click", toggleOverview);
});

function showSlide(index) {
  const slides = document.querySelectorAll(".slide");
  if (index < 0 || index >= totalSlides) return;

  slides.forEach((s, i) => {
    s.classList.remove("active");
    if (i === index) {
      s.classList.add("active");
    }
  });

  currentSlide = index;

  // Update slide counter
  const counterEl = document.getElementById("slideCounter");
  if (counterEl) {
    const formattedCurrent = String(currentSlide + 1).padStart(2, "0");
    const formattedTotal = String(totalSlides).padStart(2, "0");
    counterEl.textContent = `${formattedCurrent} / ${formattedTotal}`;
  }

  // Update Progress Bar
  const progEl = document.getElementById("slideProgressBar");
  if (progEl) {
    const pct = ((currentSlide + 1) / totalSlides) * 100;
    progEl.style.width = `${pct}%`;
  }

  // Update Speaker Notes
  const currentSlideEl = slides[currentSlide];
  const notesText = currentSlideEl.dataset.notes || "No notes for this slide.";
  const notesBox = document.getElementById("speakerNotesContent");
  if (notesBox) {
    notesBox.textContent = notesText;
  }

  // Highlight in overview
  document.querySelectorAll(".overview-thumb").forEach((th, i) => {
    th.classList.toggle("active", i === currentSlide);
  });
}

function nextSlide() {
  if (currentSlide < totalSlides - 1) {
    showSlide(currentSlide + 1);
  }
}

function prevSlide() {
  if (currentSlide > 0) {
    showSlide(currentSlide - 1);
  }
}

function toggleNotes() {
  const drawer = document.getElementById("notesDrawer");
  drawer.classList.toggle("open");
}

function toggleOverview() {
  const modal = document.getElementById("overviewModal");
  modal.classList.toggle("open");
}

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(err => console.log(err));
  } else {
    document.exitFullscreen().catch(err => console.log(err));
  }
}

function startTimer() {
  const timerEl = document.getElementById("defenseTimer");
  timerInterval = setInterval(() => {
    timerSeconds++;
    const mins = String(Math.floor(timerSeconds / 60)).padStart(2, "0");
    const secs = String(timerSeconds % 60).padStart(2, "0");
    if (timerEl) timerEl.textContent = `${mins}:${secs}`;
  }, 1000);
}

function setupKeyboardControls() {
  window.addEventListener("keydown", (e) => {
    // If overview is open, Esc closes it
    if (e.key === "Escape") {
      const modal = document.getElementById("overviewModal");
      if (modal.classList.contains("open")) {
        modal.classList.remove("open");
        return;
      }
    }

    if (e.key === "ArrowRight" || e.key === " " || e.key === "PageDown") {
      e.preventDefault();
      nextSlide();
    } else if (e.key === "ArrowLeft" || e.key === "Backspace" || e.key === "PageUp") {
      e.preventDefault();
      prevSlide();
    } else if (e.key.toLowerCase() === "n") {
      toggleNotes();
    } else if (e.key.toLowerCase() === "o") {
      toggleOverview();
    } else if (e.key.toLowerCase() === "f") {
      toggleFullscreen();
    } else if (e.key.toLowerCase() === "p") {
      window.print();
    }
  });
}

function buildOverviewGrid() {
  const container = document.getElementById("overviewGridContainer");
  const slides = document.querySelectorAll(".slide");

  slides.forEach((s, idx) => {
    const title = s.querySelector(".slide-title")?.textContent || `Slide ${idx + 1}`;
    const thumb = document.createElement("div");
    thumb.className = "overview-thumb";
    thumb.innerHTML = `
      <div class="thumb-num">Slide ${String(idx + 1).padStart(2, "0")}</div>
      <div class="thumb-title">${title}</div>
      <div style="font-size: 0.65rem; color: #38bdf8;">Click to jump</div>
    `;
    thumb.addEventListener("click", () => {
      showSlide(idx);
      toggleOverview();
    });
    container.appendChild(thumb);
  });
}

