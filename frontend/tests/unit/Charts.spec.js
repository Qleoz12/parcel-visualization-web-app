import BarChart from '@/components/Charts/BarChart.vue'
import LineChart from '@/components/Charts/LineChart.vue'
import DoughnutChart from '@/components/Charts/DoughnutChart.vue'
import ChartList from '@/components/ChartList.vue'
import Vuetify from 'vuetify'

import {
    mount,
    createLocalVue, shallowMount
} from '@vue/test-utils'
import sinon from 'sinon'

const localVue = createLocalVue()
localVue.use(Vuetify)

describe('ChartList.vue', () => {
    let vuetify

    beforeEach(() => {
        vuetify = new Vuetify()
    });

    it('should render a line chart', () => {
        const wrapper = mount(ChartList,{localVue, vuetify});
        expect(wrapper.contains(LineChart)).toBe(true);
    });

    it('should render a bar chart', () => {
        const wrapper = mount(ChartList,{localVue, vuetify});
        expect(wrapper.contains(BarChart)).toBe(true);
    });

    it('should render a doughnut chart', () => {
        const wrapper = mount(ChartList,{localVue, vuetify});
        expect(wrapper.contains(DoughnutChart)).toBe(true);
    });

    it('should call line fill method on mount', () => {
        const spy = sinon.spy();
        shallowMount(ChartList,{
            localVue,
            vuetify,
            methods: {
                fillLineData: spy
            }
        });
        sinon.assert.calledOnce(spy);
    });

    it('should call bar fill method on mount', () => {
        const spy = sinon.spy();
        shallowMount(ChartList,{
            localVue,
            vuetify,
            methods: {
                fillBarData: spy
            }
        });
        sinon.assert.calledOnce(spy);
    });

    it('should call doughnut fill method on mount', () => {
        const spy = sinon.spy();
        shallowMount(ChartList,{
            localVue,
            vuetify,
            methods: {
                fillDoughnutData: spy
            }
        });
        sinon.assert.calledOnce(spy);
    });

    it('should call line fill method on click', () => {
        const spy = sinon.spy();
        const wrapper = shallowMount(ChartList,{
            localVue,
            vuetify,
            methods: {
                fillLineData: spy
            }
        });
        wrapper.find( "#linebutton").trigger('click');
        sinon.assert.calledTwice(spy);
    });

    it('should call bar fill method on click', () => {
        const spy = sinon.spy();
        const wrapper = shallowMount(ChartList,{
            localVue,
            vuetify,
            methods: {
                fillBarData: spy
            }
        });
        wrapper.find( "#barbutton").trigger('click');
        sinon.assert.calledTwice(spy);
    });

    it('should call doughnut fill method on click', () => {
        const spy = sinon.spy();
        const wrapper = shallowMount(ChartList,{
            localVue,
            vuetify,
            methods: {
                fillDoughnutData: spy
            }
        });
        wrapper.find( "#doughnutbutton").trigger('click');
        sinon.assert.calledTwice(spy);
    });
});
