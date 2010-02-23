(function($) {
    
    $.fn.vDropDownMenu = function(target, opts) {
        var options = $.extend({'leftOffset': 0,
                                'topOffset': 0}, opts);

        $('body').click(function(){
            $target.hide();
        });
        
        var $target = $(target);
        $target.hide();
        $target.css({'position': 'absolute'});
        $target.addClass('vDropDownMenu');
        
        return this.each(function(){
            var $self = $(this);

            $self.click(function(e){
                e.preventDefault();
                e.stopPropagation();
                
                $target.css({
                    'left': $self.position().left + options.leftOffset + 'px',
                    'top': $self.position().top + $self.height() + options.topOffset + 'px',
                });

                $target.toggle();
            });
        });
    };
    
})(jQuery);