document.addEventListener('DOMContentLoaded', function() {
    // Feather icons replacement
    if (window.feather) {
        feather.replace();
    }

    // Viewport height fix for mobile
    function setViewportHeight() {
        let vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }
    setViewportHeight();
    window.addEventListener('resize', setViewportHeight);

    // Login Form AJAX with better mobile UX
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitBtn = document.getElementById('submitBtn');
            const defaultIcon = submitBtn.querySelector('#defaultIcon');
            const loadingIcon = submitBtn.querySelector('#loadingIcon');
            const successMessage = document.getElementById('successMessage');
            const errorMessage = document.getElementById('errorMessage');
            
            // Show loading state
            submitBtn.disabled = true;
            defaultIcon.classList.add('hidden');
            loadingIcon.classList.remove('hidden');
            
            // Hide previous messages
            successMessage.classList.add('hidden');
            errorMessage.classList.add('hidden');
            
            const email = document.getElementById('email').value.trim();
            console.log('Email:', email); // Debugging line
            
            try {
                const response = await fetch('/api/auth/verify_login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email }),
                });
                
                const data = await response.json();
                
                if (data.success) {
                    successMessage.textContent = data.message;
                    successMessage.classList.remove('hidden');
                    
                    // Store email in localStorage as fallback
                    localStorage.setItem('verify_email', email);
                    
                    // Redirect after a short delay
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 1500);
                } else {
                    errorMessage.textContent = data.message;
                    errorMessage.classList.remove('hidden');
                    
                    // Focus back on email input for mobile users
                    document.getElementById('email').focus();
                }
            } catch (error) {
                errorMessage.textContent = 'Network error. Please check your connection and try again.';
                errorMessage.classList.remove('hidden');
            } finally {
                submitBtn.disabled = false;
                defaultIcon.classList.remove('hidden');
                loadingIcon.classList.add('hidden');
            }
        });
    }
    
    // Verification Code Auto-Tabbing with mobile optimizations
    function moveToNext(input) {
        if (input.value.length === 1) {
            const next = input.nextElementSibling;
            if (next && next.tagName === 'INPUT') {
                next.focus();
            } else {
                // Last input - combine all codes
                combineCodes();
                // On mobile, hide keyboard after last input
                if ('virtualKeyboard' in navigator) {
                    input.blur();
                }
            }
        } else if (input.value.length === 0) {
            const prev = input.previousElementSibling;
            if (prev && prev.tagName === 'INPUT') {
                prev.focus();
            }
        }
    }
    
    function combineCodes() {
        const form = document.getElementById('verifyForm');
        if (!form) return;
        
        const fullCode = Array.from(document.querySelectorAll('input[name^="code"]'))
            .map(input => input.value)
            .join('');
        
        document.getElementById('fullCode').value = fullCode;
    }
    
    // Auto-combine codes when last input is filled
    const codeInputs = document.querySelectorAll('input[name^="code"]');
    if (codeInputs.length > 0) {
        codeInputs.forEach((input, index) => {
            input.addEventListener('input', function() {
                if (this.value.length === 1) {
                    combineCodes();
                }
            });
            
            // Better mobile UX: focus first input on page load
            if (index === 0) {
                setTimeout(() => {
                    input.focus();
                }, 300);
            }
        });
    }
    
    // Pre-fill email in verification page
    const userEmail = document.getElementById('userEmail');
    if (userEmail) {
        const email = userEmail.textContent;
        if (email === 'your email') {
            // Try to get from localStorage if session expired
            const storedEmail = localStorage.getItem('verify_email');
            if (storedEmail) {
                userEmail.textContent = storedEmail;
            }
        }
    }
    
    // Better mobile form submission
    const verifyForm = document.getElementById('verifyForm');
    if (verifyForm) {
        verifyForm.addEventListener('submit', function() {
            // On mobile, hide keyboard before form submission
            if ('virtualKeyboard' in navigator) {
                document.activeElement.blur();
            }
        });
    }
});



document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    
    // Event delegation for cart actions
    document.getElementById('cart-items-container')?.addEventListener('click', async function(e) {
        const itemElement = e.target.closest('[id^="cart-item-"]');
        if (!itemElement) return;
        
        const productId = itemElement.dataset.itemId;
        const quantityElement = itemElement.querySelector('.item-quantity');
        const priceElement = itemElement.querySelector('.item-price');
        let currentQuantity = parseInt(quantityElement.textContent);
        const price = parseFloat(priceElement.dataset.price);

        // Handle increment
        if (e.target.closest('.increment-btn')) {
            currentQuantity += 1;
            await updateCartItem(productId, currentQuantity);
            quantityElement.textContent = currentQuantity;
            updateCartSummary();
        }
        // Handle decrement
        else if (e.target.closest('.decrement-btn')) {
            if (currentQuantity > 1) {
                currentQuantity -= 1;
                await updateCartItem(productId, currentQuantity);
                quantityElement.textContent = currentQuantity;
                updateCartSummary();
            }
        }
        // Handle remove
        else if (e.target.closest('.remove-btn')) {
            if (confirm('Are you sure you want to remove this item from your cart?')) {
                await removeCartItem(productId);
                itemElement.remove();
                updateCartSummary();
                checkEmptyCart();
            }
        }
    });

    async function updateCartItem(productId, quantity) {
        try {
            const response = await fetch('/update_cart_item', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    product_id: productId,
                    quantity: quantity
                })
            });
            
            const data = await response.json();
            if (!data.success) {
                alert('Failed to update cart: ' + (data.message || 'Please try again'));
                window.location.reload();
            }
        } catch (error) {
            console.error('Cart update error:', error);
            alert('Network error - please try again');
        }
    }

    async function removeCartItem(productId) {
        try {
            const response = await fetch('/remove_cart_item', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    product_id: productId
                })
            });
            
            const data = await response.json();
            if (!data.success) {
                alert('Failed to remove item: ' + (data.message || 'Please try again'));
                window.location.reload();
            }
        } catch (error) {
            console.error('Cart remove error:', error);
            alert('Network error - please try again');
        }
    }

    function updateCartSummary() {
        // Calculate totals from visible items (matches server-side)
        let totalItems = 0;
        let subtotal = 0;
        
        document.querySelectorAll('[id^="cart-item-"]').forEach(item => {
            const quantity = parseInt(item.querySelector('.item-quantity').textContent);
            const price = parseFloat(item.querySelector('.item-price').dataset.price);
            
            totalItems += quantity;
            subtotal += quantity * price;
        });
        
        const discount = subtotal * 0.33;
        const total = subtotal - discount;
        
        // Update summary DOM
        document.getElementById('total-items').textContent = totalItems;
        document.getElementById('subtotal').textContent = subtotal.toFixed(2);
        document.getElementById('discount').textContent = discount.toFixed(2);
        document.getElementById('cart-total').textContent = total.toFixed(2);
        document.getElementById('checkout-total').textContent = total.toFixed(2);
    }

    function checkEmptyCart() {
        if (document.querySelectorAll('[id^="cart-item-"]').length === 0) {
            window.location.reload();
        }
    }
});

