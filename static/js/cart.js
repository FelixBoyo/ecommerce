var updateBtns = document.getElementsByClassName('update-cart')

for(var i = 0; i < updateBtns.length; i++){
    updateBtns[i].addEventListener('click', function(){
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log('productId:', productId,'action:', action)

        console.log ('USER:', user)
        if (user === 'AnonymousUser'){
            addCookieItem(productId, action)
        }else{
            updateUserOrder(productId, action)
        }
    })
}

function addCookieItem(productId, action){
    console.log('Not logged in...')
    
    if (action == 'add') {
        if (cart[productId] == undefined) {
            // If product is not in cart, add it with quantity of 1
            cart[productId] = { 'quantity': 1 };
        } else {
            // If product is already in cart, increment its quantity by 1
            cart[productId]['quantity'] += 1;
        }
    }
    
    if (action == 'remove') {
        // Decrease the quantity of the product
        cart[productId]['quantity'] -= 1;
    
        // If quantity is 0 or less, remove the product from the cart
        if (cart[productId]['quantity'] <= 0) {
            console.log('remove item');
            delete cart[productId];
        }
    }
    
    console.log('Cart:', cart)
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
    location.reload()

}

function updateUserOrder(productId, action){
    console.log('User is logged in, sending data..')

    var url = '/update_item/';

    fetch(url, {
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify({ 'productId':productId, 'action':action })
    })

    .then((response) =>{
        return response.json()
    })

    .then((data) =>{
         console.log('data:', data)
         location.reload()
    })
}