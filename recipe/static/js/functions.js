new WOW().init();

jQuery(document).ready(function(){ 
    jQuery('.benefit__item-bottom').matchHeight();
    jQuery('.team__name').matchHeight();
    jQuery('.team__position').matchHeight();    

    let idBtnUp = 'scroll_up';
    jQuery(window).scroll(function() {
      if(jQuery(this).scrollTop() > 400) {
        jQuery('#'+idBtnUp).fadeIn(500);
      } else {
        jQuery('#'+idBtnUp).fadeOut(500);
      }

      if( jQuery(window).width() < 992 ) {
        jQuery('.header').addClass('position-sticky');
      }
    });
    jQuery('#'+idBtnUp).click(function() {
      jQuery('body,html').animate({scrollTop:0},800);
    });

    jQuery('.whatis__item-more').click(function(){ 
    	let item = jQuery(this).parents('.whatis__item');
    	let title = item.find('.whatis__item-title').text();
    	let text = item.find('.whatis__item-content').html();
    	let modal = jQuery('#modal-whatis');

    	modal.find('.modal-title').text(title);
    	modal.find('.modal-body').html(text);
    	modal.modal('show');
    }); 

    jQuery('.header__btn').click(function(){ 
      jQuery(this).toggleClass('opened');
      jQuery('.header__menu').fadeToggle();
    });   
}); 