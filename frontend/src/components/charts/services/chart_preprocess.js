export default {
    compare(a,b) {
        const hourA = a.properties.arrival_h;
        const hourB = b.properties.arrival_h;
        if (hourA < hourB) {
            return -1;
        } else if (hourA > hourB) {
            return 1;
        } else { // Arrival hours are equal
            const minA = a.properties.arrival_m;
            const minB = b.properties.arrival_m;
            if (minA < minB) {
                return -1;
            } else if (hourA > hourB) {
                return 1;
            } else { // Arrival times are exactly equal
                return 0;
            }
        }
    },
    vehicleIds(geojson){
        const deliveries = geojson.features.filter((v) => v.properties.name === "Delivery");
        var ids = new Set()
        deliveries.forEach(dlv => {
            ids.add(dlv.properties.vehicle);
        })
        return ids
    },
    sortDeliveries(geojson, vehicleId){
        const deliveries = geojson.features.filter((v) => (v.properties.name === "Delivery" && (v.properties.vehicle === vehicleId || vehicleId == null)));
        return deliveries.sort(this.compare);
    },
    sortStops(geojson, vehicleId){
        const stops = geojson.features.filter((v) => (v.geometry.type === "Point" && v.properties.type !== "start" &&
            (v.properties.vehicle === vehicleId))).sort(this.compare);
        let prevCoords = [];
        let res = []
        stops.forEach(stop => {
            if (prevCoords[0] === stop.geometry.coordinates[0] && prevCoords[1] === stop.geometry.coordinates[1]) {
                res[res.length-1].properties.duration += stop.properties.duration;
            } else {
                prevCoords = JSON.parse(JSON.stringify(stop.geometry.coordinates));
                res.push(JSON.parse(JSON.stringify(stop)));
            }
        });
        return res.sort(this.compare);
    },
    color(geojson, vehicleId){
        for(var i = 0; i < geojson.features.length; i++){
            var prop = geojson.features[i].properties;
            if(prop.vehicle === vehicleId && prop.type !== "start" && prop.style !== undefined){
                return prop.style.color;
            }
        }
    },
    costs(scenario, stop, prevCost, prevTime){
        var minsDiff = (stop.properties.arrival_m + stop.properties.arrival_h*60) - prevTime;
        const factor = (stop.properties.arrival_mode === "Manual") ? (scenario.cost_vehicle + scenario.cost_driver) : scenario.cost_vehicle;
        let cost = (minsDiff * factor)/100; // scenario costs are in cents per minute
        if (stop.properties.arrival_mode === "Manual") {
            cost += (stop.properties.duration * scenario.cost_driver) / 100;
        }
        cost += prevCost;
        return Math.round(cost*100) / 100;
    },
    createBoxPlotDataSingle(algorithms, name, computeFunction) {
        let datacollection = {
            labels: [name],
            datasets: []
        };
        
        var colorIndex = 1;
        algorithms.forEach((alg) => {
            datacollection.datasets.push(
                {
                    label: alg.name,
                    backgroundColor: this.color(alg.geojson, colorIndex),
                    data: [computeFunction(alg)]
                }
            );
            colorIndex++;
        })

        return datacollection;
    },
    createBoxPlotData(algorithms, colors, name, calculateSingle){
      var datacollection = {
        labels: [name],
        datasets: []
      };
      this.colorIndex = 0
      algorithms.forEach((alg) => {
          datacollection.datasets.push(
          {
            label: alg.name,
            backgroundColor: colors[this.colorIndex],
            data: [this.calculate(alg, calculateSingle)]
          }
        );
        this.colorIndex += 1;
      })
      return datacollection;
    },
    calculate(algorithm, calculateSingle){
        var res = []
        // TODO temporary until we actually have a way to receive statistics from multiple runs!
        for(var i = 0; i < 16; i += 1){
            var randomOffset = Math.random() * 120 - 60;
            res.push(Math.round((calculateSingle(algorithm) + randomOffset)*100)/100)
        }
        return res;
    }
}