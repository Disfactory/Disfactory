import { Map as OlMap, View, Feature, MapBrowserEvent } from 'ol'
import { Style, Icon, Circle, Fill, Stroke } from 'ol/style'
import IconAnchorUnits from 'ol/style/IconAnchorUnits'
import { Point } from 'ol/geom'
import WMTS from 'ol/source/WMTS'
import WMTSTileGrid from 'ol/tilegrid/WMTS'
import { get as getProjection, transform } from 'ol/proj'
import { getWidth, getTopLeft } from 'ol/extent'
import { Tile as TileLayer, Vector as VectorLayer, Layer } from 'ol/layer'
import { Vector as VectorSource, OSM } from 'ol/source'
import { Zoom } from 'ol/control'
import Geolocation from 'ol/Geolocation'
import { defaults as defaultInteractions, PinchRotate } from 'ol/interaction'

import { FactoryData, FactoryStatusType } from '../types'
import { flipArgriculturalLand } from '../lib/image'
import RenderFeature from 'ol/render/Feature'
import { MapOptions } from 'ol/PluggableMap'
import IconOrigin from 'ol/style/IconOrigin'

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

export enum BASE_MAP {
  OSM,
  TAIWAN,
  SATELITE
}

type ButtonElements = {
  zoomIn: HTMLImageElement,
  zoomOut: HTMLImageElement
}

