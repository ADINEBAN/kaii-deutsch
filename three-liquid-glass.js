/**
 * WordFeather - Liquid Glass 3D Experience (Three.js)
 * High-performance ambient 3D refractive glass orbs, floating crystal polyhedra,
 * and mouse-reactive parallax atmosphere.
 */
(function (global) {
  'use strict';

  var scene, camera, renderer;
  var floatingObjects = [];
  var particles;
  var pointLight1, pointLight2, ambientLight;
  var mouseX = 0, mouseY = 0;
  var targetX = 0, targetY = 0;
  var windowHalfX = window.innerWidth / 2;
  var windowHalfY = window.innerHeight / 2;
  var isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
  var isRunning = true;
  var canvas;

  // Check user preference for reduced motion
  var prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function initThree() {
    if (typeof THREE === 'undefined') {
      console.warn('[WordFeather 3D] Three.js not yet loaded. Retrying in 100ms...');
      setTimeout(initThree, 100);
      return;
    }

    if (document.getElementById('wf-threejs-canvas')) return;

    // Create fixed background canvas
    canvas = document.createElement('canvas');
    canvas.id = 'wf-threejs-canvas';
    canvas.setAttribute('aria-hidden', 'true');
    canvas.style.cssText =
      'position:fixed;top:0;left:0;width:100vw;height:100vh;' +
      'z-index:-1;pointer-events:none;opacity:0.85;transition:opacity 0.6s ease;' +
      'will-change:transform;';
    document.body.prepend(canvas);

    // Scene setup
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 1, 1000);
    camera.position.z = 60;

    renderer = new THREE.WebGLRenderer({
      canvas: canvas,
      alpha: true,
      antialias: true,
      powerPreference: 'high-performance'
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

    // Lighting for glass refraction & specular gloss
    ambientLight = new THREE.AmbientLight(isDark ? 0x1e1b4b : 0xe0e7ff, 1.2);
    scene.add(ambientLight);

    pointLight1 = new THREE.PointLight(isDark ? 0x6366f1 : 0x2563eb, 2.5, 120);
    pointLight1.position.set(30, 20, 20);
    scene.add(pointLight1);

    pointLight2 = new THREE.PointLight(isDark ? 0xec4899 : 0x06b6d4, 2.2, 120);
    pointLight2.position.set(-30, -20, 15);
    scene.add(pointLight2);

    // Materials: Liquid Glass Translucent Polyhedra & Spheres
    var glassMaterial = new THREE.MeshPhysicalMaterial({
      color: isDark ? 0x818cf8 : 0x3b82f6,
      emissive: isDark ? 0x1e1b4b : 0x1d4ed8,
      emissiveIntensity: isDark ? 0.2 : 0.08,
      roughness: 0.1,
      metalness: 0.15,
      clearcoat: 1.0,
      clearcoatRoughness: 0.1,
      transparent: true,
      opacity: isDark ? 0.45 : 0.38,
      transmission: 0.7,
      ior: 1.5,
      reflectivity: 0.8
    });

    var glassWireMaterial = new THREE.MeshBasicMaterial({
      color: isDark ? 0xa5b4fc : 0x93c5fd,
      wireframe: true,
      transparent: true,
      opacity: isDark ? 0.22 : 0.18
    });

    // Create 16 floating crystal geometries
    var geometries = [
      new THREE.IcosahedronGeometry(2.4, 0),
      new THREE.OctahedronGeometry(2.2, 0),
      new THREE.DodecahedronGeometry(2.0, 0),
      new THREE.SphereGeometry(1.8, 24, 24),
      new THREE.TetrahedronGeometry(2.5, 0)
    ];

    for (var i = 0; i < 16; i++) {
      var geom = geometries[i % geometries.length];
      var mesh = new THREE.Mesh(geom, glassMaterial.clone());

      // Inner wireframe glow
      var wire = new THREE.Mesh(geom, glassWireMaterial);
      mesh.add(wire);

      // Distribute in a wide ambient frustum
      var posX = (Math.random() - 0.5) * 80;
      var posY = (Math.random() - 0.5) * 55;
      var posZ = (Math.random() - 0.5) * 30 - 5;

      mesh.position.set(posX, posY, posZ);

      // Store animation properties
      mesh.userData = {
        baseX: posX,
        baseY: posY,
        rotSpeedX: (Math.random() - 0.5) * 0.008 + 0.003,
        rotSpeedY: (Math.random() - 0.5) * 0.008 + 0.003,
        floatPhase: Math.random() * Math.PI * 2,
        floatSpeed: 0.0015 + Math.random() * 0.001,
        floatAmp: 1.5 + Math.random() * 2.0
      };

      scene.add(mesh);
      floatingObjects.push(mesh);
    }

    // Floating Stardust Particles
    var particleCount = 70;
    var particleGeometry = new THREE.BufferGeometry();
    var positions = new Float32Array(particleCount * 3);
    var scales = new Float32Array(particleCount);

    for (var p = 0; p < particleCount; p++) {
      positions[p * 3] = (Math.random() - 0.5) * 100;
      positions[p * 3 + 1] = (Math.random() - 0.5) * 70;
      positions[p * 3 + 2] = (Math.random() - 0.5) * 40;
      scales[p] = Math.random() * 2 + 1;
    }

    particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

    var particleMaterial = new THREE.PointsMaterial({
      color: isDark ? 0xc7d2fe : 0x38bdf8,
      size: 1.2,
      transparent: true,
      opacity: isDark ? 0.65 : 0.5,
      blending: THREE.AdditiveBlending
    });

    particles = new THREE.Points(particleGeometry, particleMaterial);
    scene.add(particles);

    // Event listeners
    window.addEventListener('resize', onWindowResize, { passive: true });
    window.addEventListener('mousemove', onMouseMove, { passive: true });
    document.addEventListener('visibilitychange', onVisibilityChange);

    // Watch for theme change
    observeThemeChange();

    // Start render loop
    requestAnimationFrame(animate);
  }

  function onWindowResize() {
    windowHalfX = window.innerWidth / 2;
    windowHalfY = window.innerHeight / 2;
    if (camera && renderer) {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    }
  }

  function onMouseMove(event) {
    mouseX = (event.clientX - windowHalfX) * 0.04;
    mouseY = (event.clientY - windowHalfY) * 0.04;
  }

  function onVisibilityChange() {
    isRunning = !document.hidden;
    if (isRunning) {
      requestAnimationFrame(animate);
    }
  }

  function updateTheme(dark) {
    isDark = dark;
    if (!scene) return;

    if (ambientLight) {
      ambientLight.color.setHex(isDark ? 0x1e1b4b : 0xe0e7ff);
    }
    if (pointLight1) {
      pointLight1.color.setHex(isDark ? 0x6366f1 : 0x2563eb);
    }
    if (pointLight2) {
      pointLight2.color.setHex(isDark ? 0xec4899 : 0x06b6d4);
    }

    floatingObjects.forEach(function (obj) {
      if (obj.material) {
        obj.material.color.setHex(isDark ? 0x818cf8 : 0x3b82f6);
        obj.material.emissive.setHex(isDark ? 0x1e1b4b : 0x1d4ed8);
        obj.material.opacity = isDark ? 0.45 : 0.38;
      }
    });

    if (particles && particles.material) {
      particles.material.color.setHex(isDark ? 0xc7d2fe : 0x38bdf8);
    }
  }

  function observeThemeChange() {
    var observer = new MutationObserver(function (mutations) {
      mutations.forEach(function (m) {
        if (m.type === 'attributes' && m.attributeName === 'data-bs-theme') {
          var dark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
          updateTheme(dark);
        }
      });
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-bs-theme'] });
  }

  var clock = 0;
  function animate() {
    if (!isRunning) return;
    requestAnimationFrame(animate);

    clock += 0.015;

    // Smooth camera damping towards mouse
    targetX += (mouseX - targetX) * 0.05;
    targetY += (mouseY - targetY) * 0.05;

    camera.position.x = targetX * 0.5;
    camera.position.y = -targetY * 0.5;
    camera.lookAt(scene.position);

    if (!prefersReducedMotion) {
      // Floating animation for polyhedra
      for (var i = 0; i < floatingObjects.length; i++) {
        var obj = floatingObjects[i];
        var u = obj.userData;

        obj.rotation.x += u.rotSpeedX;
        obj.rotation.y += u.rotSpeedY;

        obj.position.y = u.baseY + Math.sin(clock + u.floatPhase) * u.floatAmp;
        obj.position.x = u.baseX + Math.cos(clock * 0.8 + u.floatPhase) * (u.floatAmp * 0.5);
      }

      // Drift stardust
      if (particles) {
        particles.rotation.y += 0.0006;
        particles.rotation.x += 0.0003;
      }
    }

    renderer.render(scene, camera);
  }

  // Interactive 3D Emblem Helper (Can attach to any container .wf-3d-emblem)
  function create3DEmblem(containerId) {
    var el = document.getElementById(containerId);
    if (!el || typeof THREE === 'undefined') return;

    var emblemScene = new THREE.Scene();
    var emblemCam = new THREE.PerspectiveCamera(45, el.clientWidth / el.clientHeight, 0.1, 100);
    emblemCam.position.z = 6;

    var emblemRenderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    emblemRenderer.setSize(el.clientWidth, el.clientHeight);
    emblemRenderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    el.innerHTML = '';
    el.appendChild(emblemRenderer.domElement);

    var eLight1 = new THREE.PointLight(0x38bdf8, 2.5, 20);
    eLight1.position.set(5, 5, 5);
    emblemScene.add(eLight1);

    var eLight2 = new THREE.PointLight(0xec4899, 2.0, 20);
    eLight2.position.set(-5, -5, 3);
    emblemScene.add(eLight2);

    var eGeom = new THREE.IcosahedronGeometry(1.6, 0);
    var eMat = new THREE.MeshPhysicalMaterial({
      color: 0x3b82f6,
      emissive: 0x1d4ed8,
      emissiveIntensity: 0.15,
      roughness: 0.1,
      metalness: 0.2,
      clearcoat: 1.0,
      transmission: 0.75,
      transparent: true,
      opacity: 0.85
    });

    var emblemMesh = new THREE.Mesh(eGeom, eMat);
    var wireMesh = new THREE.Mesh(eGeom, new THREE.MeshBasicMaterial({ color: 0x93c5fd, wireframe: true, opacity: 0.4, transparent: true }));
    emblemMesh.add(wireMesh);
    emblemScene.add(emblemMesh);

    var isHovered = false;
    el.addEventListener('mouseenter', function () { isHovered = true; });
    el.addEventListener('mouseleave', function () { isHovered = false; });

    function renderEmblem() {
      requestAnimationFrame(renderEmblem);
      var speed = isHovered ? 0.04 : 0.012;
      emblemMesh.rotation.y += speed;
      emblemMesh.rotation.x += speed * 0.6;
      emblemRenderer.render(emblemScene, emblemCam);
    }
    renderEmblem();
  }

  // Load Three.js dynamically if not present
  function ensureThreeJsLoaded(callback) {
    if (typeof THREE !== 'undefined') {
      callback();
      return;
    }
    var script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
    script.async = true;
    script.onload = callback;
    script.onerror = function () {
      console.warn('[WordFeather 3D] Failed to load Three.js from CDN. 3D ambient background disabled.');
    };
    document.head.appendChild(script);
  }

  global.WordFeather3D = {
    init: function () {
      ensureThreeJsLoaded(initThree);
    },
    createEmblem: create3DEmblem,
    updateTheme: updateTheme
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      global.WordFeather3D.init();
    });
  } else {
    global.WordFeather3D.init();
  }

})(typeof window !== 'undefined' ? window : this);

