/**
 * AeroGuard-X1 Blueprint & Concept Studio Application.
 * Powered by Gemini Vision Engine & Aerospace Synthesis Core.
 * Handles AI prompt submission, CAD blueprints, photorealistic renders,
 * view toggles, spec parsing, and PNG/SVG export.
 */

let currentSpec = null;
let currentSvg = "";
let currentImageUrl = "";
let currentDisplayMode = "blueprint"; // "blueprint" | "render"
let currentViewMode = "multiview";

document.addEventListener("DOMContentLoaded", async () => {
  setupEventListeners();
  await loadPresets();

  // Generate initial default blueprint & image
  const defaultPrompt = "Heavy-lift agricultural hexacopter with 20L spray tank and folding arms";
  document.getElementById("promptInput").value = defaultPrompt;
  await generateBlueprint(defaultPrompt);
});

async function loadPresets() {
  try {
    const res = await fetch("/api/drone/blueprint-presets");
    const data = await res.json();
    if (!data || !data.presets) return;

    const container = document.getElementById("presetChipsContainer");
    container.innerHTML = "";

    data.presets.forEach(p => {
      const chip = document.createElement("button");
      chip.className = "prompt-chip";
      chip.textContent = p.title;
      chip.addEventListener("click", () => {
        document.getElementById("promptInput").value = p.prompt;
        generateBlueprint(p.prompt);
      });
      container.appendChild(chip);
    });
  } catch (err) {
    console.error("Failed to load presets:", err);
  }
}

function setupEventListeners() {
  // Generate Button
  const btnGen = document.getElementById("btnGenerate");
  btnGen.addEventListener("click", () => {
    const prompt = document.getElementById("promptInput").value.trim();
    if (prompt) generateBlueprint(prompt);
  });

  // Enter key in prompt input
  document.getElementById("promptInput").addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      const prompt = document.getElementById("promptInput").value.trim();
      if (prompt) generateBlueprint(prompt);
    }
  });

  // Display Switcher: CAD Blueprint vs AI Concept Render
  const btnDisplayBlueprint = document.getElementById("btnDisplayBlueprint");
  const btnDisplayRender = document.getElementById("btnDisplayRender");
  const svgContainer = document.getElementById("blueprintSvgContainer");
  const renderContainer = document.getElementById("droneImageContainer");
  const cadViewSelector = document.getElementById("cadViewSelector");

  btnDisplayBlueprint.addEventListener("click", () => {
    currentDisplayMode = "blueprint";
    btnDisplayBlueprint.classList.add("active");
    btnDisplayRender.classList.remove("active");
    svgContainer.style.display = "block";
    renderContainer.style.display = "none";
    cadViewSelector.style.display = "flex";
  });

  btnDisplayRender.addEventListener("click", () => {
    currentDisplayMode = "render";
    btnDisplayRender.classList.add("active");
    btnDisplayBlueprint.classList.remove("active");
    svgContainer.style.display = "none";
    renderContainer.style.display = "flex";
    cadViewSelector.style.display = "none";
  });

  // CAD Orthographic View Buttons
  document.querySelectorAll("#cadViewSelector .view-btn").forEach(btn => {
    btn.addEventListener("click", async () => {
      document.querySelectorAll("#cadViewSelector .view-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentViewMode = btn.dataset.view;
      const prompt = document.getElementById("promptInput").value.trim();
      await generateBlueprint(prompt, currentViewMode);
    });
  });

  // Download SVG
  document.getElementById("btnDownloadSvg").addEventListener("click", downloadSvg);

  // Download PNG Image
  document.getElementById("btnDownloadPng").addEventListener("click", downloadPng);

  // Export JSON
  document.getElementById("btnExportJson").addEventListener("click", exportJson);

  // Print Technical Drawing
  document.getElementById("btnPrintDrawing").addEventListener("click", () => window.print());
}

