// Select elements
const cookieBanner = document.querySelector("#cookie-banner");
const closeButton = document.querySelector("#close-button");
const body = document.querySelector("body");

// Check if cookie is set
if (!localStorage.getItem("cookieSeen")) {
  // Show banner
  cookieBanner.classList.add("dim");
}

// Handle close button click
closeButton.addEventListener("click", () => {
  // Set cookie
  localStorage.setItem("cookieSeen", true);
  // Hide banner
  cookieBanner.classList.remove("dim");
  cookieBanner.addEventListener("animationend", () => {
    cookieBanner.style.display = "none";
  }, {once: true});
});

// Dim other parts of the website
cookieBanner.addEventListener("transitionend", () => {
  if (cookieBanner.classList.contains("dim")) {
    body.classList.add("dimmed");
  } else {
    body.classList.remove("dimmed");
  }
});
