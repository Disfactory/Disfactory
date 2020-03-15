<template>
  <div>
    <div class="navbar-container" v-if="selectFactoryMode">
      <app-navbar :dark="false" :fixed="true" @back="onNavBack" @menu="modalActions.toggleSidebar">
        新增資訊
      </app-navbar>
    </div>

    <div class="map-container">
      <div ref="root" class="map" />
      <div ref="popup" :class="['popup', { show: popupState.show }]" :style="{ borderColor: popupData.color }">
        <div class="close" @click="popupState.show = false" data-label="map-popup-close" />
        <small :style="{ color: popupData.color }">{{ popupData.status }}</small>
        <h3>{{ popupData.name }}</h3>
        <p class="summary">{{ popupData.summary }}</p>
        <app-button outline @click="onClickEditFactoryData" :color="getButtonColorFromStatus()" data-label="map-popup-modify">
          補充資料
        </app-button>
      </div>

      <div class="ol-map-search ol-unselectable ol-control" @click="openFilterModal" data-label="map-search">
        <button>
          <img src="/images/filter.svg" alt="search">
        </button>
      </div>

      <div class="ol-fit-location ol-unselectable ol-control" @click="zoomToGeolocation" data-label="map-locate">
        <button>
          <img src="/images/locate.svg" alt="locate">
        </button>
      </div>


      <div class="center-point" v-if="selectFactoryMode" />

      <div class="factory-button-group">
        <div class="factory-secondary-actions-group">
          <div class="ol-switch-base ol-unselectable ol-control" @click="switchBaseMap" data-label="map-switch-base">
            <button>
              {{ baseMapName }}
            </button>
          </div>

        </div>

        <div class="create-factory-button" v-if="!selectFactoryMode">
          <app-button @click="onClickCreateFactoryButton" data-label="map-create-factory" color="dark-green">我想新增可疑工廠</app-button>
        </div>

        <div class="choose-location-button" v-if="selectFactoryMode">
          <app-button
            @click="onClickFinishSelectFactoryPositionButton"
            :disabled="!factoryValid"
            data-label="map-select-position"
          >
            選擇此地點
          </app-button>
          <span>可舉報範圍：白色區域</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import AppButton from '@/components/AppButton.vue'
import AppNavbar from '@/components/AppNavbar.vue'
import { createComponent, onMounted, ref, inject, computed } from '@vue/composition-api'
import { initializeMap, MapFactoryController, getFactoryStatus } from '../lib/map'
import { getFactories } from '../api'
import { MainMapControllerSymbol } from '../symbols'
import { Overlay } from 'ol'
import OverlayPositioning from 'ol/OverlayPositioning'
import { FactoryStatus } from '../types'
import { useBackPressed } from '../lib/useBackPressed'
import { useModalState } from '../lib/hooks'
import { useFactoryPopup, getPopupData } from '../lib/factoryPopup'
import { useAppState } from '../lib/appState'

