(function($){$(function(){
    var thumbs;
    /**
     * Load imagestore thumbnails
     */
    $.get('/gallery/thumbs/', function(result){
        if (result.success) {
            thumbs = result.thumbs;

            /**
             * On page load, show images
             * This solves the problem of the images not showing when an error
             * (duplicate image) occured.
             */
            $('tr.dynamic-albumimage_set').children('.field-mediafile').children('input').each(function(index){
                image = $(this).parent().siblings('.field-image').children('select').val();
                $(this).parent().append('<img src="'+thumbs[image]+'"/>');
                $(this).remove();
            });
        }
    }, 'json');

    $('select[id^="id_albumimage_set-"]').change(function(){
        var td = $(this).parents('tr').children('td.field-mediafile');
        if (td.is(':empty')) {
            /**
             * New image
             */
            td.append('<img src="'+thumbs[this.value]+'"/>');
        } else {
            /**
             * Update old image
             */
            td.children('img').attr('src', thumbs[this.value]);
        }
    });

    $('tr.add-row').click(function(){
        /**
         * Hide input
         */
        $('tr.dynamic-albumimage_set').last().children('.field-mediafile').empty();
    });
});})(django.jQuery);
