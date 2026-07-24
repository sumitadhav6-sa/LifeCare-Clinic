/**
 * LifeCare Clinic – Main JavaScript
 * Features: Navbar scroll, AOS, Counter animation,
 *           Toast notifications, OTP input, Ripple effects,
 *           Page transitions, Loading animations.
 */

// ═══════════════════════════════════════════════════════════════
// PAGE LOADER
// ═══════════════════════════════════════════════════════════════
(function() {
  const loader = document.getElementById('pageLoader');
  if (loader) {
    window.addEventListener('load', () => {
      setTimeout(() => {
        loader.classList.add('hidden');
        document.body.style.overflow = '';
      }, 1000);
    });
    document.body.style.overflow = 'hidden';
  }
})();

// ═══════════════════════════════════════════════════════════════
// NAVBAR SCROLL EFFECT
// ═══════════════════════════════════════════════════════════════
(function initNavbar() {
  const navbar = document.querySelector('.navbar-custom');
  if (!navbar) return;

  function handleScroll() {
    if (window.scrollY > 50) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  }

  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll();
})();

// ═══════════════════════════════════════════════════════════════
// AOS – ANIMATE ON SCROLL (custom lightweight implementation)
// ═══════════════════════════════════════════════════════════════
(function initAOS() {
  const elements = document.querySelectorAll('[data-aos]');
  if (!elements.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const delay = parseInt(el.getAttribute('data-aos-delay') || '0');
        setTimeout(() => {
          el.classList.add('aos-animate');
        }, delay);
        observer.unobserve(el);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -50px 0px' });

  elements.forEach(el => observer.observe(el));
})();

// ═══════════════════════════════════════════════════════════════
// ANIMATED COUNTER
// ═══════════════════════════════════════════════════════════════
(function initCounters() {
  const counters = document.querySelectorAll('[data-counter]');
  if (!counters.length) return;

  function animateCounter(el) {
    const target  = parseInt(el.getAttribute('data-counter'));
    const suffix  = el.getAttribute('data-suffix') || '';
    const prefix  = el.getAttribute('data-prefix') || '';
    const duration = 2000;
    const start    = performance.now();

    function easeOutQuart(t) {
      return 1 - Math.pow(1 - t, 4);
    }

    function update(time) {
      const elapsed  = time - start;
      const progress = Math.min(elapsed / duration, 1);
      const value    = Math.floor(easeOutQuart(progress) * target);
      el.textContent = prefix + value.toLocaleString() + suffix;

      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        el.textContent = prefix + target.toLocaleString() + suffix;
      }
    }

    requestAnimationFrame(update);
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  counters.forEach(el => observer.observe(el));
})();

// ═══════════════════════════════════════════════════════════════
// TOAST NOTIFICATION SYSTEM
// ═══════════════════════════════════════════════════════════════
const Toast = (function() {
  let container;

  function getContainer() {
    if (!container) {
      container = document.getElementById('toastContainer');
      if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
      }
    }
    return container;
  }

  const icons = {
    success: '✅',
    danger:  '❌',
    error:   '❌',
    warning: '⚠️',
    info:    'ℹ️'
  };

  const titles = {
    success: 'Success',
    danger:  'Error',
    error:   'Error',
    warning: 'Warning',
    info:    'Info'
  };

  function show(message, type = 'info', title = '', duration = 4000) {
    const c      = getContainer();
    const toast  = document.createElement('div');
    const typeStr = type === 'error' ? 'danger' : type;

    toast.className = `toast-custom toast-${typeStr}`;
    toast.innerHTML = `
      <div class="toast-icon">${icons[type] || '📢'}</div>
      <div>
        <div class="toast-title">${title || titles[type] || 'Notice'}</div>
        <div class="toast-msg">${message}</div>
      </div>
      <button onclick="this.closest('.toast-custom').remove()"
        style="margin-left:auto;background:none;border:none;font-size:1.1rem;cursor:pointer;color:#999;padding:0;line-height:1;">&times;</button>
    `;

    c.appendChild(toast);

    setTimeout(() => {
      toast.classList.add('hide');
      setTimeout(() => toast.remove(), 400);
    }, duration);

    return toast;
  }

  return {
    show,
    success: (msg, title) => show(msg, 'success', title),
    error:   (msg, title) => show(msg, 'error',   title),
    warning: (msg, title) => show(msg, 'warning', title),
    info:    (msg, title) => show(msg, 'info',    title)
  };
})();

// ═══════════════════════════════════════════════════════════════
// AUTO-SHOW FLASH MESSAGES AS TOASTS
// ═══════════════════════════════════════════════════════════════
(function showFlashToasts() {
  const alerts = document.querySelectorAll('.flash-alert');
  alerts.forEach(alert => {
    const message  = alert.getAttribute('data-message');
    const category = alert.getAttribute('data-category') || 'info';
    if (message) {
      Toast.show(message, category);
      alert.style.display = 'none';
    }
  });
})();

