<template>
    <v-list>
        <v-list-item style="width:100%">
            <v-spacer/>
            <v-list-item-action class="justify-center">
                <v-btn class="actionButton" color="secondary lighten-1" @click="cancel()">Close</v-btn>
            </v-list-item-action>
            <v-list-item-action v-if="threeButtons" class="justify-center">
                <v-btn class="actionButton" color="primary lighten-1" @click="save(false)">Save</v-btn>
            </v-list-item-action>
            <v-list-item-action class="justify-center">
                <v-btn class="actionButton" color="primary lighten-1" @click="save(true)">Save & {{action}}</v-btn>
            </v-list-item-action>
        </v-list-item>
    </v-list>
</template>

<script>
    export default {
        name: "ControlButtons",
        props: {
            action: String,
            threeButtons: Boolean
        },
        methods: {
            cancel() {
                this.$emit('cancel');
            },
            save(extra) {
                if (this.threeButtons) {
                    this.$emit('save', extra);
                } else {
                    this.$emit('save');
                }

            }
        }
    }
</script>

<style scoped>

</style>