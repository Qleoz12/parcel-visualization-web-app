export default {
    loadDepotsAndVehicles(vehicles, depots) {
        let temp = []
        depots.forEach(dep => {
            temp.push({id: dep.id, vehicles: []});
        });
        vehicles.forEach(v => {
            for (let i = 0; i < temp.length; i++) {
                let dep = temp[i];
                if (v.depot === dep.id) {
                    temp[i].vehicles.push({id: v.id, capacity: v.capacity});
                    break;
                }
            }
        });
        return temp;
    }
}
