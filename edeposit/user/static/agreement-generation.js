(function($) {
        var checkGenerationState = function (base_href, numOfRetries) {
                if( numOfRetries <= 0 ) return;
                var handler = function(){
                        $.ajax(base_href + "/has-agreement").done(function(data){
                                if( data.has_agreement ){
                                        $('#formfield-form-widgets-agreement').html(
                                                data['agreement_widget_html']
                                        );
                                        $('.agreement-download')[0].click();
                                } else {
                                        checkGenerationState(base_href, numOfRetries - 1);
                                };
                                
                        });
                };
                setTimeout(handler,1000);
        };
        var submitGeneration = function(event){
                event.preventDefault();
                var href = $(this).attr('href');
                var base_href = href.replace(/\/generate-agreement$/,'')
                var element = $(this);
                $.ajax(href).done(function(data){
                        $(element).hide();
                        $('.agreement-is-generating').fadeIn();
                        $('.not-agreement-spinner').fadeIn();
                        checkGenerationState(base_href,20);
                });
                return false;
        };

        $(function(){
                $(".generate-agreement").click(submitGeneration);
        });
})(jQuery);
