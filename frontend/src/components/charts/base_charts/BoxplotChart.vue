<script>
  import "chartjs-chart-box-and-violin-plot";
  import { generateChart, mixins } from "vue-chartjs";
  const { reactiveProp } = mixins;

  const BoxPlot = generateChart("boxplot", "boxplot");
  
  export default {
    extends: BoxPlot,
    mixins: [reactiveProp],
    props: {
      chartData: {
          type: Object,
          default: null
      },
      options: {
          type: Object,
          default: null
      }
    },
    mounted() {
      this.renderChart(this.chartData, this.options);
    }
  };
</script>