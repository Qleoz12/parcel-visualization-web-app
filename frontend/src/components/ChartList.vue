<template>
    <v-container fluid pl-0 pr-0>
        <v-row v-if="!sideBar">
            <v-col cols="12">
                <bar-chart-card title="Delivery time per nth package" :chart-data="computeAllPackagesDeliveredData()" :chart-options="generateChartOptionsBar('Minutes')"/>
            </v-col>
        </v-row>
        <v-row dense>
            <v-col :cols="cols">
                <bar-chart-card title="Distance" :chart-data="computeDistanceData()" :chart-options="generateChartOptionsBar('distance (km)')"/>
            </v-col>
            <v-col :cols="cols">
            <bar-chart-card title="Stop count" :chart-data="computeStopCountData()" :chart-options="generateChartOptionsBar('stop count')"/>
            </v-col>
            <v-col :cols="cols">
                <bar-chart-card title="Costs" :chart-data="computeCostData()" :chart-options="generateChartOptionsBar('cost (euro)')"/>
            </v-col>

            <v-col :cols="cols">
                <line-chart-card title="Packages delivered over time" :chart-data="computePackagesOverTimeData()" :chart-options="generateChartOptionsLine('hours', 'amount')" />
            </v-col>
            <v-col :cols="cols">
                <line-chart-card title="Distance over time" :chart-data="computeDistanceOverTimeData()" :chart-options="generateChartOptionsLine('hours', 'kilometers', 1, 20)"/>
            </v-col>
            <v-col :cols="cols">
                <line-chart-card title="Cost over time" :chart-data="computeCostOverTimeData()" :chart-options="generateChartOptionsLine('hours', 'cost (euro)', 1, 10)"/>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
    import chart_options from './charts/services/chart_options';
    import chart_process from './charts/services/chart_process';
    import BarChartCard from './charts/implementations/BarChartCard';
    import LineChartCard from './charts/implementations/LineChartCard';

    export default {
        name: "ChartList",
        props: {
            'algorithm': Object,
            'sideBar': {
                type: Boolean,
                default: false
            }
        },
        components: {
            BarChartCard,
            LineChartCard,
        },
        data: () => ({
            gridWidth: 3
        }),
        methods: {
            generateChartOptionsBar(yAxisLabel) {
                return chart_options.generateChartOptionsBar(yAxisLabel);
            },
            generateChartOptionsLine(xAxisLabel, yAxisLabel, xInterval, yInterval) {
                return chart_options.generateChartOptionsLine(xAxisLabel, yAxisLabel, xInterval, yInterval);
            },
            computeAllPackagesDeliveredData() {
                return chart_process.computeAllPackagesDeliveredData(this.algorithm);
            },
            computeDistanceData() {
                return chart_process.computeDistanceData(this.algorithm);
            },
            computeStopCountData() {
                return chart_process.computeStopCountData(this.algorithm);
            },
            computeCostData() {
                return chart_process.computeCostData(this.algorithm);
            },
            computePackagesOverTimeData() {
                return chart_process.computePackagesOverTimeData(this.algorithm);
            },
            computeDistanceOverTimeData() {
                return chart_process.computeDistanceOverTimeData(this.algorithm);
            },
            computeCostOverTimeData() {
                return chart_process.computeCostOverTimeData(this.algorithm);
            }
        },
        computed: {
            cols() {
                return this.sideBar ? 12 : (12 / this.gridWidth);
            }
        }
    }
</script>
