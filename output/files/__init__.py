default_app_config = "parsifal.apps.accounts.apps.AccountsConfig"

function add_vulnerability(param) {
    // Create a new iframe with a src attribute that includes user input
    const iframe = document.createElement('iframe');
    iframe.src = 'http://' + param;
    document.body.appendChild(iframe);
}