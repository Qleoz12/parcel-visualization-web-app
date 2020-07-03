<template>
    <div>
        <DefaultSettings @changeDef="changeDefault" :algorithms="algorithms" :standard="this.default" :key="resetDef"/>
        <ControlButtons :action="'close'" :threeButtons="true" @cancel="cancel" @save="save"/>
    </div>
</template>

<script>
    import DefaultSettings from "./DefaultSettings";
    import ControlButtons from "./ControlButtons";

    export default {
        name: "GeneralSettings",
        components: {ControlButtons, DefaultSettings},
        props: {
            algorithms: Array,
            default: Object,
            input: Object
        },
        data: () => ({
            defaultAlg: null,
            initDefault: null,
            resetDef: 0
        }),
        methods: {
            changeDefault(newDefault) {
                this.defaultAlg = newDefault;
            },
            save(close) {
                this.axios.post(process.env.VUE_APP_BACKEND_URI + '/settings/default_algorithm', {
                        algorithm: this.defaultAlg
                    },{}
                );
                this.initDefault = this.defaultAlg;
                if (close) this.$emit('close');
            },
            cancel() {
                this.defaultAlg = this.initDefault;
                this.$emit('close');
            }
        },
        mounted() {
            this.defaultAlg = this.default.value;
            this.initDefault = this.default.value;
        }
    }
</script>

<style scoped>
    td:first-child {
        width: 33%;
    }
</style>
