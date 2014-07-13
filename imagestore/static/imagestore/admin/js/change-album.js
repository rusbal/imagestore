(function($){$(function(){
    var thumbs;
    /**
     * Load imagestore thumbnails
     */
    $.get('/gallery/thumbs/', function(result){
        if (result.success) {
            thumbs = result.thumbs;
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

    /**
     * On page load, hide input
     */
    $('tr.dynamic-albumimage_set').find('.field-mediafile input').empty();
});})(django.jQuery);