// ═══════════════════════════════════════════════════════════════
// OTP INPUT HANDLER
// ═══════════════════════════════════════════════════════════════
(function initOTPInput() {
  const otpInputs = document.querySelectorAll('.otp-input');
  if (!otpInputs.length) return;

  otpInputs.forEach((input, idx) => {
    input.addEventListener('input', (e) => {
      const val = e.target.value.replace(/\D/g, '');
      e.target.value = val.slice(-1);

      if (val && idx < otpInputs.length - 1) {
        otpInputs[idx + 1].focus();
      }

      if (val) input.classList.add('filled');
      else      input.classList.remove('filled');

      // Auto-combine all OTP digits into hidden input
      const combined = Array.from(otpInputs).map(i => i.value).join('');
      const hidden = document.getElementById('otpHidden');
      if (hidden) hidden.value = combined;
    });

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Backspace' && !input.value && idx > 0) {
        otpInputs[idx - 1].focus();
        otpInputs[idx - 1].value = '';
        otpInputs[idx - 1].classList.remove('filled');
      }
      if (e.key === 'ArrowLeft'  && idx > 0)                   otpInputs[idx - 1].focus();
      if (e.key === 'ArrowRight' && idx < otpInputs.length - 1) otpInputs[idx + 1].focus();
    });

    input.addEventListener('paste', (e) => {
      e.preventDefault();
      const paste = (e.clipboardData || window.clipboardData).getData('text').replace(/\D/g, '');
      paste.split('').forEach((char, i) => {
        if (otpInputs[i]) {
          otpInputs[i].value = char;
          otpInputs[i].classList.add('filled');
        }
      });
      const hidden = document.getElementById('otpHidden');
      if (hidden) hidden.value = paste.slice(0, otpInputs.length);
      if (otpInputs[paste.length]) otpInputs[paste.length].focus();
    });
  });

  // Focus first input on load
  if (otpInputs[0]) otpInputs[0].focus();
})();

// ═══════════════════════════════════════════════════════════════
// OTP RESEND COUNTDOWN TIMER
// ═══════════════════════════════════════════════════════════════
(function initResendTimer() {
  const countdownEl = document.getElementById('otpCountdown');
  const resendBtn   = document.getElementById('resendOtpBtn');
  if (!countdownEl) return;

  let timeLeft = 60;

  const interval = setInterval(() => {
    timeLeft--;
    countdownEl.textContent = timeLeft;

    if (timeLeft <= 0) {
      clearInterval(interval);
      countdownEl.closest('.resend-area').innerHTML = `
        <form method="POST" action="/auth/resend-otp" style="display:inline;">
          <input type="hidden" name="csrf_token" value="${document.querySelector('meta[name=csrf-token]')?.content || ''}">
          <button type="submit" class="btn btn-link p-0 text-decoration-none fw-600" style="color:var(--accent);">
            <i class="fas fa-redo me-1"></i> Resend OTP
          </button>
        </form>
      `;
    }
  }, 1000);
})();

// ═══════════════════════════════════════════════════════════════
// PASSWORD STRENGTH METER
// ═══════════════════════════════════════════════════════════════
(function initPasswordStrength() {
  const pwInput = document.getElementById('passwordInput');
  const meter   = document.getElementById('passwordStrength');
  if (!pwInput || !meter) return;

  function getStrength(pw) {
    let score = 0;
    if (pw.length >= 8)  score++;
    if (pw.length >= 12) score++;
    if (/[A-Z]/.test(pw)) score++;
    if (/[0-9]/.test(pw)) score++;
    if (/[^A-Za-z0-9]/.test(pw)) score++;
    return score;
  }

  const labels = ['', 'Very Weak', 'Weak', 'Fair', 'Strong', 'Very Strong'];
  const colors = ['', '#f44336', '#ff9800', '#ffc107', '#4caf50', '#00c853'];

  pwInput.addEventListener('input', () => {
    const score = getStrength(pwInput.value);
    meter.style.display = pwInput.value ? 'block' : 'none';
    meter.innerHTML = `
      <div style="height:4px;background:#e0e0e0;border-radius:2px;margin-top:6px;overflow:hidden;">
        <div style="height:100%;width:${score * 20}%;background:${colors[score]};border-radius:2px;transition:all 0.3s;"></div>
      </div>
      <small style="color:${colors[score]};font-size:0.78rem;font-weight:600;">${labels[score]}</small>
    `;
  });
})();

