<template>
  <v-card outlined>
    <v-card-text>
      <v-card-title class="justify-center">{{ title }}</v-card-title>
      <bar-chart :chart-data="chartData" :options="chartOptions" v-if="singleChart"/> 
      <!-- Put multiple charts next to each other iff multiple chartdata objects are fed into one card-->
      <v-container class="ma-0 pa-0" v-else>
        <v-row no-gutters>
          <v-col
            v-for="(chart, i) in chartData"
            :key="i"
            :cols="12 / chartData.length"
          >
            <bar-chart :chart-data="chart" :options="chartOptions[i]"/>
          </v-col>
        </v-row>
      </v-container>
    </v-card-text>
  </v-card>
</template>

<script>
    import BarChart from '../base_charts/BarChart';

    export default {
        name: "BarChartCard",
        components: {
            BarChart,
        },
        props: {
          title: {
            type: String,
            default: ''
          },
          chartData: {
            type: [Object, Array],
            default: null
          },
          chartOptions: {
            type: [Object, Array],
            default: null
          }
        },
        computed: {
          singleChart() {
            return !(Array.isArray(this.chartData) && Array.isArray(this.chartOptions));
          }
        }
    }
</script>