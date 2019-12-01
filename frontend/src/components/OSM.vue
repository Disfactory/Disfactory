<template>
  <div ref="root" class="map" />
</template>

<script lang="ts">
import { createComponent, onMounted, ref } from '@vue/composition-api'
import 'ol/ol.css'
import { initializeMap } from '../lib/map'

export default createComponent({
  setup () {
    const root = ref<HTMLElement>(null)

    onMounted(() => {
      initializeMap(root.value!)
    })

    return { root }
  }
})
</script>

<style lang="scss" scoped>
.map {
  top: 0;
  bottom: 0;
  width: 100%;
  height: calc(100vh - 47px);
}
</style>