// ═══════════════════════════════════════════════════════════════
// APPOINTMENT BOOKING – DOCTOR SELECTION & SLOTS
// ═══════════════════════════════════════════════════════════════
(function initBookingForm() {
  const doctorSelect = document.getElementById('doctorSelect');
  const slotGrid     = document.getElementById('slotGrid');
  const slotInput    = document.getElementById('slotInput');
  const feeDisplay   = document.getElementById('feeDisplay');

  if (!doctorSelect) return;

  doctorSelect.addEventListener('change', async function() {
    const doctorId = this.value;
    if (!doctorId) {
      if (slotGrid) slotGrid.innerHTML = '<p class="text-muted small">Select a doctor first.</p>';
      return;
    }

    try {
      slotGrid.innerHTML = '<div class="text-center py-3"><div class="spinner-border spinner-border-sm text-primary"></div> Loading slots...</div>';

      const resp = await fetch(`/patient/get-slots/${doctorId}`);
      const data = await resp.json();

      if (feeDisplay) {
        feeDisplay.textContent = `₹${data.fee}`;
        feeDisplay.closest('.fee-card')?.classList.remove('d-none');
      }

      if (!data.slots || !data.slots.length) {
        slotGrid.innerHTML = '<p class="text-muted small">No slots available for this doctor.</p>';
        return;
      }

      slotGrid.innerHTML = data.slots.map(slot => `
        <button type="button" class="slot-btn ripple" data-slot="${slot}"
          onclick="selectSlot(this, '${slot}')">
          <i class="fas fa-clock me-1" style="font-size:0.7rem;"></i>${slot}
        </button>
      `).join('');

    } catch (err) {
      slotGrid.innerHTML = '<p class="text-danger small">Failed to load slots.</p>';
    }
  });
})();

function selectSlot(btn, slot) {
  document.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
  const input = document.getElementById('slotInput');
  if (input) input.value = slot;
}

// ═══════════════════════════════════════════════════════════════
// SIDEBAR TOGGLE (Mobile)
// ═══════════════════════════════════════════════════════════════
(function initSidebar() {
  const toggleBtn  = document.getElementById('sidebarToggle');
  const sidebar    = document.getElementById('sidebar');
  const overlay    = document.getElementById('sidebarOverlay');

  if (!toggleBtn || !sidebar) return;

  toggleBtn.addEventListener('click', () => {
    sidebar.classList.toggle('show');
    overlay?.classList.toggle('show');
  });

  overlay?.addEventListener('click', () => {
    sidebar.classList.remove('show');
    overlay.classList.remove('show');
  });
})();

// ═══════════════════════════════════════════════════════════════
// CONFIRM DELETE DIALOGS
// ═══════════════════════════════════════════════════════════════
function confirmDelete(msg, formId) {
  if (confirm(msg || 'Are you sure you want to delete this?')) {
    const form = document.getElementById(formId);
    if (form) form.submit();
  }
}

// ═══════════════════════════════════════════════════════════════
// SMOOTH SCROLL FOR ANCHOR LINKS
// ═══════════════════════════════════════════════════════════════
(function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (href === '#') return;
      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
})();

// ═══════════════════════════════════════════════════════════════
// PARALLAX EFFECT FOR HERO
// ═══════════════════════════════════════════════════════════════
(function initParallax() {
  const hero = document.querySelector('.hero-section');
  if (!hero) return;

  window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;
    const shapes  = hero.querySelectorAll('.hero-shape');
    shapes.forEach((shape, i) => {
      const speed = (i + 1) * 0.08;
      shape.style.transform = `translateY(${scrollY * speed}px)`;
    });
  }, { passive: true });
})();

// ═══════════════════════════════════════════════════════════════
// FORM VALIDATION ENHANCEMENT
// ═══════════════════════════════════════════════════════════════
(function initFormValidation() {
  const forms = document.querySelectorAll('.needs-validation');
  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      if (!this.checkValidity()) {
        e.preventDefault();
        e.stopPropagation();
        Toast.warning('Please fill in all required fields correctly.');
      }
      this.classList.add('was-validated');
    });
  });
})();

