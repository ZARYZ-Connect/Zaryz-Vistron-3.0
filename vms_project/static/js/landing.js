// ================= MOBILE MENU =================

function toggleMenu() {
  document.getElementById("nav-links").classList.toggle("active");
}


// ================= REVEAL ANIMATION =================

const reveals = document.querySelectorAll(".reveal");

function revealOnScroll() {

  reveals.forEach((element) => {

    const windowHeight = window.innerHeight;
    const elementTop = element.getBoundingClientRect().top;
    const revealPoint = 120;

    if (elementTop < windowHeight - revealPoint) {
      element.classList.add("active");
    }

  });

}

window.addEventListener("scroll", revealOnScroll);


// ================= NAVBAR SCROLL EFFECT =================

const nav = document.querySelector(".nav");

window.addEventListener("scroll", () => {

  if (window.scrollY > 20) {

    nav.style.background = "rgba(2,6,23,0.7)";
    nav.style.backdropFilter = "blur(10px)";

  } else {

    nav.style.background = "transparent";
    nav.style.backdropFilter = "none";

  }

});
