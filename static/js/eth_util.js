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
        if(jqXHR.responseText.indexOf("The CSRF token has expired") !== -1) {

            form.parent().find(".read_result").html("Session timed out, reload the page.");
        } else {
            form.parent().find(".read_result").html("Server error");
        }
    }
}

function make_form(form_id, displayFn) {
    $(form_id).submit(function(event) {
        form = $(form_id);
        event.preventDefault();
        $.post(form.attr("action"), form.serialize())
            .done(readSuccess(form, displayFn)).fail(readFail(form));      
    });
}