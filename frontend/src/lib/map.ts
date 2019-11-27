import { Vector as VectorSource } from 'ol/source'
import { Style, Icon } from 'ol/style'
import { Map as OlMap, Feature } from 'ol'
import IconAnchorUnits from 'ol/style/IconAnchorUnits'
import { transform } from 'ol/proj'
import { Point } from 'ol/geom'
import { Vector as VectorLayer } from 'ol/layer'

import { FactoryData } from '../types'

let factoriesLayerSource: VectorSource
const factoryMap = new Map()

const iconStyle = new Style({
  image: new Icon({
    anchorYUnits: IconAnchorUnits.PIXELS,
    src: '/images/marker-red.png'
  })
})

export function addFactories (map: OlMap, factories: FactoryData[]) {
  const features = factories.filter(factory => !factoryMap.has(factory.id)).map(data => {
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
}
