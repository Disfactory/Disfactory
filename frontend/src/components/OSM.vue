<template>
  <div id="map"></div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";
import { Map, View } from "ol";
import TileLayer from "ol/layer/Tile";
import WMTS from "ol/source/WMTS";
import WMTSTileGrid from "ol/tilegrid/WMTS";
import { get as getProjection } from "ol/proj";
import { getWidth, getTopLeft } from "ol/extent";

import "ol/ol.css";

@Component
export default class OSM extends Vue {
  mounted() {
    const projection = getProjection("EPSG:3857");
    const projectionExtent = projection.getExtent();
    const resolutions = new Array(20);
    const size = getWidth(projectionExtent) / 256;
    const matrixIds = new Array(20);
    for (let z = 0; z < 20; ++z) {
      // generate resolutions and matrixIds arrays for this WMTS
      resolutions[z] = size / Math.pow(2, z);
      matrixIds[z] = z;
    }

    new Map({
      target: "map",
      layers: [
        new TileLayer({
          source: new WMTS({
            matrixSet: "EPSG:3857",
            format: "image/png",
            url: "https://wmts.nlsc.gov.tw/wmts",
            layer: "EMAP",
            tileGrid: new WMTSTileGrid({
              origin: getTopLeft(projectionExtent),
              resolutions: resolutions,
              matrixIds: matrixIds
            }),
            style: "default",
            wrapX: true,
            attributions:
              '<a href="https://maps.nlsc.gov.tw/" target="_blank">國土測繪圖資服務雲</a>'
          }),
          opacity: 0.5
        }),
        new TileLayer({
          source: new WMTS({
            matrixSet: "EPSG:3857",
            format: "image/png",
            url: "https://wmts.nlsc.gov.tw/wmts/LUIMAP/{Style}/{TileMatrixSet}/{TileMatrix}/{TileRow}/{TileCol}",
            layer: "LUIMAP",
            requestEncoding: 'REST',
            tileGrid: new WMTSTileGrid({
              origin: getTopLeft(projectionExtent),
              resolutions: resolutions,
              matrixIds: matrixIds
            }),
            tileLoadFunction: function (imageTile, src) {
              // console.log(imageTile.getTileCoord());
              (imageTile as any).getImage().src = src;
            },
            style: "default",
            wrapX: true,
            attributions:
              '<a href="https://maps.nlsc.gov.tw/" target="_blank">國土測繪圖資服務雲</a>'
          }),
          opacity: 0.5
        })
      ],
      view: new View({
        center: [0, 0],
        zoom: 2
      })
    });
  }
}
</script>

<style lang="scss" scoped>
#map {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 100%;
}
</style>
