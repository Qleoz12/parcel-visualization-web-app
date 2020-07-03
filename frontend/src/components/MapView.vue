<template>
<!-- The leaflet map component -->
<l-map
    ref="map"
    style='height: 100%; z-index: 0; display: inline-block'
    :center="center"
    :zoom="zoom"
    :options="{zoomSnap:0.25, worldCopyJump: true, wheelPxPerZoomLevel: 15}"
    @ready="newMapSize"
    @update:zoom="updateZoom"
    @update:center="updateCenter"
>
    <!-- UNCOMMENT TO ENABLE USING MULTIPLE MAPS -->
    <!-- <l-control-layers/> -->
    <l-control-scale
        position="bottomright"
        :imperial="false"
        :metric="true"
    />
    <!-- Button for toggling the display of an overlay showing roads that allow autonomous vehicles -->
    <l-control position="bottomleft">
        <v-btn class="mt-5" color="tertiary" @click="toggleAutonomousRoads()">
            <span v-show="!filter.autonomousRoads" class="mr-3"><v-icon>mdi-eye</v-icon></span>
            <span v-show="filter.autonomousRoads" class="mr-3"><v-icon>mdi-eye-off</v-icon></span>
            autonomous roads
        </v-btn>
    </l-control>
    <!-- The layer that renders the artwork of the actual map  -->
    <l-tile-layer
        v-for="tileProvider in tileProviders"
        :key="tileProvider.name"
        :name="tileProvider.name"
        :visible="tileProvider.visible"
        :url="tileProvider.url"
        :attribution="tileProvider.attribution"
        layer-type="base"
    />
    <!-- Vector tile layer for the autonomous road network -->
    <l-vt-grid-layer
        :geojson="autonomousGeojson"
        :visible="filter.autonomousRoads"
    />
    <!-- Show the routes, delivery points and depots that were received from the back-end on the map -->
    <l-feature-group ref="handovers">
        <template v-if="handovers">
            <l-geo-json
                v-for="handover in filterStorages(handovers)"
                :key="'h'+handover.properties.key"
                :visible="showHandover(handover.properties.route_number)"
                :geojson="handover"
                :options="geojsonBadgeOptions"
            />
        </template>
        <l-geo-json
            v-for="handover in handovers"
            :key="handover.properties.key"
            :visible="showHandover(handover.properties.vehicle)"
            :geojson="handover"
            :options="geojsonOptions"
        />
    </l-feature-group>
    <l-feature-group ref="pickups">
        <l-geo-json
            v-for="pickup in pickups"
            :key="pickup.properties.title"
            :visible="showHandover(pickup.properties.vehicle)"
            :geojson="pickup"
            :options="geojsonOptions"
        />
    </l-feature-group>
    <l-feature-group ref="modeChanges">
        <l-geo-json
            v-for="modeChange in modeChanges"
            :key="modeChange.properties.vehicle.toString()+modeChange.properties.arrival_m.toString()"
            :visible="showHandover(modeChange.properties.vehicle)"
            :geojson="modeChange"
            :options="geojsonOptions"
        />
    </l-feature-group>
    <l-feature-group ref="starts">
        <l-geo-json
                v-for="start in starts"
                :key="start.properties.route_number"
                :visible="show(start.properties.route_number)"
                :geojson="start"
                :options="geojsonOptions"
        />
    </l-feature-group>
    <l-feature-group ref="deliveries">
        <template v-if="deliveries">
            <l-geo-json
                v-for="delivery in filterStorages(deliveries)"
                :key="'p'+delivery.properties.parcels[0]"
                :visible="show(delivery.properties.route_number) && filter.deliveryPoints"
                :geojson="delivery"
                :options="geojsonBadgeOptions"
                @click="toggleSingleRoute(delivery)"
            />
        </template>
        <l-geo-json
            v-for="delivery in deliveries"
            :key="delivery.properties.number"
            :visible="show(delivery.properties.route_number) && filter.deliveryPoints"
            :geojson="delivery"
            :options="geojsonOptions"
            @click="toggleSingleRoute(delivery.properties.number)"
        />
    </l-feature-group>
    <l-feature-group ref="singleRoutes">
        <template v-for="singleRoute in singleRoutes">
            <l-geo-json
                v-if="singleRoute.properties.number === singleRouteNum"
                :key="singleRoute.properties.number"
                :geojson="singleRoute"
                :options="geojsonOptions"
                @click="toggleSingleRoute(singleRoute.properties.number)"
            />
        </template>
    </l-feature-group>
    <l-feature-group ref="routes">
        <l-geo-json
            v-for="route in routes"
            :key="route.properties.number"
            :visible="show(route.properties.number) && filter.routes"
            :geojson="route"
            :options="geojsonOptions"
            @add="zoomToFeatures()"
            @click="showOneRoute(route.properties.number)"
        />
    </l-feature-group>
    <l-feature-group ref="depots">
        <l-geo-json
            v-for="depot in depots"
            :key="depot.properties.number"
            :visible="showDepot(depot.properties.route_numbers) && filter.depots"
            :geojson="depot"
            :options="geojsonOptions"
        />
        <l-geo-json
            v-for="depot in depots"
            :key="depot.properties.length"
            :visible="showDepot(depot.properties.route_numbers)"
            :geojson="depot"
            :options="geojsonBadgeOptions"
        />
    </l-feature-group>
    <l-moving-marker
        v-for="route in routes"
        :key="route.properties.number"
        :route="route"
        :deliveries="deliveries"
        :starts="starts"
        :delays="delays.filter(d => d.properties.route_number === route.properties.number)"
        :modeChanges="modeChanges"
        :pickups="pickups"
        :handovers="handovers"
        :duration="(route.properties.duration_h * 60 + route.properties.duration_m) * 60000"
        :maxDuration="maxDuration"
        :lngLats="route.geometry.coordinates"
        :iconColor="route.properties.style.color"
        :visible="show(route.properties.number)"
        :options="{zIndexOffset: -100, riseOnHover: true}"
        :vehicleCapacity="vehicleCapacity[route.properties.number-1]"
        @removeFromMarker="removeParcelFromMarker"
        @addToMarker="addParcelToMarker"
        @removeDelivery="removeDelivery"
        @addDelivery="addDelivery"
        @restart="initBadges"
    />
