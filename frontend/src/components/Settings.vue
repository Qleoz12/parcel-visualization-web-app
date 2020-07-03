<template>
    <v-dialog v-model="dialog" v-if="loaded" persistent max-width="900px" min-height="900px">
        <v-card class="" outlined>
            <v-toolbar flat>
                <v-toolbar-title>
                    Settings
                </v-toolbar-title>
                <v-spacer></v-spacer>
                <v-btn icon @click="closeDialog()">
                    <v-icon color="red">fa-times</v-icon>
                </v-btn>
            </v-toolbar>
            <v-tabs v-model="settings">
                <v-tab :key="0">
                    General Settings
                </v-tab>
                <v-tab :key="1">
                    Order settings
                </v-tab>
                <v-tab
                    v-for="(algorithm, i) in algorithms"
                    :key="i+2"
                >{{algorithm.name}} Settings</v-tab>
            </v-tabs>
        </v-card>
        <v-tabs-items v-model="settings">
            <v-tab-item :key="0">
                <GeneralSettings @close="closeDialog" :algorithms="selectAlgorithms" :default="this.default" :input="input"/>
            </v-tab-item>
            <v-tab-item :key="1">
                <OrderSettings @saveSettings="saveOr" @close="closeDialog" :orderNumber="input.orders" :depotRange="input.depotRadius"/>
            </v-tab-item>
            <v-tab-item :key="2">
                <VehicleSettings v-if="algorithms[0].id === 0" @saveSettings="saveV" @close="closeDialog" :algorithm="algorithms[0]" :index="0"/>
                <ScenarioSettings v-else :algorithm="algorithms[0]" @saveSettings="saveScen" @close="closeDialog" :index="0"/>
            </v-tab-item>
            <v-tab-item v-if="algorithms.length>1" :key="3">
                <VehicleSettings v-if="algorithms[1].id === 0" @saveSettings="saveV" @close="closeDialog" :algorithm="algorithms[1]" :index="1"/>
                <ScenarioSettings v-else :algorithm="algorithms[1]" @saveSettings="saveScen" @close="closeDialog" :index="1"/>
            </v-tab-item>
        </v-tabs-items>
    </v-dialog>
</template>

<script>
    import GeneralSettings from "./settings/GeneralSettings";
    import OrderSettings from "./settings/OrderSettings";
    import VehicleSettings from "./settings/VehicleSettings";
    import ScenarioSettings from "./settings/ScenarioSettings";

    export default {
        name: "Settings",
        components: {ScenarioSettings, VehicleSettings, OrderSettings, GeneralSettings},
        props: {
            algorithms: Array,
            selectAlgorithms: Array,
            default: Object,
            input: Object
        },
        data: () => ({
            dialog: false,
            settings: null,
            loaded: false
        }),
        methods: {
            openDialog() {
                this.dialog = true;
                this.loaded = true;
            },
            closeDialog() {
                this.dialog = false;
                this.loaded = false;
            },
            saveOr(orders, depotRadius, randomize) {
                if (randomize) this.closeDialog();
                this.$emit('saveOrders', orders, depotRadius, randomize);
            },
            saveV(vehicles, depots, alg, scenario) {
                this.closeDialog();
                this.$emit('saveVehicles', vehicles, depots, alg, scenario);
            },
            saveScen(scenario, alg) {
                this.closeDialog();
                this.$emit('saveScenario', scenario, alg);
            }
        },
        mounted() {
        }
    }
</script>

<style>
    .actionButton {
        width:180px;
        margin-left:10px;
    }
</style>
