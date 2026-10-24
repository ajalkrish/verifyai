const API_URL = "http://127.0.0.1:8000/api/analyze";
const MAX_FILE_SIZE = 10 * 1024 * 1024;
const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"];

const imageInput = document.getElementById("imageInput");
const dropZone = document.getElementById("dropZone");
const emptyState = document.getElementById("emptyState");
const previewState = document.getElementById("previewState");
const imagePreview = document.getElementById("imagePreview");
const fileName = document.getElementById("fileName");
const uploadMessage = document.getElementById("uploadMessage");
const analyzeButton = document.getElementById("analyzeButton");
const buttonText = document.getElementById("buttonText");

const initialResult = document.getElementById("initialResult");
const loadingState = document.getElementById("loadingState");
const resultContent = document.getElementById("resultContent");
const errorState = document.getElementById("errorState");
const errorMessage = document.getElementById("errorMessage");

let selectedFile = null;
let previewUrl = null;
let isAnalyzing = false;

document.getElementById("year").textContent = new Date().getFullYear();

function setUploadMessage(message, isError = false) {
  uploadMessage.textContent = message;
  uploadMessage.classList.toggle("error", isError);
}

function clearPreviewUrl() {
  if (previewUrl) {
    URL.revokeObjectURL(previewUrl);
    previewUrl = null;
  }
}

function selectImage(file) {
  if (!file) return;

  if (!ALLOWED_TYPES.includes(file.type)) {
    setUploadMessage("Choose a JPG, PNG, or WEBP image.", true);
    return;
  }

  if (file.size > MAX_FILE_SIZE) {
    setUploadMessage("This image exceeds the 10 MB limit.", true);
    return;
  }

  clearPreviewUrl();
  selectedFile = file;
  previewUrl = URL.createObjectURL(file);
  imagePreview.src = previewUrl;
  fileName.textContent = `${file.name} · ${(file.size / (1024 * 1024)).toFixed(2)} MB`;

  emptyState.hidden = true;
  previewState.hidden = false;
  analyzeButton.disabled = false;
  setUploadMessage("Image selected. Ready to analyze.");
  resetResult();
}

function resetResult() {
  initialResult.hidden = false;
  loadingState.hidden = true;
  resultContent.hidden = true;
  errorState.hidden = true;
}

function clearImage() {
  if (isAnalyzing) return;

  selectedFile = null;
  imageInput.value = "";
  clearPreviewUrl();
  imagePreview.removeAttribute("src");
  emptyState.hidden = false;
  previewState.hidden = true;
  analyzeButton.disabled = true;
  setUploadMessage("");
  resetResult();
}

function setLoading(loading) {
  isAnalyzing = loading;
  analyzeButton.disabled = loading || !selectedFile;
  buttonText.textContent = loading ? "Analyzing..." : "Analyze image";
  initialResult.hidden = loading || resultContent.hidden === false;
  loadingState.hidden = !loading;
  if (loading) {
    resultContent.hidden = true;
    errorState.hidden = true;
  }
}

function formatScore(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "Unavailable";
  return number.toFixed(4);
}

function setScore(label, bar, value) {
  const number = Number(value);
  label.textContent = formatScore(number);
  bar.style.width = Number.isFinite(number)
    ? `${Math.max(0, Math.min(1, number)) * 100}%`
    : "0%";
}

function displayResult(data) {
  const prediction = String(data.prediction || "Inconclusive");
  const scores = data.model_scores || {};

  initialResult.hidden = true;
  loadingState.hidden = true;
  errorState.hidden = true;
  resultContent.hidden = false;

  const badge = document.getElementById("predictionBadge");
  const title = document.getElementById("predictionTitle");
  const description = document.getElementById("predictionDescription");

  badge.className = "prediction-badge";
  if (/real/i.test(prediction) && !/fake/i.test(prediction)) {
    badge.classList.add("real");
    title.textContent = "Likely real";
    description.textContent = "The model score favors the real-image label.";
  } else if (/fake|ai-generated/i.test(prediction)) {
    badge.classList.add("fake");
    title.textContent = "Likely AI-generated";
    description.textContent = "The model score favors the fake-image label.";
  } else {
    badge.classList.add("uncertain");
    title.textContent = prediction;
    description.textContent = "The model did not produce a decisive result.";
  }

  setScore(document.getElementById("realScore"),
           document.getElementById("realBar"), scores.real);
  setScore(document.getElementById("fakeScore"),
           document.getElementById("fakeBar"), scores.fake);
}

async function analyzeImage() {
  if (!selectedFile || isAnalyzing) return;

  setLoading(true);
  setUploadMessage("");

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      body: formData
    });

    let data;
    try {
      data = await response.json();
    } catch {
      throw new Error("The server returned an invalid response.");
    }

    if (!response.ok) {
      throw new Error(data.detail || data.message || `Server error (${response.status}).`);
    }

    if (!data.prediction) {
      throw new Error("The server response did not contain a prediction.");
    }

    displayResult(data);
  } catch (error) {
    initialResult.hidden = true;
    loadingState.hidden = true;
    resultContent.hidden = true;
    errorState.hidden = false;

    if (error instanceof TypeError) {
      errorMessage.textContent =
        "Cannot connect to the analysis server. Make sure the VerifyAI backend is running.";
    } else {
      errorMessage.textContent = error.message || "An unexpected error occurred.";
    }
  } finally {
    isAnalyzing = false;
    analyzeButton.disabled = !selectedFile;
    buttonText.textContent = "Analyze image";
  }
}

dropZone.addEventListener("click", (event) => {
  if (event.target.closest("button")) return;
  if (!previewState.hidden) return;
  imageInput.click();
});

dropZone.addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    if (previewState.hidden) imageInput.click();
  }
});

imageInput.addEventListener("change", () => {
  selectImage(imageInput.files[0]);
});

for (const eventName of ["dragenter", "dragover"]) {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.add("dragging");
  });
}

for (const eventName of ["dragleave", "drop"]) {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.remove("dragging");
  });
}

dropZone.addEventListener("drop", (event) => {
  selectImage(event.dataTransfer.files[0]);
});

document.getElementById("removeImage").addEventListener("click", (event) => {
  event.stopPropagation();
  clearImage();
});

analyzeButton.addEventListener("click", analyzeImage);

document.getElementById("resetButton").addEventListener("click", () => {
  if (!isAnalyzing) resetResult();
});

document.getElementById("retryButton").addEventListener("click", analyzeImage);
