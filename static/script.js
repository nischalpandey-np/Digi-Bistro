document.addEventListener('DOMContentLoaded', () => {
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    const menuForm = document.getElementById('menu-form');
    const itemsField = document.getElementById('items');

    addToCartButtons.forEach(button => {
        button.addEventListener('click', () => {
            const item = button.getAttribute('data-item');
            const input = document.querySelector(`input[name="${item}"]`);
            if (input.value == 0) {
                input.value = 1;
                button.textContent = 'Remove';
            } else {
                input.value = 0;
                button.textContent = 'Add to Cart';
            }
        });
    });

    menuForm.addEventListener('submit', (event) => {
        const items = {};
        document.querySelectorAll('.quantity-input').forEach(input => {
            const quantity = parseInt(input.value, 10);
            if (quantity > 0) {
                items[input.name] = quantity;
            }
        });
        itemsField.value = JSON.stringify(items);
    });
});