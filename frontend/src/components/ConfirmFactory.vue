<template>
  <div class="confirm-factory-page">
    <h2 class="mt-2 mb-2">確認及補充工廠資訊</h2>

    <p>請確認工廠地點及照片，並補充工廠資訊。</p>

    <h3 class="mt-2 mb-2 required">工廠地點</h3>

    <minimap
      :initialFactories="initialFactories"
      :initialLocation="initialLocation"
      :pinLocation="appState.factoryLocation"
    />

    <p>
      返回<a @click="gotoStepOne">步驟(1/3)</a>編輯
    </p>

    <h3 class="mt-2 mb-2 required">工廠照片</h3>

    <p>
      返回<a @click="gotoStepTwo">步驟(2/3)</a>編輯
    </p>

    {{ JSON.stringify(previewImages) }}

    <h3 class="mt-2 mb-2 required">聯絡人暱稱</h3>

    <p>{{ formState.nickname }}</p>

    <h3 class="mt-2 mb-2 required">聯絡方式 (email或電話)</h3>

    <p>{{ formState.contact }}</p>

    <v-container class="bottom-button-container d-flex justify-center">
      <v-btn x-large rounded @click="onSubmit" style="width: 100%" v-bind="attrs" v-on="on">
        確認送出
      </v-btn>
    </v-container>
  </div>
</template>

<script lang="ts">
import { createComponent, inject, ref, onMounted } from '@vue/composition-api'

import { MainMapControllerSymbol } from '../symbols'
import { MapFactoryController, initializeMinimap } from '../lib/map'
import { useAppState } from '../lib/appState'

import Minimap from './Minimap.vue'

export default createComponent({
  name: 'ConfirmFactory',
  components: {
    Minimap
  },
  props: {
    formState: {
      type: Object,
      default: {}
    },
    previewImages: {
      type: Array,
      default: []
    }
  },
  setup () {
    const mapController = inject(MainMapControllerSymbol, ref<MapFactoryController>())
    const [appState, { pageTransition }] = useAppState()

    const initialFactories = mapController.value?.factories
    const initialLocation = mapController.value?.mapInstance.map.getView().getCenter()

    return {
      appState,
      initialFactories,
      initialLocation,
      gotoStepOne () {
        if (mapController.value) {
          pageTransition.gotoCreateStep(0)
          mapController.value.mapInstance.setLUILayerVisible(true)
        }
      },
      gotoStepTwo () {
        pageTransition.gotoCreateStep(1)
      }
    }
  }
})
</script>

<style lang="scss" scoped>
.confirm-factory-page {
  @import '@/styles/typography.scss';

  background-color: white;
  z-index: 1;
  position: absolute;
  width: 100%;
  height: 100%;

  padding-bottom: 50px;
  overflow-y: auto;
  overflow-x: hidden;

  padding: 20px 15px;
}

.bottom-button-container {
  background: white;
  position: fixed;
  bottom: 0;
  left: 0;
  padding: 10px 15px;
}
</style>
