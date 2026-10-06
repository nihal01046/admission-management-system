// Main JavaScript for College Admission & Enrollment Management System

document.addEventListener('DOMContentLoaded', function () {
  // 1. Password Visibility Toggle
  document.querySelectorAll('.toggle-password').forEach(function (toggle) {
    toggle.addEventListener('click', function () {
      const targetId = this.getAttribute('data-target');
      const input = targetId ? document.getElementById(targetId) : this.previousElementSibling;
      if (input) {
        if (input.type === 'password') {
          input.type = 'text';
          this.classList.remove('bi-eye');
          this.classList.add('bi-eye-slash');
        } else {
          input.type = 'password';
          this.classList.remove('bi-eye-slash');
          this.classList.add('bi-eye');
        }
      }
    });
  });

  // 2. Mobile Sidebar Toggle
  const sidebarToggle = document.getElementById('sidebarToggle');
  const portalSidebar = document.querySelector('.portal-sidebar');
  if (sidebarToggle && portalSidebar) {
    sidebarToggle.addEventListener('click', function () {
      portalSidebar.classList.toggle('show');
    });
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function (e) {
      if (window.innerWidth < 992 && !portalSidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
        portalSidebar.classList.remove('show');
      }
    });
  }

  // 3. Auto dismiss alert messages after 5 seconds
  setTimeout(function () {
    document.querySelectorAll('.alert-auto-dismiss').forEach(function (alert) {
      alert.style.transition = 'opacity 0.5s ease';
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 500);
    });
  }, 5000);
});

// Admin Dashboard Bar Chart Renderer (Vanilla Canvas for zero-external-failure reliability)
function initAdminChart(canvasId, labels, appliedData, approvedData) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const width = canvas.width;
  const height = canvas.height;
  
  // Padding & bounds
  const padLeft = 40;
  const padRight = 20;
  const padTop = 30;
  const padBottom = 40;
  
  const chartWidth = width - padLeft - padRight;
  const chartHeight = height - padTop - padBottom;
  
  // Clear
  ctx.clearRect(0, 0, width, height);
  
  const maxVal = Math.max(...appliedData, ...approvedData, 10);
  const roundedMax = Math.ceil(maxVal / 10) * 10 || 50;
  
  // Draw horizontal grid lines
  ctx.strokeStyle = '#E2E8F0';
  ctx.lineWidth = 1;
  ctx.fillStyle = '#94A3B8';
  ctx.font = '11px sans-serif';
  ctx.textAlign = 'right';
  
  const gridSteps = 4;
  for (let i = 0; i <= gridSteps; i++) {
    const val = Math.round((roundedMax / gridSteps) * i);
    const y = padTop + chartHeight - (chartHeight / gridSteps) * i;
    
    ctx.beginPath();
    ctx.moveTo(padLeft, y);
    ctx.lineTo(width - padRight, y);
    ctx.stroke();
    
    ctx.fillText(val, padLeft - 8, y + 4);
  }
  
  // Draw Bars
  const numGroups = labels.length;
  const groupWidth = chartWidth / numGroups;
  const barWidth = Math.min(groupWidth * 0.32, 22);
  const gap = 4;
  
  for (let i = 0; i < numGroups; i++) {
    const groupX = padLeft + i * groupWidth + (groupWidth - (barWidth * 2 + gap)) / 2;
    
    // Applied bar (Blue)
    const appliedVal = appliedData[i] || 0;
    const appliedHeight = (appliedVal / roundedMax) * chartHeight;
    const appliedY = padTop + chartHeight - appliedHeight;
    
    ctx.fillStyle = '#1677FF';
    ctx.beginPath();
    ctx.roundRect(groupX, appliedY, barWidth, appliedHeight, [4, 4, 0, 0]);
    ctx.fill();
    
    // Approved bar (Green)
    const approvedVal = approvedData[i] || 0;
    const approvedHeight = (approvedVal / roundedMax) * chartHeight;
    const approvedY = padTop + chartHeight - approvedHeight;
    
    ctx.fillStyle = '#10B981';
    ctx.beginPath();
    ctx.roundRect(groupX + barWidth + gap, approvedY, barWidth, approvedHeight, [4, 4, 0, 0]);
    ctx.fill();
    
    // Label
    ctx.fillStyle = '#64748B';
    ctx.textAlign = 'center';
    ctx.fillText(labels[i], groupX + barWidth + gap / 2, height - padBottom + 18);
  }
}
