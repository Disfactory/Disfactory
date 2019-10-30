<template>
  <div ref="root" id="map" />
</template>

<script lang="ts">
import { createComponent, onMounted, ref } from '@vue/composition-api'

import { Map, View } from 'ol'
import WMTS from 'ol/source/WMTS'
import WMTSTileGrid from 'ol/tilegrid/WMTS'
import { get as getProjection } from 'ol/proj'
import { getWidth, getTopLeft } from 'ol/extent'

import { Draw, Modify, Snap } from 'ol/interaction'
import { Tile as TileLayer, Vector as VectorLayer } from 'ol/layer'
import { OSM, Vector as VectorSource } from 'ol/source'
import { Circle as CircleStyle, Fill, Stroke, Style } from 'ol/style'
import GeometryType from 'ol/geom/GeometryType'

import { flipArgriculturalLand } from '../lib/image'

import 'ol/ol.css'

export default createComponent({
  setup () {
    const root = ref<HTMLElement>(null)

    const getWMTSTileGrid = () => {
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

      return new WMTSTileGrid({
        origin: getTopLeft(projectionExtent),
        resolutions: resolutions,
        matrixIds: matrixIds
      })
    }

    const getBaseLayer = (wmtsTileGrid: WMTSTileGrid) => {
      return new TileLayer({
        source: new WMTS({
          matrixSet: 'EPSG:3857',
          format: 'image/png',
          url: 'https://wmts.nlsc.gov.tw/wmts',
          layer: 'EMAP',
          tileGrid: wmtsTileGrid,
          crossOrigin: 'Anonymous',
          style: 'default',
          wrapX: true,
          attributions:
            '<a href="https://maps.nlsc.gov.tw/" target="_blank">國土測繪圖資服務雲</a>'
        }),
        opacity: 0.5
      })
    }

    const getLUIMapLayer = (wmtsTileGrid: WMTSTileGrid) => {
      return new TileLayer({
        source: new WMTS({
          matrixSet: 'EPSG:3857',
          format: 'image/png',
          url: 'https://wmts.nlsc.gov.tw/wmts/LUIMAP/{Style}/{TileMatrixSet}/{TileMatrix}/{TileRow}/{TileCol}',
          layer: 'LUIMAP',
          requestEncoding: 'REST',
          tileGrid: wmtsTileGrid,
          tileLoadFunction: function (imageTile, src) {
            const image = (imageTile as any).getImage()
            flipArgriculturalLand(src).then(newSrc => {
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
    }

    onMounted(() => {
      const tileGrid = getWMTSTileGrid()

      const source = new VectorSource()
      const vector = new VectorLayer({
        source,
        style: new Style({
          fill: new Fill({
            color: 'rgba(255, 255, 255, 0.2)'
          }),
          image: new CircleStyle({
            radius: 7,
            fill: new Fill({
              color: '#ffcc33'
            })
          })
        })
      })

      const map = new Map({
        target: root.value!,
        layers: [
          getBaseLayer(tileGrid),
          getLUIMapLayer(tileGrid),
          vector
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

      const modify = new Modify({ source })
      map.addInteraction(modify)

      const draw = new Draw({
        source,
        type: GeometryType.POINT,
        condition: (e) => {
          return false
        }
      })
      map.addInteraction(draw)
      const snap = new Snap({ source })
      map.addInteraction(snap)
    })

    return { root }
  }
})
</script>

<style lang="scss" scoped>
#map {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 100%;
}
</style>
