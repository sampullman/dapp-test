
function setBrowserSpecific() {
    var agent = navigator.userAgent;

    if(agent.indexOf("Chrome") > -1) {
        $('#mm_chrome').show();

    } else if (agent.indexOf("Opera") > -1) {
        $('#mm_opera').show();

    } else if (agent.indexOf("Firefox") > -1) {
        $('#mm_firefox').show();

    }  else {
        $('#mm_alt').show();

    }
}

function linkTab(link, target) {
    link.on('click', function() {
        $(this).siblings().removeClass('active_link');
        $(this).addClass('active_link');
        var activeTarget = target.parent().find('.active');

        var repeatClick = (activeTarget.length > 0) && $(activeTarget[0]).is(target);

        if(!repeatClick) {
            $(activeTarget[0])[effect2](200, function() {
                target.fadeIn(200);
                target.siblings().removeClass('active');
                target.addClass('active');
            });
        }
    });
}

function linkDropdown(link, target, callback) {
    link.on('click', function() {
        var activeTarget = target.parent().find('.active');

        var repeatClick = (activeTarget.length > 0) && $(activeTarget[0]).is(target);

        if(repeatClick) {
            target.slideUp(200);
            target.removeClass('active');
            link.removeClass('active_link');
            if(callback) callback(link, target, false);
        } else {
            target.slideDown(200);
            target.addClass('active');
            $(this).addClass('active_link');
            if(callback) callback(link, target, true);
        }
    });
}

function linkTabHelper(targetId) {
    linkTab($(targetId + '_link'), $(targetId));
}

function linkDropdowns(dropdowns) {
    $(dropdowns).each(function(i, item) {
        var question = $($(item).find('.question'));
        var answer = $($(item).find('.answer'));
        linkDropdown(question, answer, function(link, target, showing) {
            var symbol = showing ? "-" : "+";
            link.find(".symbol").text(symbol);
        });
    });
}

$(document).ready(function() {

    setBrowserSpecific();

    linkTabHelper('#metamask');
    linkTabHelper('#mist');
    linkTabHelper('#parity');
    linkTabHelper('#myetherwallet');

    linkDropdowns(".question_wrap");

});