async function generateBlueprint(prompt, viewMode = currentViewMode) {
  const loader = document.getElementById("loadingOverlay");
  const imgSpinner = document.getElementById("imageLoadingSpinner");
  loader.classList.add("active");
  if (imgSpinner) imgSpinner.style.display = "flex"; // show image loader

  try {
    const res = await fetch("/api/drone/generate-blueprint", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, view_mode: viewMode })
    });
    const data = await res.json();

    if (data.status === "success") {
      currentSpec = data.spec;
      currentSvg = data.svg;
      currentImageUrl = data.image_url;

      // Render CAD SVG in viewport
      document.getElementById("blueprintSvgContainer").innerHTML = data.svg;

      // Render Concept Image in viewport (if any)
      if (data.image_url) {
        const imgEl = document.getElementById("droneRenderImg");
        imgEl.src = data.image_url;
      }

      // Hide image spinner once image src set (or if fallback static asset)
      if (imgSpinner) imgSpinner.style.display = "none";

      // Render Gemini AI Engineering Rationale
      if (data.ai_analysis) {
        const rationaleEl = document.getElementById("geminiAiAnalysisText");
        if (rationaleEl) rationaleEl.textContent = data.ai_analysis;
      }

      // Update Render Badge with Model information
      if (data.image_meta) {
        const badgeEl = document.getElementById("renderBadge");
        if (badgeEl) {
          const model = data.image_meta.model_used || "Gemini 2.5 Vision Engine";
          const configName = (data.spec.configuration || "DRONE").toUpperCase();
          badgeEl.innerHTML = `<strong style="color: #38bdf8;">${model}</strong> | ${configName} Concept Render`;
        }
      }

      // Update Spec Sheet
      updateSpecSheet(data.spec);
    }
  } catch (err) {
    console.error("Error generating blueprint & drone render:", err);
    // hide image spinner on error as well
    if (imgSpinner) imgSpinner.style.display = "none";
  } finally {
    loader.classList.remove("active");
  }
}

  const loader = document.getElementById("loadingOverlay");
  loader.classList.add("active");

  try {
    const res = await fetch("/api/drone/generate-blueprint", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, view_mode: viewMode })
    });
    const data = await res.json();

    if (data.status === "success") {
      currentSpec = data.spec;
      currentSvg = data.svg;
      currentImageUrl = data.image_url;

      // Render CAD SVG in viewport
      document.getElementById("blueprintSvgContainer").innerHTML = data.svg;

      // Render Concept Image in viewport
      if (data.image_url) {
        const imgEl = document.getElementById("droneRenderImg");
        imgEl.src = data.image_url;
      }

      // Render Gemini AI Engineering Rationale
      if (data.ai_analysis) {
        const rationaleEl = document.getElementById("geminiAiAnalysisText");
        if (rationaleEl) rationaleEl.textContent = data.ai_analysis;
      }

      // Update Render Badge with Model information
      if (data.image_meta) {
        const badgeEl = document.getElementById("renderBadge");
        if (badgeEl) {
          const model = data.image_meta.model_used || "Gemini 2.5 Vision Engine";
          const configName = (data.spec.configuration || "DRONE").toUpperCase();
          badgeEl.innerHTML = `<strong style="color: #38bdf8;">${model}</strong> | ${configName} Concept Render`;
        }
      }

      // Update Spec Sheet
      updateSpecSheet(data.spec);
    }
  } catch (err) {
    console.error("Error generating blueprint & drone render:", err);
  } finally {
    loader.classList.remove("active");
  }
}

function updateSpecSheet(spec) {
  document.getElementById("specDroneName").textContent = spec.name;
  document.getElementById("specDroneConfig").textContent = spec.configuration.toUpperCase();
  document.getElementById("specDroneConfig").style.color = spec.color_accent;
  document.getElementById("specDroneConfig").style.borderColor = spec.color_accent;

  document.getElementById("valWheelbase").textContent = `${spec.wheelbase_mm.toFixed(0)} mm`;
  document.getElementById("valAuw").textContent = `${spec.auw_kg.toFixed(2)} kg`;
  document.getElementById("valPayload").textContent = `${spec.payload_capacity_kg.toFixed(2)} kg`;
  document.getElementById("valProps").textContent = `${spec.propeller_dia_inch.toFixed(1)}" Carbon`;
  document.getElementById("valFlightTime").textContent = `${spec.flight_time_mins.toFixed(1)} mins`;
  document.getElementById("valSpeed").textContent = `${spec.max_speed_kmh.toFixed(0)} km/h`;
  document.getElementById("valMotorKv").textContent = `${spec.motor_kv} KV`;
  document.getElementById("valBattery").textContent = spec.battery_type;

  // Features list
  const featContainer = document.getElementById("specFeaturesList");
  featContainer.innerHTML = spec.key_features.map(f => `
    <div class="feature-pill" style="border-left-color: ${spec.color_accent};">
      ${f}
    </div>
  `).join("");
}

function downloadSvg() {
  if (!currentSvg) return;
  const blob = new Blob([currentSvg], { type: "image/svg+xml;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${(currentSpec?.name || "drone").toLowerCase().replace(/\s+/g, "_")}_blueprint.svg`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function downloadPng() {
  // If in Render mode and an image URL is active, download it directly
  if (currentDisplayMode === "render" && currentImageUrl) {
    const a = document.createElement("a");
    a.download = `${(currentSpec?.name || "drone").toLowerCase().replace(/\s+/g, "_")}_render.png`;
    a.href = currentImageUrl;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    return;
  }

  // If in Blueprint mode, convert the vector SVG to high-resolution PNG
  if (!currentSvg) return;
  const svgEl = document.querySelector("#blueprintSvgContainer svg");
  if (!svgEl) return;

  const svgData = new XMLSerializer().serializeToString(svgEl);
  const canvas = document.createElement("canvas");
  canvas.width = 1600;
  canvas.height = 1000;
  const ctx = canvas.getContext("2d");

  const img = new Image();
  const svgBlob = new Blob([svgData], { type: "image/svg+xml;charset=utf-8" });
  const url = URL.createObjectURL(svgBlob);

  img.onload = () => {
    ctx.drawImage(img, 0, 0);
    URL.revokeObjectURL(url);

    const a = document.createElement("a");
    a.download = `${(currentSpec?.name || "drone").toLowerCase().replace(/\s+/g, "_")}_blueprint.png`;
    a.href = canvas.toDataURL("image/png");
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };
  img.src = url;
}

function exportJson() {
  if (!currentSpec) return;
  const jsonStr = JSON.stringify(currentSpec, null, 2);
  const blob = new Blob([jsonStr], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${currentSpec.name.toLowerCase().replace(/\s+/g, "_")}_specs.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
