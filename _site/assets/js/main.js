document.addEventListener("DOMContentLoaded", function() {
  // Initialize SweetScroll for smooth scrolling
  new SweetScroll({});
  
  // Initialize particles.js with interactive snow effect
  particlesJS("particles-js", {
    particles: {
      number: {
        value: 120,
        density: {
          enable: true,
          value_area: 800
        }
      },
      color: {
        value: ["#ffffff", "#a8d8ff", "#c8e8ff"]
      },
      shape: {
        type: "circle",
        stroke: {
          width: 0,
          color: "#000000"
        }
      },
      opacity: {
        value: 0.8,
        random: true,
        anim: {
          enable: true,
          speed: 0.5,
          opacity_min: 0.1,
          sync: false
        }
      },
      size: {
        value: 4,
        random: true,
        anim: {
          enable: true,
          speed: 2,
          size_min: 0.5,
          sync: false
        }
      },
      line_linked: {
        enable: false
      },
      move: {
        enable: true,
        speed: 1.5,
        direction: "bottom",
        random: true,
        straight: false,
        out_mode: "out",
        bounce: false,
        attract: {
          enable: false,
          rotateX: 600,
          rotateY: 1200
        }
      }
    },
    interactivity: {
      detect_on: "canvas",
      events: {
        onhover: {
          enable: true,
          mode: "repulse"
        },
        onclick: {
          enable: true,
          mode: "push"
        },
        resize: true
      },
      modes: {
        grab: {
          distance: 200,
          line_linked: {
            opacity: 0.5
          }
        },
        bubble: {
          distance: 200,
          size: 6,
          duration: 2,
          opacity: 0.8,
          speed: 3
        },
        repulse: {
          distance: 100,
          duration: 0.4
        },
        push: {
          particles_nb: 6
        },
        remove: {
          particles_nb: 2
        }
      }
    },
    retina_detect: true
  });
  
  // Add custom mouse interaction for wind effect
  let mouseX = 0;
  let mouseY = 0;
  let windowHalfX = window.innerWidth / 2;
  let windowHalfY = window.innerHeight / 2;
  
  document.addEventListener('mousemove', function(event) {
    mouseX = (event.clientX - windowHalfX) / 100;
    mouseY = (event.clientY - windowHalfY) / 100;
    
    // Apply wind effect to particles based on mouse position
    if (window.pJSDom && window.pJSDom[0] && window.pJSDom[0].pJS) {
      const pJS = window.pJSDom[0].pJS;
      pJS.particles.move.direction = mouseX > 0 ? "bottom-right" : "bottom-left";
      pJS.particles.move.speed = 1.5 + Math.abs(mouseX) * 0.3;
    }
  });
  
  window.addEventListener('resize', function() {
    windowHalfX = window.innerWidth / 2;
    windowHalfY = window.innerHeight / 2;
  });
}, false);