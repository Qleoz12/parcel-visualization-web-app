import chart_preprocess from './chart_preprocess';

export default {
  /**
   * Compute the distances for a given algorithm.
   * @param algorithm the algorithm to calculate the distances for.
   */
  computeDistanceData(algorithm) {
    var datasets = []

    chart_preprocess.vehicleIds(algorithm.geojson).forEach((vehicleId) => {
        var data = []
        const route = algorithm.geojson.features.filter(x => x.properties.type === "route" && x.properties.number === (vehicleId))[0];
        data.push(Math.round(route.properties.distance/1000*10)/10);

        var color = chart_preprocess.color(algorithm.geojson, vehicleId);
        datasets.push({"label": "Vehicle " + vehicleId ,"data" : data, "fill": false, backgroundColor: color, borderColor: color});

    });

    return {
      labels: ["Distance"], 
      datasets: datasets
    };
  },
  /**
   * Compute the stop counts for a given algorithm.
   * @param algorithm the algorithm to count the stops from.
   */
  computeStopCountData(algorithm) {
    var datasets = []

    chart_preprocess.vehicleIds(algorithm.geojson).forEach((vehicleId) => {
        var nrOfStops = chart_preprocess.sortStops(algorithm.geojson, vehicleId).length;
        var color = chart_preprocess.color(algorithm.geojson, vehicleId);

        datasets.push({"label": "Vehicle " + vehicleId ,"data" : [nrOfStops], "fill": false, backgroundColor: color, borderColor: color});
    });

    return {
      labels: ["Stop Count"], 
      datasets: datasets
    };
  },
  /**
   * Compute the costs for a given algorithm.
   * @param algorithm the algorithm to calculate the costs for.
   */
  computeCostData(algorithm) {
    var datasets = []

    chart_preprocess.vehicleIds(algorithm.geojson).forEach((vehicleId) => {
      var data = []
      let costs = 0;
      let prevTime = 0;
      chart_preprocess.sortStops(algorithm.geojson, vehicleId).forEach(dlv => {
          costs = chart_preprocess.costs(algorithm.scenario, dlv, costs, prevTime);
          prevTime = dlv.properties.arrival_m + dlv.properties.arrival_h*60;
      });
      data.push(costs);

      var color = chart_preprocess.color(algorithm.geojson, vehicleId)
      datasets.push({"label": "Vehicle " + vehicleId ,"data" : data, "fill": false, backgroundColor: color, borderColor: color});
    });

    return {
      labels: ["Cost"], 
      datasets: datasets
    };
  },
  /**
   * Compute the amount of packages delivered over time for a given algorithm.
   * @param algorithm the algorithm to calculate the amount of packages for.
   */
  computePackagesOverTimeData(algorithm) {
    var datasets = []

    chart_preprocess.vehicleIds(algorithm.geojson).forEach((vehicleId) => {
      var count = 0
      var data = []
      data.push({x: 0, y: 0})
      
      chart_preprocess.sortDeliveries(algorithm.geojson, vehicleId).forEach(dlv => {
        count += 1
        data.push({x: dlv.properties.arrival_m / 60.0 + dlv.properties.arrival_h, y: count})
      });

      var color = chart_preprocess.color(algorithm.geojson, vehicleId)
      datasets.push({"label": "Vehicle " + vehicleId ,"data" : data, "fill": false, backgroundColor: color, borderColor: color});
    });

    return {
      datasets: datasets
    };
  },
  /**
   * Compute the distance driven over time for a given algorithm.
   * @param algorithm the algorithm to calculate the distance for.
   */
  computeDistanceOverTimeData(algorithm) {
    var datasets = [];

    chart_preprocess.vehicleIds(algorithm.geojson).forEach((vehicleId) => {
        var data = [];
        data.push({x: 0, y: 0})
        chart_preprocess.sortDeliveries(algorithm.geojson, vehicleId).forEach(dlv => {
            var distance = dlv.properties.distance/1000;
            data.push({x: dlv.properties.arrival_m / 60.0 + dlv.properties.arrival_h, y: distance})
        });
        const route = algorithm.geojson.features.filter(x => x.properties.type === "route" && x.properties.number === (vehicleId))[0];
        const finalDist = route.properties.distance/1000;
        const finalTime = route.properties.duration_m/60 + route.properties.duration_h;
        data.push({x: finalTime, y: finalDist})
        var color = chart_preprocess.color(algorithm.geojson, vehicleId)
        datasets.push({"label": "Vehicle " + vehicleId ,"data" : data, "fill": false, backgroundColor: color, borderColor: color});
    });

    return {
      datasets: datasets
    };
  },
  /**
   * Compute the costs developed over time for a given algorithm.
   * @param algorithm the algorithm to calculate the costs for.c
   */
  computeCostOverTimeData(algorithm) {
    var datasets = []

    chart_preprocess.vehicleIds(algorithm.geojson).forEach((vehicleId) => {
      var data = []
      data.push({x: 0, y: 0});
      let prevTime = 0;
      let cost = 0;

      chart_preprocess.sortStops(algorithm.geojson, vehicleId).forEach(stop => {
        cost = chart_preprocess.costs(algorithm.scenario, stop, cost, prevTime);
        data.push({x: stop.properties.arrival_m / 60.0 + stop.properties.arrival_h, y: cost});
        prevTime = stop.properties.arrival_m + stop.properties.arrival_h*60;
      });

      var color = chart_preprocess.color(algorithm.geojson, vehicleId)
      datasets.push({"label": "Vehicle " + vehicleId ,"data" : data, "fill": false, backgroundColor: color, borderColor: color});
    });

    return {
      datasets: datasets
    };
  },
  /**
   * Compute the costs and idle time for a given set of algorithms.
   * @param algorithms the algorithms to calculate the costs and idle times for.
   */
  computeCostAndIdleTimeData(algorithms) {
    let costDataset = [];
    let idleTimeDataset = [];
    let colorIndex = 1;

    algorithms.forEach(alg => {
        let time = 0;
        let cost = 0;

        let prev = 0;
        chart_preprocess.vehicleIds(alg.geojson).forEach((vehicleId) => {
            chart_preprocess.sortStops(alg.geojson, vehicleId).forEach(stop => {
                time += stop.properties.duration;
                if (prev === 0 && alg.id === 1) time += stop.properties.arrival_h*60 + stop.properties.arrival_m;
                if (stop.properties.type === 'end') time += (stop.properties.arrival_h*60 + stop.properties.arrival_m) - prev;
                prev = stop.properties.arrival_h*60 + stop.properties.arrival_m;
            });
        });

        this.computeCostData(alg).datasets.forEach(set => {
            cost += set.data[0];
        });

        let color = chart_preprocess.color(alg.geojson, colorIndex);
        costDataset.push({label: alg.name, backgroundColor: color, data: [Math.round(cost*10)/10]});
        idleTimeDataset.push({label: alg.name, backgroundColor: color, data: [time]});

        colorIndex++;
    });
    return [
      {labels: ['Cost'], datasets: costDataset},
      {labels: ['Idle Time'], datasets: idleTimeDataset}
    ];
  },
  /**
   * Compute the distance and time driven for a given set of algorithms.
   * @param algorithms the algorithms to calculate the distance and driven times for.
   */
  computeDistanceAndTimeData(algorithms) {
    let distanceDataset = [];
    let timeDataset = [];
    let colorIndex = 1;

    algorithms.forEach(alg => {
        let dist = 0;
        let time = 0;

        alg.geojson.features.filter(x => x.properties.type === "route").forEach(ft => {
          dist = dist + ft.properties.distance;
          time = time + ft.properties.duration_h * 60 + ft.properties.duration_m;
        });

        var color = chart_preprocess.color(alg.geojson, colorIndex)
        distanceDataset.push({label: alg.name, backgroundColor: color, data: [Math.round(dist/1000*10)/10]});
        timeDataset.push({label: alg.name, backgroundColor: color, data: [time]});

        colorIndex++;

    });

    return [
      {labels: ['Distance'], datasets: distanceDataset},
      {labels: ['Time'], datasets: timeDataset}
    ];
  },
  /**
   * Compute the packages delivered over time for a given set of algorithms.
   * @param algorithms the algorithms to calculate the packages delivered for.
   */
  computePackagesOverTimeComparisonData(algorithms) {
    let datasets = [];
    
    var colorIndex = 1;

    algorithms.forEach(alg => {
      var count = 0;
      var data = [{x: 0, y: 0}];

      chart_preprocess.sortDeliveries(alg.geojson).forEach(dlv => {
        count += 1;
        data.push({x: (dlv.properties.arrival_h * 60.0) + dlv.properties.arrival_m, y: count});
      });

      let color = chart_preprocess.color(alg.geojson, colorIndex);
      datasets.push({label: alg.name, backgroundColor: color, borderColor: color, data: data, fill: false, showLine: true});

      colorIndex++;
    });

    return {
      datasets: datasets
    };
  },
  /**
   * Compute the distance driven over time for a given set of algorithms.
   * @param algorithms the algorithms to calculate the distances for.
   */
  computeDistanceOverTimeComparisonData(algorithms) {
    let datasets = [];
    
    var colorIndex = 1;

    algorithms.forEach(alg => {
      
      let vehicleDistances = alg.vehicles.map(v => {
        return {vehicle: parseInt(v.id) + 1, prevDistance: 0};
      });

      let data = [{x: 0, y: 0}];
      let totalPrev = 0;

      alg.geojson.features
        .filter(f => f.properties.name === "Delivery" || f.properties.name === "end")
        .sort(chart_preprocess.compare)
        .forEach(d => {
          let vdIndex = vehicleDistances.findIndex(vd => {
            return vd.vehicle === d.properties.vehicle;
          });

          let newDist = d.properties.distance - vehicleDistances[vdIndex].prevDistance + totalPrev;
          vehicleDistances[vdIndex].prevDistance = d.properties.distance;
          totalPrev = newDist;

          data.push({x: (d.properties.arrival_h * 60) + d.properties.arrival_m, y: Math.round(newDist / 100) / 10});
      });

      let color = chart_preprocess.color(alg.geojson, colorIndex);
      datasets.push({label: alg.name, backgroundColor: color, borderColor: color, data: data, fill: false, showLine: true});
    
      colorIndex++;
    })

    return {
      labels: ["1", "2", "3", "4", "5", "6","7","8","9","10"],
      datasets: datasets
    };
  },
  /**
   * Compute the costs over time for a given set of algorithms.
   * @param algorithms the algorithms to calculate the distances for.
   **/
  computeCostOverTimeComparisonData(algorithms) {
    let datasets = [];

    var colorIndex = 1;

    algorithms.forEach(alg => {
      let stopList = [];
      chart_preprocess.vehicleIds(alg.geojson).forEach((vehicleId) => {
        stopList = stopList.concat(chart_preprocess.sortStops(alg.geojson, vehicleId));
      });
      const sortedList = stopList.sort(chart_preprocess.compare);

      let data = [{x: 0, y: 0}];
      let totalCost = 0, prevTime = 0;

      sortedList.forEach(stop => {
        totalCost += chart_preprocess.costs(alg.scenario, stop, 0, prevTime);
        prevTime = stop.properties.arrival_m + stop.properties.arrival_h*60;
        data.push({x: prevTime, y: totalCost});
      });

      let color = chart_preprocess.color(alg.geojson, colorIndex);
      datasets.push({label: alg.name, backgroundColor: color, borderColor: color, data: data, fill: false, showLine: true});

      colorIndex++;
    })

    return {
      labels: ["1", "2", "3", "4", "5", "6","7","8","9","10"],
        datasets: datasets
    };
  },
  computeRandomBoxPlotData(name, algorithms, calculateSingle){
      var datacollection = {
        labels: [name],
        datasets: []
      };
      
      var colorIndex = 1;

      algorithms.forEach(alg => {
          datacollection.datasets.push(
          {
            label: alg.name,
            backgroundColor: chart_preprocess.color(alg.geojson, colorIndex),
            data: [chart_preprocess.calculate(alg, calculateSingle)]
          }
        );

        colorIndex++;
      });

      return datacollection;
    },
    /**
   * Compute the packages delivered over time for a given set of algorithms.
   * @param algorithm the algorithms to calculate the packages delivered for.
   */
  computeAllPackagesDeliveredData(algorithm) {
    let datasets = [];
    chart_preprocess.vehicleIds(algorithm.geojson).forEach((vehicleId) => {
      let data = [];
      let totalPrev = 0;
      chart_preprocess
        .sortDeliveries(algorithm.geojson, vehicleId)
        .forEach(delivery => {
          const inBetweenTime = (delivery.properties.arrival_h*60) + delivery.properties.arrival_m - totalPrev;
          totalPrev += inBetweenTime;
          data.push(inBetweenTime);
        });
      let color = chart_preprocess.color(algorithm.geojson, vehicleId);
      datasets.push({label: 'Vehicle ' + vehicleId, backgroundColor: color, data: data});
    });

    let labels = [];

    let nrOfRoutes = algorithm.geojson.features.filter(x => x.properties.type === "route").length;
    let deliveryCountsPerRoute = Array(nrOfRoutes).fill(0);

    algorithm.geojson.features
      .filter(x => x.properties.type === "delivery")
      .forEach(dlv => { deliveryCountsPerRoute[dlv.properties.route_number - 1]++; });

    let highestDeliveryCount = deliveryCountsPerRoute.reduce(function(a, b) { return Math.max(a, b) })

    for (let i = 1; i <= highestDeliveryCount; i++) {
        labels.push(i);
    }

    return {labels: labels, datasets: datasets};
  },
  /**
   * 
   * @param {*} algorithms 
   */
  computeTotalDistanceBoxPlotData(algorithms) {
    return chart_preprocess.createBoxPlotDataSingle(algorithms, "Total distance in km", (algorithm) => {
      var data = []
      chart_preprocess.vehicleIds(algorithm.geojson).forEach((vehicleId) => {
          let lastDelivery = chart_preprocess.sortDeliveries(algorithm.geojson, vehicleId).pop();
          data.push(Math.round(lastDelivery.properties.distance / 100) / 10);
      });

      return data;
    });
  },
  /**
   * 
   * @param {Array} algorithms 
   */
  computeTotalTimeBoxPlotData(algorithms) {
    return chart_preprocess.createBoxPlotDataSingle(algorithms, "Total time in minutes", (algorithm) => {
      var data = []
        chart_preprocess.vehicleIds(algorithm.geojson).forEach((vehicleId) => {
          let lastDelivery = chart_preprocess.sortDeliveries(algorithm.geojson, vehicleId).pop();
          data.push(lastDelivery.properties.arrival_h * 60 + lastDelivery.properties.arrival_m);
        });

        return data;
    });
  },
  /**
   * 
   * @param {Array} algorithms 
   */
  computeTotalCostsBoxPlotData(algorithms) {
    return chart_preprocess.createBoxPlotDataSingle(algorithms, "Total cost in euro's", (algorithm) => {
      var data = [];
      this.computeCostData(algorithm).datasets.forEach(set => {
          data.push(set.data[0]);
      });
      return data;
    });
  }
}



    