</l-map>
</template>

<script>
import L from 'leaflet';
import LMovingMarker from './MovingMarker';
import LVtGridLayer from './VtGridLayer';
import {
    // LControlLayers, //UNCOMMENT TO ENABLE USING MULTIPLE MAPS
    LMap,
    LControlScale,
    LTileLayer,
    LFeatureGroup,
    LGeoJson,
    LControl
} from 'vue2-leaflet';

export default {
    name: "MapView",
    props: {
        geojson: Object,
        maxDuration: Number,
        vehicleCapacity: Array
    },
    components: {
        // LControlLayers, //UNCOMMENT TO ENABLE USING MULTIPLE MAPS
        LMap,
        LControlScale,
        LTileLayer,
        LFeatureGroup,
        LGeoJson,
        LMovingMarker,
        LVtGridLayer,
        LControl
    }, data() {
        return {
            tileProviders: [{
                attribution: '&copy; <a target="_blank" href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a target="_blank" href="https://carto.com/attributions">CARTO</a>',
                name: 'Light',
                visible: true,
                url: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager_labels_under/{z}/{x}/{y}{r}.png'
            // UNCOMMENT TO ENABLE DARK MAP, BUT MAKES IT HARD TO SEE MARKERS
            // }, {
            //     attribution: '&copy; <a target="_blank" href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a target="_blank" href="https://carto.com/attributions">CARTO</a>',
            //     name: 'Dark',
            //     visible: false,
            //     url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
            }],
            zoom: 8,
            center: [52, 5],
            deliveries: null,
            depots: null,
            routes: null,
            delays: null,
            handovers: null,
            modeChanges: null,
            pickups: null,
            starts: null,
            oneRoute: 0,
            deliveryKey: 99,
            deliveryRoute: null,
            deliveryPoint: null,
            filter: {
                autonomousRoads: false,
                deliveryPoints: true,
                routes: true,
                depots: true,
            },
            singleRouteNum: -1,
            singleRoutes: [],
            autonomousGeojson: null,
            testOptions: {
                pointToLayer: function(geoJsonPoint, latlng) {
                    return L.marker(latlng, {
                        icon: L.ExtraMarkers.icon({
                            icon: 'fa-stopwatch',
                            iconColor: 'red',
                            prefix: 'fa',
                            svg: true
                        }),
                        riseOnHover: true
                    });
                },
            },
            geojsonOptions: {
                pointToLayer: function(geoJsonPoint, latlng) {
                    return L.marker(latlng, {
                        icon: L.ExtraMarkers.icon({
                            icon: geoJsonPoint.properties.style.icon,
                            iconColor: geoJsonPoint.properties.style.color,
                            markerColor: geoJsonPoint.properties.style.markerColor,
                            prefix: 'fa',
                            svg: true
                        }),
                        riseOnHover: true
                    });
                },
                style: function(geoJsonFeature) {
                    return geoJsonFeature.properties.style;
                },
                onEachFeature: function(feature, layer) {
                    let parcels = "";
                    switch (feature.properties.type) {
                        case "route":
                            layer.bindTooltip(
                                "<h2>" + feature.properties.title + "</h2>" +
                                "Total distance: " + Math.round(feature.properties.distance/1000*10)/10 + " km<br/>" +
                                "Total duration: " + feature.properties.duration_h + "h " + feature.properties.duration_m + "m<br/>" +
                                "<i>Click to hide/show other routes</i>",
                                {sticky: true}
                            );
                            break;
                        case "single_route":
                            layer.bindTooltip(
                                "<h2>" + feature.properties.title + "</h2>" +
                                "Total distance: " + Math.round(feature.properties.distance/1000*10)/10 + " km<br/>" +
                                "Total duration: " + feature.properties.duration_h + "h " + feature.properties.duration_m + "m<br/>" +
                                "<i>Click to hide route</i>",
                                {sticky: true}
                            );
                            break;
                        case "delivery":
                            if (feature.properties.parcels && feature.properties.parcels.length !== 0) {
                                parcels = "Parcels: ";
                                feature.properties.parcels.forEach(p => {
                                    parcels += p + ", "
                                });
                                parcels = parcels.substr(0, parcels.length - 2) + "<br/>";
                            }
                            layer.bindTooltip(
                                "<h2>" + feature.properties.title + "</h2>" +
                                "Traveled distance: " + Math.round(feature.properties.distance/1000*10)/10 + " km<br/>" +
                                "Arrival time: " + feature.properties.arrival_h + "h " + feature.properties.arrival_m + "m<br/>" +
                                parcels +
                                "<i>Click to show/hide route to this delivery</i>",
                                {sticky: true}
                            );
                            break;
                        default:
                            layer.bindTooltip("<h2>" + feature.properties.title + "</h2>", {sticky: true});
                            break;
                    }
                }
            },
            geojsonBadgeOptions: {
                pointToLayer: function(geoJsonPoint, latlng) {
                    return L.marker(latlng, {
                        icon: L.ExtraMarkers.icon({
                            icon: geoJsonPoint.properties.style.icon,
                            iconColor: geoJsonPoint.properties.style.color,
                            markerColor: geoJsonPoint.properties.style.markerColor,
                            innerHTML: "<div><span class='parcels-badge'>"+geoJsonPoint.properties.parcels.length+"</span></div>",
                            prefix: 'fa',
                            svg: true
                        }),
                        riseOnHover: true
                    });
                },
                onEachFeature: function(feature, layer) {
                    if (feature.properties.type === "depot" || feature.properties.type === "handover") {
                        let parcelString = "";
                        feature.properties.parcels.forEach(p => {
                            parcelString += p.toString() + ", "
                        })
                        parcelString = parcelString.substr(0, parcelString.length - 2);
                        layer.bindTooltip("<h2>" + feature.properties.title + "</h2>" +
                            "Parcels: " + parcelString,
                            {sticky: true}
                        );
                    }
                }
            }
        };
    },
    mounted() {
        this.deliveries = this.$props.geojson.features.filter((feature) => feature.properties.type === "delivery");
        this.depots = this.$props.geojson.features.filter((feature) => feature.properties.type === "depot");
        this.routes = this.$props.geojson.features.filter((feature) => feature.properties.type === "route");
        this.delays = this.$props.geojson.features.filter((feature) => feature.properties.type === "delayed");
        this.handovers = this.$props.geojson.features.filter((feature) => feature.properties.type === "handover");
        this.modeChanges = this.$props.geojson.features.filter((feature) => feature.properties.type === "mode_change");
        this.pickups = this.$props.geojson.features.filter((feature) => feature.properties.type === "pickup");
        this.starts = this.$props.geojson.features.filter((feature) => feature.properties.type === "start");
        this.singleRoutes = this.deliveries.map(function(x) {return x.properties.single_route});
        this.initBadges();
    },
    methods: {
        /**
         * Method that resets the depot storages to initial values.
         */
        initBadges: function() {
            this.initDepotBadges();
            this.filterStorages(this.deliveries).forEach(dlv => dlv.properties.parcels = []);
            this.filterStorages(this.handovers).forEach(ho => ho.properties.parcels = []);
        },
        /**
         * Method that resets the depot storages to initial values.
         */
        initDepotBadges() {
            this.depots.forEach(dep => {
                dep.properties.parcels = [];
            });
            this.pickups.forEach(pickup => {
                this.addToDepot(this.getDepot(pickup), pickup);
            });
        },
        /**
         * Method that filters the items in a list with parcels in their storage.
         */
        filterStorages(list) {
            return list.filter(x => x.properties.parcels.length > 0);
        },
        /**
         * Method that adds a parcel to a depot or deliveries' storage if it is not the delivery parcel itself.
         */
        addDelivery(parcel) {
            if (parcel.toDepot) {
                this.addParcelToMarker(parcel);
            } else {
                const index = this.find(this.deliveries, parcel)
                if (index > -1 && this.deliveries[index].properties.number !== parcel.properties.parcels[0]) {
                    this.deliveries[index].properties.parcels.push(parcel.properties.parcels[0]);
                }
            }
        },
        /**
         * Method that removes a parcel from a depot or a deliveries' storage if it is not the delivery parcel itself.
         */
        removeDelivery(parcel) {
            if (parcel.toDepot) {
                this.removeParcelFromMarker(parcel);
            } else {
                const index = this.find(this.deliveries, parcel)
                if (index > -1 && this.deliveries[index].properties.number !== parcel.properties.parcels[0]) {
                    this.deliveries[index].properties.parcels = this.deliveries[index].properties.parcels
                        .filter(x => x !== parcel.properties.parcels[0]);
                }
            }
        },
        /**
         * Method that adds a parcel to the marker that is available at its location.
         * The preferred marker is depot, otherwise delivery, and otherwise handover.
         */
        addParcelToMarker(parcel) {
            let index = this.getDepot(parcel);
            if (index > -1) {
                this.addToDepot(index, parcel);
            } else {
                let index = this.find(this.deliveries, parcel);
                if (index > -1) {
                    this.deliveries[index].properties.parcels.push(parcel.properties.parcels[0]);
                } else {
                    index = this.find(this.handovers, parcel);
                    if (index > -1) this.handovers[index].properties.parcels.push(parcel.properties.parcels[0]);
                }
            }
        },
        /**
         * Method that removes a parcel from its marker's storage.
         */
        removeParcelFromMarker: function(parcel) {
            let index = this.getDepot(parcel);
            if (index > -1) {
                this.removeFromDepot(index, parcel);
            } else {
                index = this.contains(this.deliveries, parcel);
                if (index > -1) {
                    this.deliveries[index].properties.parcels = this.deliveries[index].properties.parcels
                        .filter(x => x !== parcel.properties.parcels[0]);
                } else {
                    index = this.contains(this.handovers, parcel);
                    this.handovers[index].properties.parcels = this.handovers[index].properties.parcels
                        .filter(x => x !== parcel.properties.parcels[0]);
                }
            }
        },
        /**
         * Method to check whether a list has a parcel in its current storage.
         */
        contains: function(list, parcel) {
            for (let i = 0; i < list.length; i++) {
                if (list[i].properties.parcels.includes(parcel.properties.parcels[0])) {
                    return i;
                }
            }
            return -1;
        },
        /**
         * Method to check whether a list contains a point at a given location.
         */
        find: function(list, parcel) {
            for (let i = 0; i < list.length; i++) {
                if (list[i].geometry.coordinates[0] === parcel.geometry.coordinates[0] && list[i].geometry
                    .coordinates[1] === parcel.geometry.coordinates[1]) {
                    return i;
                }
            }
            return -1;
        },
        /**
         * Method to alter a depot's parcel storage.
         * Call this method when encountering a pickup.
         */
        removeFromDepot(index, pickup) {
            const parcels = pickup.properties.parcels;
            parcels.forEach(p => {
                if (this.depots[index].properties.parcels.includes(p)) {
                    for (let i = 0; i < this.depots[index].properties.parcels.length; i++) {
                        if (this.depots[index].properties.parcels[i] === p) {
                            this.depots[index].properties.parcels.splice(i, 1);
                            break;
                        }
                    }
                }
            });
            this.updateDepotColor();
        },
        /**
         * Method to add a parcel to a depot's storage
         */
        addToDepot(index, pickup) {
            pickup.properties.parcels.forEach(p => {
                if (!this.depots[index].properties.parcels.includes(p)) {
                    this.depots[index].properties.parcels.push(p)
                }
            });
            this.updateDepotColor();
        },
        /**
         * Method to update the color of a depot icon.
         */
        updateDepotColor() {
            this.depots.forEach(dep => {
                if (dep.properties.parcels.length === 0) {
                    dep.properties.style.color = "white";
                    dep.properties.style.markerColor = "black";
                } else {
                    dep.properties.style.color = "black";
                    dep.properties.style.markerColor = "white";
                }
            })
        },
        /**
         * Method to find the depot at a pickup location.
         */
        getDepot(pickup) {
            for (let i = 0; i < this.depots.length; i++) {
                if (this.depots[i].geometry.coordinates[0] === pickup.geometry.coordinates[0] && this.depots[i]
                    .geometry.coordinates[1] === pickup.geometry.coordinates[1]) {
                    return i;
                }
            }
            return -1;
        },
        /**
         * Method to show one route
         */
        showOneRoute(route) {
            if (this.oneRoute == route) {
                this.oneRoute = 0;
            } else {
                this.oneRoute = route;
            }
        },
        /**
         * Zooms and pans the map to the bounds of the routes
         */
        zoomToFeatures() {
            let bounds = this.$refs.routes.mapObject.getBounds();
            this.$refs.map.mapObject.flyToBounds(bounds, {padding: [25, 25]});
        },
        /**
         * Method called to change to new size
         */
        newMapSize() {
            this.$refs.map.mapObject.invalidateSize(false);
        },
        /**
         * Method to decide whether to show a certain route
         */
        show(routeNumber) {
            if (this.deliveryRoute != null && this.deliveryRoute.properties.number == routeNumber) {
                return false;
            } else {
                return (this.oneRoute == 0 || this.oneRoute == routeNumber);
            }

        },
        /**
         * Method to decide whether to show certain depots
         */
        showDepot(routeNumbers) {
            return (this.oneRoute == 0 || routeNumbers.includes(this.oneRoute));
        },
        /**
         * Method to decide whether to show a certain depot
         */
        showHandover(routeNumber) {
            return (this.oneRoute == 0 || routeNumber == this.oneRoute);
        },
        /**
         * Method to toggle the visibility of the autonomous roads overlay
         */
        toggleAutonomousRoads() {
            this.filter.autonomousRoads = !this.filter.autonomousRoads;
            if (this.autonomousGeojson != null) return;
            this.axios
                .get(process.env.VUE_APP_BACKEND_URI + '/autonomous/geojson')
                .then(response => {
                    this.autonomousGeojson = response.data
                })
        },
        /**
         * Method that gets called when the map zoom is updated to check whether to show delivery points
         * @param zoom the new zoom level of the map
         */
        updateZoom(zoom) {
            this.zoom = zoom;
            this.filter.deliveryPoints = zoom > 9;
        },
        /**
         * Method that gets called when the map center is updated
         * @param center the new center of the map
         */
        updateCenter(center) {
            this.center = center;
        },
        /**
         * Method that toggles the display of overlays for individual delivery routes.
         * @param num: the delivery number
         */
        toggleSingleRoute(num) {
            if (this.singleRouteNum === num) {
                this.singleRouteNum = -1;
            } else {
                this.singleRouteNum = num;
            }
        }
    }
}
</script>

<style>
    .parcels-badge {
        position: absolute;
        right:-13px;
        top:-8px;
        background:black;
        text-align: center;
        border-radius: 30px 30px 30px 30px;
        color:white;
        padding:3px 8px;
        font-size:14px;
    }
</style>
