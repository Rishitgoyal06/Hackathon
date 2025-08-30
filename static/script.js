// Smart Attendance System - Enhanced Frontend JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeAnimations();
    addInteractiveEffects();
    createLoadingStates();
    addProgressBars();
    initializeTooltips();
    addTypingEffect();
});

function initializeAnimations() {
    // Stagger card entrance animations
    const cards = document.querySelectorAll('.feature-card, .stats-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

function addInteractiveEffects() {
    // Enhanced button interactions with ripple effect
    const buttons = document.querySelectorAll('.btn-action');

    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();

            // Create ripple effect
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                background: rgba(255,255,255,0.3);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple 0.6s ease-out;
                pointer-events: none;
            `;

            this.appendChild(ripple);
            setTimeout(() => ripple.remove(), 600);

            // Show enhanced feedback
            showEnhancedFeedback(this.textContent.trim());
        });
    });

    // Add CSS for ripple animation
    if (!document.querySelector('#ripple-styles')) {
        const style = document.createElement('style');
        style.id = 'ripple-styles';
        style.textContent = `
            @keyframes ripple {
                to { transform: scale(2); opacity: 0; }
            }
            .btn-action { position: relative; overflow: hidden; }
        `;
        document.head.appendChild(style);
    }
}

function createLoadingStates() {
    // Add loading spinners to stats
    const statsNumbers = document.querySelectorAll('.stats-number');
    statsNumbers.forEach(stat => {
        const finalValue = stat.textContent;
        stat.textContent = '...';

        setTimeout(() => {
            animateNumber(stat, finalValue);
        }, 500);
    });
}

function animateNumber(element, finalValue) {
    const isPercentage = finalValue.includes('%');
    const isFraction = finalValue.includes('/');

    if (isPercentage) {
        const target = parseInt(finalValue);
        animateCounter(element, 0, target, '%');
    } else if (isFraction) {
        element.textContent = finalValue;
    } else {
        const target = parseInt(finalValue);
        animateCounter(element, 0, target);
    }
}

function animateCounter(element, start, end, suffix = '') {
    const duration = 1500;
    const increment = (end - start) / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if (current >= end) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current) + suffix;
    }, 16);
}

function addProgressBars() {
    // Add progress indicators to profile section
    const profileSection = document.querySelector('.profile-section');
    if (profileSection) {
        const progressHTML = `
            <div class="progress-indicators mt-3">
                <div class="progress-item">
                    <span class="progress-label">Profile Complete</span>
                    <div class="progress-bar-custom">
                        <div class="progress-fill" style="width: 85%"></div>
                    </div>
                </div>
            </div>
        `;
        profileSection.insertAdjacentHTML('beforeend', progressHTML);

        // Add progress bar styles
        const progressStyles = `
            .progress-indicators { margin-top: 1rem; }
            .progress-item { margin-bottom: 0.5rem; }
            .progress-label {
                color: rgba(255,255,255,0.9);
                font-size: 0.9rem;
                font-weight: 500;
            }
            .progress-bar-custom {
                height: 6px;
                background: rgba(255,255,255,0.2);
                border-radius: 3px;
                overflow: hidden;
                margin-top: 0.5rem;
            }
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #a8edea, #fed6e3);
                border-radius: 3px;
                transition: width 2s ease;
                animation: progressGlow 2s ease-in-out infinite alternate;
            }
            @keyframes progressGlow {
                from { box-shadow: 0 0 5px rgba(255,255,255,0.3); }
                to { box-shadow: 0 0 15px rgba(255,255,255,0.6); }
            }
        `;

        if (!document.querySelector('#progress-styles')) {
            const style = document.createElement('style');
            style.id = 'progress-styles';
            style.textContent = progressStyles;
            document.head.appendChild(style);
        }
    }
}

function initializeTooltips() {
    // Add tooltips to nav icons
    const navIcons = document.querySelectorAll('.nav-icon');
    const tooltips = ['Notifications', 'Calendar', 'Analytics'];

    navIcons.forEach((icon, index) => {
        if (tooltips[index]) {
            icon.setAttribute('title', tooltips[index]);
            icon.style.position = 'relative';
        }
    });
}

function addTypingEffect() {
    // Add typing effect to hero subtitle
    const subtitle = document.querySelector('.hero-subtitle');
    if (subtitle) {
        const text = subtitle.textContent;
        subtitle.textContent = '';

        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                subtitle.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 50);
            }
        };

        setTimeout(typeWriter, 1000);
    }
}
}