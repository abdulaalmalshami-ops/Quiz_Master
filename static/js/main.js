/**
 * Quiz Master Global Interactions
 * Purpose: Add premium feedback and smooth transitions project-wide.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Page Transitions
    document.body.classList.add('page-loaded');

    // 2. Button Ripple Effect
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function (e) {
            const x = e.clientX - e.target.offsetLeft;
            const y = e.clientY - e.target.offsetTop;

            const ripple = document.createElement('span');
            ripple.classList.add('ripple-effect');
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;

            this.appendChild(ripple);

            setTimeout(() => ripple.remove(), 600);
        });
    });

    // 3. Auto-hide Alerts/Messages
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-20px)';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // 4. Smooth Card Interaction (Glow Tracking)
    document.querySelectorAll('.card, .stat-card').forEach(card => {
        card.addEventListener('mousemove', e => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            card.style.setProperty('--mouse-x', `${x}px`);
            card.style.setProperty('--mouse-y', `${y}px`);
        });
    });

    // 5. Tooltip/Title replacement (Optional - clean look)
    document.querySelectorAll('[title]').forEach(el => {
        el.setAttribute('data-title', el.getAttribute('title'));
        el.removeAttribute('title');

        el.addEventListener('mouseenter', e => {
            const tooltip = document.createElement('div');
            tooltip.className = 'custom-tooltip';
            tooltip.innerText = el.getAttribute('data-title');
            document.body.appendChild(tooltip);

            const rect = el.getBoundingClientRect();
            tooltip.style.left = `${rect.left + (rect.width / 2)}px`;
            tooltip.style.top = `${rect.top - 10}px`;
        });

        el.addEventListener('mouseleave', () => {
            document.querySelectorAll('.custom-tooltip').forEach(t => t.remove());
        });
    });
});
