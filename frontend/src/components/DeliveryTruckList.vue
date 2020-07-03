<template>
    <v-expansion-panels>
        <v-expansion-panel
            v-for="(vehicle,i) in algorithm.vehicles"
            :key="i"
        >
            <v-expansion-panel-header>
                <DeliveryTruck :number="vehicle.id" :color="vehicle.color" :name="vehicle.name"/>
            </v-expansion-panel-header>
            <v-expansion-panel-content>
                <v-spacer/>
                <delivery-truck-chart-list :number="vehicle.id" :color="vehicle.color" :algorithm="algorithm"/>  
            </v-expansion-panel-content>
        </v-expansion-panel>

    </v-expansion-panels>
</template>

<script>
    import DeliveryTruck from './DeliveryTruck';
    import DeliveryTruckChartList from './DeliveryTruckChartList';

    export default {
        name: "DeliveryTruckList",
        props: ['algorithm'],
        components: {
            DeliveryTruck,
            DeliveryTruckChartList,
        },
    }
</script>

<style scoped>

</style>
