
function balanceDisplay(info) {
    console.log(info);
    return $('<table>').append(row("Coins", info.balance));
}

$(document).ready(function() {

    //x.substr(2, x.length)

    make_form("#balance", balanceDisplay);
});