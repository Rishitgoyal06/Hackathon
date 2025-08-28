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

function showEnhancedFeedback(action) {
    // Create modern toast notification
    const toast = document.createElement('div');
    toast.className = 'modern-toast';
    toast.innerHTML = `
        <div class="toast-content">
            <div class="toast-icon">
                <i class="fas fa-rocket"></i>
            </div>
            <div class="toast-text">
                <strong>${action}</strong>
                <p>Feature coming soon with Flask integration!</p>
            </div>
            <button class="toast-close">&times;</button>
        </div>
    `;
    
    // Add toast styles
    if (!document.querySelector('#toast-styles')) {
        const style = document.createElement('style');
        style.id = 'toast-styles';
        style.textContent = `
            .modern-toast {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
                animation: slideIn 0.3s ease;
            }
            .toast-content {
                background: rgba(255,255,255,0.95);
                backdrop-filter: blur(20px);
                border-radius: 16px;
                padding: 1rem 1.5rem;
                display: flex;
                align-items: center;
                gap: 1rem;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                border: 1px solid rgba(255,255,255,0.3);
                min-width: 300px;
            }
            .toast-icon {
                width: 40px;
                height: 40px;
                background: linear-gradient(45deg, #667eea, #764ba2);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 1.2rem;
            }
            .toast-text strong {
                color: #333;
                font-weight: 600;
                display: block;
            }
            .toast-text p {
                color: #666;
                margin: 0;
                font-size: 0.9rem;
            }
            .toast-close {
                background: none;
                border: none;
                font-size: 1.5rem;
                color: #999;
                cursor: pointer;
                padding: 0;
                width: 24px;
                height: 24px;
            }
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(toast);
    
    // Close functionality
    toast.querySelector('.toast-close').addEventListener('click', () => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    });
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => toast.remove(), 300);
        }
    }, 4000);
}