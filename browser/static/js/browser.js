

function accountDisplay(info) {
    console.log(info);
    var wei = info.balance;
    return $('<table>').append(row("Balance", etherRadio(wei)))
                    .append(row("Transactions", info.tx_count));
}

function transactionDisplay(info) {
    var to = (info.to === null) ? "New Contract" : info.to;

    var display = $('<table>').append(row("Block", "#"+info.blockNumber+" "+info.blockHash))
        .append(row("From", info.from)).append(row("To", to)).append(row("Value", etherRadio(info.value)))
        .append(row("Max gas", info.gas)).append(row("Gas price", info.gasPrice));
    if(info.txReceipt) {
        display.append(row("Gas used", info.gasUsed));       
    }
    return display;
}

$(document).ready(function() {

    make_form("#transaction", transactionDisplay);
    make_form("#account", accountDisplay);
    
});