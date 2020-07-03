<template>
    <div style="display: none;">
        <slot v-if="ready"></slot>
    </div>
</template>

<script>
    import L from 'leaflet'
    import {findRealParent, propsBinder} from 'vue2-leaflet'

    /**
     * Defines the properties of the MovingMarker.
     */
    const props = {
        /**
         * The locations of the route.
         */
        route: {
            type: Object,
            required: true
        },
        /**
         * An array of all deliveries.
         */
        deliveries: {
            type: Array,
            required: true
        },
        delays: {
            type: Array,
            default: []
        },
        /**
         * An array of all start locations.
         */
        starts: {
            type: Array,
            required: true
        },
        /**
         * An array of all modeChanges.
         */
        modeChanges: {
            type: Array,
            required: true
        },
        /**
         * An array of all pickups.
         */
        pickups: {
            type: Array,
            required: true
        },
        /**
         * An array of all handovers.
         */
        handovers: {
            type: Array,
            required: true
        },
        /**
         * The duration of the route.
         */
        duration: {
            type: Number,
            required: true
        },
        /**
         * The duration of the longest route.
         */
        maxDuration: {
            type: Number,
            required: true
        },
        /**
         * The locations of the MovingMarker.
         */
        lngLats: {
            type: [Object, Array],
            custom: true,
            required: true
        },
        /**
         * The iconColor of the MovingMarker.
         */
        iconColor: {
            type: String,
            custom: false,
            default: 'black'
        },
        /**
         * The visibility state of the MovingMarker.
         */
        visible: {
            type: Boolean,
            custom: true,
            default: true
        },
        /**
         * The zIndex of the MovingMarker.
         */
        zIndexOffset: {
            type: Number,
            custom: false,
            default: 1000
        },
        /**
         * The options of the MovingMarker.
         */
        options: {
            type: Object,
            default: () => ({})
        },
        /**
         * The capacity of the corresponding vehicle.
         */
        vehicleCapacity: {
            type: Number,
            default: -1
        }
    };

    /**
     * Converts lngLats to latLngs.
     * @param {Array} lngLats The lngLats to convert.
     */
    function lngLatsToLatLngs(lngLats) {
        return lngLats.map(lngLat => [lngLat[1], lngLat[0]]);
    }

    export default {
        name: 'l-moving-marker',
        props: props,
        /**
         * Stores some properties as local data.
         */
        data () {
            return {
                ready: false,
                dur: null,
                maxDur: null,
                spd: null,
                latLngs: null,
                latLngsLength: null,
                storage: [],
                locationListeners: [], // in format of { location: Array, callback: function(boolean hasPassed) }
                pastPickups: null,
                capacity: null,
                initStorage: null,
                markerStyle: "z-index:500;position:absolute;right:-30px;top:-30px;background:"+this.iconColor+";text-align:center;font-size:14px;color:black;padding:3px 8px;border-radius:30px 30px 30px 30px;",
                iconStyle: "position:absolute;top:-20px;right:-15px;"
            };
        },
        /**
         * Gets called when the MovingMarker is mounted.
         */
        mounted () {
            this.mdchngs = this.$props.modeChanges;
            this.dur = this.$props.duration;
            this.maxDur = this.$props.maxDuration;
            this.spd = 100;
            this.latLngs = lngLatsToLatLngs(this.$props.lngLats);
            this.latLngsLength = this.latLngs.length;
            this.capacity = this.vehicleCapacity === -1 ? "/"+"&#8734" : "/"+this.vehicleCapacity;
            this.animate(this.latLngs, this.dur);
            this.ready = true;

            this.$root.$on('startMovingMarker', this.start);
            this.$root.$on('pauseMovingMarker', this.pause);
            this.$root.$on('resetMovingMarker', this.reset);
            this.$root.$on('speedChangeMovingMarker', this.changeSpeed);
            this.$root.$on('positionChangeMovingMarker', this.changePosition);

            this.setStartMode();
            this.registerDeliveryListeners();
            this.registerHandoverListeners();
            this.registerModeListeners();
            this.registerPickupListeners();

            if (typeof this.timer !== 'undefined') return; // never start timer loop twice
            this.startTimer();
            this.initStorage = this.storage;
        },
        /**
         * Removes the layer on the map, before the MovingMarker is removed.
         */
        beforeDestroy () {
            if (this.mapObject.isStarted()) {
                this.mapObject.stop();
            }
            this.parentContainer.removeLayer(this);
        },
        methods: {
            /**
             * Registers location listeners for delivery points.
             */
            registerDeliveryListeners: function() {
                this.deliveries.forEach((delivery) => {
                    if (this.route.properties.number !== delivery.properties.route_number) return;
                    let coords = delivery.geometry.coordinates;
                    const forDelivery = delivery;
                    this.registerLocationListener(coords, (hasPassed) => {
                        if (hasPassed) {
                            forDelivery.properties.style.markerColor = "black";
                            this.removeDelivery(forDelivery.properties.number);
                        } else {
                            forDelivery.properties.style.markerColor = "white";
                            this.storage.push(forDelivery.properties.number);
                        }
                        this.sendToMap(forDelivery, hasPassed);
                        this.updateMarker();
                    });
                });
            },
            /**
             * Method that fires an event to the parent to add a parcel to a depot if the delivery is done at a depot.
             * @param {Object} delivery The corresponding delivery.
             * @param {Boolean} passed Whether the MovingMarker has passed.
             */
            sendToMap: function(delivery, passed) {
                if (passed) {
                    this.$emit('addDelivery', {
                        geometry: delivery.geometry,
                        properties: {parcels: [delivery.properties.number]},
                        toDepot: delivery.properties.to_depot
                    });
                } else if (!passed) {
                    this.$emit('removeDelivery', {
                        geometry: delivery.geometry,
                        properties: {parcels: [delivery.properties.number]},
                        toDepot: delivery.properties.to_depot
                    });
                }
            },
            /**
             * Method that removes a delivery from the moving marker's storage.
             * @param {Object} delivery The corresponding delivery.
             */
            removeDelivery: function(delivery) {
                for (let i = 0; i < this.storage.length; i++) {
                    if (this.storage[i] === delivery) {
                        this.storage.splice(i, 1);
                    }
                }
            },
            /**
             * Registers location listeners for handover points.
             */
            registerHandoverListeners: function() {
                this.handovers.forEach((handover) => {
                    if (this.route.properties.number !== handover.properties.route_number) return;
                    let coords = handover.geometry.coordinates;
                    const forHandover = handover;
                    let started = false;
                    this.registerLocationListener(coords, (hasPassed) => {
                        if (hasPassed) {
                            started = true;
                            this.handover(forHandover, started);
                        } else {
                            this.handover(forHandover, started);
                        }
                        this.updateMarker();
                    });
                });
            },
            /**
             * Registers location listeners for mode change points.
             */
            registerModeListeners: function() {
                // register listeners for deliveries
                this.modeChanges.forEach((modeChange) => {
                    let routeNumber = modeChange.properties.route_number;
                    if (this.route.properties.number !== routeNumber) return;
                    let coords = modeChange.geometry.coordinates;
                    this.registerLocationListener(coords, (hasPassed) => {
                        if (hasPassed) {
                            this.changeMode();
                        }
                        this.updateMarker();
                    });
                });
            },
            /**
             * Change the mode of the vehicle.
             */
            setStartMode: function () {
                this.mode = 'Manual';
                this.starts.forEach((start) => {
                    let routeNumber = start.properties.vehicle;
                    if (this.route.properties.number === routeNumber) {
                        this.mode = start.properties.mode;
                    }
                });
                this.changeIcon();
            },
            /**
             * Change the mode of the vehicle.
             */
            changeMode: function() {
                if (this.mode === 'Autonomous') {
                    this.mode = 'Manual';
                } else {
                    this.mode = 'Autonomous';
                }
                this.changeIcon();
            },
            /**
             * Change the icon of the vehicle.
             */
            changeIcon: function() {
                if (this.mode === 'Autonomous') {
                    this.icon = 'robot';
                } else {
                    this.icon = 'car';
                }
            },
            /**
             * Registers location listeners for pickup points.
             */
            registerPickupListeners: function() {
                this.pickups.forEach((pickup) => {
                    if (this.route.properties.number !== pickup.properties.route_number) return;
                    let coords = pickup.geometry.coordinates;
                    const forPickup = pickup;
                    let started = false;
                    this.registerLocationListener(coords, (hasPassed) => {
                        if (hasPassed) {
                            started = true;
                            forPickup.properties.parcels.forEach((p) => this.storage.push(p));
                            this.$emit('removeFromMarker', forPickup);
                        } else {
                            forPickup.properties.parcels.forEach((p) => this.removeDelivery(p));
                            if (started) this.$emit('addToMarker', forPickup);
                        }
                        this.updateMarker();
                    });
                });
            },
            /**
             * Method that updates the storage and sends messages to the map when a handover takes place.
             * @param {Object} handover The corresponding handover.
             * @param {Boolean} started Whether the simulation has started.
             */
            handover: function(handover, started) {
                handover.properties.total_parcels.forEach((p) => {
                    if (this.storage.includes(p)) {
                        this.removeDelivery(p);
                        if (this.previousIndex !== 0 ) {
                            this.$emit('addToMarker', {geometry: handover.geometry, properties: {parcels: [p]}});
                        }
                    } else if (started) {
                        this.storage.push(p);
                        this.$emit('removeFromMarker', {geometry: handover.geometry, properties: {parcels: [p]}});
                    }
                })
            },
            /**
             * Method that periodically checks where this truck currently is,
             * and compares this to this.latLngs to find out where the truck is in time.
             */
            startTimer: function() {
                this.previousIndex = 0;
                this.timer = setInterval(() => {
                    // calculate where on the route the vehicle is
                    let currentlyAt = this.mapObject.getLatLng();
                    let currentlyAtArr = [currentlyAt.lat, currentlyAt.lng];
                    // find nearest index we are currently at
                    let closestCurrentlyMetric = this.closest(currentlyAtArr, this.latLngs.slice(this.previousIndex, this.previousIndex + 40));
                    let closestCurrently = closestCurrentlyMetric[1];

                    this.currentlyAtIndex = this.latLngs.indexOf(closestCurrently);
                    this.previousIndex = this.currentlyAtIndex;

                    // check for all registered listeners if a coordinate on the route is known
                    this.locationListeners.forEach((listener) => {
                        if (typeof listener.locationOnRoute === 'undefined' || this.latLngs.indexOf(listener.locationOnRoute) === -1) {
                            let closestOnRoute = this.closest(listener.location, this.latLngs);
                            let distanceToRoute = closestOnRoute[0];
                            let locationOnRoute = closestOnRoute[1];
                            if(Math.sqrt(distanceToRoute) < 1e-3){
                                listener.locationOnRoute = locationOnRoute;
                                listener.lastKnownStatePassed = false;
                                listener.callback(false);
                            } else {
                                throw "Location passed to registerLocationListener() was too far away from the route";
                            }
                        }
                    });
                    this.traverseListeners();
                }, 50); // few times per second, calculation above should not be very time consuming
            },
            /**
             * Method that traverses all listeners.
             */
            traverseListeners: function() {
                this.locationListeners.forEach((listener) => {
                    let packageAtIndex = this.latLngs.indexOf(listener.locationOnRoute);

                    if (packageAtIndex < this.currentlyAtIndex) {
                        // we passed the given location
                        if (!listener.lastKnownStatePassed) {
                            listener.lastKnownStatePassed = true;
                            listener.callback(true);
                        }
                    } else {
                        // we did not yet pass the given location
                        if (listener.lastKnownStatePassed) {
                            listener.lastKnownStatePassed = false;
                            listener.callback(false);
                        }
                    }
                })
            },
            /**
             * Method that registers a callback function.
             * @param {Array} location The location where the callback function is called.
             * @param {Function} callback The callback function should be in form: callback(boolean hasPassed).
             */
            registerLocationListener: function(location, callback) { // callback
                // swap coords because latlong and longlat are different
                this.locationListeners.push({ location: [location[1], location[0]], callback: callback });
            },
            /**
             * Starts moving the MovingMarker.
             */
            start: function () {
                this.mapObject.start();
            },
            /**
             * Pauses moving the MovingMarker.
             */
            pause: function () {
                this.mapObject.pause();
            },
            resetSimulation: function () {
                let added_dur = 0;
                this.delays.forEach((delay) => {
                    added_dur += delay.properties.duration;
                });
                added_dur *= 60000;
                this.$root.$emit('resetSimulation', this.duration + added_dur);
            },
            /**
             * Resets the MovingMarker to its initial state.
             */
            reset: function () {
                if (this.mapObject.isStarted()) {
                    this.mapObject.stop();
                }
                this.parentContainer.removeLayer(this);
                this.previousIndex = 0;
                this.setStartMode();
                this.storage = [];
                this.latLngs = lngLatsToLatLngs(this.$props.lngLats);
                this.animate(this.latLngs, this.dur);
            },
            /**
             * Changes the speed of the MovingMarker.
             * @param {Number} speed The new speed of the MovingMarker as a factor of the real speed.
             */
            changeSpeed: function (speed) {
                let oldSpeed = this.spd.valueOf();
                this.spd = speed;
                let duration = Math.round(this.dur / speed);
                this.mapObject._durations = this.mapObject._createDurations(this.mapObject._latlngs, duration);
                this.mapObject._currentDuration = this.mapObject._durations[0];
                for (let [key, value] of Object.entries(this.mapObject._stations)) {
                    this.mapObject._stations[key] = value * (oldSpeed / speed);
                }
            },
            /**
             * Methods that returns the closest location to an array of locations.
             * @param {Array} arr The location to compare.
             * @param {Array} fromWhich The array of locations to compare.
             */
            closest: function(arr, fromWhich) {
                let closest = [0,0];
                let smallestDistance = 100000000;
                fromWhich.forEach(latLng => {
                    let distance = this.distance(arr, latLng);
                    if (distance < smallestDistance){
                        closest = latLng;
                        smallestDistance = distance;
                    }
                });
                return [smallestDistance, closest];
            },
            /**
             * Methods that returns the distance between two given locations.
             * @param {Array} arr The first location to compare.
             * @param {Array} latLng The second location to compare.
             */
            distance: function(arr, latLng) {
                return Math.pow(arr[0] - latLng[0], 2) + Math.pow(arr[1] - latLng[1], 2)
            },
            /**
             * Changes the position of the MovingMarker.
             * @param {Number} sliderPercentage The new position of the MovingMarker in percentage of the longest route.
             */
            changePosition: function (sliderPercentage, running) {
                // Remove the MovingMarker from map
                this.mapObject.pause();
                this.parentContainer.removeLayer(this);
                if ((sliderPercentage / 100) < (this.dur / this.maxDur)) {
                    // Move the new MovingMarker to a percentage of the route
                    let latLngs = lngLatsToLatLngs(this.$props.lngLats);
                    let positionFraction = (this.maxDur * sliderPercentage) / (this.dur * 100);
                    let spliceAt = Math.round(positionFraction * (latLngs.length - 1));
                    latLngs.splice(0, spliceAt);
                    // Set the duration, so the current speed is maintained
                    let dur = Math.round((1 - positionFraction) * this.dur);
                    // Create the new MovingMarker
                    this.animate(latLngs, dur);
                    // Start the MovingMarker
                    if (running) this.mapObject.start();
                } else {
                    this.animate([this.latLngs[this.latLngs.length - 1]], 0);
                }
            },
            /**
             * Adds the MovingMarker to the map.
             * @param {Array} latLngs The locations of the MovingMarker.
             * @param {Number} dur The duration of the MovingMarker.
             * @see See [Documentation](https://github.com/ewoken/Leaflet.MovingMarker) of the MovingMarker.
             */
            animate: function (latLngs, dur) {
                var options = this.options;
                // Set icon to be the truck icon with badge to display the number of parcels
                options.icon = L.divIcon({});
                // Create the mapObject, in this case the actual moving marker
                this.mapObject = L.Marker.movingMarker(latLngs, Math.round(dur / this.spd), options);

                var pastDelayLocations = [];

                this.delays.forEach((d) => {
                    let latLng = [d.geometry.coordinates[1], d.geometry.coordinates[0]];
                    if (!pastDelayLocations.some((l) => (l[0] == latLng[0] && l[1] == latLng[1]))) {
                        let closest = this.closest(latLng, latLngs);
                        let index = latLngs.indexOf(closest[1]);

                        this.mapObject.addStation(index, 60000 * d.properties.duration / this.spd);

                        pastDelayLocations.push(latLng);
                    }
                });

                this.updateMarker();
                // Reset the marker at the end of the animation
                this.mapObject.on('end', this.resetSimulation);
                // Enable responding to DomEvents such as clicks
                L.DomEvent.on(this.mapObject, this.$listeners);
                // Bind the props
                propsBinder(this, this.mapObject, props);
                // Find the parent, or the map, of this marker
                const parent = this.$parent;
                this.parentContainer = findRealParent(parent);
                // Add the marker layer to the map
                this.parentContainer.addLayer(this, !this.visible);
            },
            /**
             * Methods that updates the MovingMarker icon and tooltip.
             */
            updateMarker: function() {
                let parcelString = "";
                this.storage.forEach(p => {
                    parcelString += p + ", ";
                });
                parcelString = parcelString.substr(0, parcelString.length-2);
                const icon = L.divIcon({
                    className: "markerWithBadge",
                    html: "<span style='"+this.markerStyle+"'>"+this.storage.length+this.capacity+"</span>" +
                        "<v-icon class='mdi mdi-36px mdi-"+this.icon+"' style='"+this.iconStyle+"'/>"
                });
                this.mapObject.setIcon(icon);
                this.mapObject.unbindTooltip();
                this.mapObject.bindTooltip("<h2>Vehicle "+this.route.properties.number+"</h2>" +
                    "Parcels: "+parcelString+"<br/>" +
                    "Mode: "+this.mode,
                    {sticky: true}
                );
            },
            /**
             * Sets the visibility state of the MovingMarker to newVal if not equal to oldVal.
             * @param {Boolean} newVal The new visibility state of the MovingMarker.
             * @param {Boolean} oldVal The old visibility state of the MovingMarker.
             */
            setVisible (newVal, oldVal) {
                if (newVal === oldVal) return;
                if (this.mapObject) {
                    if (newVal) {
                        this.parentContainer.addLayer(this);
                    } else {
                        this.parentContainer.removeLayer(this);
                    }
                }
            }
        }
    }
</script>

<style scoped>
</style>
