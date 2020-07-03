<template>
  <div style="display: none;">
    <slot v-if="ready"></slot>
  </div>
</template>

<script>
  import L from 'leaflet'
  import { findRealParent } from 'vue2-leaflet'
  import geojsonvt from 'geojson-vt'

  const props = {
    visible: {
      type: Boolean,
      custom: true,
      default: true
    },
    geojson: {
      type: Object,
      custom: true,
      default: () => ({}),
    },
    options: {
      type: Object,
      default: () => ({
        maxZoom: 24,  // max zoom to preserve detail on
        tolerance: 2, // simplification tolerance (higher means simpler)
        extent: 4096, // tile extent (both width and height)
        buffer: 64,   // tile buffer on each side
        debug: 0,     // logging level (0 to disable, 1 or 2)
        indexMaxZoom: 4,        // max zoom in the initial tile index
        indexMaxPoints: 100000, // max number of points per tile in the index
        solidChildren: false,   // whether to include solid tile children in the index
        style: {
          weight: 2
        }
      })
    }
  }

  export default {
    name: 'l-vt-grid-layer',
    props: props,
    data () {
      return {
        ready: false
      }
    },
    watch: {
      geojson() {
        console.log("autonomous roads loaded")
        this.updateLayer()
      },
      visible() {
        if (this.geojson != null) {
          this.updateLayer()
        }
      }
    },
    mounted () {
      // Find the parent, or the map, of this layer
      this.parentContainer = findRealParent(this.$parent)
      this.ready = true;
    },
    beforeDestroy () {
      // If this layer is destroyed, its layer on the map should first be removed
      this.removeLayer()
    },
    methods: {
      removeLayer() {
        if (this.mapObject != null) {
          this.parentContainer.removeLayer(this)
        }
      },
      updateLayer() {
        this.ready = false;
        this.removeLayer();
        this.mapObject = L.gridLayer.geoJson(this.geojson, this.options);
        L.DomEvent.on(this.mapObject, this.$listeners);
        this.parentContainer.addLayer(this, !this.visible);
        this.ready = true;
      }
    }
  }

  L.GridLayer.GeoJSON = L.GridLayer.extend({
    options: {
      async: false
    },

    initialize: function (geojson, options) {
      L.setOptions(this, options);
      L.GridLayer.prototype.initialize.call(this, options);
      this.tileIndex = geojsonvt(geojson, this.options);
    },

    createTile: function (coords) {
      // create a <canvas> element for drawing
      var tile = L.DomUtil.create('canvas', 'leaflet-tile');
      // setup tile width and height according to the options
      var size = this.getTileSize();
      tile.width = size.x;
      tile.height = size.y;
      // get a canvas context and draw something on it using coords.x, coords.y and coords.z
      var ctx = tile.getContext('2d');
      // return the tile so it can be rendered on screen
      var tileInfo = this.tileIndex.getTile(coords.z, coords.x, coords.y);
      var features = tileInfo ? tileInfo.features : [];
      for (var i = 0; i < features.length; i++) {
          var feature = features[i];
          this.drawFeature(ctx, feature);
      }
      return tile;
    },

    drawFeature: function (ctx, feature) {
      // var typeChanged = type !== feature.type;
      var type = feature.type;
      ctx.beginPath();
      if (this.options.style) this.setStyle(ctx, this.options.style);
      if (type === 2 || type === 3) {
          for (var j = 0; j < feature.geometry.length; j++) {
              var ring = feature.geometry[j];
              for (var k = 0; k < ring.length; k++) {
                  var p = ring[k];
                  if (k) ctx.lineTo(p[0] / 16.0, p[1] / 16.0);
                  else ctx.moveTo(p[0] / 16.0, p[1] / 16.0);
              }
          }
      } else if (type === 1) {
          for (var h = 0; h < feature.geometry.length; h++) {
              var q = feature.geometry[h];
              ctx.arc(q[0] / 16.0, q[1] / 16.0, 2, 0, Math.PI * 2, true);
          }
      }
      if (type === 3) ctx.fill('evenodd');

      ctx.stroke();
    },

    setStyle: function (ctx, style) {
      var stroke = style.stroke || true;
      var color;
      if (stroke) {
        ctx.lineWidth = style.weight || 5;
        color = this.setOpacity(style.color, style.opacity);
        ctx.strokeStyle = color;

      } else {
        ctx.lineWidth = 0;
        ctx.strokeStyle = {};
      }
      var fill = style.fill || true;
      if (fill) {
        ctx.fillStyle = style.fillColor || '#03f';
        color = this.setOpacity(style.fillColor, style.fillOpacity);
        ctx.fillStyle = color;
      } else {
        ctx.fillStyle = {};
      }
    },

    setOpacity: function (color, opacity) {
      if (opacity) {
          var c = color || '#03f';
          if (c.iscolorHex()) {
              var colorRgb = c.colorRgb();
              return "rgba(" + colorRgb[0] + "," + colorRgb[1] + "," + colorRgb[2] + "," + opacity + ")";
          } else {
              return color;
          }
      } else {
          return color;
      }
    }
  })

  L.gridLayer.geoJson = function (geojson, options) {
    return new L.GridLayer.GeoJSON(geojson, options);
  };

  String.prototype.iscolorHex = function () {
    var sColor = this.toLowerCase();
    var reg = /^#([0-9a-fA-f]{3}|[0-9a-fA-f]{6})$/;
    return reg.test(sColor);
  }


  String.prototype.colorRgb = function () {
    var sColor = this.toLowerCase();
    if (sColor.length === 4) {
      var sColorNew = "#";
      for (var i = 1; i < 4; i += 1) {
        sColorNew += sColor.slice(i, i + 1).concat(sColor.slice(i, i + 1));
      }
      sColor = sColorNew;
    }
    var sColorChange = [];
    for (var x = 1; x < 7; x += 2) {
      sColorChange.push(parseInt("0x" + sColor.slice(x, x + 2)));
    }
    return sColorChange;
  };  

</script>

