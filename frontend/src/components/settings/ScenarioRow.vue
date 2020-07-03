<template>
    <tr>
        <td class="body-1">{{content.title}}</td>
        <td>
            <v-checkbox
                    v-model="content.infinite"
                    label="Infinite"
                    :disabled="content.disabled"
                    @change="changeInfinite"
            ></v-checkbox>
        </td>
        <td>
            <v-slider
                    v-if="content.slider"
                    v-model="content.model"
                    class="align-center"
                    :max="content.max"
                    :min="content.min"
                    :disabled="content.infinite"
                    hide-details
                    @change="change"
            >
                <template v-slot:append>
                    <v-text-field
                            v-model="content.model"
                            class="mt-0 pt-0"
                            hide-details
                            single-line
                            type="number"
                            style="width: 60px"
                            @change="change"
                    ></v-text-field>
                </template>
            </v-slider>
            <v-text-field
                    v-else
                    v-model="content.model"
                    @keyup.native="change"
                    @change="change"
                    class="mt-0 pt-0"
                    hide-details
                    single-line
                    step=".1"
                    type="number"
                    style="width: 60px"
            ></v-text-field>
        </td>
    </tr>
</template>

<script>
    export default {
        name: "ScenarioRow",
        props: {
            content: Object
        },
        methods: {
            changeInfinite() {
                if (!this.content.disabled) {
                    this.$emit('changeInfinite', this.content.id, this.content.infinite);
                }
            },
            change() {
                if (!this.content.slider) this.content.model = Math.round(this.content.model*10)/10
                this.$emit('change', this.content.id, this.content);
            }
        }
    }
</script>

<style scoped>
    td:first-child {
        width:30%;
    }
    td:nth-child(2) {
        width:10%;
    }
</style>
