w3 = new Web3();
Buffer = ethereumjs.Buffer.Buffer;

function balanceDisplay(info) {
    console.log(info);
    return $('<table>').append(row("Coins", info.balance));
}

function sendDisplay(info) {
    console.log(info);
    return $('<table>').append(row("Transaction sent", info.tx_id));
}

function makeTransaction(sender, sender_key, receiver, nonce, amount) {

    var data = w3.eth.abi.encodeFunctionCall({
		"inputs": [
			{   "name": "receiver",
			    "type": "address"
            },
            {   "name": "amount",
				"type": "uint256"
			}
		],
		"name": "send",
		"type": "function"
    }, [strip_hex(receiver), amount]);

    var rawTx = {
        nonce: '0x'+nonce.toString(16),
        gasPrice: '0xB', 
        gasLimit: '0xC634',
        to: "0x16dF1321541Db03Fc2f1AA071ae8f73F1180b774", 
        value: '0x00', 
        data: data
    }
      
    var tx = new ethereumjs.Tx(rawTx);
    tx.sign(new Buffer(sender_key, 'hex'));
    
    return tx.serialize().toString('hex');
}

function sendTransaction(info) {
    console.log(info);
    form = $("#send");
    var sender = $("[name=id]").val();
    var sender_key = $("[name=key]").val();
    var receiver = $("[name=receiver]").val();
    var nonce = info.tx_count + info.tx_pending;
    var amount = parseInt($("[name=amount]").val());
    
    if(sender_key.length == 0) {
        showError(form, "Private key required.");
    } else {
        var tx = makeTransaction(sender, sender_key, receiver, nonce, amount);
        $.post(form.attr("action"), {"tx_data": tx})
            .done(readSuccess(form, sendDisplay)).fail(readFail(form));
    }
}

$(document).ready(function() {

    //x.substr(2, x.length)

    make_form("#balance", balanceDisplay);

    $("#send").submit(function(event) {
        form = $("#send");
        event.preventDefault();
        var sender = $("[name=id]").val();
        $.post("/api/account/", {"id": sender})
            .done(readSuccess(form, sendTransaction)).fail(readFail(form));
    });
    
});