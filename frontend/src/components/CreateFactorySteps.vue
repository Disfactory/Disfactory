<template>
  <div class="create-factory-steps" v-if="appState.isCreateMode">
    <v-app-bar
      fixed
      color="white"
    >
      <div class="btn-container" :class="{ hide: appState.createStepIndex === 1 }">
        <v-btn icon @click="onBack">
          <v-icon>mdi-keyboard-backspace</v-icon>
        </v-btn>
      </div>

      <v-spacer></v-spacer>
      <v-toolbar-title>新增可疑工廠 步驟 ({{ appState.createStepIndex }}/3)</v-toolbar-title>
      <v-spacer></v-spacer>

      <div class="btn-container">
        <v-btn icon @click="cancelCreateFactory">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </div>

    </v-app-bar>


    <div class="page create-factory-step-1" v-if="appState.createStepIndex === 1">
      <v-btn rounded color="white" class="mr-2">
        顯示經緯度
      </v-btn>

      <v-btn rounded color="white">
        切換地圖模式•簡易地圖
      </v-btn>

      <v-container fluid class="choose-location-btn-container d-flex justify-center" bottom="50">
        <v-btn x-large rounded @click="chooseLocation">
          選擇此地點
        </v-btn>
      </v-container>
    </div>

    <div class="page create-factory-step-2" v-if="appState.createStepIndex === 2">
      Step 2
    </div>

    <div class="page create-factory-step-3" v-if="appState.createStepIndex === 3">
      Step 3
    </div>

  </div>
</template>

<script lang="ts">
import { createComponent, inject, ref } from '@vue/composition-api'

import { useAppState } from '../lib/appState'
import { useAlertState } from '../lib/useAlert'

import { MainMapControllerSymbol } from '../symbols'
import { MapFactoryController } from '../lib/map'

export default createComponent({
  name: 'CreateFactorySteps',
  setup (props) {
    const [appState, { pageTransition, setFactoryLocation }] = useAppState()
    const [, alertActions] = useAlertState()

    const mapController = inject(MainMapControllerSymbol, ref<MapFactoryController>())

    function cancelCreateFactory () {
      if (mapController.value) {
        mapController.value.mapInstance.setLUILayerVisible(false)
        pageTransition.closeFactoryPage()
      }
    }

    const onBack = () => {
      if (appState.createStepIndex === 1) {
        cancelCreateFactory()
      } else if (appState.createStepIndex === 2) {
        if (mapController.value) {
          mapController.value.mapInstance.setLUILayerVisible(true)
          pageTransition.previousCreateStep()
        }
      } else {
        pageTransition.previousCreateStep()
      }
    }


    return {
      appState,
      cancelCreateFactory,
      onBack,
      chooseLocation () {
        if (!mapController.value) return

        if (!appState.canPlaceFactory) {
          alertActions.showAlert('此地點不在農地範圍內，\n請回報在農地範圍內的工廠。')
          return
        }

        mapController.value.mapInstance.setLUILayerVisible(false)

        setFactoryLocation(appState.mapLngLat as [number, number])

        pageTransition.nextCreateStep()
      }
    }
  }
})
</script>

<style lang="scss" scoped>
.btn-container.hide {
  visibility: hidden;
  pointer-events: none;
}

.create-factory-steps {
  .page {
    padding: 20px 15px;

    .choose-location-btn-container {
      position: fixed;
      bottom: 50px;
    }
  }
}
</style>
