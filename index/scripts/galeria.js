$(document).ready( function() {

          $('img').mouseover(function(){
          $(this).width(600).height(400)     
            });

          $('img').mouseout(function(){

               $(this).width(300).height(200)

            });
          $("img[rel]").overlay();
        });