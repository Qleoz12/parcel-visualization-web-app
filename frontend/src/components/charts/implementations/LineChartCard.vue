<template>
    <v-card outlined>
        <v-card-text>
            <v-card-title class="justify-center">{{ title }}</v-card-title>
            <line-chart :chart-data="chartData" :options="chartOptions"/>
        </v-card-text>
    </v-card>
</template>
<script>
    import LineChart from '../base_charts/LineChart';

    export default {
        name: "LineChartCard",
        components: {
            LineChart,
        },
        props: {
            title: {
                type: String,
                default: ''
            },
            chartData: {
                type: Object,
                default: null
            },
            chartOptions: {
                type: Object,
                default: null
            }
        },
    }
</script>