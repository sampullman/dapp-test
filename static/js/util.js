
$.notify.defaults({ className: "info" });

function copyToClipboard(element) {
    element.select();
    document.execCommand("Copy");
}