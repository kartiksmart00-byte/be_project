const buttons = document.querySelectorAll(".feature-text");

buttons.forEach(btn => {
  btn.addEventListener("click", () => {
    // सभी buttons से active हटाओ
    buttons.forEach(b => b.classList.remove("active"));
    // clicked button को active दो
    this.classList.add("active");
  });
});
