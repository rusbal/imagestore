(function($){$(function(){
    var thumbs;
    var n = $('select#id_user option').size();
    if (n <= 2) {
        $('select#id_user option:last').attr('selected', 'selected');
    }

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
                if (image === "") {
                    $(this).parent().append('<img src="" style="visibility:hidden"/>');
                } else {
                    $(this).parent().append('<img src="'+thumbs[image]+'"/>');
                }
                $(this).remove();
            });
        }
    }, 'json');

    function img_to_td(img, td){
        if (td.is(':empty')) {
            /**
             * New image
             */
            td.append('<img src="'+img+'"/>');
        } else {
            /**
             * Update old image
             */
            td.children('img').attr('src', img);
        }
    }

    $('select[id^="id_albumimage_set-"]').change(function(){
        var td = $(this).parents('tr').children('td.field-mediafile');
        if (this.value) {
            if (this.value in thumbs) {
                img_to_td(thumbs[this.value], td);
                td.children('img').css('visibility', 'visible');
            } else {
                /**
                 * Get new value of thumbs
                 */
                var thumb_key = this.value;
                $.get('/gallery/thumbs/', function(result){
                    if (result.success) {
                        thumbs = result.thumbs;
                        img_to_td(thumbs[thumb_key], td);
                        td.children('img').css('visibility', 'visible');
                    }
                }, 'json');
            }
        } else {
            td.children('img').css('visibility', 'hidden');
        }
    });

    $('tr.add-row a').click(function(){
        /**
         * Hide input
         */
        $('tr.dynamic-albumimage_set').last().children('.field-mediafile').empty();
    });
});})(django.jQuery);
