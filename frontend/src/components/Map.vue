<template>
  <div>
    <div class="navbar-container" v-if="selectFactoryMode">
      <app-navbar :dark="false" :fixed="true" @back="onNavBack">
        新增資訊
      </app-navbar>
    </div>

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
          <app-button @click="onClickCreateFactoryButton">我要新增違建工廠</app-button>
        </div>

        <div class="choose-location-button" v-if="selectFactoryMode">
          <app-button
            @click="onClickFinishSelectFactoryPositionButton"
            :disabled="!factoryValid"
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
import { createComponent, onMounted, ref, inject } from '@vue/composition-api'
import { initializeMap, MapFactoryController, getStatusBorderColor, getFactoryStatus } from '../lib/map'
import { getFactories } from '../api'
import { MainMapControllerSymbol } from '../symbols'
import { Overlay } from 'ol'
import OverlayPositioning from 'ol/OverlayPositioning'
import { FactoryStatus, FactoryData, FactoryStatusText } from '../types'
import { useBackPressed } from '../lib/useBackPressed'
import { useGA } from '@/lib/useGA'

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
    const { event } = useGA()
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
        const status = getFactoryStatus(factory)
        popupData.value.color = getStatusBorderColor(status)
        popupData.value.status = FactoryStatusText[status][0]
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
        positioning: OverlayPositioning.BOTTOM_LEFT
      })

      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      const mapController = initializeMap(root.value!, {
        onMoved: async function ([longitude, latitude, range], canPlaceFactory) {
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
            popupData.value.show = false
          }
        }
      })

      mapController.mapInstance.map.addOverlay(popupOverlay)
      mapControllerRef.value = mapController

      mapController.mapInstance.setLUILayerVisible(false)
    })

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
      popupData.value.show = false

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
      popup,
      factoryValid,
      zoomToGeolocation: function () {
        if (mapControllerRef.value) {
          event('zoomToGeolocation')
          mapControllerRef.value.mapInstance.zoomToGeolocation()
        }
      },
      onNavBack () {
        onBack()
      },
      popupData,
      onClickEditFactoryData,
      onClickCreateFactoryButton,
      onClickFinishSelectFactoryPositionButton
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
}

.map {
  height: 100%;
}

.factory-button-group {
  position: fixed;
  bottom: 60px;

  .create-factory-button {
    transform: translateX(calc(50vw - 102px));
  }

  .choose-location-button {
    position: relative;
    transform: translateX(calc(50vw - 72px));

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
