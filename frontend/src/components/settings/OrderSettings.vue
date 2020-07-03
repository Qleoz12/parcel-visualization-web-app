<template>
    <v-container>
        <v-list>
            <v-list-item>
                <p>These settings are used during order randomization. This means changes are visible after a randomization
                    of delivery points.<br>
                    <strong>N.B.</strong> This order generation has not been implemented for the Almende Algorithm yet,
                    so changing these settings will have no effect on this algorithm's input and output
                </p>
            </v-list-item>
            <v-list-item>
                <v-simple-table style="width:100%">
                    <tbody>
                    <tr>
                        <td class="body-1">Number of orders</td>
                        <td>
                            <v-slider
                                    v-model="newOrderNum"
                                    :max="ordersMax"
                                    :min="ordersMin"
                            >
                                <template v-slot:append>
                                    <v-text-field
                                            v-model="newOrderNum"
                                            class="mt-0 pt-0"
                                            type="number"
                                            style="width: 60px"
                                    ></v-text-field>
                                </template>
                            </v-slider>
                        </td>
                    </tr>
                    <tr>
                        <td class="body-1">Generate orders around depots with a radius of ... (km)</td>
                        <td>
                            <v-slider
                                    v-model="newDepotRange"
                                    :max="depotMax"
                                    :min="depotMin"
                            >
                                <template v-slot:append>
                                    <v-text-field
                                            v-model="newDepotRange"
                                            class="mt-0 pt-0"
                                            type="number"
                                            style="width: 60px"
                                    ></v-text-field>
                                </template>
                            </v-slider>
                        </td>
                    </tr>
                    </tbody>
                </v-simple-table>
            </v-list-item>
        </v-list>
        <ControlButtons :action="'randomize'" :threeButtons="true" @cancel="cancel" @save="save"/>
    </v-container>
</template>

<script>
    import ControlButtons from "./ControlButtons";

    export default {
        name: "OrderSettings",
        components: {ControlButtons},
        props: {
            orderNumber: Number,
            depotRange: Number
        },
        component: {
            ControlButtons
        },
        data: () => ({
            ordersMin: 1,
            ordersMax: 50,
            depotMin: 5,
            depotMax: 100,
            prevOrderNum: 0,
            prevDepotRange: 0,
            newOrderNum: 0,
            newDepotRange: 0
        }),
        methods: {
            save(randomize) {
                this.$emit('saveSettings', this.newOrderNum, this.newDepotRange*1000, randomize);
                this.prevOrderNum = this.newOrderNum;
                this.prevDepotRange = this.newDepotRange;
            },
            cancel() {
                this.newOrderNum = this.prevOrderNum;
                this.newDepotRange = this.prevDepotRange;
                this.$emit('close');
            }
        },
        mounted() {
            this.newOrderNum = this.orderNumber;
            this.newDepotRange = this.depotRange/1000;
            this.prevOrderNum = this.orderNumber;
            this.prevDepotRange = this.depotRange/1000;
        }
    }
</script>

<style scoped>
    td:first-child {
        width:33%;
    }
</style>
