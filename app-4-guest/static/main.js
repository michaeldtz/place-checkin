
$(document).ready(function(){

    function init(){
        var guestUid = document.cookie;
        if(guestUid == ""){
            switchSite(window.location.hash.slice(1))
        } else {
            $("#qrcodeimg").attr("/qrcode?guestUid=" + guestUid)
            window.location.hash = "#qrcode" 
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
                name            : "",
                address         : "",
                zip             : "",
                city            : "",
                country         : "",
                phone           : "",
                email           : "",
                confirmedDPS    : true,
                confirmedCorrectness : true
            }
        } 

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
            }
        });
    });

    init();
    
});