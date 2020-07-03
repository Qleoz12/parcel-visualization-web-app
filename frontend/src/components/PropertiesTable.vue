<template>
    <v-list-item>
    <v-data-table
    hide-default-header
    hide-default-footer
    :headers="headers"
    :items="items"
    :footer-props="{ 'items-per-page-options': []}"
    ></v-data-table>
    </v-list-item>
</template>

<script>
  export default {
    props: ['algorithms'],
    data () {
      return {
        headers: [
          {
            text: 'Label',
            align: 'start',
            sortable: false,
            value: 'key',
          },{
            text: 'Value',
            align: 'start',
            sortable: false,
            value: 'value',
          },
        ],
        items: [
          { key: 'Version', value: '0.6.0-alpha', },
          { key: 'Map Data', value: 'OpenStreetMap', }
        ]
      }
    },
    mounted() {
        for (let i = 0; i < this.$props.algorithms.length; i++) {
            this.items.push({key: 'Algorithm '+ (i+1), value: this.$props.algorithms[i].name});
        }
    }
  }
</script>

<style scoped>
  td {
    word-break: keep-all;
    overflow-wrap: normal;
    white-space: nowrap
  }
</style>