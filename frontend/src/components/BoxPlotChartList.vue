<template>
  <v-container fluid pa-0>
    <v-row dense>
      <!-- TODO: Fix data for the boxplot charts -->
      <v-col :cols="cols">
        <box-plot-chart-card title="Total distance in km" :chart-data="computeTotalDistanceBoxPlotData()"/>
      </v-col>
      <v-col :cols="cols">
        <box-plot-chart-card title="Total time in minutes" :chart-data="computeTotalTimeBoxPlotData()"/>
      </v-col>
      <v-col :cols="cols">
        <box-plot-chart-card title="Total cost in euro's" :chart-data="computeTotalCostsBoxPlotData()"/>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
  import BoxPlotChartCard from './charts/implementations/BoxPlotChartCard';
  import chart_process from './charts/services/chart_process'; 

  export default {
    name: "BoxPlotChartList",
    props: {
        'algorithms': Array,
        'sideBar': {
            type: Boolean,
            default: false
        }
    },
    components: {
      BoxPlotChartCard,
    },
    data: () => ({
        gridWidth: 3
    }),
    methods: {   
      computeTotalDistanceBoxPlotData() {
        return chart_process.computeTotalDistanceBoxPlotData(this.algorithms);
      },
      computeTotalTimeBoxPlotData() {
        return chart_process.computeTotalTimeBoxPlotData(this.algorithms);
      },
      computeTotalCostsBoxPlotData() {
        return chart_process.computeTotalCostsBoxPlotData(this.algorithms);
      }
    },
    computed: {
      cols() {
        return this.sideBar ? 12 : (12 / this.gridWidth);
      }
    }
  }

</script>