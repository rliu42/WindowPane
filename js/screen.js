// var root = new Firebase("https://window-pane.firebaseio.com");
FRAME_WIDTH = 640;
FRAME_HEIGHT = 480;
// var id = -1;
// var update = false;
// var image = new Image();
// var state;
// var r = confirm("Join this map?");
//
// if (r == true) {
//     root.once("value", function(ss) {
//         resize_canvas()
//         image.src = ss.val().IMAGE || "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Civil_and_Naval_Ensign_of_France.svg/2000px-Civil_and_Naval_Ensign_of_France.svg.png";
//         FRAME_WIDTH = ss.val().FRAME_WIDTH
//         FRAME_HEIGHT = ss.val().FRAME_HEIGHT
//         var screens = ss.val()["screens"] || [];
//         id = screens.length;
//         alert(id)
//         screens.push({
//             center: {
//                 x: -1,
//                 y: -1
//             },
//             dims: {
//                 h: -1,
//                 w: -1
//             },
//             rotation: 0
//         });
//         root.child("screens").update(screens);
//         update = true
//         root.child("screens").child(id).on("value", function(ss) {
//             if (update) {
//                 state = ss.val();
//                 updateCanvas(state);
//             }
//         });
//
//     });
// }

function globalToLocal(action) {
    // x = screen.center.x
    // y = screen.center.y
    // w = screen.dims.w
    // h = screen.dims.h
    // r = screen.rotation

    x = 320;
    y = 240;
    w = 320;
    h = 240;
    r = 0;

    masterCanvasWidth = 800;
    masterCanvasHeight = 300;

    canvasWidth = $('#colors_sketch')[0].width;
    canvasHeight = $('#colors_sketch')[0].height;


    // canvas = document.getElementById("colors_sketch");
    //TEMP CODE need firebase to get dimensions of full image
    // imgW = image.width;
    // imgH = image.height;

    topLeftXPercent = (x - w / 2)/FRAME_WIDTH;
    topLeftYPercent = (y - h / 2)/FRAME_HEIGHT;

    // console.log(action);

    $.each(action.events, function(i, event) {
        event.x = ((event.x/masterCanvasWidth - topLeftXPercent)*(FRAME_WIDTH/w))*canvasWidth;
        event.y = ((event.y/masterCanvasHeight - topLeftYPercent)*(FRAME_HEIGHT/h))*canvasHeight;
    });
    // context = canvas.getContext("2d");
    // context.clearRect(0, 0, canvas.width, canvas.height);
    //context.rotate(r)
    // context.drawImage(image, topLeftX, topLeftY, w / FRAME_WIDTH * imgW, h / FRAME_HEIGHT * imgH, 0, 0, canvas.width, canvas.height);

    // console.log(action);
    action.isOld = true;
    return action;
}

function localToGlobal(action) {
    x = 320;
    y = 240;
    w = 320;
    h = 240;
    r = 0;

    masterCanvasWidth = 800;
    masterCanvasHeight = 300;

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
