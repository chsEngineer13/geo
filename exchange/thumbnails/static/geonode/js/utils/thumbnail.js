/*
 * Create a thumbnal based on the center of an OL3 
 * map canvas.
 */

var getThumbnailPathFromUrl = function() {
    // determine the object type and id from the URL 
    var path_info = window.location.pathname.split('/').slice(-2)

    // put it together in a URL
    return '/thumbnails/' + path_info[0] + '/' + path_info[1];
}

var createMapThumbnail = function() {
    var canvas = $('.ol-viewport canvas');

    // first, calculate the center 'thumbnail'
    //   of the image.
    var thumb_w = 240, thumb_h = 180;
    var w = canvas.width(), h = canvas.height();
    var c_x = w/2, c_y = h/2;
    var x0 = c_x - thumb_w/2;
    var y0 = c_y - thumb_h/2;

    // then get the thumbnail from the image itself.
    var clip = canvas[0].getContext('2d').getImageData(x0,y0,thumb_w,thumb_h);

    // create a temporary canvas for the 
    //  new thumbnail.
    var thumb_canvas = $('<canvas>').appendTo('body');
    thumb_canvas[0].width = thumb_w;
    thumb_canvas[0].height = thumb_h;
    thumb_canvas[0].getContext('2d').putImageData(clip,0,0);

    // get the PNG for saving...
    var png_data = thumb_canvas[0].toDataURL('image/png');

    // and remove the element from the DOM.
    thumb_canvas.remove();

    var url = getThumbnailPathFromUrl();

    $.ajax({
        type: "POST",
        url: url,
        data: png_data,
        success: function(data, status, jqXHR) {
            return true;
        }
    });
    return true;
}
