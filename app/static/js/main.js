/**
 * Screenshot to Code - Main JavaScript
 * Enhanced UI interactions and accessibility features
 */

'use strict';

// Main Application Object
const ScreenshotToCode = {
    
    // Configuration
    config: {
        alertAutoHideDelay: 6000,
        animationDuration: 300,
        debounceDelay: 250,
        breakpoints: {
            sm: 640,
            md: 768,
            lg: 1024,
            xl: 1280
        }
    },
    
    // Initialize the application
    init() {
        console.log('🚀 Initializing Screenshot to Code App...');
        
        // Core functionality
        this.setupNavigation();
        this.setupAlerts();
        this.setupForms();
        this.setupScrollEffects();
        this.setupAnimations();
        this.setupAccessibility();
        this.setupPerformanceMonitoring();
        
        // Enhanced features
        this.setupTheme();
        this.setupPageTransitions();
        
        // Mark as initialized
        document.body.classList.add('app-initialized');
        console.log('✅ App initialized successfully');
    },
    
    // Navigation functionality
    setupNavigation() {
        const mobileMenuButton = document.getElementById('mobile-menu-button');
        const mobileMenu = document.getElementById('mobile-menu');
        
        if (!mobileMenuButton || !mobileMenu) return;
        
        // Mobile menu toggle
        mobileMenuButton.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleMobileMenu();
        });
        
        // Close menu on outside click
        document.addEventListener('click', (e) => {
            if (!mobileMenu.contains(e.target) && !mobileMenuButton.contains(e.target)) {
                this.closeMobileMenu();
            }
        });
        
        // Handle escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeMobileMenu();
            }
        });
        
        // Smooth scroll for anchor links
        this.setupSmoothScroll();
        
        // Navbar scroll effect
        this.setupNavbarScrollEffect();
    },
    
    // Toggle mobile menu with accessibility support
    toggleMobileMenu() {
        const mobileMenuButton = document.getElementById('mobile-menu-button');
        const mobileMenu = document.getElementById('mobile-menu');
        const icon = mobileMenuButton.querySelector('i');
        const isOpen = !mobileMenu.classList.contains('hidden');
        
        if (!isOpen) {
            // Open menu
            mobileMenu.classList.remove('hidden');
            mobileMenu.classList.add('mobile-menu-enter');
            icon.classList.remove('fa-bars');
            icon.classList.add('fa-times');
            mobileMenuButton.setAttribute('aria-expanded', 'true');
            document.body.style.overflow = 'hidden';
            
            // Focus first menu item
            const firstMenuItem = mobileMenu.querySelector('a');
            if (firstMenuItem) {
                setTimeout(() => firstMenuItem.focus(), 100);
            }
        } else {
            this.closeMobileMenu();
        }
    },
    
    // Close mobile menu
    closeMobileMenu() {
        const mobileMenuButton = document.getElementById('mobile-menu-button');
        const mobileMenu = document.getElementById('mobile-menu');
        const icon = mobileMenuButton?.querySelector('i');
        
        if (!mobileMenu || mobileMenu.classList.contains('hidden')) return;
        
        mobileMenu.classList.add('hidden');
        mobileMenu.classList.remove('mobile-menu-enter');
        if (icon) {
            icon.classList.remove('fa-times');
            icon.classList.add('fa-bars');
        }
        if (mobileMenuButton) {
            mobileMenuButton.setAttribute('aria-expanded', 'false');
        }
        document.body.style.overflow = '';
    },
    
    // Smooth scroll setup
    setupSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;
                
                const target = document.querySelector(targetId);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                    
                    // Update URL without causing scroll
                    history.pushState(null, null, targetId);
                }
            });
        });
    },
    
    // Navbar scroll effect
    setupNavbarScrollEffect() {
        const nav = document.querySelector('nav');
        if (!nav) return;
        
        let lastScrollY = window.scrollY;
        
        const handleScroll = this.debounce(() => {
            const currentScrollY = window.scrollY;
            
            // Add/remove shadow based on scroll position
            if (currentScrollY > 10) {
                nav.classList.add('shadow-lg');
            } else {
                nav.classList.remove('shadow-lg');
            }
            
            // Hide/show navbar on scroll (optional)
            if (currentScrollY > 100) {
                if (currentScrollY > lastScrollY) {
                    nav.style.transform = 'translateY(-100%)';
                } else {
                    nav.style.transform = 'translateY(0)';
                }
            } else {
                nav.style.transform = 'translateY(0)';
            }
            
            lastScrollY = currentScrollY;
        }, 100);
        
        window.addEventListener('scroll', handleScroll, { passive: true });
    },
    
    // Alert system
    setupAlerts() {
        // Auto-hide flash messages
        setTimeout(() => {
            const alerts = document.querySelectorAll('.alert');
            alerts.forEach(alert => {
                this.fadeOutElement(alert, () => alert.remove());
            });
        }, this.config.alertAutoHideDelay);
        
        // Setup dismiss buttons
        document.querySelectorAll('.alert button').forEach(button => {
            button.addEventListener('click', (e) => {
                const alert = button.closest('.alert');
                if (alert) {
                    this.fadeOutElement(alert, () => alert.remove());
                }
            });
        });
    },
    
    // Form enhancements
    setupForms() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => this.enhanceForm(form));
    },
    
    // Enhance individual form
    enhanceForm(form) {
        // Real-time validation
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', this.debounce(() => this.validateField(input), 500));
        });
        
        // Form submission with loading state
        form.addEventListener('submit', (e) => {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
            }
        });
    },
    
    // Field validation
    validateField(field) {
        const value = field.value.trim();
        const type = field.type;
        const required = field.hasAttribute('required');
        
        let isValid = true;
        let message = '';
        
        // Required validation
        if (required && !value) {
            isValid = false;
            message = 'This field is required';
        }
        
        // Email validation
        if (type === 'email' && value && !this.isValidEmail(value)) {
            isValid = false;
            message = 'Please enter a valid email address';
        }
        
        // Update field appearance
        this.updateFieldValidation(field, isValid, message);
        
        return isValid;
    },
    
    // Update field validation state
    updateFieldValidation(field, isValid, message) {
        const wrapper = field.closest('.form-group') || field.parentElement;
        const errorElement = wrapper.querySelector('.field-error') || this.createErrorElement();
        
        if (isValid) {
            field.classList.remove('border-red-500');
            field.classList.add('border-green-500');
            errorElement.textContent = '';
            errorElement.classList.add('hidden');
        } else {
            field.classList.remove('border-green-500');
            field.classList.add('border-red-500');
            errorElement.textContent = message;
            errorElement.classList.remove('hidden');
            
            if (!wrapper.contains(errorElement)) {
                wrapper.appendChild(errorElement);
            }
        }
    },
    
    // Create error element
    createErrorElement() {
        const error = document.createElement('p');
        error.className = 'field-error text-sm text-red-600 mt-1 hidden';
        return error;
    },
    
    // Email validation
    isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    },
    
    // Enhanced performance monitoring
    setupPerformanceMonitoring() {
        // Monitor Core Web Vitals
        this.observeWebVitals();
        
        // Setup lazy loading for images
        this.setupLazyLoading();
        
        // Preload critical resources
        this.preloadCriticalResources();
    },
    
    // Web Vitals monitoring
    observeWebVitals() {
        // Largest Contentful Paint
        if ('PerformanceObserver' in window) {
            const lcpObserver = new PerformanceObserver((entryList) => {
                for (const entry of entryList.getEntries()) {
                    console.log('LCP:', entry.startTime);
                }
            });
            lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
            
            // Cumulative Layout Shift
            const clsObserver = new PerformanceObserver((entryList) => {
                let clsScore = 0;
                for (const entry of entryList.getEntries()) {
                    if (!entry.hadRecentInput) {
                        clsScore += entry.value;
                    }
                }
                console.log('CLS:', clsScore);
            });
            clsObserver.observe({ entryTypes: ['layout-shift'] });
        }
    },
    
    // Lazy loading setup
    setupLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    },
    
    // Preload critical resources
    preloadCriticalResources() {
        const criticalImages = ['/static/images/hero-bg.jpg', '/static/images/demo.png'];
        criticalImages.forEach(src => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.as = 'image';
            link.href = src;
            document.head.appendChild(link);
        });
    },
    
    // Scroll effects and animations
    setupScrollEffects() {
        // Intersection Observer for animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);
        
        // Observe elements for animation
        document.querySelectorAll('.slide-up, .fade-in, .card').forEach(el => {
            observer.observe(el);
        });
        
        let ticking = false;
        let lastKnownScrollPosition = 0;
        
        const updateScrollEffects = (scrollPos) => {
            // Parallax effects
            this.updateParallaxElements(scrollPos);
            
            // Progress bar
            this.updateReadingProgress(scrollPos);
            
            // Navigation background
            this.updateNavigationBackground(scrollPos);
            
            ticking = false;
        };
        
        window.addEventListener('scroll', () => {
            lastKnownScrollPosition = window.scrollY;
            
            if (!ticking) {
                requestAnimationFrame(() => updateScrollEffects(lastKnownScrollPosition));
                ticking = true;
            }
        });
    },
    
    // Parallax elements
    updateParallaxElements(scrollPos) {
        const parallaxElements = document.querySelectorAll('.parallax');
        parallaxElements.forEach(element => {
            const speed = element.dataset.speed || 0.5;
            const yPos = -(scrollPos * speed);
            element.style.transform = `translateY(${yPos}px)`;
        });
    },
    
    // Reading progress
    updateReadingProgress(scrollPos) {
        const progressBar = document.querySelector('.reading-progress');
        if (progressBar) {
            const winHeight = window.innerHeight;
            const docHeight = document.documentElement.scrollHeight;
            const totalDocScrollLength = docHeight - winHeight;
            const scrollProgress = scrollPos / totalDocScrollLength;
            progressBar.style.width = `${scrollProgress * 100}%`;
        }
    },
    
    // Navigation background
    updateNavigationBackground(scrollPos) {
        const nav = document.querySelector('nav');
        if (nav) {
            if (scrollPos > 100) {
                nav.classList.add('nav-scrolled');
            } else {
                nav.classList.remove('nav-scrolled');
            }
        }
    },
    
    // Animation setup
    setupAnimations() {
        // Stagger animations for multiple elements
        const staggerElements = document.querySelectorAll('.stagger-children > *');
        staggerElements.forEach((el, index) => {
            el.style.animationDelay = `${index * 100}ms`;
        });
        
        // Parallax effects (optional)
        this.setupParallax();
        
        const animationObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                    
                    // Staggered animations for children
                    const children = entry.target.querySelectorAll('.stagger-child');
                    children.forEach((child, index) => {
                        setTimeout(() => {
                            child.classList.add('animate-in');
                        }, index * 100);
                    });
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });
        
        // Observe elements for animation
        const animatedElements = document.querySelectorAll('.animate-on-scroll');
        animatedElements.forEach(el => animationObserver.observe(el));
    },
    
    // Parallax effects
    setupParallax() {
        const parallaxElements = document.querySelectorAll('[data-parallax]');
        if (parallaxElements.length === 0) return;
        
        const handleParallax = this.throttle(() => {
            const scrolled = window.pageYOffset;
            
            parallaxElements.forEach(el => {
                const rate = scrolled * -0.5;
                el.style.transform = `translateY(${rate}px)`;
            });
        }, 16); // 60fps
        
        window.addEventListener('scroll', handleParallax, { passive: true });
    },
    
    // Accessibility enhancements
    setupAccessibility() {
        // Focus management
        this.setupFocusManagement();
        
        // Keyboard navigation
        this.setupKeyboardNavigation();
        
        // Screen reader announcements
        this.setupScreenReaderAnnouncements();
        
        // Reduced motion preferences
        this.respectReducedMotion();
    },
    
    // Focus management
    setupFocusManagement() {
        // Focus visible polyfill
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
        });
        
        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-navigation');
        });
        
        // Skip to main content
        const skipLink = document.querySelector('.skip-link');
        if (skipLink) {
            skipLink.addEventListener('click', (e) => {
                e.preventDefault();
                const mainContent = document.getElementById('main-content');
                if (mainContent) {
                    mainContent.focus();
                    mainContent.scrollIntoView();
                }
            });
        }
    },
    
    // Keyboard navigation
    setupKeyboardNavigation() {
        // Escape key handling for dropdowns
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                // Close any open dropdowns
                document.querySelectorAll('[aria-expanded="true"]').forEach(el => {
                    el.setAttribute('aria-expanded', 'false');
                    const dropdown = document.getElementById(el.getAttribute('aria-controls'));
                    if (dropdown) {
                        dropdown.classList.add('hidden');
                    }
                });
            }
        });
    },
    
    // Screen reader announcements
    setupScreenReaderAnnouncements() {
        // Create live region for announcements
        const liveRegion = document.createElement('div');
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'sr-only';
        liveRegion.id = 'live-region';
        document.body.appendChild(liveRegion);
    },
    
    // Announce to screen readers
    announce(message, priority = 'polite') {
        const liveRegion = document.getElementById('live-region');
        if (liveRegion) {
            liveRegion.setAttribute('aria-live', priority);
            liveRegion.textContent = message;
            
            // Clear after announcement
            setTimeout(() => {
                liveRegion.textContent = '';
            }, 1000);
        }
    },
    
    // Respect reduced motion preferences
    respectReducedMotion() {
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            document.documentElement.style.setProperty('--animation-duration', '0.01ms');
            document.documentElement.style.setProperty('--transition-duration', '0.01ms');
        }
    },
    
    // Performance optimizations
    setupPerformance() {
        // Lazy load images
        this.setupLazyLoading();
        
        // Preload critical resources
        this.preloadCriticalResources();
    },
    
    // Lazy loading for images
    setupLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            images.forEach(img => imageObserver.observe(img));
        } else {
            // Fallback for older browsers
            images.forEach(img => {
                img.src = img.dataset.src;
            });
        }
    },
    
    // Preload critical resources
    preloadCriticalResources() {
        // Preload fonts
        const fontUrls = [
            'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap'
        ];
        
        fontUrls.forEach(url => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.as = 'style';
            link.href = url;
            document.head.appendChild(link);
        });
    },
    
    // Utility functions
    
    // Set button loading state
    setButtonLoading(button, isLoading) {
        if (isLoading) {
            button.dataset.originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Processing...';
            button.disabled = true;
        } else {
            button.innerHTML = button.dataset.originalText || button.innerHTML;
            button.disabled = false;
            delete button.dataset.originalText;
        }
    },
    
    // Fade out element
    fadeOutElement(element, callback) {
        element.style.transition = 'all 0.5s ease-out';
        element.style.transform = 'translateX(100%)';
        element.style.opacity = '0';
        setTimeout(() => {
            if (callback) callback();
        }, 500);
    },
    
    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Throttle function
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    // Get viewport size
    getViewportSize() {
        return {
            width: Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0),
            height: Math.max(document.documentElement.clientHeight || 0, window.innerHeight || 0)
        };
    },
    
    // Check if mobile
    isMobile() {
        return this.getViewportSize().width < this.config.breakpoints.md;
    },
    
    // Show notification
    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} fixed top-24 right-4 z-50 max-w-sm slide-up`;
        notification.innerHTML = `
            <div class="flex items-start">
                <div class="flex-shrink-0">
                    <i class="fas ${this.getAlertIcon(type)}"></i>
                </div>
                <div class="ml-3 flex-1">
                    <p class="text-sm font-medium">${message}</p>
                </div>
                <div class="ml-4 flex-shrink-0">
                    <button onclick="this.parentElement.parentElement.remove()" class="transition-colors duration-200">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove
        setTimeout(() => {
            if (notification.parentElement) {
                this.fadeOutElement(notification, () => notification.remove());
            }
        }, duration);
        
        // Announce to screen readers
        this.announce(message);
    },
    
    // Get alert icon
    getAlertIcon(type) {
        const icons = {
            success: 'fa-check-circle text-green-500',
            error: 'fa-exclamation-circle text-red-500',
            warning: 'fa-exclamation-triangle text-yellow-500',
            info: 'fa-info-circle text-blue-500'
        };
        return icons[type] || icons.info;
    },
    
    // Modern modal system
    createModal(options = {}) {
        const {
            title = 'Modal',
            content = '',
            size = 'md',
            closable = true,
            backdrop = true
        } = options;
        
        // Create modal HTML
        const modal = document.createElement('div');
        modal.className = `modal-overlay fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm opacity-0 transition-opacity duration-300`;
        
        modal.innerHTML = `
            <div class="modal-content bg-white rounded-3xl shadow-2xl transform scale-95 transition-all duration-300 ${this.getModalSize(size)}">
                ${closable ? '<button class="modal-close absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-2xl">&times;</button>' : ''}
                <div class="modal-header px-8 py-6 border-b border-gray-200">
                    <h3 class="text-2xl font-bold text-gray-900">${title}</h3>
                </div>
                <div class="modal-body px-8 py-6">
                    ${content}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Show modal with animation
        requestAnimationFrame(() => {
            modal.classList.remove('opacity-0');
            modal.querySelector('.modal-content').classList.remove('scale-95');
        });
        
        // Event listeners
        if (closable) {
            const closeBtn = modal.querySelector('.modal-close');
            closeBtn.addEventListener('click', () => this.closeModal(modal));
        }
        
        if (backdrop) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal);
                }
            });
        }
        
        // Escape key to close
        const escapeHandler = (e) => {
            if (e.key === 'Escape') {
                this.closeModal(modal);
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);
        
        return modal;
    },
    
    // Close modal with animation
    closeModal(modal) {
        modal.classList.add('opacity-0');
        modal.querySelector('.modal-content').classList.add('scale-95');
        
        setTimeout(() => {
            modal.remove();
        }, 300);
    },
    
    // Get modal size classes
    getModalSize(size) {
        const sizes = {
            sm: 'max-w-md',
            md: 'max-w-lg',
            lg: 'max-w-2xl',
            xl: 'max-w-4xl'
        };
        return sizes[size] || sizes.md;
    },
    
    // Toast notification system
    showToast(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        const icons = {
            success: 'fas fa-check-circle text-green-500',
            error: 'fas fa-exclamation-circle text-red-500',
            warning: 'fas fa-exclamation-triangle text-yellow-500',
            info: 'fas fa-info-circle text-blue-500'
        };
        
        toast.className = `toast fixed top-20 right-4 z-50 bg-white rounded-xl shadow-lg border border-gray-200 p-4 transform translate-x-full transition-transform duration-300 max-w-sm`;
        
        toast.innerHTML = `
            <div class="flex items-start">
                <i class="${icons[type]} mr-3 mt-0.5"></i>
                <div class="flex-1">
                    <p class="text-sm font-medium text-gray-900">${message}</p>
                </div>
                <button class="toast-close ml-2 text-gray-400 hover:text-gray-600">
                    <i class="fas fa-times text-xs"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Show toast
        requestAnimationFrame(() => {
            toast.classList.remove('translate-x-full');
        });
        
        // Close button
        toast.querySelector('.toast-close').addEventListener('click', () => {
            this.closeToast(toast);
        });
        
        // Auto-hide
        setTimeout(() => {
            this.closeToast(toast);
        }, duration);
        
        return toast;
    },
    
    // Close toast
    closeToast(toast) {
        toast.classList.add('translate-x-full');
        setTimeout(() => toast.remove(), 300);
    },
    
    // Smooth page transitions
    setupPageTransitions() {
        // Add loading overlay
        const loadingOverlay = document.createElement('div');
        loadingOverlay.id = 'page-loading';
        loadingOverlay.className = 'fixed inset-0 bg-white z-50 flex items-center justify-center opacity-0 pointer-events-none transition-opacity duration-300';
        loadingOverlay.innerHTML = `
            <div class="text-center">
                <div class="w-12 h-12 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin mb-4"></div>
                <p class="text-gray-600 font-medium">Loading...</p>
            </div>
        `;
        document.body.appendChild(loadingOverlay);
        
        // Intercept navigation
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a[href]');
            if (link && link.hostname === window.location.hostname && !link.hasAttribute('target')) {
                e.preventDefault();
                this.navigateWithTransition(link.href);
            }
        });
    },
    
    // Navigate with smooth transition
    navigateWithTransition(url) {
        const overlay = document.getElementById('page-loading');
        overlay.classList.remove('pointer-events-none', 'opacity-0');
        
        setTimeout(() => {
            window.location.href = url;
        }, 300);
    },
    
    // Initialize theme system
    setupTheme() {
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', this.toggleTheme.bind(this));
        }
        
        // Apply saved theme
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.applyTheme(savedTheme);
    },
    
    // Toggle theme
    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.applyTheme(newTheme);
        localStorage.setItem('theme', newTheme);
    },
    
    // Apply theme
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        const themeToggle = document.querySelector('.theme-toggle i');
        if (themeToggle) {
            themeToggle.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    ScreenshotToCode.init();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Page is hidden - pause animations, videos, etc.
        document.querySelectorAll('video, audio').forEach(media => {
            if (!media.paused) {
                media.pause();
                media.dataset.autopaused = 'true';
            }
        });
    } else {
        // Page is visible - resume media
        document.querySelectorAll('[data-autopaused]').forEach(media => {
            media.play();
            delete media.dataset.autopaused;
        });
    }
});

// Handle online/offline status
window.addEventListener('online', function() {
    ScreenshotToCode.showToast('Connection restored', 'success');
});

window.addEventListener('offline', function() {
    ScreenshotToCode.showToast('Connection lost. Some features may be unavailable.', 'warning', 10000);
});

// Export for global access
window.ScreenshotToCode = ScreenshotToCode;
