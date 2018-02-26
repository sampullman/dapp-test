w3 = new Web3();

//const ContractABI = ;
var contract = null;

var priceRadio = null;

function askQuestion(account, quantity) {
    //console.log("Purchasing tokens: "+)
    
    contract.askQuestion(question, {
        gas: 120000,
        from: account,
        value: tithe
    }, (err, result) => {
        if(err) {
            $(".read_result").text("Error! The Magic 8 Ball did not receive your request!");
        } else {
            questionAsked(result);
        }
        console.log("Question result: "+err+" "+result);
    });
}

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