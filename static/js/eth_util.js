
var testCallback = function(error, result) { console.log(error+" "+result);};

BN = BigNumber.another();

function etherRadio(wei) {
    var eth = BN(wei).div(BN(1e18)).toNumber();
    var value = $('<span class="eth_value">'+eth+'</span>');
    console.log(wei);

    var form = $('<form class="eth_convert">').append('<input type="hidden" name="value" value='+wei+' />')
            .append('<label><input type="radio" name="eth" id="ether" value="ether" checked /><span>Ether</span></label>')
            .append('<label><input type="radio" name="eth" id="wei" value="wei" /><span>Wei</span></label>');
    form.find('input[type=radio][name=eth]').change(function() {
        setRadioValueHelper(value, this.value, wei);
    });
    return [form, value];
}

function setRadioValueHelper(valueElement, denomination, wei) {
    var eth = BN(wei).div(BN(1e18)).toNumber();
    if (denomination == 'ether') {
        valueElement.html(eth);
    } else if (denomination == 'wei') {
        valueElement.html(wei);
    }
}

function setRadioValue(radio, wei) {
    var denomination = $(radio[0].find('input[name=eth]:checked')).val();
    setRadioValueHelper(radio[1], denomination, wei);
}

function row(title, value) {
    return $('<tr>').append('<td class="disp_title">'+title+':</td>')
                    .append($('<td class="disp_value"></td>').append(value));
}

function showError(form, error) {
    form.parent().find(".read_result").html(error);
}

function readSuccess(form, displayFn) {
    return function(response) {
        console.log("Success");
        console.log(response);

        var data = JSON.parse(response);
        if("errors" in data) {
            showError(form, data.errors[0]);
        } else {
            var resultDiv = form.parent().find(".read_result");
            resultDiv.html("");
            resultDiv.append(displayFn(data));
        }
    }
}

function readFail(form) {
    return function(jqXHR, textStatus, errorThrown) {
        console.log(jqXHR);
        console.log(textStatus);
        console.log(errorThrown);
        if(jqXHR.responseText.indexOf("The CSRF token has expired") !== -1) {

            showError(form, "Session timed out, reload the page.");
        } else {
            showError(form, "Server error");
        }
    }
}

function make_form(formIdd, displayFn) {
    $(formIdd).submit(function(event) {
        form = $(formIdd);
        event.preventDefault();
        $.post(form.attr("action"), form.serialize())
            .done(readSuccess(form, displayFn)).fail(readFail(form));      
    });
}

function strip_hex(hex_str) {
    if(hex_str.startsWith('0x')) {
        hex_str = hex_str.substring(2, hex_str.length);
    }
    return hex_str;
}

function getWeb3js() {
    if (typeof web3 !== 'undefined') {
        // Use Mist/MetaMask's provider
        return new Web3(web3.currentProvider);
        console.log("Using metamask");
    } else {
        return new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));
    }
}

function setNetwork(netId) {
    switch(netId) {
    case 1:
        $("#network").text("Main network");
        break;
    case 3:
        $("#network").text("Ropsten test network");
        break;
    case 8178:
        $("#network").text("Podo test network");
        break;
    default:
        $("#network").text("Unknown network");
        break;
    }
}