var root = new Firebase("https://window-pane.firebaseio.com");
var FRAME_WIDTH;
var FRAME_HEIGHT;
var id = -1;
var update = false;

root.once("value", function(ss) {
    FRAME_WIDTH = ss.val().FRAME_WIDTH
    FRAME_HEIGHT = ss.val().FRAMEHEIGHT
    var screens = ss.val()["screens"] || [];
    alert(screens)
    var r = confirm("Join this map?");
    if (r == true) {
        id = screens.length();
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
                alert(ss.val())
            }
        });
    }
});
