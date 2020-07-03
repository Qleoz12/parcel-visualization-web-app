<template>
  <v-card outlined>
    <v-card-text>
      <v-card-title class="justify-center">{{ title }}</v-card-title>
      <box-plot-chart :chart-data="chartData"/>
    </v-card-text>
    <!-- <button @click="fillData()">Randomize</button> -->
  </v-card>
</template>

<script>
  import BoxPlotChart from '../base_charts/BoxplotChart';

  export default {
    name: "BoxPlotChartCard",
    components: {
        BoxPlotChart,
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
      },
      // fillData: {
      //   type: Function,
      //   default: () => {}
      // }
    },
  }
</script>
