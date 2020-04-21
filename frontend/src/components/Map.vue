<template>
  <div>
    <div class="navbar-container" v-if="selectFactoryMode">
      <app-navbar :dark="false" :fixed="true" @back="onNavBack" @menu="modalActions.toggleSidebar">
        新增資訊
      </app-navbar>
    </div>

    <div class="map-container">
      <div ref="root" class="map"></div>

      <div ref="popup" :class="['popup', { show: popupState.show }]" :style="{ borderColor: popupData.color }">
        <div class="close" @click="popupState.show = false" data-label="map-popup-close" />
        <small :style="{ color: popupData.color }">{{ popupData.status }}</small>
        <h3>{{ popupData.name }}</h3>
        <p class="summary">{{ popupData.summary }}</p>
        <app-button outline @click="onClickEditFactoryData" :color="getButtonColorFromStatus()" data-label="map-popup-modify">
          補充資料
        </app-button>
      </div>

      <div class="region-alert" v-if="selectFactoryMode">
        白色區域：農地範圍，為可回報範圍。<br>灰色區域：非農地範圍，不在回報範圍內。
      </div>

      <div class="ol-map-search ol-unselectable ol-control" @click="openFilterModal" data-label="map-search" v-show="!selectFactoryMode">
        <button>
          <img src="/images/filter.svg" alt="search">
        </button>
      </div>

      <div class="ol-fit-location ol-unselectable ol-control" @click="zoomToGeolocation" data-label="map-locate">
        <button>
          <img src="/images/locate.svg" alt="locate">
        </button>
      </div>

      <div class="center-point" v-if="selectFactoryMode && !locationTooltipVisibility" />
      <div class="location-tooltip-backdrop" v-if="selectFactoryMode && showLocationInput" @click="dismissLocationInput" />
      <div class="location-tooltip" v-if="selectFactoryMode && locationTooltipVisibility">
        <div class="circle" />
        <div class="line" />
        <div class="box flex justify-between" v-if="!showLocationInput">
          <p>
            經度：{{ factoryLngLat[0].toFixed(7) }}
            <br>
            緯度：{{ factoryLngLat[1].toFixed(7) }}
            <br>
            <small>以上經緯度版本為WGS84</small>
          </p>

          <div class="flex align-items-end">
            <app-button color="white" small @click="onClickLocationSearch">搜尋經緯度</app-button>
          </div>
        </div>
        <div class="box box-input flex flex-column" v-if="showLocationInput">
          <div>
            <label>經度：</label>
            <app-text-field type="number" placeholder="請輸入經度。例：121.5253618" small v-model="inputLongitude" />
          </div>

          <div>
            <label>緯度：</label>
            <app-text-field type="number" placeholder="請輸入緯度。例：25.0459660" small v-model="inputLatitude" />
          </div>

          <div style="text-align: center;">
            <app-button color="white" small auto @click="onClickSubmitLocation">定位</app-button>
          </div>
        </div>
      </div>

      <div class="factory-button-group">
        <div class="factory-secondary-actions-group">
          <div class="ol-switch-luilayer-visibility ol-unselectable ol-control" data-label="map-set-luilayer-visibility" @click="toggleLUILayerVisibility" v-if="!selectFactoryMode">
            <button>
              {{ setLUILayerVisibilityText }}
            </button>
          </div>

          <div class="ol-switch-base ol-unselectable ol-control" @click="switchBaseMap" data-label="map-switch-base">
            <button>
              {{ baseMapName }}
            </button>
          </div>

          <div class="ol-switch-base ol-unselectable ol-control" @click="toggleLocationTooltipVisibility" data-label="map-location-tooltip" v-if="selectFactoryMode">
            <button>
              {{ locationTooltipControlText }}
            </button>
          </div>
        </div>

        <div class="create-factory-button" v-if="!selectFactoryMode">
          <app-button @click="onClickCreateFactoryButton" data-label="map-create-factory" color="dark-green">我想新增可疑工廠</app-button>
        </div>

        <div class="choose-location-button" v-if="selectFactoryMode">
          <app-button
            @click="onClickFinishSelectFactoryPositionButton"
            data-label="map-select-position"
            color="dark-green"
          >
            選擇此地點
          </app-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import AppButton from '@/components/AppButton.vue'
