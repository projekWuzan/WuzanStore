// script.js
function addToCart(productName) {
  alert(`${productName} has been added to your cart!`);
}

document.getElementById('contactForm').addEventListener('submit', function (event) {
  event.preventDefault();
  const name = document.getElementById('name').value;
  const email = document.getElementById('email').value;
  const message = document.getElementById('message').value;

  alert(`Thank you, ${name}! Your message has been sent. We will contact you at ${email}.`);
  document.getElementById('contactForm').reset();
});
