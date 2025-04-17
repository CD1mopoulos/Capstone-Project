document.addEventListener("DOMContentLoaded", function () {
  const questions = document.querySelectorAll(".question");

  questions.forEach((question) => {
    question.addEventListener("click", function () {
      const isExpanded = this.getAttribute("aria-expanded") === "true";
      const answer = this.nextElementSibling;
      const icon = this.querySelector("ion-icon");

      // Collapse all other questions
      questions.forEach((q) => {
        if (q !== this) {
          q.setAttribute("aria-expanded", "false");
          const otherAnswer = q.nextElementSibling;
          const otherIcon = q.querySelector("ion-icon");
          if (otherAnswer) otherAnswer.style.maxHeight = null;
          if (otherIcon) otherIcon.setAttribute("name", "add-outline");
        }
      });

      // Toggle current question
      if (isExpanded) {
        this.setAttribute("aria-expanded", "false");
        answer.style.maxHeight = null;
        icon.setAttribute("name", "add-outline");
      } else {
        this.setAttribute("aria-expanded", "true");
        answer.style.maxHeight = answer.scrollHeight + "px";
        icon.setAttribute("name", "remove-outline");
      }
    });
  });
});
