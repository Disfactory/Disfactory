import { Map as OlMap, View, Feature, MapBrowserEvent } from 'ol'
import { Style, Icon } from 'ol/style'
import IconAnchorUnits from 'ol/style/IconAnchorUnits'
import { Point } from 'ol/geom'
import WMTS from 'ol/source/WMTS'
import WMTSTileGrid from 'ol/tilegrid/WMTS'
import { get as getProjection, transform } from 'ol/proj'
import { getWidth, getTopLeft } from 'ol/extent'
import { Tile as TileLayer, Vector as VectorLayer } from 'ol/layer'
import { Vector as VectorSource, OSM } from 'ol/source'
import { Zoom } from 'ol/control'
import Geolocation from 'ol/Geolocation'

import { FactoryData, FactoryStatusType } from '../types'
import { flipArgriculturalLand } from '../lib/image'
import RenderFeature from 'ol/render/Feature'

const factoryStatusImageMap = {
  D: '/images/marker-green.svg',
  F: '/images/marker-red.svg',
  A: '/images/marker-blue.svg'
}

export const factoryBorderColor = {
  D: '#6D8538',
  F: '#A22929',
  A: '#447287'
}

type ButtonElements = {
  zoomIn: HTMLImageElement,
  zoomOut: HTMLImageElement
}

const mapControlButtons = Object.entries({
  zoomIn: '/images/zoom-in.svg',
  zoomOut: '/images/zoom-out.svg'
}).reduce((acc, [key, image]) => {
  const label = document.createElement('img')
  label.setAttribute('src', image)

  return {
    ...acc,
    [key]: label
  }
}, {}) as ButtonElements

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

export class MapFactoryController {
  private _map: OLMap
  private appliedFilters: FactoryStatusType[] = []
  private _factoriesLayerSource?: VectorSource
  private factoryMap = new Map<string, FactoryData>()

  constructor (map: OLMap) {
    this._map = map
  }

  get mapInstance () {
    return this._map
  }

  get factoriesLayerSource () {
    // create or return _factoriesLayerSource
    if (!this._factoriesLayerSource) {
      this._factoriesLayerSource = new VectorSource({ features: [] })

      const vectorLayer = new VectorLayer({
        source: this._factoriesLayerSource
      })

      this.mapInstance.map.addLayer(vectorLayer)
    }

    return this._factoriesLayerSource
  }

  public getFactory (id: string) {
    return this.factoryMap.get(id)
  }

  public updateFactory (id: string, factory: FactoryData) {
    this.factoryMap.set(id, factory)
  }

  public addFactories (factories: FactoryData[]) {
    const createFactoryFeature = this.createFactoryFeature.bind(this)
    const features = factories
      .filter(factory => !this.factoryMap.has(factory.id))
      .map(createFactoryFeature)

    this.factoriesLayerSource.addFeatures(features)
  }

  public hideFactories (factories: FactoryData[]) {
    factories.forEach(factory => {
      const feature = this.factoriesLayerSource.getFeatureById(factory.id)
      feature.setStyle(nullStyle)
    })
  }

  public setFactoryStatusFilter (filters: FactoryStatusType[]) {
    this.appliedFilters = filters

    // reset filter if filters is an empty array
    if (filters.length === 0) {
      return this.displayAllFactory()
    } else {
      this.updateFactoriesFeatureStyle()
    }
  }

  private isFactoryVisible (factory: FactoryData) {
    if (this.appliedFilters.length === 0) {
      return true
    } else {
      return this.appliedFilters.includes(factory.status)
    }
  }

  private getFactoryStyle (factory: FactoryData): Style {
    const visible = this.isFactoryVisible(factory)
    return visible ? iconStyleMap[factory.status] : nullStyle
  }

  private createFactoryFeature (factory: FactoryData) {
    const feature = new Feature({
      geometry: new Point(transform([factory.lng, factory.lat], 'EPSG:4326', 'EPSG:3857'))
    })
    feature.setId(factory.id)
    feature.setStyle(this.getFactoryStyle(factory))

    this.factoryMap.set(factory.id, factory)

    return feature
  }

  private forEachFeatureFactory (fn: (feature: Feature, factory: FactoryData) => void) {
    this.factoriesLayerSource.getFeatures().forEach(feature => {
      const id = feature.getId() as string
      const factory = this.factoryMap.get(id) as FactoryData

      fn(feature, factory)
    })
  }

  private displayAllFactory () {
    this.forEachFeatureFactory((feature, factory) => {
      feature.setStyle(iconStyleMap[factory.status])
    })
  }

