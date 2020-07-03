<template>
    <div>
        <v-card>
            <v-card-text>
                This truck has driven {{statistics.totalKM}} kilometers in {{statistics.totalHours}} hour(s) and
                {{statistics.totalMinutes}} minute(s).
                In total {{statistics.totalPackages}} packages were dropped of.
            </v-card-text>
            <bar-chart-card title="Delivery time per package" :chart-data="computeDeliveryTimeData()" :chart-options="generateBarChartOptions('Minutes')"/>
        </v-card>
        
    </div>
</template>

<script>
    import BarChartCard from './charts/implementations/BarChartCard';
    import chart_options from './charts/services/chart_options';
    import chart_preprocess from './charts/services/chart_preprocess';

    export default {
        name: "DeliveryTruckChartList",

        props: {
            number: Number,
            algorithm: Object,
            color: String,
        },
        components: {
            BarChartCard
        },
        data: () => ({
                statistics: {totalKM: 0, totalPackages: 0, totalHours: 0, totalMinutes: 0},
        }),
        methods: {
            generateBarChartOptions(label) {
                return chart_options.generateChartOptionsBar(label, true);
            },
            fillVariables() {
                const route = this.algorithm.geojson.features.filter(x => x.properties.type === "route" && x.properties.number === (this.number+1))[0];
                this.statistics.totalKM = (route.properties.distance/1000).toFixed(1);
                this.statistics.totalPackages = this.algorithm.geojson.features.filter(x => x.properties.type === "delivery" && x.properties.vehicle === (this.number+1)).length;
                const minutes = Math.round(route.properties.duration_h*60 + route.properties.duration_m);
                this.statistics.totalMinutes = minutes % 60;
                this.statistics.totalHours = Math.floor(minutes / 60);
            },
            computeDeliveryTimeData() {
                let datasets = [];
                let prev = 0;
                const deliveries = chart_preprocess.sortDeliveries(this.algorithm.geojson, this.number+1);
                deliveries.forEach(delivery => {
                    const step = delivery.properties;
                    const givenTime = step.arrival_h*60 + step.arrival_m;
                    let inBetweenTime = Math.round(givenTime - prev);
                    let temp = {label: 'Package ' + step.number, backgroundColor: this.color, data: [inBetweenTime]}
                    datasets.push(temp);
                    prev = givenTime;
                });
                return {labels: ['Packages'], datasets: datasets};
            },
        },
        async mounted() {
            this.fillVariables();
        }
    }
</script>

<style scoped>
</style>
