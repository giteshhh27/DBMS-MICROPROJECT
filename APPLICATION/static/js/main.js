/**
 * Library Management System - Frontend JavaScript
 * Handles sidebar toggling, search filtering, modals, tabs, and form validation.
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Mobile Sidebar Toggle
  const mobileToggle = document.getElementById('mobileToggle');
  const sidebar = document.getElementById('sidebar');
  if (mobileToggle && sidebar) {
    mobileToggle.addEventListener('click', function () {
      sidebar.classList.toggle('open');
    });

    // Close when clicking outside on mobile
    document.addEventListener('click', function (e) {
      if (window.innerWidth <= 900 &&
          !sidebar.contains(e.target) &&
          !mobileToggle.contains(e.target) &&
          sidebar.classList.contains('open')) {
        sidebar.classList.remove('open');
      }
    });
  }

  // 2. Client-side Table Filter / Search
  const tableSearchInputs = document.querySelectorAll('[data-table-search]');
  tableSearchInputs.forEach(input => {
    input.addEventListener('input', function () {
      const targetTableId = this.getAttribute('data-table-search');
      const table = document.getElementById(targetTableId);
      if (!table) return;

      const filter = this.value.toLowerCase().trim();
      const rows = table.querySelectorAll('tbody tr');

      rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(filter) ? '' : 'none';
      });
    });
  });

  // 3. Tab Navigation
  const tabButtons = document.querySelectorAll('.tab-btn');
  tabButtons.forEach(btn => {
    btn.addEventListener('click', function () {
      const targetId = this.getAttribute('data-tab-target');
      const parent = this.closest('.tabs-container') || document;

      // Update button active state
      parent.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      this.classList.add('active');

      // Update pane active state
      parent.querySelectorAll('.tab-pane').forEach(pane => {
        if (pane.id === targetId) {
          pane.style.display = 'block';
        } else {
          pane.style.display = 'none';
        }
      });
    });
  });

  // 4. Modal Triggers
  const openModalBtns = document.querySelectorAll('[data-open-modal]');
  openModalBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      const modalId = this.getAttribute('data-open-modal');
      const modal = document.getElementById(modalId);
      if (!modal) return;

      // Auto-populate data attributes into modal form inputs
      // e.g. data-issue-id="5" -> sets input[name="issue_id"] value to 5
      Array.from(this.attributes).forEach(attr => {
        if (attr.name.startsWith('data-param-')) {
          const paramName = attr.name.replace('data-param-', '');
          const targetInput = modal.querySelector(`[name="${paramName}"]`);
          if (targetInput) {
            targetInput.value = attr.value;
          }
          // Also set text for display elements with matching ID, e.g. modalFineAmount
          const displayEl = modal.querySelector(`[data-display="${paramName}"]`);
          if (displayEl) {
            displayEl.textContent = attr.value;
          }
        }
      });

      modal.classList.add('active');
    });
  });

  const closeModalBtns = document.querySelectorAll('[data-close-modal]');
  closeModalBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      const modal = this.closest('.modal-overlay');
      if (modal) modal.classList.remove('active');
    });
  });

  // Close modal when clicking on overlay background
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', function (e) {
      if (e.target === this) {
        this.classList.remove('active');
      }
    });
  });

  // 5. Form Validation Enhancements
  const forms = document.querySelectorAll('form[data-validate]');
  forms.forEach(form => {
    form.addEventListener('submit', function (e) {
      const requiredInputs = form.querySelectorAll('[required]');
      let isValid = true;
      let firstInvalid = null;

      requiredInputs.forEach(input => {
        if (!input.value.trim()) {
          isValid = false;
          input.style.borderColor = 'var(--danger)';
          if (!firstInvalid) firstInvalid = input;
        } else {
          input.style.borderColor = '';
        }
      });

      // Email validation
      const emailInputs = form.querySelectorAll('input[type="email"]');
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      emailInputs.forEach(input => {
        if (input.value && !emailRegex.test(input.value.trim())) {
          isValid = false;
          input.style.borderColor = 'var(--danger)';
          alert('Please enter a valid email address.');
          if (!firstInvalid) firstInvalid = input;
        }
      });

      // Quantity validation
      const numberInputs = form.querySelectorAll('input[type="number"]');
      numberInputs.forEach(input => {
        const min = input.getAttribute('min');
        if (min !== null && input.value !== '' && Number(input.value) < Number(min)) {
          isValid = false;
          input.style.borderColor = 'var(--danger)';
          alert(`Value cannot be less than ${min}.`);
          if (!firstInvalid) firstInvalid = input;
        }
      });

      if (!isValid) {
        e.preventDefault();
        if (firstInvalid) firstInvalid.focus();
      }
    });
  });
});