  private updateFactoriesFeatureStyle () {
    this.forEachFeatureFactory((feature, factory) => {
      feature.setStyle(this.getFactoryStyle(factory))
    })
  }
}

const getWMTSTileGrid = () => {
  const projection = getProjection('EPSG:3857')
  const projectionExtent = projection.getExtent()
  const resolutions = new Array(21)
  const size = getWidth(projectionExtent) / 256
  const matrixIds = new Array(21)
  for (let z = 0; z < 21; ++z) {
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

const getBaseLayer = () => {
  return new TileLayer({
    source: new OSM({
      crossOrigin: 'Anonymous',
      attributions:
        '<a href="https://osm.tw/" target="_blank">OpenStreetMap 台灣</a>'
    }),
    opacity: 0.6
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

type MapEventHandler = {
  onMoved?: (location: [number, number, number], canPlaceFactory: boolean) => void,
  onClicked?: (location: [number, number], feature?: Feature | RenderFeature) => void
}

export class OLMap {
  private _map: OlMap
  private mapDom: HTMLElement
  private geolocation: Geolocation

  constructor (target: HTMLElement, handler: MapEventHandler = {}) {
    this.mapDom = target

    this._map = this.instantiateOLMap(this.mapDom)
    this.geolocation = this.setupGeolocationTracking(this._map)

    this.setupEventListeners(this._map, handler)
  }

  get map () {
    return this._map
  }

  private setupEventListeners (map: OlMap, handler: MapEventHandler) {
    // eslint-disable-next-line @typescript-eslint/no-misused-promises
    map.on('moveend', async () => {
      const view = map.getView()
      const zoom = view.getZoom()

      // resolution in meter
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      const resolution = view.getResolutionForZoom(zoom!)
      const range = Math.ceil(resolution)

      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      const [lng, lat] = transform(view.getCenter()!, 'EPSG:3857', 'EPSG:4326')

      if (handler.onMoved) {
        const { width, height } = this.mapDom.getBoundingClientRect()
        const canPlace = await this.canPlaceFactory([width / 2, height / 2])
        handler.onMoved([lng, lat, range], canPlace)
      }
    })

    // eslint-disable-next-line @typescript-eslint/no-misused-promises
    map.on('click', async (event) => {
      if (handler.onClicked) {
        const [lng, lat] = transform(event.coordinate, 'EPSG:3857', 'EPSG:4326')
        const feature = map.forEachFeatureAtPixel(event.pixel, (feature) => feature)
        handler.onClicked([lng, lat], feature)
      }
    })
  }

  private instantiateOLMap (target: HTMLElement) {
    const tileGrid = getWMTSTileGrid()
    const view = new View({
      center: transform([120.1, 23.234], 'EPSG:4326', 'EPSG:3857'),
      zoom: 16
    })

    return new OlMap({
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      target,
      layers: [
        getBaseLayer(),
        getLUIMapLayer(tileGrid)
      ],
      view,
      controls: [
        new Zoom({
          zoomInLabel: mapControlButtons.zoomIn,
          zoomOutLabel: mapControlButtons.zoomOut
        })
      ]
    })
  }

  private setupGeolocationTracking (map: OlMap) {
    const view = map.getView()

    const geolocation = new Geolocation({
      trackingOptions: {
        enableHighAccuracy: true
      },
      projection: view.getProjection()
    })

    geolocation.setTracking(true)

    const positionLayer = this.setupgeolocationLayer(geolocation)

    map.addLayer(positionLayer)

    return geolocation
  }

  private setupgeolocationLayer (geolocation: Geolocation) {
    const positionFeature = new Feature()
    geolocation.on('change:position', function () {
      const coordinates = geolocation.getPosition()
      positionFeature.setGeometry(coordinates ? new Point(coordinates) : undefined)
    })

    let run = false
    geolocation.on('change', () => {
      if (run) {
        return
      }

      const position = geolocation.getPosition()
      if (position) {
        this.zoomToGeolocation()
        run = true
      }
    })

    const positionLayer = new VectorLayer({
      source: new VectorSource({
        features: [positionFeature]
      })
    })

    return positionLayer
  }

  public zoomToGeolocation () {
    const location = this.geolocation.getPosition()
    if (!location) {
      return
    }

    const view = this._map.getView()
    view.setCenter(location)
    view.setZoom(16)
  }

  public canPlaceFactory (pixel: MapBrowserEvent['pixel']): Promise<boolean> {
    return new Promise(resolve => {
      this._map.forEachLayerAtPixel(pixel, function (_, data) {
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
}

export function initializeMap (target: HTMLElement, handler: MapEventHandler = {}) {
  const mapInstance = new OLMap(target, handler)
  return new MapFactoryController(mapInstance)
}
