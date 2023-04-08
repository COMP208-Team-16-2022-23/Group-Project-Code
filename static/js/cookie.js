// Get the cookie banner element
var cookieBanner = document.getElementById('cookie-banner');

// Get the close button element
var closeButton = document.getElementById('close-button');

// Get the body element
var body = document.getElementsByTagName('body')[0];

// Check if the user has accepted the cookie policy
if (getCookie('cookie-policy') != 'accepted') {
    // Show the cookie banner
    cookieBanner.style.display = 'block';

    // Add the no-scroll class to the body element to block interaction with other parts of the website
    body.classList.add('no-scroll');
}

// Add a click event listener to the close button
closeButton.addEventListener('click', function () {
    // Set a cookie to indicate that the user has accepted the cookie policy (expires in 365 days)
    setCookie('cookie-policy', 'accepted', 365);

    // Remove the cookie banner
    cookieBanner.remove();

    // Remove the no-scroll class from the body element to re-enable scrolling and interaction with other parts of the website
    body.classList.remove('no-scroll');
});

// Set a cookie with the given name, value, and expiration days
function setCookie(name, value, days) {
    var expires = '';
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = '; expires=' + date.toUTCString();
    }
    document.cookie = name + '=' + value + expires + '; path=/';
}

// Get the value of the cookie with the given name
function getCookie(name) {
    var nameEQ = name + '=';
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}