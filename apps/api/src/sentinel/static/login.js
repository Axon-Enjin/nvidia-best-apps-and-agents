"use strict";
const form = document.querySelector("#login-form");
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = document.querySelector("#sign-in");
  const error = document.querySelector("#login-error");
  button.disabled = true;
  button.textContent = "Signing in…";
  error.hidden = true;
  try {
    const fields = Object.fromEntries(new FormData(form));
    const response = await fetch("/api/session", {
      method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(fields),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(typeof result.detail === "string" ? result.detail : "Check your sign-in details.");
    // Session stays in its HttpOnly cookie; CSRF is obtained from the session endpoint after navigation.
    window.location.assign("/");
  } catch (failure) {
    error.textContent = failure instanceof TypeError ? "Cannot reach the local server. Check that it is running and try again." : failure.message;
    error.hidden = false;
    error.focus();
  } finally {
    button.disabled = false;
    button.textContent = "Sign in";
  }
});
