document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById("ticketForm");
    const submitBtn = document.getElementById("submitBtn");
    const btnText = document.getElementById("btnText");
    const btnLoading = document.getElementById("btnLoading");
  
    const countdownSpan = document.getElementById("countdown");
    
    function formatTime(seconds) {
        if (seconds <= 0) return "0s";
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = seconds % 60;
        
        let parts = [];
        if (h > 0) parts.push(`${h}h`);
        if (m > 0) parts.push(`${m}m`);
        if (s > 0 || parts.length === 0) parts.push(`${s}s`);
        
        return parts.join(" ");
    }

    if (countdownSpan) {
        // Get raw seconds from data attribute
        let timeLeft = parseInt(countdownSpan.dataset.seconds);
        
        const timer = setInterval(() => {
            timeLeft--; // Decrement first to show immediate change or wait 1s? 
            // Better to decrement after 1s, but we usually want to show the next second.
            
            if (timeLeft <= 0) {
                clearInterval(timer);
                window.location.reload(); 
            } else {
                countdownSpan.innerText = formatTime(timeLeft);
            }
        }, 1000);
    }
    
    if(form && submitBtn) {
        form.addEventListener("submit", function () {
            // Only disable button if the browser's basic validation passes
            if (form.checkValidity()) {
                submitBtn.disabled = true;
                if(btnText) btnText.classList.add("d-none");
                if(btnLoading) btnLoading.classList.remove("d-none");
            }
        });
    }
});
