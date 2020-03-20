
$(document).ready(function(){

    function init(){
        
        switchSite(window.location.hash.slice(1));

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

  
    init();
    
});