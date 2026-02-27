document.addEventListener('DOMContentLoaded', () => {
    const hasPlayed = sessionStorage.getItem('introPlayed');
    const overlay = document.getElementById('intro-overlay');

    if (hasPlayed === 'true' && overlay) {
        overlay.remove();
        document.body.classList.remove('intro-active');
        return;
    }

    if (!overlay) return;

    document.body.classList.add('intro-active');

    const tl = gsap.timeline({
        onComplete: () => {
            sessionStorage.setItem('introPlayed', 'true');
            overlay.remove();
            document.body.classList.remove('intro-active');
        }
    });

    // 2. GSAP animates logo: scale 0.3 to 1.0, opacity 0 to 1, duration 0.8s, ease power3.out
    tl.to('.intro-logo-container', {
        scale: 1,
        opacity: 1,
        duration: 0.8,
        ease: 'power3.out'
    });

    // 4. Wordmark letters stagger animation
    tl.to('.intro-wordmark span', {
        y: 0,
        opacity: 1,
        duration: 0.4,
        stagger: 0.06,
        ease: 'back.out(1.7)'
    }, "-=0.2");

    // 5. Tagline "Exam Cell, Reimagined." fades in
    tl.to('.intro-tagline', {
        opacity: 1,
        duration: 0.4
    }, "+=0.1");

    // 7. Progress bar at bottom of overlay fills 0 to 100% over 2 seconds
    tl.to('.intro-progress-bar', {
        width: '100%',
        duration: 2.0,
        ease: 'power1.inOut'
    }, 0);

    // 8. After 3.5 seconds total: overlay animates out, y 0 to -100vh, opacity 1 to 0, 0.6s ease-in-out
    tl.to(overlay, {
        y: '-100vh',
        opacity: 0,
        duration: 0.6,
        ease: 'power2.inOut',
        delay: 0.5
    });

    // 12. Add event listener: on any click or keypress during animation, skip immediately
    const skipAnimation = () => {
        tl.progress(1);
    };

    window.addEventListener('click', skipAnimation, { once: true });
    window.addEventListener('keydown', skipAnimation, { once: true });
});