// ═══════════════════════════════════════════════════════════════
// SUCCESS ANIMATION (appointment booked)
// ═══════════════════════════════════════════════════════════════
function showSuccessAnimation(message) {
  const overlay = document.createElement('div');
  overlay.style.cssText = `
    position:fixed;inset:0;background:rgba(26,35,126,0.85);
    backdrop-filter:blur(10px);z-index:99999;
    display:flex;align-items:center;justify-content:center;
    animation:fadeInUp 0.4s ease;
  `;

  overlay.innerHTML = `
    <div style="background:white;border-radius:24px;padding:50px 40px;text-align:center;max-width:380px;width:90%;animation:scaleIn 0.4s cubic-bezier(0.34,1.56,0.64,1);">
      <div class="success-circle" style="margin:0 auto 24px;">
        <svg width="50" height="50" viewBox="0 0 50 50" fill="none" xmlns="http://www.w3.org/2000/svg">
          <polyline class="checkmark-svg" points="10,27 20,37 40,17"
            stroke="white" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        </svg>
      </div>
      <h3 style="color:var(--primary);font-weight:800;margin-bottom:10px;">Appointment Booked!</h3>
      <p style="color:var(--text-muted);font-size:0.95rem;line-height:1.7;">${message || 'Your appointment has been successfully booked. Awaiting confirmation.'}</p>
      <button onclick="this.closest('[style]').remove()"
        style="margin-top:24px;background:var(--gradient-accent);color:white;border:none;padding:12px 32px;border-radius:12px;font-weight:700;cursor:pointer;font-size:0.95rem;">
        <i class="fas fa-check me-2"></i>Continue
      </button>
    </div>
  `;

  document.body.appendChild(overlay);
  setTimeout(() => overlay.remove(), 6000);
}

// ═══════════════════════════════════════════════════════════════
// ADMIN: Quick status update
// ═══════════════════════════════════════════════════════════════
async function updateAppointmentStatus(apptId, newStatus, csrfToken) {
  try {
    const resp = await fetch(`/admin/appointments/update-status/${apptId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `status=${newStatus}&csrf_token=${csrfToken}`
    });
    const data = await resp.json();
    if (data.success) {
      Toast.success(`Status updated to ${newStatus}!`);
      setTimeout(() => location.reload(), 1000);
    } else {
      Toast.error('Failed to update status.');
    }
  } catch {
    Toast.error('Network error. Please try again.');
  }
}

// ═══════════════════════════════════════════════════════════════
// TABLE SEARCH FILTER
// ═══════════════════════════════════════════════════════════════
(function initTableSearch() {
  const searchInput = document.getElementById('tableSearch');
  if (!searchInput) return;

  searchInput.addEventListener('input', function() {
    const query = this.value.toLowerCase();
    const rows  = document.querySelectorAll('.searchable-row');
    rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      row.style.display = text.includes(query) ? '' : 'none';
    });
  });
})();

// ═══════════════════════════════════════════════════════════════
// DATE PICKER MIN DATE (today)
// ═══════════════════════════════════════════════════════════════
(function setMinDate() {
  const dateInputs = document.querySelectorAll('input[type="date"].appointment-date');
  const today = new Date().toISOString().split('T')[0];
  dateInputs.forEach(input => {
    input.setAttribute('min', today);
    if (!input.value) input.value = today;
  });
})();

// ═══════════════════════════════════════════════════════════════
// BOOTSTRAP TOOLTIP INIT
// ═══════════════════════════════════════════════════════════════
(function initTooltips() {
  const tooltipTriggers = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltipTriggers.forEach(el => {
    try {
      new bootstrap.Tooltip(el, { trigger: 'hover' });
    } catch {}
  });
})();

// ═══════════════════════════════════════════════════════════════
// RIPPLE EFFECT FOR BUTTONS
// ═══════════════════════════════════════════════════════════════
(function initRipple() {
  document.addEventListener('click', function(e) {
    const btn = e.target.closest('.btn-primary-custom, .btn-accent-custom, .btn-hero-primary');
    if (!btn) return;

    const rect   = btn.getBoundingClientRect();
    const ripple = document.createElement('span');
    const size   = Math.max(rect.width, rect.height);
    const x      = e.clientX - rect.left - size / 2;
    const y      = e.clientY - rect.top  - size / 2;

    ripple.style.cssText = `
      position:absolute;width:${size}px;height:${size}px;
      left:${x}px;top:${y}px;
      background:rgba(255,255,255,0.3);
      border-radius:50%;transform:scale(0);
      animation:rippleAnim 0.6s linear;
      pointer-events:none;
    `;

    if (!document.getElementById('rippleStyle')) {
      const style = document.createElement('style');
      style.id = 'rippleStyle';
      style.textContent = '@keyframes rippleAnim{to{transform:scale(4);opacity:0;}}';
      document.head.appendChild(style);
    }

    btn.style.position = 'relative';
    btn.style.overflow = 'hidden';
    btn.appendChild(ripple);
    setTimeout(() => ripple.remove(), 600);
  });
})();

// ═══════════════════════════════════════════════════════════════
// EXPOSE GLOBALS
// ═══════════════════════════════════════════════════════════════
window.Toast               = Toast;
window.showSuccessAnimation = showSuccessAnimation;
window.selectSlot          = selectSlot;
window.confirmDelete       = confirmDelete;
window.updateAppointmentStatus = updateAppointmentStatus;
