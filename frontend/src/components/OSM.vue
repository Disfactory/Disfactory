<template>
  <div id="map"></div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { Map, View } from 'ol'
import TileLayer from 'ol/layer/Tile'
import WMTS from 'ol/source/WMTS'
import WMTSTileGrid from 'ol/tilegrid/WMTS'
import { get as getProjection } from 'ol/proj'
import { getWidth, getTopLeft } from 'ol/extent'
import { toGrayScale } from '../lib/image'

import 'ol/ol.css'

@Component
export default class OSM extends Vue {
  mounted () {
    const projection = getProjection('EPSG:3857')
    const projectionExtent = projection.getExtent()
    const resolutions = new Array(20)
    const size = getWidth(projectionExtent) / 256
    const matrixIds = new Array(20)
    for (let z = 0; z < 20; ++z) {
      // generate resolutions and matrixIds arrays for this WMTS
      resolutions[z] = size / Math.pow(2, z)
      matrixIds[z] = z
    }

    const map = new Map({
      target: 'map',
      layers: [
        new TileLayer({
          source: new WMTS({
            matrixSet: 'EPSG:3857',
            format: 'image/png',
            url: 'https://wmts.nlsc.gov.tw/wmts',
            layer: 'EMAP',
            tileGrid: new WMTSTileGrid({
              origin: getTopLeft(projectionExtent),
              resolutions: resolutions,
              matrixIds: matrixIds
            }),
            crossOrigin: 'Anonymous',
            style: 'default',
            wrapX: true,
            attributions:
              '<a href="https://maps.nlsc.gov.tw/" target="_blank">國土測繪圖資服務雲</a>'
          }),
          opacity: 0.5
        }),
        new TileLayer({
          source: new WMTS({
            matrixSet: 'EPSG:3857',
            format: 'image/png',
            url: 'https://wmts.nlsc.gov.tw/wmts/LUIMAP/{Style}/{TileMatrixSet}/{TileMatrix}/{TileRow}/{TileCol}',
            layer: 'LUIMAP',
            requestEncoding: 'REST',
            tileGrid: new WMTSTileGrid({
              origin: getTopLeft(projectionExtent),
              resolutions: resolutions,
              matrixIds: matrixIds
            }),
            tileLoadFunction: function (imageTile, src) {
              // console.log(imageTile.getTileCoord());
              // (imageTile as any).getImage().src = src

              const image = (imageTile as any).getImage()
              toGrayScale(src).then(newSrc => {
                image.src = newSrc
              })
            },
            crossOrigin: 'Anonymous',
            style: 'default',
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
    })

    map.on('click', function (event) {
      // console.log(event)
      map.forEachLayerAtPixel(event.pixel, function (layer, data) {
        const [r, g, b, a] = data
        console.log(`rgba(${r}, ${g}, ${b}, ${a})`)
        // console.log(layer.getProperties())
      }, {
        layerFilter: function (layer) {
          // only handle click event on LUIMAP
          return layer.getProperties().source.layer_ === 'LUIMAP'
        }
      })
    })
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