export default createComponent({
  components: {
    AppButton,
    AppNavbar
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
    enterSelectFactoryMode: {
      type: Function,
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

    const [, modalActions] = useModalState()
    const [appState] = useAppState()

    const [popupState] = useFactoryPopup()
    const popupData = computed(() => appState.factoryData ? getPopupData(appState.factoryData) : {})
    const baseMap = ref(0)
    const baseMapName = computed(() => '切換不同地圖')

    const setPopup = (id: string) => {
      if (!mapControllerRef.value) return
      const factory = mapControllerRef.value.getFactory(id)

      if (factory) {
        appState.factoryData = factory
        popupState.show = true
      }
    }

    const onClickEditFactoryData = () => {
      if (!appState.factoryData) {
        return
      }

      props.openEditFactoryForm(appState.factoryData)
    }

    onMounted(() => {
      const popupOverlay = new Overlay({
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        element: popup.value!,
        positioning: OverlayPositioning.BOTTOM_LEFT
      })

      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      const mapController = initializeMap(root.value!, {
        onMoved: async function ([longitude, latitude, range], canPlaceFactory) {
          factoryValid.value = canPlaceFactory
          factoryLngLat.value = [longitude, latitude]
          try {
            const factories = await getFactories(range, longitude, latitude)
            if (Array.isArray(factories)) {
              mapController.addFactories(factories)
            }
          } catch (e) {
            // TODO: handle here
          }
        }, // TODO: do on start move to lock selection
        onClicked: async function (_, feature) {
          if (feature) {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            popupOverlay.setPosition((feature.getGeometry() as any).getCoordinates())
            setPopup(feature.getId() as string)
          } else {
            popupState.show = false
          }
        }
      })

      mapController.mapInstance.map.addOverlay(popupOverlay)
      mapControllerRef.value = mapController

      mapController.mapInstance.setLUILayerVisible(false)
    })

    const switchBaseMap = () => {
      baseMap.value = (baseMap.value + 1 < 3) ? baseMap.value + 1 : 0
      mapControllerRef.value?.mapInstance.changeBaseMap(baseMap.value)
    }

    const onBack = () => {
      if (mapControllerRef.value) {
        mapControllerRef.value.mapInstance.setLUILayerVisible(false)
      }
      props.exitSelectFactoryMode()
    }

    function onClickCreateFactoryButton () {
      if (!mapControllerRef.value) return

      mapControllerRef.value.mapInstance.setLUILayerVisible(true)
      props.enterSelectFactoryMode()
      popupState.show = false

      useBackPressed(onBack)
    }

    function onClickFinishSelectFactoryPositionButton () {
      if (!mapControllerRef.value) return

      mapControllerRef.value.mapInstance.setLUILayerVisible(false)

      props.setFactoryLocation(factoryLngLat.value)
      props.exitSelectFactoryMode()
      props.openCreateFactoryForm()
    }

    return {
      root,
      modalActions,
      popup,
      factoryValid,
      baseMapName,
      switchBaseMap,
      zoomToGeolocation: function () {
        if (mapControllerRef.value) {
          mapControllerRef.value.mapInstance.zoomToGeolocation()
        }
      },
      onNavBack () {
        onBack()
      },
      popupState,
      popupData,
      onClickEditFactoryData,
      onClickCreateFactoryButton,
      onClickFinishSelectFactoryPositionButton,
      getButtonColorFromStatus: function () {
        if (!appState.factoryData) {
          return 'default'
        }

        const status = getFactoryStatus(appState.factoryData)
        return {
          [FactoryStatus.NEW]: 'blue',
          [FactoryStatus.EXISTING_INCOMPLETE]: 'gray',
          [FactoryStatus.EXISTING_COMPLETE]: 'gray',
          [FactoryStatus.REPORTED]: 'default'
        }[status]
      }
    }
  }
})
</script>

<style lang="scss" scoped>
@import '~@/styles/variables';
@import '~@/styles/utils';

.map-container {
  top: 47px;
  bottom: 0;
  width: 100%;
  height: calc(100% - 47px);
  position: absolute;

  .ol-switch-base {
    background: #6E8501;
    position: relative;
    width: auto;
    height: auto;
    text-align: center;
    display: inline-block;

    button {
      display: inline-block;
      width: auto;
      font-size: 14px;
    }
  }
}

.map {
  height: 100%;
}

.factory-button-group {
  position: fixed;
  width: 100%;
  left: 0;
  bottom: 60px;
  display: flex;

  flex-direction: column;
  justify-content: center;

  .create-factory-button {
    max-width: 250px;
    margin: 0 auto;
  }

  .choose-location-button {
    position: relative;
    margin: 0 auto;

    span {
      user-select: none;
      position: absolute;
      color: white;
      text-align: center;
      width: 190px;
      left: -22px;
      top: 60px;
    }
  }
}

.factory-secondary-actions-group {
  max-width: 300px;
  margin: 0 auto;

  display: flex;
  margin-bottom: 10px;
  justify-content: center;
}


.center-point {
  width: 25px;
  height: 25px;
  border-radius: 50%;
  display: block;
  background-color: $red-color;
  border: solid 2px white;

  position: fixed;
  top: 50%;
  left: 0;
  z-index: 2;

  transform: translate(calc(50vw - 12.5px), 12.5px);
}

@keyframes fadein {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

.popup {
  display: none;
  opacity: 0;
  animation-name: fadein;
  animation-duration: 500ms;
  transform: translate(-17px, -18px);
  border-radius: 3px;
  border: solid 3px #a22929;
  background-color: #ffffff;
  min-width: 240px;
  padding: 20px;
  position: relative;

  .close {
    @include close-button;
  }

  h3 {
    width: calc(100% - 24px);
    margin: 0;
    font-size: 20px;
    line-height: 1.8;
  }

  p {
    margin: 5px 0;
    font-size: 14px;
    line-height: 2;
  }

  p.summary {
    white-space: pre-wrap;
    margin-bottom: 15px;
    font-size: 14px;
    font-weight: 500;
  }
}

.popup.show {
  display: block;
  opacity: 1;
}

.navbar-container {
  position: absolute;
  top: -47px;
  left: 0;
  z-index: 2;
}
</style>