import AppNavbar from '@/components/AppNavbar.vue'
import AppTextField from '@/components/AppTextField.vue'
import { createComponent, onMounted, ref, inject, computed } from '@vue/composition-api'
import { initializeMap, MapFactoryController, getFactoryStatus } from '../lib/map'
import { getFactories } from '../api'
import { MainMapControllerSymbol } from '../symbols'
import { Overlay } from 'ol'
import OverlayPositioning from 'ol/OverlayPositioning'
import { FactoryStatus } from '../types'
import { useBackPressed } from '../lib/useBackPressed'
import { useGA } from '@/lib/useGA'
import { useModalState } from '../lib/hooks'
import { useFactoryPopup, getPopupData } from '../lib/factoryPopup'
import { useAppState } from '../lib/appState'
import { useAlertState } from '../lib/useAlert'
import { permalink } from '../lib/permalink'

export default createComponent({
  components: {
    AppButton,
    AppNavbar,
    AppTextField
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
    const { event } = useGA()
    const root = ref<HTMLElement>(null)
    const popup = ref<HTMLDivElement>(null)
    const factoryValid = ref(false)
    const factoryLngLat = ref<number[]>([])
    const mapControllerRef = inject(MainMapControllerSymbol, ref<MapFactoryController>())

    const [, modalActions] = useModalState()
    const [appState] = useAppState()
    const [, alertActions] = useAlertState()

    const [popupState] = useFactoryPopup()
    const popupData = computed(() => appState.factoryData ? getPopupData(appState.factoryData) : {})
    const baseMap = ref(0)
    const baseMapName = computed(() => '切換不同地圖')

    const luiVisibibility = ref(mapControllerRef?.value?.mapInstance.getLUILayerVisible() || false)
    const setLUILayerVisibilityText = computed(() => {
      if (luiVisibibility.value) {
        return '隱藏農地範圍'
      } else {
        return '顯示農地範圍'
      }
    })
    const toggleLUILayerVisibility = () => {
      const bool = !luiVisibibility.value

      mapControllerRef?.value?.mapInstance.setLUILayerVisible(bool)
    }

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

    const locationTooltipVisibility = ref(false)
    const showLocationInput = ref(false)
    const toggleLocationTooltipVisibility = () => {
      locationTooltipVisibility.value = !locationTooltipVisibility.value
    }
    const locationTooltipControlText = computed(() => {
      if (locationTooltipVisibility.value) {
        return '隱藏經緯度'
      } else {
        return '顯示經緯度'
      }
    })
    const inputLongitude = ref('')
    const inputLatitude = ref('')
    const onClickLocationSearch = () => {
      showLocationInput.value = true
    }
    const dismissLocationInput = () => {
      showLocationInput.value = false
    }
    const onClickSubmitLocation = () => {
      if (!mapControllerRef.value) return

      const lng = parseFloat(inputLongitude.value)
      const lat = parseFloat(inputLatitude.value)
      if (!inputLongitude.value ||
          !inputLatitude.value ||
          isNaN(lng) ||
          isNaN(lat)
      ) {
        // TODO: show invalid input error
        dismissLocationInput()
      } else {
        mapControllerRef.value.mapInstance.setCoordinate(lng, lat)
        dismissLocationInput()
      }
    }

    onMounted(() => {
      const popupOverlay = new Overlay({
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        element: popup.value!,
        positioning: OverlayPositioning.BOTTOM_LEFT
      })

      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      const mapController = initializeMap(root.value!, {
        onMoved: async function ([longitude, latitude, range, zoom], canPlaceFactory) {
          permalink.lat(latitude)
          permalink.lng(longitude)
          permalink.zoom(zoom)
          window.location.hash = permalink.dumps()

          factoryValid.value = canPlaceFactory
          factoryLngLat.value = [longitude, latitude]
          event('moveMap')
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
            event('clickPopup')
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            popupOverlay.setPosition((feature.getGeometry() as any).getCoordinates())
            setPopup(feature.getId() as string)
          } else {
            popupState.show = false
          }
        },
        onLUILayerVisibilityChange: function (visible) {
          luiVisibibility.value = visible
        },
        onZoomed: function (zoom) {
          permalink.zoom(zoom)
          window.location.hash = permalink.dumps()
        }
      }, {
        getInitialLocation: function () {
          permalink.load(window.location)

          if (permalink.dumps() !== '') {
            // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
            return [permalink.lng()!, permalink.lat()!, permalink.zoom()!]
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
      locationTooltipVisibility.value = false
      showLocationInput.value = false

      useBackPressed(onBack)
    }

    function onClickFinishSelectFactoryPositionButton () {
      if (!mapControllerRef.value) return

      if (!factoryValid.value) {
        alertActions.showAlert('此地點不在農地範圍內，\n請回報在農地範圍內的工廠。')
        return
      }

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
      toggleLUILayerVisibility,
      setLUILayerVisibilityText,
      zoomToGeolocation: function () {
        if (mapControllerRef.value) {
          event('zoomToGeolocation')
          try {
            mapControllerRef.value.mapInstance.zoomToGeolocation()
          } catch (err) {
            alertActions.showAlert('您沒開放手機定位權限， \n請開放定位權限以用定位功能。')
          }
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
      },
      locationTooltipVisibility,
      toggleLocationTooltipVisibility,
      locationTooltipControlText,
      factoryLngLat,
      showLocationInput,
      onClickLocationSearch,
      onClickSubmitLocation,
      dismissLocationInput,
      inputLongitude,
      inputLatitude
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

  .ol-switch-base, .ol-switch-luilayer-visibility {
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
  }
}

.factory-secondary-actions-group {
  max-width: 300px;
  margin: 0 auto;

  display: flex;
  margin-bottom: 10px;
  justify-content: center;

  .ol-control:last-child {
    margin-left: 5px;
  }
}

.center-point {
  width: 25px;
  height: 25px;
  border-radius: 50%;
  display: block;
  background-color: $red-color;
  border: solid 1px white;

  position: fixed;
  top: 50%;
  left: 0;
  z-index: 2;

  transform: translate(calc(50vw - 12.5px), 12.5px);
}

.location-tooltip {
  width: 0.1px;
  height: 0.1px;

  position: fixed;
  top: 50%;
  left: 50vw;

  z-index: 2;

  .circle {
    position: absolute;
    background-color: $dark-green-color;

    transform: translate(-12.5px, 12.5px);

    width: 25px;
    height: 25px;
    border-radius: 50%;
    display: block;
    border: solid 1px white;
  }

  .line {
    width: 4px;
    height: 60px;
    background-color: $dark-green-color;
    border-width: 0 1px;
    border-style: solid;
    border-color: white;

    position: absolute;
    transform: translate(-2px, -46px);
  }

  .box {
    width: 287px;
    height: 85px;
    background-color: $dark-green-color;
    color: white;
    padding: 12px 18px;
    border: solid 1px white;

    transform: translate(-143.5px, -130px);

    p {
      margin: 0;
      font-size: 14px;
      line-height: 1.5;
    }

    small {
      margin-top: 1em;
    }
  }

  .box-input {
    height: auto;
    transform: translate(-143.5px, -200px);

    label {
      font-size: 14px;
    }

    input {
      margin-top: 5px;
    }

    & > div:not(:last-child) {
      margin-bottom: 15px;
    }
  }
}

.location-tooltip-backdrop {
  height: 100%;
  width: 100%;
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1;
  background-color: rgba(0, 0, 0, 0.5);
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

.region-alert {
  user-select: none;
  position: absolute;
  top: 0;
  left: 0;

  background-color: #6E8501;
  color: white;
  width: 100%;
  padding: 10px 20px;
  font-size: 14px;
  line-height: 19px;
}

</style>
