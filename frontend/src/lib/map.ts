import { Style, Icon } from 'ol/style'
import IconAnchorUnits from 'ol/style/IconAnchorUnits'
import { Map as OlMap, View, Feature, MapBrowserEvent } from 'ol'
import { Point } from 'ol/geom'
import WMTS from 'ol/source/WMTS'
import WMTSTileGrid from 'ol/tilegrid/WMTS'
import { get as getProjection, transform } from 'ol/proj'
import { getWidth, getTopLeft } from 'ol/extent'
import { Tile as TileLayer, Vector as VectorLayer } from 'ol/layer'
import { Vector as VectorSource } from 'ol/source'
import { Zoom, ZoomToExtent, defaults } from 'ol/control'

import { FactoryData, FactoryStatusType } from '../types'

import { flipArgriculturalLand } from '../lib/image'
import { getFactories } from '@/api'

let factoriesLayerSource: VectorSource
const factoryMap = new Map<string, FactoryData>()

// internal map references
let map: OlMap
let mapDom: HTMLElement

const factoryStatusImageMap = {
  D: '/images/marker-green.svg',
  F: '/images/marker-red.svg',
  A: '/images/marker-blue.svg'
}


type ButtonElements = {
  zoomIn: HTMLImageElement
  zoomOut: HTMLImageElement
  locate: HTMLImageElement
}

const mapControlButtons = Object.entries({
  zoomIn: '/images/zoom-in.svg',
  zoomOut: '/images/zoom-out.svg',
  locate: '/images/locate.svg'
}).reduce((acc, [key, image]) => {
  const label = document.createElement('img')
  label.setAttribute('src', image)

  return {
    ...acc,
    [key]: label
  }
}, {}) as ButtonElements

const zoomToExtendLabel = document.createElement('img')
zoomToExtendLabel.setAttribute('src', '/images/locate.svg')


const iconStyleMap = Object.entries(factoryStatusImageMap).reduce((acc, [status, src]) => ({
  ...acc,
  [status]: new Style({
    image: new Icon({
      anchorYUnits: IconAnchorUnits.PIXELS,
      src
    })
  })
}), {}) as {[key in FactoryStatusType]: Style}

const nullStyle = new Style({})

let appliedFilters: FactoryStatusType[] = []

function isFactoryVisible (factory: FactoryData) {
  if (appliedFilters.length === 0) {
    return true
  } else {
    return appliedFilters.includes(factory.status)
  }
}

function getFactoryStyle (factory: FactoryData): Style {
  const visible = isFactoryVisible(factory)
  return visible ? iconStyleMap[factory.status] : nullStyle
}

function createFactoryFeature (factory: FactoryData) {
  const feature = new Feature({
    geometry: new Point(transform([factory.lng, factory.lat], 'EPSG:4326', 'EPSG:3857'))
  })
  feature.setId(factory.id)
  feature.setStyle(getFactoryStyle(factory))

  factoryMap.set(factory.id, factory)

  return feature
}

export function addFactories (factories: FactoryData[]) {
  const features = factories.filter(factory => !factoryMap.has(factory.id)).map(createFactoryFeature)

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
}

export function hideFactories (factories: FactoryData[]) {
  factories.forEach(factory => {
    const feature = factoriesLayerSource.getFeatureById(factory.id)
    feature.setStyle(nullStyle)
  })
}

function forEachFeatureFactory (fn: (feature: Feature, factory: FactoryData) => any) {
  factoriesLayerSource.getFeatures().forEach(feature => {
    const id = feature.getId() as string
    const factory = factoryMap.get(id) as FactoryData

    fn(feature, factory)
  })
}

function displayAllFactory () {
  forEachFeatureFactory((feature, factory) => {
    feature.setStyle(iconStyleMap[factory.status])
  })
}

function updateFactoriesFeatureStyle () {
  forEachFeatureFactory((feature, factory) => {
    feature.setStyle(getFactoryStyle(factory))
  })
}

export function setFactoryStatusFilter (filters: FactoryStatusType[]) {
  // factory layer doesn't get initialized yet
  if (!factoriesLayerSource) {
    return
  }
  appliedFilters = filters

  // reset filter if filters is an empty array
  if (filters.length === 0) {
    return displayAllFactory()
  }

  updateFactoriesFeatureStyle()
}
// TODO: remove this
(window as any).setFactoryStatusFilter = setFactoryStatusFilter

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
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const image: HTMLImageElement = (imageTile as any).getImage()
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

export function getMap () {
  return map
}

type MapEventHandler = {
  onMoved?: (location: [number, number], canPlaceFactory: boolean) => any;
}

function canPlaceFactory (pixel: MapBrowserEvent['pixel']): Promise<boolean> {
  return new Promise(resolve => {
    map.forEachLayerAtPixel(pixel, function (_, data) {
      const [,,, a] = data

      return resolve(a === 1)
    }, {
      layerFilter: function (layer) {
        // only handle click event on LUIMAP
        return layer.getProperties().source.layer_ === 'LUIMAP'
      }
    })
  })
}

export function initializeMap (target: HTMLElement, handler: MapEventHandler = {}) {
  const tileGrid = getWMTSTileGrid()

  mapDom = target

  map = new OlMap({
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    target,
    layers: [
      getBaseLayer(tileGrid),
      getLUIMapLayer(tileGrid)
    ],
    view: new View({
      center: transform([120.1, 23.234], 'EPSG:4326', 'EPSG:3857'),
      zoom: 15
    }),
    controls: [
      new ZoomToExtent({
        label: mapControlButtons.locate,
      }),
      new Zoom({
        zoomInLabel: mapControlButtons.zoomIn,
        zoomOutLabel: mapControlButtons.zoomOut,
      })
    ]
  })

  map.on('click', function (event) {
    // console.log(event)
    map.forEachLayerAtPixel(event.pixel, function (_, data) {
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

  // eslint-disable-next-line @typescript-eslint/no-misused-promises
  map.on('moveend', async function () {
    const view = map.getView()
    const zoom = view.getZoom()

    // resolution in meter
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    const resolution = view.getResolutionForZoom(zoom!)
    const range = Math.ceil(resolution)

    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    const [lng, lat] = transform(view.getCenter()!, 'EPSG:3857', 'EPSG:4326')

    const factories = await getFactories(range, lng, lat)
    addFactories(factories)

    if (handler.onMoved) {
      const { width, height } = mapDom.getBoundingClientRect()
      handler.onMoved([lng, lat], await canPlaceFactory([width / 2, height / 2]))
    }
  })

  // TODO: remove this
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  ;(window as any).map = map
}
