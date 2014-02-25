jQuery.fn.edepositRegistration = function(){
	var producent_fields = Array(
		'#formfield-form-widgets-producent-title',
		'#formfield-form-widgets-producent-home_page',
		'#formfield-form-widgets-producent-location',
		'#formfield-form-widgets-producent-contact',
		'#formfield-form-widgets-producent-agreement',
		'#formfield-form-widgets-producent-street',
		'#formfield-form-widgets-producent-city',
		'#formfield-form-widgets-producent-country'
	);
	var producent_fieldsets = Array(
		'#fieldset-3',
		'#fieldset-4'
	);
	var producent_fieldset_legends = Array(
		'#fieldsetlegend-3',
		'#fieldsetlegend-4'
	);
	return this.each(function(){
		var edepositRegistration = jQuery(this);
		edepositRegistration.find('#form-widgets-producent-new_producent-0').each(function(){
			this.checkNewProducent = function () {
				if( jQuery(this).attr('checked') ){
					edepositRegistration.find('#formfield-form-widgets-producent').hide();
					jQuery.each(producent_fields, function(index,value){
						edepositRegistration.find(value).fadeIn();
					});
					jQuery.each(producent_fieldset_legends, function(index,value){
						edepositRegistration.find(value).addClass('required');
					});
					jQuery.each(producent_fieldsets, function(index,value){
						edepositRegistration.find(value).find('label span.required').fadeIn();
					});
				} else {
					edepositRegistration.find('#formfield-form-widgets-producent').fadeIn();
					jQuery.each(producent_fields, function(index,value){
						edepositRegistration.find(value).fadeOut().hide(); // pro pripad, ze neni element videt. 
					});
					jQuery.each(producent_fieldset_legends, function(index,value){
						edepositRegistration.find(value).removeClass('required');
					});
					jQuery.each(producent_fieldsets, function(index,value){
						edepositRegistration.find(value).find('label span.required').fadeOut().hide();
					});
				};
				return this;
			};
			jQuery(this).change(this.checkNewProducent);
			this.checkNewProducent();
		});
		return this;
	});
};

jQuery.fn.edepositRegistrationFormTabsHandler = function(){
	return this.each(function(){
		var form = jQuery(this);
                var fieldsetsWithEmptyRequiredFields = function() {
                        var fieldsets = form.find("fieldset");
                        return fieldsets;
                };
                form.registerButton = form.find('#form-buttons-register');
                form.continueRegistrationButton = form.find('#form-button-continueregistration')
		return this;
	});
};

jQuery.fn.edepositFormLegends = function(){
	return this.each(function(){
		var form = jQuery(this);
                var infoText = "ⓘ";
                form.find('span.formHelp').each(function(index){
                        var help = jQuery(this);
                        help.attr('title',help.html());
                        help.html(infoText);
                        help.addClass('with-tooltip');
                        help.removeClass('formHelp');
                });
		return this;
	});
};

jQuery.fn.edepositFormLoadStyle = function(){
	return this.each(function(){
		var form = jQuery(this);
                if( form.attr('action').contains('++add++edeposit.content.epublication')){
                        $('head').append('<link rel="stylesheet" href="http://www.janprucha.cz/edeposit-registration.css" type="text/css" />');
                };
		return this;
	});
};


jQuery(document).ready(function() {
        $("#form").edepositRegistrationFormTabsHandler()
                .edepositFormLegends()
                .edepositFormLoadStyle();
        
	// No overlays for IE6
	// if (!jQuery.browser.msie || parseInt(jQuery.browser.version, 10) >= 7) {
	// 	// Set up overlays
	// 	$("a#personaltools-join").prepOverlay({
	// 		subtype: 'ajax',
	// 		filter: 'div.edeposit-user-registration',
	// 		formselector: 'form',
	// 		noform: 'close',
	// 	});
	// }
});
