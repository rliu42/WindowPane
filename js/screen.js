var root = new Firebase("https://window-pane.firebaseio.com");
var FRAME_WIDTH;
var FRAME_HEIGHT;
var id = -1;
var update = false;
var image = new Image();
var state;
image.src = "http://wallpapercave.com/wp/4JKHi7a.jpg";

root.once("value", function(ss) {
    resize_canvas()
    FRAME_WIDTH = ss.val().FRAME_WIDTH
    FRAME_HEIGHT = ss.val().FRAME_HEIGHT
    var screens = ss.val()["screens"] || [];
    var r = confirm("Join this map?");
    if (r == true) {
        console.log(screens)
        id = screens.length;
        alert(id)
        screens.push({
            center: {
                x: -1,
                y: -1
            },
            dims: {
                h: -1,
                w: -1
            },
            rotation: 0
        });
        root.child("screens").update(screens);
        update = true
        root.child("screens").child(id).on("value", function(ss) {
            if (update) {
                state = ss.val();
                updateCanvas(state)
            }
        });
    }
});

function updateCanvas(screen) {
    x = screen.center.x
    y = screen.center.y
    w = screen.dims.w
    h = screen.dims.h
    r = screen.rotation
    canvas = document.getElementById("colors_sketch");
    //TEMP CODE need firebase to get dimensions of full image
    imgW = image.width;
    imgH = image.height;

    topLeftX = (x-w/2)/FRAME_WIDTH*imgW;
    topLeftY= (y+h/2)/FRAME_HEIGHT*imgH;
    context = canvas.getContext("2d");
    context.clearRect(0,0,canvas.width, canvas.height);
    context.drawImage(image, topLeftX, topLeftY, w/FRAME_WIDTH*imgW, h/FRAME_HEIGHT*imgH, 0, 0, canvas.width, canvas.height);
}
