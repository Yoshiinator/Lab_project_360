const folder = "dicePngs/";

fetch('store-items.json')
  .then(res => res.json())
    .then(items => {
        const grid = document.getElementById('storeGrid');
        const template = document.getElementById('itemTemplate');
        console.log("anything");

        items.forEach(item => {
            const clone = template.content.cloneNode(true);
            clone.querySelector('.card-img-top').src = folder + item.image;
            clone.querySelector('.card-img-top').alt = item.name;
            clone.querySelector('.card-title').textContent = item.name;
            clone.querySelector('.card-text').textContent = item.description;
            clone.querySelector('.price').textContent = `$${item.price.toFixed(2)}`;
            grid.appendChild(clone);
        });
    });
