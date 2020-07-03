<template>
    <v-list-item>
        <v-list-item-action>
        <v-icon :color="color">mdi-bus</v-icon>
        </v-list-item-action>
        <v-list-item-content>
        <v-list-item-title>{{name}}</v-list-item-title>
        </v-list-item-content>
    </v-list-item>
</template>

<script>
  export default {
    props: ['number', 'color', 'name'],
    data: () => ({
    }),
  }
</script>
