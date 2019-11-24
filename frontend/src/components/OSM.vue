<template>
  <div ref="root" id="map" />
</template>

<script lang="ts">
import { createComponent, onMounted, ref } from '@vue/composition-api'

import { Map as OlMap, View, Feature } from 'ol'
import WMTS from 'ol/source/WMTS'
import WMTSTileGrid from 'ol/tilegrid/WMTS'
import { get as getProjection, transform } from 'ol/proj'
import { getWidth, getTopLeft } from 'ol/extent'

import { Draw, Modify, Snap } from 'ol/interaction'
import { Tile as TileLayer, Vector as VectorLayer } from 'ol/layer'
import { OSM, Vector as VectorSource } from 'ol/source'
import { Circle as CircleStyle, Fill, Stroke, Style, Icon, Image } from 'ol/style'
import IconAnchorUnits from 'ol/style/IconAnchorUnits'
import GeometryType from 'ol/geom/GeometryType'
import { Point } from 'ol/geom'
import { FactoriesResponse } from '../types'

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

      const map = new OlMap({
        target: root.value!,
        layers: [
          getBaseLayer(tileGrid),
          getLUIMapLayer(tileGrid)
        ],
        view: new View({
          center: transform([120.1, 23.234], 'EPSG:4326', 'EPSG:3857'),
          zoom: 15
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

      let factoriesLayerSource: VectorSource
      let factoryMap = new Map()

      const iconStyle = new Style({
        image: new Icon({
          anchorYUnits: IconAnchorUnits.PIXELS,
          src: '/images/marker-red.png'
        })
      })

      map.on('moveend', async function (event) {
        const view = map.getView()
        const zoom = view.getZoom()

        // resolution in meter
        const resolution = view.getResolutionForZoom(zoom!)
        const range = Math.ceil(resolution)

        const [lng, lat] = transform(view.getCenter()!, 'EPSG:3857', 'EPSG:4326')

        const res = await fetch(`/server/api/factories?range=${range}&lng=${lng}&lat=${lat}`)
        const data = await res.json() as FactoriesResponse

        const features = data.filter(factory => !factoryMap.has(factory.id)).map(data => {
          const feature = new Feature({
            geometry: new Point(transform([data.lng, data.lat], 'EPSG:4326', 'EPSG:3857'))
          })
          feature.setId(data.id)
          feature.setStyle(iconStyle)

          factoryMap.set(data.id, data)

          return feature
        })

        if (!factoriesLayerSource) {
          factoriesLayerSource = new VectorSource({
            features
          })
          const vectorLayer = new VectorLayer({
            source: factoriesLayerSource
          })

          map.addLayer(vectorLayer)
        } else {
          factoriesLayerSource.addFeatures(features)
        }
      })

      // TODO: remove this
      ;(window as any).map = map
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
