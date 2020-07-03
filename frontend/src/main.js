import Vue from 'vue'
import App from './App.vue'

// Import axios, a library for making elegant http requests
import axios from 'axios';

// Import vuetify, a material design component library
import vuetify from './plugins/vuetify';

// Import leaflet, a library for layers on the map
import 'leaflet/dist/leaflet.css';

// Import leaflet.movingmarkers, a library for moving markers around on the map
import 'Leaflet-MovingMaker/MovingMarker.js'

// Import leaflet.extra-markers, a library for custom markers on the map
import 'leaflet-extra-markers/dist/css/leaflet.extra-markers.min.css';
import 'leaflet-extra-markers/dist/js/leaflet.extra-markers.min.js';

// Import fontawesome, a library for custom icons on the markers
import '@fortawesome/fontawesome-free/css/all.css'
import '@fortawesome/fontawesome-free/js/all.js'

Vue.config.productionTip = false

Vue.prototype.axios = axios;

new Vue({
  vuetify,
  render: h => h(App)
}).$mount('#app')
