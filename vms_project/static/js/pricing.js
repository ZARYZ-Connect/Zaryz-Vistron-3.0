document.addEventListener("DOMContentLoaded", () => {

  const reveals = document.querySelectorAll(".reveal");

  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry, index) => {
      if (entry.isIntersecting) {

        setTimeout(() => {
          entry.target.classList.add("active");
        }, index * 150);

        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.2
  });

  reveals.forEach(el => {
    observer.observe(el);
  });

});
