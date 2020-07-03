<script>
    import { Bar, mixins } from "vue-chartjs";
    const { reactiveProp } = mixins

    export default {
        name: "BarChart",
        extends: Bar,
        mixins: [reactiveProp],
        props: {
            chartData: {
                type: [Promise, Object],
                default: null
            },
            options: {
                type: Object,
                default: null
            }
        },
        mounted () {
            this.renderChart(this.chartData, this.options)
        }
    }
</script>

<style scoped>

</style>