const makeMapButtons = () => {
  return Object.entries({
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
}

const iconStyleMap = Object.entries(factoryStatusImageMap).reduce((acc, [status, src]) => ({
  ...acc,
  [status]: new Style({
    image: new Icon({
      anchorYUnits: IconAnchorUnits.PIXELS,
      anchorOrigin: IconOrigin.BOTTOM_LEFT,
      src
    })
  })
}), {}) as {[key in FactoryStatusType]: Style}

const nullStyle = new Style({})

const minimapPinStyle = new Style({
  image: new Circle({
    fill: new Fill({
      color: '#A22929'
    }),
    radius: 12,
    stroke: new Stroke({
      color: '#FFFFFF',
      width: 1
    })
  })
})

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

  get factories () {
    return [...this.factoryMap.values()]
  }

  get factoriesLayerSource () {
    // create or return _factoriesLayerSource
    if (!this._factoriesLayerSource) {
      this._factoriesLayerSource = new VectorSource({ features: [] })

      const vectorLayer = new VectorLayer({
        source: this._factoriesLayerSource,
        zIndex: 3
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

const getBaseLayer = (type: BASE_MAP, wmtsTileGrid: WMTSTileGrid) => {
  const source = (() => {
    switch (type) {
      case BASE_MAP.OSM:
        return new OSM({
          crossOrigin: 'Anonymous',
          attributions:
            '<a href="https://osm.tw/" target="_blank">OpenStreetMap 台灣</a>'
        })
      case BASE_MAP.TAIWAN:
        return new WMTS({
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
        })
      case BASE_MAP.SATELITE:
        return new WMTS({
          matrixSet: 'EPSG:3857',
          format: 'image/png',
          url: 'https://wmts.nlsc.gov.tw/wmts/PHOTO_MIX/default/EPSG:3857/{TileMatrix}/{TileRow}/{TileCol}',
          layer: 'EMAP',
          tileGrid: wmtsTileGrid,
          requestEncoding: 'REST',
          crossOrigin: 'Anonymous',
          style: 'default',
          wrapX: true,
          attributions:
            '<a href="https://maps.nlsc.gov.tw/" target="_blank">國土測繪圖資服務雲</a>'
        })
      default:
        return new OSM({
          crossOrigin: 'Anonymous',
          attributions:
            '<a href="https://osm.tw/" target="_blank">OpenStreetMap 台灣</a>'
        })
    }
  })()

  return new TileLayer({
    source,
    opacity: 0.6,
    zIndex: 1
  })
}

const getLUIMapLayer = (wmtsTileGrid: WMTSTileGrid) => {
  return new TileLayer({
    source: new WMTS({
      matrixSet: 'EPSG:3857',
      format: 'image/png',
      url: 'https://wmts.nlsc.gov.tw/wmts/nURBAN2/default/EPSG:3857/{TileMatrix}/{TileRow}/{TileCol}',
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
    opacity: 0.5,
    zIndex: 2
  })
}

type MapEventHandler = {
  onMoved?: (location: [number, number, number], canPlaceFactory: boolean) => void,
  onClicked?: (location: [number, number], feature?: Feature | RenderFeature) => void
}

type OLMapOptions = {
  minimap?: boolean
}

export class OLMap {
  private _map: OlMap
  private mapDom: HTMLElement
  private geolocation?: Geolocation
  private baseLayer: TileLayer
  private tileGrid: WMTSTileGrid = getWMTSTileGrid()
  private minimapPinFeature?: Feature

  constructor (target: HTMLElement, handler: MapEventHandler = {}, options: OLMapOptions = {}) {
    this.mapDom = target

    this.baseLayer = getBaseLayer(BASE_MAP.OSM, this.tileGrid)
    this._map = this.instantiateOLMap(this.mapDom, this.baseLayer, options)
    this.geolocation = this.setupGeolocationTracking(this._map)

    if (!options.minimap) {
      this.geolocation = this.setupGeolocationTracking(this._map)
    }

    this.setupEventListeners(this._map, handler)
  }

  get map () {
    return this._map
  }

  private setupEventListeners (map: OlMap, handler: MapEventHandler) {
    const move = async () => {
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
    }

    // eslint-disable-next-line @typescript-eslint/no-misused-promises
    map.on('change:resolution', move)
    // eslint-disable-next-line @typescript-eslint/no-misused-promises
    map.on('moveend', move)

    // eslint-disable-next-line @typescript-eslint/no-misused-promises
    map.on('click', async (event) => {
      if (handler.onClicked) {
        const [lng, lat] = transform(event.coordinate, 'EPSG:3857', 'EPSG:4326')
        const feature = map.forEachFeatureAtPixel(event.pixel, (feature) => feature)
        handler.onClicked([lng, lat], feature)
      }
    })
  }

  private instantiateOLMap (target: HTMLElement, baseLayer: TileLayer, options: OLMapOptions = {}) {
    const tileGrid = getWMTSTileGrid()
    const view = new View({
      center: transform([120.1, 23.234], 'EPSG:4326', 'EPSG:3857'),
      zoom: 16
    })

    const mapControlButtons = makeMapButtons()

    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    const mapOptions: MapOptions = {
      target,
      layers: [
        baseLayer,
        getLUIMapLayer(tileGrid)
      ],
      view,
      controls: [
        new Zoom({
          zoomInLabel: mapControlButtons.zoomIn,
          zoomOutLabel: mapControlButtons.zoomOut
        })
      ],
      interactions: defaultInteractions({
        pinchRotate: false
      }).extend([
        new PinchRotate({
          threshold: 0.4
        })
      ])
    }

    if (options.minimap) {
      mapOptions.controls = []
      mapOptions.interactions = []
    }

    return new OlMap(mapOptions)
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
    if (!this.geolocation) {
      return
    }

    const location = this.geolocation.getPosition()
    if (!location) {
      return
    }

    const view = this._map.getView()
    view.setCenter(location)
    view.setZoom(16)
  }

  public changeBaseMap (type: BASE_MAP) {
    this._map.removeLayer(this.baseLayer)
    this.baseLayer = getBaseLayer(type, this.tileGrid)
    this._map.addLayer(this.baseLayer)
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

      resolve(false)
    })
  }

  private getLUIMAPLayer (): Promise<Layer> {
    return new Promise((resolve, reject) => {
      let layer
      this._map.getLayers().forEach(_layer => {
        if (_layer.getProperties().source.layer_ === 'LUIMAP') {
          layer = _layer
          resolve(_layer as Layer)
        }
      })

      if (!layer) {
        reject(new TypeError('LUIMAP Layer not found'))
      }
    })
  }

  public async setLUILayerVisible (visible: boolean) {
    const layer = await this.getLUIMAPLayer()
    layer.setVisible(visible)
  }

  public setMinimapPin (longitude: number, latitude: number) {
    const coordinate = transform([longitude, latitude], 'EPSG:4326', 'EPSG:3857')

    if (!this.minimapPinFeature) {
      const feature = new Feature({
        geometry: new Point(coordinate)
      })
      feature.setStyle(minimapPinStyle)
      this.minimapPinFeature = feature

      const source = new VectorSource({
        features: [
          feature
        ]
      })

      const vectorLayer = new VectorLayer({
        source,
        zIndex: 4
      })

      this.map.addLayer(vectorLayer)
    } else {
      this.minimapPinFeature.setGeometry(new Point(coordinate))
    }

    this._map.getView().setCenter(coordinate)
  }
}

export function initializeMap (target: HTMLElement, handler: MapEventHandler = {}) {
  const mapInstance = new OLMap(target, handler);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (window as any).changeBaseMap = mapInstance.changeBaseMap.bind(mapInstance)
  return new MapFactoryController(mapInstance)
}

export function initializeMinimap (target: HTMLElement, center: number[]) {
  const mapInstance = new OLMap(target, {}, { minimap: true })
  mapInstance.map.getView().setCenter(center)
  return new MapFactoryController(mapInstance)
}
