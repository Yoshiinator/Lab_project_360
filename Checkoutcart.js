const folder = "dicePngs/";

fetch('store-items.json')
  .then(res => res.json())
    .then(items => {
        const grid = document.getElementById('Checkoutgrid');
        const template = document.getElementById('itemTemplate');
        console.log("anything");
        var total = 0;

        items.forEach(item => {
            const clone = template.content.cloneNode(true);
            clone.querySelector('.card-title').textContent = item.name;
            clone.querySelector('.price').textContent = `$${item.price.toFixed(2)}`;
            clone.querySelector('.quantity').textContent = item.quantity;
            grid.appendChild(clone);

            total += item.price * item.quantity;
        });

        document.querySelector('.totalPrice').textContent = `Total: $${total.toFixed(2)}`;
    });

