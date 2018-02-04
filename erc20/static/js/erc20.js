w3 = new Web3();

var priceRadio = null;

function updatePrice() {
    var quantity = $("#purchase input[name=quantity]").val();
    if(quantity == "") {
        quantity = 0;
    } else {
        quantity = parseInt(quantity);
    }
    setRadioValue(priceRadio, quantity * tokenPrice);
}

$(document).ready(function() {

    //x.substr(2, x.length)
    w3 = getWeb3js();

    if(w3.givenProvider && w3.eth.net) {
        $(".have_web3").show();
        $(".no_web3").hide();

        w3.eth.net.getId((err, netId) => {
            console.log("Got network "+netId);
            setNetwork(netId);
        });
    } else {
        $(".have_web3").hide();
        $(".no_web3").show();
    }

    priceRadio = etherRadio(tokenPrice);
    $("#token_unit").append(priceRadio[0]);
    $("#token_price").append(priceRadio[1]);
    $("#purchase input[name=quantity]").on('input', function() {
        updatePrice();
    });
    updatePrice();
});