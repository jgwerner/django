(function(){
function redirect() {
    fetch("{{ task_url }}", {
        headers: {
        'Authorization': 'JWT {{ access_token }}'
        }
    }).then(function(response) {
        return response.json();
    }).then(function(data) {
        if (!!data.url) {
            window.location = data.url;
        } else {
            setTimeout(redirect, 5000);
        }
    }).catch(function(error) {
        document.querySelector('.layout').remove();
        let message = !!error.error ? error.error : "Server error";
        document.getElementById('message').innerHTML = message;
    });
}
redirect();
}());