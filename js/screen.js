var root = new Firebase("https://window-pane.firebaseio.com");
var FRAME_WIDTH;
var FRAME_HEIGHT;
var masterCanvasWidth = 2880;
var masterCanvasHeight = 1519;
var id = -1;
var update = false;
var image = new Image();
var state;
var landscape = window.innerWidth > window.innerHeight;

root.child("IMAGE").on("value", function(ss) {
    image.src = ss.val();
});

$(document).ready(function() {
    var r = confirm("Join this map?");
    if (r == true) {
        root.once("value", function(ss) {
            resize_canvas()
            FRAME_WIDTH = ss.val().FRAME_WIDTH
            FRAME_HEIGHT = ss.val().FRAME_HEIGHT
            var screens = ss.val()["screens"] || [];
            if (ss.val().valid == "yes" && ss.val().RELOAD > 0) {
                id = ss.val().RELOAD;
                root.update({
                    valid: "no"
                })
            } else {
                id = screens.length
                screens.push({
                    innerWidth: window.innerWidth,
                    innerHeight: window.innerHeight,
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
            }
            root.child("screens").update(screens);
            $("#id").html(id)
            update = true
            root.child("screens").child(id).on("value", function(ss) {
                if (update) {
                    state = ss.val();
                    if (state) {
                        updateCanvas(state);
                    } else {
                        id = -1
                    }
                }
            });

        });
    }
});

function reload() {
    if (id > 0) {
        root.update({
            RELOAD: id,
            valid: "yes"
        })
    }
    location.reload(true)
}

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
    topLeftX = (x - w / 2) / (!landscape ? FRAME_WIDTH : FRAME_HEIGHT) * imgW;
    topLeftY = (y - h / 2) / (!landscape ? FRAME_HEIGHT : FRAME_WIDTH) * imgH;
    context = canvas.getContext("2d");
    context.clearRect(0, 0, canvas.width, canvas.height);
    //context.rotate(r)
    context.drawImage(image, topLeftX, topLeftY, w / FRAME_WIDTH * imgW, h / FRAME_HEIGHT * imgH, 0, 0, canvas.width, canvas.height);


}

function globalToLocal(action) {
    x = state.center.x
    y = state.center.y
    w = state.dims.w
    h = state.dims.h
    r = state.rotation
    //set masterCanvasWidth and masterCanvasHeight
    canvasWidth = $('#colors_sketch')[0].width;
    canvasHeight = $('#colors_sketch')[0].height;

    topLeftXPercent = (x - w / 2)/FRAME_WIDTH;
    topLeftYPercent = (y - h / 2)/FRAME_HEIGHT;

    $.each(action.events, function(i, event) {
        event.x = ((event.x/masterCanvasWidth - topLeftXPercent)*(FRAME_WIDTH/w))*canvasWidth;
        event.y = ((event.y/masterCanvasHeight - topLeftYPercent)*(FRAME_HEIGHT/h))*canvasHeight;
    });

    action.isOld = true;
    return action;
}

function localToGlobal(action) {

    x = state.center.x
    y = state.center.y
    w = state.dims.w
    h = state.dims.h
    r = state.rotation
    //set masterCanvasWidth and masterCanvasHeight

    canvasWidth = $('#colors_sketch')[0].width;
    canvasHeight = $('#colors_sketch')[0].height;

    topLeftXPercent = (x - w / 2)/FRAME_WIDTH;
    topLeftYPercent = (y - h / 2)/FRAME_HEIGHT;

    $.each(action.events, function(i, event) {
        event.x = masterCanvasWidth*((event.x/canvasWidth)*(w/FRAME_WIDTH) + topLeftXPercent);
        event.y = masterCanvasHeight*((event.y/canvasHeight)*(h/FRAME_HEIGHT) + topLeftYPercent);
    })

    return action;
}
