<template>
    <v-list>
        <v-list-item>
            <v-simple-table>
                <tbody>
                <tr>
                    <td class="body-1">Default algorithm to show on page load</td>
                    <td>
                        <v-select
                                :items="algorithms"
                                item-text="text"
                                item-value="value"
                                v-model="localStandard"
                                class="mt-5"
                                solo
                                v-bind:return-object="true"
                                @change="changeDefault($event)"
                        ></v-select>
                    </td>
                </tr>
                </tbody>
            </v-simple-table>
        </v-list-item>
    </v-list>
</template>

<script>
    export default {
        name: "DefaultSettings",
        props: {
            algorithms: Array,
            standard: Object
        },
        data: () => ({
            localStandard: null
        }),
        methods: {
            changeDefault(event) {
                this.$emit('changeDef', event.value);
            }
        },
        mounted() {
            this.localStandard = this.standard;
        }
    }
</script>
