document.addEventListener("DOMContentLoaded", function() {
  // Initialize SweetScroll for smooth scrolling
  new SweetScroll({});
  
  // Get weather-based particle configuration
  function getParticleConfig() {
    const storedWeather = sessionStorage.getItem('siteWeather');
    const weather = storedWeather ? JSON.parse(storedWeather) : { name: 'clear' };
    
    // Base configuration
    const config = {
      particles: {
        number: {
          value: 80,
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
          value: 0.7,
          random: true,
          anim: {
            enable: true,
            speed: 0.5,
            opacity_min: 0.1,
            sync: false
          }
        },
        size: {
          value: 3,
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
          speed: 1,
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
    };
    
    // Weather-specific modifications
    switch(weather.name) {
      case 'snowy':
        config.particles.number.value = 150;
        config.particles.color.value = ["#ffffff", "#e8f4ff", "#d4ebff"];
        config.particles.size.value = 4;
        config.particles.move.speed = 2;
        config.particles.move.direction = "bottom";
        config.particles.opacity.value = 0.9;
        break;
        
      case 'rainy':
        config.particles.number.value = 200;
        config.particles.color.value = ["#a8c8e8", "#7ab0d8", "#5898c8"];
        config.particles.shape.type = "edge";
        config.particles.size.value = 2;
        config.particles.size.anim.enable = false;
        config.particles.move.speed = 8;
        config.particles.move.direction = "bottom";
        config.particles.move.straight = true;
        config.particles.opacity.value = 0.5;
        break;
        
      case 'stormy':
        config.particles.number.value = 250;
        config.particles.color.value = ["#8090a0", "#6080a0", "#4070a0"];
        config.particles.shape.type = "edge";
        config.particles.size.value = 2;
        config.particles.move.speed = 12;
        config.particles.move.direction = "bottom-left";
        config.particles.move.straight = true;
        config.particles.opacity.value = 0.6;
        break;
        
      case 'cloudy':
        config.particles.number.value = 60;
        config.particles.color.value = ["#ffffff", "#e0e0e0", "#c8d8e8"];
        config.particles.size.value = 5;
        config.particles.move.speed = 0.5;
        config.particles.move.direction = "none";
        config.particles.opacity.value = 0.4;
        break;
        
      case 'clear':
      default:
        // Add some sparkle for clear weather
        config.particles.number.value = 50;
        config.particles.color.value = ["#ffffff", "#fffacd", "#ffecd2"];
        config.particles.size.value = 2;
        config.particles.move.speed = 0.3;
        config.particles.move.direction = "none";
        config.particles.opacity.anim.speed = 1;
        break;
    }
    
    return config;
  }
  
  // Initialize particles with weather-based config
  const particleConfig = getParticleConfig();
  particlesJS("particles-js", particleConfig);
  
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
      const storedWeather = sessionStorage.getItem('siteWeather');
      const weather = storedWeather ? JSON.parse(storedWeather) : { name: 'clear' };
      
      // Different wind behavior based on weather
      if (weather.name === 'rainy' || weather.name === 'stormy') {
        pJS.particles.move.direction = mouseX > 2 ? "bottom-right" : "bottom-left";
        pJS.particles.move.speed = (weather.name === 'stormy' ? 12 : 8) + Math.abs(mouseX) * 0.5;
      } else if (weather.name !== 'snowy') {
        pJS.particles.move.direction = mouseX > 0 ? "right" : "left";
        pJS.particles.move.speed = 0.5 + Math.abs(mouseX) * 0.2;
      } else {
        pJS.particles.move.direction = mouseX > 0 ? "bottom-right" : "bottom-left";
        pJS.particles.move.speed = 2 + Math.abs(mouseX) * 0.3;
      }
    }
  });
  
  window.addEventListener('resize', function() {
    windowHalfX = window.innerWidth / 2;
    windowHalfY = window.innerHeight / 2;
  });
}, false);