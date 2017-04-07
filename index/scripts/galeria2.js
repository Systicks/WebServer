
    $(document).ready( function() {
      var num=0
          $('img').click(function(){
            if( $(this).prop("class") == "arrowleft" || $(this).prop("class") == "arrowright" ) 
              {return}//para no mostrar la imagen de las flechas
              $("#imagen").prop("src", this.src)
              $("img").css("border-color", "black")
              $(this).css("border-color", "blue")
            });

          $('.arrowright').click(function(){
            var x
            if(num<=7)
            {
              num = num+1
              x = "#img" + num
              $(x).hide(200)
            }
            });
          $('.arrowleft').click(function(){
            var x
            x = "#img" + num
            $(x).show(200)
            if(num>=1)
              num=num-1
            });
          $('.arrowright').mouseover(function(){
            $(".arrowright").animate({
            opacity: '0.7', width:"200%", height: "30%"
            });

          });
          $('.arrowright').mouseout(function(){
            $(".arrowright").animate({
            opacity: '1', width:"20px", height: "40px"
            });
          });
          $('.arrowleft').mouseover(function(){
            $(".arrowleft").animate({
            opacity: '0.7'
            });
          });
          $('.arrowleft').mouseout(function(){
            $(".arrowleft").animate({
            opacity: '1', width:"20px", height: "40px"
            });
          });
          
          $("img[title]").tooltip();

        });