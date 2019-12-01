<template>
  <div id="app">
    <app-navbar>農地違章工廠舉報</app-navbar>
    <filter-modal :open="filterModalOpen" :dismiss="closeFilterModal" />
    <OSM />
    <div class="create-factory-button">
      <app-button @click="toggleFactoryPage">我要新增違建工廠</app-button>
    </div>

    <form-page v-if="createFactoryPageOpen" :close="closeFactoryPage"></form-page>
  </div>
</template>

<script lang="ts">
import OSM from '@/components/OSM.vue'
import AppNavbar from '@/components/AppNavbar.vue'
import AppButton from '@/components/AppButton.vue'
import FilterModal from '@/components/FilterModal.vue'

import FormPage from '@/components/FormPage.vue'

import { createComponent, ref } from '@vue/composition-api'

export default createComponent({
  name: 'App',
  components: {
    OSM,
    AppButton,
    AppNavbar,
    FilterModal,
    FormPage
  },
  setup () {
    const filterModalOpen = ref(false)
    const closeFilterModal = () => {
      filterModalOpen.value = false
    }

    const createFactoryPageOpen = ref(false)
    const toggleFactoryPage = () => {
      createFactoryPageOpen.value = !createFactoryPageOpen.value
    }

    const closeFactoryPage = () => {
      createFactoryPageOpen.value = false
    }

    return {
      filterModalOpen,
      closeFilterModal,

      createFactoryPageOpen,
      toggleFactoryPage,
      closeFactoryPage
    }
  }
})
</script>

<style lang="scss">
@import '~@/styles/index';

.create-factory-button {
  position: fixed;
  left: 50vw;
  bottom: 48px;
  transform: translateX(-50%);
}
</style>
