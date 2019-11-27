import { Vector as VectorSource } from 'ol/source'
import { Style, Icon } from 'ol/style'
import { Map as OlMap, Feature } from 'ol'
import IconAnchorUnits from 'ol/style/IconAnchorUnits'
import { transform } from 'ol/proj'
import { Point } from 'ol/geom'
import { Vector as VectorLayer } from 'ol/layer'

import { FactoryData, FactoryStatusType } from '../types'

let factoriesLayerSource: VectorSource
const factoryMap = new Map<string, FactoryData>()

const iconStyle = new Style({
  image: new Icon({
    anchorYUnits: IconAnchorUnits.PIXELS,
    src: '/images/marker-red.png'
  })
})

function createFactoryFeature (factory: FactoryData) {
  const feature = new Feature({
    geometry: new Point(transform([factory.lng, factory.lat], 'EPSG:4326', 'EPSG:3857'))
  })
  feature.setId(factory.id)
  feature.setStyle(iconStyle)

  factoryMap.set(factory.id, factory)

  return feature
}

export function addFactories (map: OlMap, factories: FactoryData[]) {
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

export function removeFactories (factories: FactoryData[]) {
  factories.forEach(factory => {
    const feature = factoriesLayerSource.getFeatureById(factory.id)
    factoriesLayerSource.removeFeature(feature)
  })
}

function displayAllFactory (map: OlMap) {
  const displayFactoryIds = factoriesLayerSource.getFeatures().map(fet => fet.getId() as string)
  const allFactories = [...factoryMap.values()]

  const missingFactory = allFactories.filter(factory => !displayFactoryIds.includes(factory.id))
  addFactories(map, missingFactory)
}

export function setFactoryStatusFilter (map: OlMap, filters: FactoryStatusType[]) {
  // factory layer doesn't get initialized yet
  if (!factoriesLayerSource) {
    return
  }

  // reset filter if filters is an empty array
  if (filters.length === 0) {
    return displayAllFactory(map)
  }

  const allFactories = [...factoryMap.values()]
  const filteredFactories = allFactories.filter(factory => filters.includes(factory.type))

  const displayFactoryIds = factoriesLayerSource.getFeatures().map(fet => fet.getId() as string)
  const displayFactories = displayFactoryIds.map(id => factoryMap.get(id)!)

  // intersection calculation
  const intersectionFactories = filteredFactories
    .filter(factory => displayFactories.find(f => f.id === factory.id))
  const factoriesToBeAdded = filteredFactories
    .filter(factory => !intersectionFactories.find(f => f.id === factory.id))
  const factoriesToBeRemoved = displayFactories
    .filter(factory => !intersectionFactories.find(f => f.id === factory.id))

  // add & remove features
  removeFactories(factoriesToBeRemoved)
  addFactories(map, factoriesToBeAdded)
}
