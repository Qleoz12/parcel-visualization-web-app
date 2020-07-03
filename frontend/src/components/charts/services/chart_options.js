export default {
    generateChartOptionsBar(labelName, maintainAspectRatio=false) {
        return {
            scales: {
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: labelName
                    },
                    stacked: false,
                    ticks: {
                        beginAtZero: true
                    },
                }],
                xAxes: [{
                    stacked: false,
                    ticks: {
                        beginAtZero: true
                    },
                }],
            },
            reactive: true,
            maintainAspectRatio: maintainAspectRatio,
        };
    },
    generateChartOptionsLine(xName, yName, stepX=1, stepY=1, suggestedMinX=0, suggestedMinY=0, maintainAspectRatio=false){
        return {
            scales: {
                yAxes: [{
                    type: 'linear',
                    scaleLabel: {
                        display: true,
                        labelString: yName
                    },
                    stacked: false,
                    ticks: {
                        suggestedMin: suggestedMinY,
                        stepSize: stepY
                    },
                }],
                xAxes: [{
                    type: 'linear',
                    scaleLabel: {
                        display: true,
                        labelString: xName
                    },
                    stacked: false,
                    ticks: {
                        suggestedMin: suggestedMinX,
                        stepSize: stepX
                    },
                }],
            },
            reactive: true,
            maintainAspectRatio: maintainAspectRatio,
        }
    }
}