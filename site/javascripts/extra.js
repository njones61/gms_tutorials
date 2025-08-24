// Custom JavaScript for GMS Tutorials

// Add smooth scrolling to anchor links
document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Add copy button to code blocks
document.addEventListener('DOMContentLoaded', function() {
    const codeBlocks = document.querySelectorAll('pre code');
    
    codeBlocks.forEach(block => {
        const copyButton = document.createElement('button');
        copyButton.textContent = 'Copy';
        copyButton.className = 'copy-button';
        copyButton.style.cssText = `
            position: absolute;
            top: 5px;
            right: 5px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 3px;
            padding: 2px 8px;
            font-size: 12px;
            cursor: pointer;
        `;
        
        copyButton.addEventListener('click', function() {
            navigator.clipboard.writeText(block.textContent);
            this.textContent = 'Copied!';
            setTimeout(() => {
                this.textContent = 'Copy';
            }, 2000);
        });
        
        const pre = block.parentElement;
        pre.style.position = 'relative';
        pre.appendChild(copyButton);
    });
});
