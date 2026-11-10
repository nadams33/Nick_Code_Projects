const expressionDisplay = document.querySelector("#expression");
const resultDisplay = document.querySelector("#result");
const errorDisplay = document.querySelector("#error");
const keypad = document.querySelector(".keypad");

let expression = "";
let showingResult = false;

function render() {
  expressionDisplay.textContent = expression
    .replaceAll("*", "×")
    .replaceAll("/", "÷")
    .replaceAll("-", "−");
}

function appendValue(value) {
  if (showingResult && /[0-9.(]/.test(value)) {
    expression = "";
  }
  showingResult = false;
  errorDisplay.textContent = "";
  expression += value;
  render();
}

function clear() {
  expression = "";
  showingResult = false;
  resultDisplay.textContent = "0";
  errorDisplay.textContent = "";
  render();
}

function backspace() {
  showingResult = false;
  errorDisplay.textContent = "";
  expression = expression.slice(0, -1);
  render();
}

async function calculate() {
  if (!expression.trim()) return;

  errorDisplay.textContent = "";
  try {
    const response = await fetch("/calc", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ expression }),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Unable to calculate this expression.");
    }

    resultDisplay.textContent = new Intl.NumberFormat(undefined, {
      maximumFractionDigits: 10,
    }).format(payload.result);
    showingResult = true;
  } catch (error) {
    errorDisplay.textContent = error.message || "Unable to reach the calculator.";
  }
}

keypad.addEventListener("click", (event) => {
  const button = event.target.closest("button");
  if (!button) return;

  if (button.dataset.action === "clear") clear();
  else if (button.dataset.action === "backspace") backspace();
  else if (button.dataset.action === "calculate") calculate();
  else if (button.dataset.value) appendValue(button.dataset.value);
});

document.addEventListener("keydown", (event) => {
  if (/^[0-9.+\-*/()%]$/.test(event.key)) {
    event.preventDefault();
    appendValue(event.key);
  } else if (event.key === "Enter" || event.key === "=") {
    event.preventDefault();
    calculate();
  } else if (event.key === "Backspace") {
    event.preventDefault();
    backspace();
  } else if (event.key === "Escape") {
    clear();
  }
});
