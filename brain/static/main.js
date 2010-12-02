$(document).ready(function() {
    /*
    $('.blob').hover(
        function(){
            $.getJSON('/id/'+this.id, function(data){
                $('#detail').html('<pre>'+data.content+'</pre>');
				$('#detail').show('fast');
            });
        },
        function(){
            $('#detail').hide('fast');
        }
    );
    */
    $('.blob').click(function(){
//        location.href='/edit/'+this.id;
        $.getJSON('/id/'+this.id, function(data){
            $('#detail').html('<pre>'+data.content+'</pre>');
//             $('#detail').show('fast');
        });
    });

    $("#main").fadeIn('slow');
//     $("#main").show();
//     $(".login").hover(function() {
//         $("#logdrop").show('fast');
//     },function(){
//         $("#logdrop").hide('fast');
//     });
});
