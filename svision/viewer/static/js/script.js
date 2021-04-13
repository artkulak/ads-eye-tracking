// start recording

window.saveDataAcrossSessions = true;

function recordGaze() { //.setTracker("TFFacemesh")
    var start = new Date().getTime();
    webgazer.setRegression('ridge').setGazeListener(function (data, elapsedTime) {
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
            'width':  $(window).width(),
            'height': $(window).height(),
            'time': end-start,
        },
        dataType: 'json',
        success: function (data) {
            console.log('point sent');
        }
        });

    }).showPredictionPoints(true).begin();

}

// exporting data to .csv file
function saveGaze() {
    webgazer.pause();
    $.ajax({
        url: '/export_stats',
        data: {
            'heatmap': true,
            'emotions': true
        },
        dataType: 'json',
        beforeSend: function(){
            swal({
                title: "Preparing data...",
                text: "Please wait",
                buttons: false
              });
        },

        success: function (data) {
            const button = document.createElement('div');
            button.innerHTML = '<a href="' + archieve_path + '" download>Download archieve</a><div id="plotly_graph_1"></div><div id="plotly_graph_2"></div>';  

            swal({
              title: 'Download archieve',
              content: button,
              // closeOnEsc: false,
              // allowOutsideClick: false,
              // closeModal: true
            }).then( isConfirm => {
              sleep(500).then(() => {
                // window.location.replace("/");
              })
            });   
            plotly_graph_1 = JSON.parse(data['plotly_graph_1'])
            plotly_graph_2 = JSON.parse(data['plotly_graph_2'])
            Plotly.react('plotly_graph_1', plotly_graph_1.data, plotly_graph_1.layout);
            Plotly.react('plotly_graph_2', plotly_graph_2.data, plotly_graph_2.layout);
        }
        });
}

function skipCalibration(){
    webgazer.pause();
    $(".Calibration").hide();
    // clears the canvas
    var canvas = document.getElementById("plotting_canvas");
    canvas.width=0;
    canvas.height=0;
}


window.onbeforeunload = function() {
    webgazer.end();
}
