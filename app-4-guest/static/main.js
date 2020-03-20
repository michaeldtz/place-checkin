
$(document).ready(function(){

    function init(){
        var guestUid = document.cookie;
        console.log(document.cookie)
        if(guestUid == ""){
            currentSite = window.location.hash.slice(1)
            if (currentSite == "qrcode"){
                currentSite = "home"
                window.location.hash = "#" + currentSite
            }
            
            switchSite(currentSite)
        } else {
            $("#qrcodenavlink").removeClass("inactive")
            $("#qrcodeimg").attr("/qrcode?guestUid=" + guestUid)
            window.location.hash = "#qrcode" 
            switchSite("qrcode")
        }

        fetch("/getconfig", {})
            .then(function(response) {
                return response.json();
            }).then(function(data) {
                if(data.success == true){
                    $("#linkImpressum").attr("href",data.config.linkImpressum);
                    $("#linkDPInfo").attr("href",data.config.linkDPInfo);
                    
                    $(".brandcolor-topborder").css("border-top","7px solid " + data.config.brandColor);
                    $(".btn-primary").css("background-color",data.config.brandColor);
                    $(".btn-primary").css("border-color",data.config.brandColor);
                    $("#headerIcon").attr("src",data.config.headerIcon);   
                }
            });
    }

    function switchSite(site){
        if (site == "")
            site = "home"
    
        $(".site").addClass("inactive"); 
        $("#" + site).removeClass("inactive"); 
    }

    $(window).bind('hashchange', function () { //detect hash change
        var site = window.location.hash.slice(1); //hash to string (= "myanchor")
        switchSite(site)    
    });
    
    $("ul.nav li").click(function() { 
        $("li").removeClass("active"); 
        $(this).addClass("active"); 
    }); 

    $("#submitSignup").click(() => {

        var signupRequest = {
            guest : {
                name            : $("#inputName").val(),
                address         : $("#inputAddress").val(),
                zip             : $("#inputZip").val(),
                city            : $("#inputCity").val(),
                country         : $("#inputCountry").val(),
                phone           : $("#inputPhone").val(),
                email           : $("#inputEmail").val(),
                confirmedDPS    : $("#confirmedDPS").is(":checked") ? true : false
            }
        } 
        
        checkResult = checkInput(signupRequest)
        if(checkResult.success == true){
            $("#signuperror").text("");
            fetch("/guest/signup", {
                method: 'POST',
                headers : {"content-type": "application/json"},
                body: JSON.stringify(signupRequest)
            }).then(function(response) {
                return response.json();
            }).then(function(data) {
                if(data.success){
                    document.cookie = "guestuid=" + data.guestUid + "; expires=0; path=/";
                    $("#qrcodeimg").attr(data.qrCodeURL)
                    window.location.hash = "#qrcode"      
                } else {
                    $("#signuperror").text(data.message)
                }
            });
        } else {
            $("#signuperror").text(checkResult.message)
        }
    });

    function checkInput(request){

        errorMessage = ""
        success = true

        for (name in request.guest){
            if (name == "confirmedDPS")
                continue;
            if (request.guest[name] == ""){
                success = false
                errorMessage = "Bitte erfassen Sie alle Daten. Siehe rote Markierung der fehlenden Felder."
                $("#input" + name.slice(0,1).toUpperCase() + name.slice(1)).addClass("bg-danger-border")
            }
        }

        if (success == true){
            if (request.guest.confirmedDPS != true){
                success = false;
                errorMessage = "Bitte bestätigen Sie die Datenschutz-Richtlinien.";
            }
        }

        return {
            success : success,
            message : errorMessage
        }

    }
    init();
    
});