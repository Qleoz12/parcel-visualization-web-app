<template>
    <div>
        <v-list v-if="loaded">
            <v-list-item>
                <v-simple-table style="width:100%">
                    <tbody>
                    <ScenarioRow
                            v-for="(setting, i) in rows"
                            :key="i"
                            :content="setting"
                            @changeInfinite="changeInfinite"
                            @change="change"
                    />
                    </tbody>
                </v-simple-table>
            </v-list-item>
        </v-list>
        <ControlButtons :action="'reload'" :threeButtons="false" @cancel="cancel" @save="save"/>
    </div>
</template>

<script>
    import ControlButtons from "./ControlButtons";
    import ScenarioRow from "./ScenarioRow";

    export default {
        name: "ScenarioSettings",
        props: {
            algorithm: Object,
            index: Number
        },
        components: {
            ScenarioRow,
            ControlButtons
        },
        data: () => ({
            loaded: false,
            initScenario: null,
            newScenario: null,
            rows: [
                {
                    id: 1,
                    title: "Number of available vehicles",
                    min: 1,
                    max: 50,
                    disabled: false,
                    infinite: false,
                    slider: true,
                    model: null
                },
                {
                    id: 2,
                    title: "Number of available drivers",
                    min: 1,
                    max: 50,
                    disabled: false,
                    infinite: false,
                    slider: true,
                    model: null
                },
                {
                    id: 3,
                    title: "Capacity of the vehicles",
                    min: 1,
                    max: 50,
                    disabled: false,
                    infinite: false,
                    slider: true,
                    model: null
                },
                {
                    id: 4,
                    title: "Drivers' active time after a mode change",
                    min: 1,
                    max: 50,
                    disabled: true,
                    infinite: false,
                    slider: true,
                    model: null
                },
                {
                    id: 5,
                    title: "Time needed for a mode change",
                    min: 1,
                    max: 50,
                    disabled: true,
                    infinite: false,
                    slider: true,
                    model: null
                },
                {
                    id: 6,
                    title: "Vehicle cost per time step",
                    min: 1,
                    max: 50,
                    disabled: true,
                    infinite: false,
                    slider: false,
                    model: null
                },
                {
                    id: 7,
                    title: "Driver cost per time step",
                    min: 1,
                    max: 50,
                    disabled: true,
                    infinite: false,
                    slider: false,
                    model: null
                },
            ]
        }),
        methods: {
            load() {
                this.newScenario = this.initScenario;
                this.rows[0].infinite = this.newScenario.vehicles === -1
                this.rows[0].model = this.newScenario.vehicles;
                this.rows[1].infinite = this.newScenario.drivers === -1
                this.rows[1].model = this.newScenario.drivers;
                this.rows[2].infinite = this.newScenario.capacity === -1
                this.rows[2].model = this.newScenario.capacity;
                this.rows[3].model = this.newScenario.time_active;
                this.rows[4].model = this.newScenario.time_mode;
                this.rows[5].model = this.newScenario.cost_vehicle;
                this.rows[6].model = this.newScenario.cost_driver;
                this.loaded=true;
            },
            getValueById(rowId) {
                switch (rowId) {
                    case 1:
                        return this.newScenario.vehicles;
                    case 2:
                        return this.newScenario.drivers;
                    case 3:
                        return this.newScenario.capacity;
                    case 4:
                        return this.newScenario.time_active;
                    case 5:
                        return this.newScenario.time_mode;
                    case 6:
                        return this.newScenario.cost_vehicle;
                    case 7:
                        return this.newScenario.cost_driver;
                }
            },
            updateValueById(rowId, newVal) {
                switch (rowId) {
                    case 1:
                        this.newScenario.vehicles = newVal;
                        break;
                    case 2:
                        this.newScenario.drivers = newVal;
                        break;
                    case 3:
                        this.newScenario.capacity = newVal;
                        break;
                    case 4:
                        this.newScenario.time_active = newVal;
                        break;
                    case 5:
                        this.newScenario.time_mode = newVal;
                        break;
                    case 6:
                        this.newScenario.cost_vehicle = newVal;
                        break;
                    case 7:
                        this.newScenario.cost_driver = newVal;
                        break;
                }
            },
            changeInfinite(rowId, infinite) {
                this.rows.forEach(row => {
                    if (row.id === rowId) {
                        if (infinite || !infinite && this.getValueById(rowId) === -1) {
                            row.model = row.max;
                        } else {
                            row.model = this.getValueById(rowId);
                        }
                    }
                });
            },
            change(rowId, obj) {
                this.rows.forEach(row => {
                    if (row.id === rowId) {
                        row = obj;
                    }
                });
            },
            save() {
                this.rows.forEach(row => {
                    const newVal = !row.disabled && row.infinite ? -1 : row.model;
                    this.updateValueById(row.id, newVal);
                });

                this.initScenario = this.newScenario;
                this.$emit('saveSettings', this.newScenario, this.index);
            },
            cancel() {
                this.loaded = false;
                this.load();
                this.$emit('close');
            }
        },
        mounted() {
            this.initScenario = this.algorithm.scenario;
            this.load();
        }
    }
</script>
