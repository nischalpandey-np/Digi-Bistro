document.addEventListener('DOMContentLoaded', function() {
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    const quantityInputs = document.querySelectorAll('.quantity-input');
    const menuForm = document.getElementById('menu-form');
    const orderForm = document.getElementById('order-form-content');

    // Handle Add to Cart / Remove from Cart Button
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function() {
            const itemName = this.getAttribute('data-item');
            const correspondingInput = menuForm.querySelector(`input[name="${itemName}"]`);
            if (correspondingInput.disabled) {
                correspondingInput.disabled = false;
                  correspondingInput.value = 1; // Start with quantity 1 when added to cart
                this.textContent = 'Remove Item from cart';
            } else {
                correspondingInput.disabled = true;
                correspondingInput.value = 0;
                this.textContent = 'Add to Cart';
            }
        });
    });

    // Handle Menu Form Submission
    if (menuForm) {
        menuForm.addEventListener('submit', function(event) {
            event.preventDefault();

            const formData = new FormData(menuForm);
            const items = {};

            for (const [key, value] of formData.entries()) {
                if (value > 0) {
                    items[key] = value;
                }
            }

            if (Object.keys(items).length === 0) {
                alert('Please add at least one item to the cart.');
                return;
            }

            const queryString = new URLSearchParams(items).toString();
            window.location.href = `order.html?${queryString}`;
        });
    }

    /// Populate Order Form with Items
if (orderForm) {
    const queryParams = new URLSearchParams(window.location.search);
    const itemsField = document.getElementById('items');
    const items = [];

    queryParams.forEach((value, key) => {
        items.push(`${key}=${value}`);
    });

    itemsField.value = items.join(', ');
}

});
