// set cookie function
function setCookie(name, value, days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/";
}

// get cookie function
function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

// check if cookie exists
if (!getCookie('cookie-accepted')) {
    // show cookie banner
    var cookieBanner = document.getElementById('cookie-banner');
    cookieBanner.classList.add('show');

    // block interaction with other parts of the website
    var body = document.getElementsByTagName('body')[0];
    body.classList.add('no-scroll');

    // accept cookies button click event
    var acceptCookiesButton = document.getElementById('accept-cookies');
    acceptCookiesButton.addEventListener('click', function () {
        // set cookie and hide cookie banner
        setCookie('cookie-accepted', 'true', 365);
        cookieBanner.classList.remove('show');

        // unblock interaction with other parts of the website
        body.classList.remove('no-scroll');
    });
}