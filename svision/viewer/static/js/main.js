var calibrated = false;
var start = '';
window.onload = async function() {

    webgazer.params.showVideoPreview = true;
    await faceapi.nets.ssdMobilenetv1.loadFromUri('../static/models');
    await faceapi.nets.faceExpressionNet.loadFromUri('../static/models');
    await faceapi.nets.faceLandmark68Net.loadFromUri('../static/models');
    //start the webgazer tracker
    webgazer.setRegression('ridge') /* currently must set regression and tracker */
        //.setTracker('clmtrackr')
        .setGazeListener(async function(data, clock) {

            const canvas = webgazer.getVideoElementCanvas();
            image_src = canvas.toDataURL("image/png");
            var img = new Image(640, 480);
            img.src = image_src


            const results = await faceapi.detectAllFaces(img,  new faceapi.SsdMobilenetv1Options({ minConfidence: 0.6 })).withFaceLandmarks().withFaceExpressions();


            
            if (results.length>0){
                expressions = results[0]['expressions'];
            } else {
                expressions = [];
            }
            
            keywords = ['angry', 'disgusted', 'fearful', 'happy', 'neutral', 'sad', 'surprised'];
            expression_scores = []
            for (var i = 0; i < keywords.length; i++){
                expression_scores.push(expressions[keywords[i]])
            }

            if (calibrated){
                if (data == null) {
                    return;
                }
                // send points via ajax to python backend
                var end = new Date().getTime();
        
                $.ajax({
                url: '/recieve_points',
                data: {
                    'x': data.x,
                    'y': data.y,
                    'username': username,
                    'expressions': expression_scores.join(';'),
                    'width':  $(window).width(),
                    'height': $(window).height(),
                    'time': end-start,
                },
                dataType: 'json',
                success: function (data) {
                    console.log('point sent');
                }
                });
            }
          //   console.log(data); /* data is an object containing an x and y key which are the x and y prediction coordinates (no bounds limiting) */
          //   console.log(clock); /* elapsed time in milliseconds since webgazer.begin() was called */
        }).begin();
        webgazer.showVideoPreview(true) /* shows all video previews */
            .showPredictionPoints(true) /* shows a square every 100 milliseconds where current prediction is */
            .applyKalmanFilter(true); /* Kalman Filter defaults to on. Can be toggled by user. */

    //Set up the webgazer video feedback.
    var setup = function() {

        //Set up the main canvas. The main canvas is used to calibrate the webgazer.
        var canvas = document.getElementById("plotting_canvas");
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        canvas.style.position = 'fixed';
    };
    setup();

};

// Set to true if you want to save the data even if you reload the page.
window.saveDataAcrossSessions = true;

window.onbeforeunload = function() {
    webgazer.end();
}

/**
 * Restart the calibration process by clearing the local storage and reseting the calibration point
 */
function Restart(){
    //document.getElementById("Accuracy").innerHTML = "<a>Not yet Calibrated</a>";
    webgazer.clearData();
    ClearCalibration();
    PopUpInstruction();
}
