<template>
  <div class="map-container">
    <div ref="root" class="map" />

    <div class="center-point" v-if="selectFactoryMode" />

    <div class="factory-button-group">
      <div class="create-factory-button" v-if="!selectFactoryMode">
        <app-button @click="toggleFactoryPage">我要新增違建工廠</app-button>
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
import { createComponent, onMounted, ref } from '@vue/composition-api'
import 'ol/ol.css'
import { initializeMap } from '../lib/map'

export default createComponent({
  components: {
    AppButton
  },
  props: {
    toggleFactoryPage: {
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
    }
  },
  setup (props) {
    const root = ref<HTMLElement>(null)
    const factoryValid = ref(false)
    const factoryLngLat = ref<number[]>([])

    onMounted(() => {
      initializeMap(root.value!, {
        onMoved: function ([longitude, latitude], canPlaceFactory) {
          factoryLngLat.value = [longitude, latitude]
          factoryValid.value = canPlaceFactory
        }
        // TODO: do on start move to lock selection
      })
    })


    return {
      root,
      factoryValid,
      selectCenterPoint () {
        props.setFactoryLocation(factoryLngLat.value)
        props.exitSelectFactoryMode()
      }
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

  transform: translate(calc(50vw - 12.5px), calc(50vh - 12.5px));
}
</style>
