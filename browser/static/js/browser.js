
BN = BigNumber.another();

function etherRadio(wei) {
    var eth = BN(wei).div(BN(1e18)).toNumber();
    var value = $('<span class="eth_value">'+eth+'</span>');
    console.log(wei);

    var form = $('<form class="eth_convert">').append('<input type="hidden" name="value" value='+wei+' />')
            .append('<label><input type="radio" name="eth" id="ether" value="ether" checked /><span>Ether</span></label>')
            .append('<label><input type="radio" name="eth" id="wei" value="wei" /><span>Wei</span></label>');
    form.find('input[type=radio][name=eth]').change(function() {
        var eth = BN(wei).div(BN(1e18)).toNumber();
        if (this.value == 'ether') {
            value.html(eth);
        } else if (this.value == 'wei') {
            value.html(wei);
        }
    });
    return [form, value];
}

function row(title, value) {
    return $('<tr>').append('<td class="disp_title">'+title+':</td>')
                    .append($('<td class="disp_value"></td>').append(value));
}

function accountDisplay(info) {
    console.log(info);
    var wei = info.balance;
    return $('<table>').append(row("Balance", etherRadio(wei)))
                    .append(row("Transactions", info.tx_count));
}

function transactionDisplay(info) {
    var display = $('<table>').append(row("Block", "#"+info.blockNumber+" "+info.blockHash))
        .append(row("From", info.from)).append(row("To", info.to)).append(row("Value", etherRadio(info.value)))
        .append(row("Max gas", info.gas)).append(row("Gas price", info.gasPrice));
    if(info.txReceipt) {
        display.append(row("Gas used", info.gasUsed));       
    }
    return display;
}

function readSuccess(form, displayFn) {
    return function(response) {
        console.log("Success");
        console.log(response);

        var data = JSON.parse(response);
        var resultDiv = form.parent().find(".read_result");
        if("errors" in data) {
            resultDiv.html(data.errors[0]);
        } else {
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
        if(jqXHR.indexOf("The CSRF token has expired") !== -1) {

            form.parent().find(".read_result").html("Session timed out, reload the page.");
        } else {
            form.parent().find(".read_result").html("Server error");
        }
    }
}

function make_read_form(name, displayFn) {
    $("#"+name).submit(function(event) {
        form = $("#"+name);
        event.preventDefault();
        $.post("/api/"+name+"/", form.serialize())
            .done(readSuccess(form, displayFn)).fail(readFail(form));      
    });
}

$(document).ready(function() {
    console.log("HELLO");

    make_read_form("transaction", transactionDisplay);
    make_read_form("account", accountDisplay);
    
});