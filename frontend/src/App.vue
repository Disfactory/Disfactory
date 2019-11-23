<template>
  <div id="app">
    <OSM />
  </div>
</template>

<script lang="ts">
import OSM from './components/OSM.vue'
import { createComponent } from '@vue/composition-api'

export default createComponent({
  components: { OSM }
})
</script>

<style lang="scss">
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
