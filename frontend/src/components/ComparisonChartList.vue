<template>
    <v-container fluid pa-0>
        <v-row dense>
          <v-col :cols="cols">
            <line-chart-card title="Packages delivered over time" :chart-data="computePackagesOverTimeComparisonData()" :chart-options="generateChartOptionsLine('Minutes', 'Packages', 30, 5)" />
          </v-col>
          <v-col :cols="cols">
            <line-chart-card title="Distance driven over time" :chart-data="computeDistanceOverTimeComparisonData()" :chart-options="generateChartOptionsLine('Minutes', 'Km', 30, 100)" />
          </v-col>
            <v-col :cols="cols">
                <line-chart-card title="Costs over time" :chart-data="computeCostOverTimeComparisonData()" :chart-options="generateChartOptionsLine('Minutes', 'Euro', 30, 10)" />
            </v-col>

          <v-col :cols="cols">
            <bar-chart-card title="Total distance & Time" :chart-data="computeDistanceAndTimeData()" :chart-options="generateChartOptionsBarComparison('Km', 'Hours')"/>
          </v-col>
          <v-col :cols="cols">
            <bar-chart-card title="Cost & Idle time" :chart-data="computeCostAndIdleTimeData()" :chart-options="generateChartOptionsBarComparison('Euro', 'Minutes')"/>
          </v-col>
        </v-row>   
    </v-container>
</template>

<script>
    import chart_options from "./charts/services/chart_options";
    import chart_process from "./charts/services/chart_process";
    import LineChartCard from "./charts/implementations/LineChartCard";
    import BarChartCard from "./charts/implementations/BarChartCard";

    export default {
        name: "ComparisonChartList",
        props: {
            algorithms: Array,
            sideBar: {
                type: Boolean,
                default: false,
            }
        },
        components: {
            LineChartCard,
            BarChartCard,
        },
        data: () => ({
            gridWidth: 2
        }),
        methods: {
            generateChartOptionsLine(xAxisLabel, yAxisLabel, xInterval, yInterval) {
                return chart_options.generateChartOptionsLine(xAxisLabel, yAxisLabel, xInterval, yInterval);
            },
            generateChartOptionsBarComparison(yLabel1, yLabel2) {
                return [
                    chart_options.generateChartOptionsBar(yLabel1, false),
                    chart_options.generateChartOptionsBar(yLabel2, false),
                ];
            },
            computePackagesOverTimeComparisonData() {
                return chart_process.computePackagesOverTimeComparisonData(this.algorithms);
            },
            computeDistanceOverTimeComparisonData() {
                return chart_process.computeDistanceOverTimeComparisonData(this.algorithms);
            },
            computeCostOverTimeComparisonData() {
                return chart_process.computeCostOverTimeComparisonData(this.algorithms);
            },
            computeDistanceAndTimeData() {
                return chart_process.computeDistanceAndTimeData(this.algorithms);
            },
            computeCostAndIdleTimeData() {
                return chart_process.computeCostAndIdleTimeData(this.algorithms);
            }
        },
        computed: {
            cols() {
                return this.sideBar ? 12 : (12 / this.gridWidth);
            }
        }
    }
</script>

<style scoped>
</style>
