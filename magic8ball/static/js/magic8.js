

const ContractABI = [{"constant":true,"inputs":[],"name":"tithe","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"anonymous":false,"inputs":[{"indexed":false,"name":"answer","type":"string"}],"name":"AnswerEvent","type":"event"},{"constant":false,"inputs":[{"name":"question","type":"string"}],"name":"askQuestion","outputs":[{"name":"","type":"string"}],"payable":true,"stateMutability":"payable","type":"function"},{"constant":false,"inputs":[],"name":"kill","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_tithe","type":"uint256"}],"name":"setTithe","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_wizard","type":"address"}],"name":"setWizard","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[{"name":"_tithe","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"}];
var contract = null;
var tithe = null;
var questionTime = null;
var questionHash = null;
var pendingPollId = null;
var pending = false;

var testCallback = function(error, result) { console.log(error+" "+result);};

function questionDisplay(info) {
    console.log(info);
    return $('<table>').append(row("Question sent", info.answer));
}

function confirmNewQuestion(callback) {
    vex.dialog.confirm({
        message: 'You have a pending question, do you want to ask another? The old one will appear in the history once answered.',
        callback: callback
    })
}

function askQuestion(account, question, tithe) {
    console.log(""+tithe+" Asking "+question+" for "+account)
    $(".read_result").text("Asking the Magic 8 ball...");
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

function questionAsked(tx_hash) {
    pending = true;
    $(".read_result").text("The Magic 8 Ball is thinking...");
    questionTime = Date.now();
    questionHash = tx_hash;
    pendingPollId = setTimeout(checkAnswer, 2000);
}

function checkAnswer() {
    $.post("/magic8ball/api/answer/", {"tx_hash": questionHash})
        .done(function(response) {
            var data = JSON.parse(response);
            if("errors" in data) {
                console.log(response);
                showResult("There was a problem checking your answer :(\nCome back later and find it in the history.");

            } else if(data.pending) {

                pendingPollId = setTimeout(checkAnswer, 2000);

            } else if(data.result.data.status != "success") {
                showResult('Magic 8 Ball rejected your question!\nTry again with higher gas price or ether value.');

            } else {
                showResult('Magic 8 Ball says: "'+data.result.data.answer+'"');
            }
        }).fail(function(jqXHR, textStatus, errorThrown) {
            console.log(jqXHR);
            showResult("There was a problem checking your answer :(\nCome back later and find it in the history.");
        });
}

function showResult(text) {
    pending = false;
    $(".read_result").text(text);
}

$(document).ready(function() {
    vex.defaultOptions.className = 'vex-theme-wireframe';

    w3 = getWeb3js();
    ContractDef = web3.eth.contract(ContractABI);
    w3.eth.net.getId((err, netId) => {
        
        switch (netId) {
        case 1:
            $("#network").text("Main network");
            break;
        case 3:
            $("#network").text("Ropsten test network");
            break;
        case 8178:
            $("#network").text("Podo test network");
            contract = ContractDef.at(podoTestInfo['contract_hash']);
            console.log(contract);
            break;
        default:
            $("#network").text("Unknown network");
            break;
        }
        if(contract) {
            contract.tithe((err, result) => {
                console.log(err+" "+result);
                tithe = parseInt(result)+1;
                if(!err) {
                    $("#cost").text(" for "+tithe+" wei");
                }
            });
        }
    });

    $("#ball").click(function() {
        $("#ball_inner").addClass("rotate");
    });
    $("#ball_inner").on(
        "webkitAnimationEnd oanimationend msAnimationEnd animationend",
        function() {
            $("#ball_inner").removeClass("rotate");
        }
    );

    $("#question").submit(function(event) {
        console.log("Questioning..."+contract+" "+w3.eth.accounts.length);
        form = $("#question");
        event.preventDefault();
        var question = $("[name=question]").val();

        if(contract && tithe !== null) {
            w3.eth.getCoinbase(function(error, result) {
                
                if(error) {
                    console.log(error);
                    $(".read_result").text("Error accessing account!");
                    return;
                }
                if(pending) {
                    
                    confirmNewQuestion(function(yes) {
                        if(yes) {
                            askQuestion(result, question, tithe);
                        }
                    });
                    
                } else {
                    askQuestion(result, question, tithe);
                }
            });
        }
    });
});