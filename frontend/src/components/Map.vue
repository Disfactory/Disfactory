<template>
  <div class="map-container">
    <div ref="root" class="map" />
    <div ref="popup" :class="['popup', { show: popupData.show }]" :style="{ borderColor: popupData.color }">
      <div class="close" @click="popupData.show = false" />
      <h3>{{ popupData.name }}</h3>
      <p :style="{ color: popupData.color }">{{ popupData.status }}</p>
      <app-button outline @click="onClickEditFactoryData">
        補充資料
      </app-button>
    </div>

    <div class="ol-map-search ol-unselectable ol-control" @click="openFilterModal">
      <button>
        <img src="/images/search.svg" alt="search">
      </button>
    </div>

    <div class="ol-fit-location ol-unselectable ol-control" @click="zoomToGeolocation">
      <button>
        <img src="/images/locate.svg" alt="locate">
      </button>
    </div>

    <div class="center-point" v-if="selectFactoryMode" />

    <div class="factory-button-group">
      <div class="create-factory-button" v-if="!selectFactoryMode">
        <app-button @click="openCreateFactoryForm">我要新增違建工廠</app-button>
      </div>

      <div class="choose-location-button" v-if="selectFactoryMode">
        <app-button
          @click="selectCenterPoint"
          :disabled="!factoryValid"
        >
          選擇此地點
        </app-button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import AppButton from '@/components/AppButton.vue'
import { createComponent, onMounted, ref, inject } from '@vue/composition-api'
import { initializeMap, MapFactoryController, factoryBorderColor } from '../lib/map'
import { getFactories } from '../api'
import { MainMapControllerSymbol } from '../symbols'
import { Overlay } from 'ol'
import OverlayPositioning from 'ol/OverlayPositioning'
import { FACTORY_STATUS, FactoryData } from '../types'

export default createComponent({
  components: {
    AppButton
  },
  props: {
    openCreateFactoryForm: {
      type: Function,
      required: true
    },
    openEditFactoryForm: {
      type: Function,
      required: true
    },
    selectFactoryMode: {
      type: Boolean,
      required: true
    },
    exitSelectFactoryMode: {
      type: Function,
      required: true
    },
    setFactoryLocation: {
      type: Function,
      required: true
    },
    openFilterModal: {
      type: Function,
      required: true
    }
  },
  setup (props) {
    const root = ref<HTMLElement>(null)
    const popup = ref<HTMLDivElement>(null)
    const factoryValid = ref(false)
    const factoryLngLat = ref<number[]>([])
    const mapControllerRef = inject(MainMapControllerSymbol, ref<MapFactoryController>())

    const popupData = ref({
      show: false,
      id: '',
      name: '',
      color: '',
      status: ''
    })
    const popupFactoryData = ref<FactoryData>(null)

    const setPopup = (id: string) => {
      if (!mapControllerRef.value) return
      const factory = mapControllerRef.value.getFactory(id)
      if (factory) {
        popupData.value.id = factory.id
        popupData.value.name = factory.name
        popupData.value.color = factoryBorderColor[factory.status]
        popupData.value.status = FACTORY_STATUS[factory.status]
        popupData.value.show = true
        popupFactoryData.value = factory
      }
    }
    const onClickEditFactoryData = () => {
      if (!popupFactoryData.value) {
        return
      }

      props.openEditFactoryForm(popupFactoryData.value)
    }

    onMounted(() => {
      const popupOverlay = new Overlay({
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        element: popup.value!,
        positioning: OverlayPositioning.BOTTOM_LEFT,
        stopEvent: false
      })

      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      const mapController = initializeMap(root.value!, {
        onMoved: async function ([longitude, latitude, range], canPlaceFactory) {
          try {
            const factories = await getFactories(range, longitude, latitude)
            if (Array.isArray(factories)) {
              mapController.addFactories(factories)
            }
          } catch (e) {
            console.error(e)
          }

          factoryLngLat.value = [longitude, latitude]
          factoryValid.value = canPlaceFactory
        }, // TODO: do on start move to lock selection
        onClicked: async function (_, feature) {
          if (feature) {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            popupOverlay.setPosition((feature.getGeometry() as any).getCoordinates())
            setPopup(feature.getId() as string)
          }
        }
      })

      mapController.mapInstance.map.addOverlay(popupOverlay)
      mapControllerRef.value = mapController
    })

    return {
      root,
      popup,
      factoryValid,
      selectCenterPoint () {
        props.setFactoryLocation(factoryLngLat.value)
        props.exitSelectFactoryMode()
      },
      zoomToGeolocation: function () {
        if (mapControllerRef.value) {
          mapControllerRef.value.mapInstance.zoomToGeolocation()
        }
      },
      popupData,
      onClickEditFactoryData
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.map-container {
  top: 47px;
  bottom: 0;
  width: 100%;
  height: calc(100% - 47px);
  position: absolute;
}

.map {
  height: 100%;
}

.factory-button-group {
  position: fixed;
  bottom: 48px;

  .create-factory-button {
    transform: translateX(calc(50vw - 125.735px));
  }

  .choose-location-button {
    transform: translateX(calc(50vw - 86.835px));
  }
}

.center-point {
  width: 25px;
  height: 25px;
  border-radius: 50%;
  display: block;
  background-color: $red-color;
  border: solid 2px white;

  position: fixed;
  top: 0;
  left: 0;
  z-index: 2;

  transform: translate(calc(50vw - 12.5px), calc(50vh - 12.5px + 47px - 25px));
}

.popup {
  opacity: 0;
  transition: opacity 0.2s linear;
  transform: translate(-16px, 25px);
  border-radius: 3px;
  border: solid 3px #a22929;
  background-color: #ffffff;
  min-width: 240px;
  padding: 20px;
  position: relative;

  .close {
    position: absolute;
    top: 30px;
    right: 20px;
    width: 24px;
    height: 24px;
    cursor: pointer;

    &::before, &::after {
      display: block;
      content: '';
      width: 100%;
      height: 3px;
      background: #000;
      transform-origin: center;
      position: absolute;
      border-radius: 5px;
    }

    &::before {
      transform: rotate(45deg);
    }

    &::after {
      transform: rotate(-45deg);
    }
  }

  h3 {
    margin: 0;
    font-size: 20px;
    line-height: 1.8;
  }

  p {
    margin: 5px 0;
    font-size: 14px;
    line-height: 2;
  }
}

.popup.show {
  opacity: 1;
}
</style>
