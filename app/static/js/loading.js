/**
 * Loading states and animations
 */

// Loading spinner component
class LoadingSpinner {
    constructor(container) {
        this.container = container;
        this.spinner = null;
    }

    show(message = 'Loading...') {
        const spinnerHTML = `
            <div class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center" id="loading-overlay">
                <div class="bg-white rounded-2xl p-8 shadow-2xl max-w-sm w-full mx-4 transform animate-scale-in">
                    <div class="flex flex-col items-center space-y-4">
                        <div class="relative">
                            <div class="w-16 h-16 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin"></div>
                            <div class="absolute inset-0 flex items-center justify-center">
                                <div class="w-8 h-8 bg-gradient-to-br from-purple-400 to-purple-600 rounded-full opacity-20 animate-pulse"></div>
                            </div>
                        </div>
                        <p class="text-lg font-semibold text-gray-800">${message}</p>
                        <div class="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
                            <div class="h-full bg-gradient-to-r from-purple-500 to-blue-500 animate-progress"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.spinner = document.createElement('div');
        this.spinner.innerHTML = spinnerHTML;
        document.body.appendChild(this.spinner);
    }

    hide() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.add('animate-fade-out');
            setTimeout(() => {
                if (this.spinner) {
                    this.spinner.remove();
                    this.spinner = null;
                }
            }, 300);
        }
    }

    updateMessage(message) {
        const messageElement = this.spinner?.querySelector('p');
        if (messageElement) {
            messageElement.textContent = message;
        }
    }
}

// Progress bar component
class ProgressBar {
    constructor(container) {
        this.container = container;
        this.bar = null;
        this.value = 0;
    }

    create() {
        const progressHTML = `
            <div class="progress-container">
                <div class="progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">
                    <div class="progress-fill"></div>
                </div>
                <div class="progress-text">0%</div>
            </div>
        `;

        this.container.innerHTML = progressHTML;
        this.bar = this.container.querySelector('.progress-fill');
    }

    setValue(value) {
        this.value = Math.min(100, Math.max(0, value));
        if (this.bar) {
            this.bar.style.width = `${this.value}%`;
            this.bar.setAttribute('aria-valuenow', this.value);
            const text = this.container.querySelector('.progress-text');
            if (text) {
                text.textContent = `${Math.round(this.value)}%`;
            }
        }
    }

    increment(amount = 1) {
        this.setValue(this.value + amount);
    }

    reset() {
        this.setValue(0);
    }
}

// Toast notification component
class Toast {
    static show(message, type = 'info', duration = 3000) {
        const colors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            warning: 'bg-yellow-500',
            info: 'bg-blue-500'
        };

        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };

        const toastHTML = `
            <div class="fixed top-4 right-4 z-50 transform transition-all duration-300 translate-x-full" id="toast">
                <div class="${colors[type]} text-white px-6 py-4 rounded-lg shadow-lg flex items-center space-x-3 max-w-md">
                    <span class="text-2xl">${icons[type]}</span>
                    <p class="font-medium">${message}</p>
                    <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white/80 hover:text-white">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
            </div>
        `;

        const toast = document.createElement('div');
        toast.innerHTML = toastHTML;
        document.body.appendChild(toast);

        const toastElement = document.getElementById('toast');
        
        // Animate in
        setTimeout(() => {
            toastElement.classList.remove('translate-x-full');
        }, 10);

        // Auto dismiss
        setTimeout(() => {
            toastElement.classList.add('translate-x-full');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
}

// Skeleton loader
class SkeletonLoader {
    static create(count = 1, type = 'line') {
        const templates = {
            line: '<div class="skeleton-line"></div>',
            card: `
                <div class="skeleton-card">
                    <div class="skeleton-image"></div>
                    <div class="skeleton-line"></div>
                    <div class="skeleton-line" style="width: 80%;"></div>
                </div>
            `,
            circle: '<div class="skeleton-circle"></div>'
        };

        return Array(count).fill(templates[type]).join('');
    }
}

// Loading button state
class LoadingButton {
    constructor(button) {
        this.button = button;
        this.originalText = button.innerHTML;
        this.isLoading = false;
    }

    setLoading(loading = true) {
        this.isLoading = loading;
        
        if (loading) {
            this.button.disabled = true;
            this.button.innerHTML = `
                <svg class="animate-spin h-5 w-5 inline-block mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
            `;
        } else {
            this.button.disabled = false;
            this.button.innerHTML = this.originalText;
        }
    }
}

// Smooth scroll to element
function smoothScrollTo(element, duration = 500) {
    const target = typeof element === 'string' ? document.querySelector(element) : element;
    if (!target) return;

    const targetPosition = target.getBoundingClientRect().top + window.pageYOffset;
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition;
    let startTime = null;

    function animation(currentTime) {
        if (startTime === null) startTime = currentTime;
        const timeElapsed = currentTime - startTime;
        const run = ease(timeElapsed, startPosition, distance, duration);
        window.scrollTo(0, run);
        if (timeElapsed < duration) requestAnimationFrame(animation);
    }

    function ease(t, b, c, d) {
        t /= d / 2;
        if (t < 1) return c / 2 * t * t + b;
        t--;
        return -c / 2 * (t * (t - 2) - 1) + b;
    }

    requestAnimationFrame(animation);
}

// Fade in elements on scroll
class ScrollFadeIn {
    constructor(selector = '.fade-in-on-scroll') {
        this.elements = document.querySelectorAll(selector);
        this.init();
    }

    init() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1
        });

        this.elements.forEach(el => observer.observe(el));
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Initialize scroll animations
    new ScrollFadeIn();

    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                smoothScrollTo(target);
            }
        });
    });
});

// Export for use in other scripts
window.LoadingSpinner = LoadingSpinner;
window.ProgressBar = ProgressBar;
window.Toast = Toast;
window.SkeletonLoader = SkeletonLoader;
window.LoadingButton = LoadingButton;
window.smoothScrollTo = smoothScrollTo;
