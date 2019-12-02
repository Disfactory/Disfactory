<template>
  <div id="app">
    <app-navbar :hide="createFactoryPageOpen" :fixed="true">農地違章工廠舉報</app-navbar>
    <filter-modal :open="filterModalOpen" :dismiss="closeFilterModal" />
    <Map
      :toggleFactoryPage="toggleFactoryPage"
      :selectFactoryMode="selectFactoryMode"
      :exitSelectFactoryMode="exitSelectFactoryMode"
    />

    <form-page
      v-if="createFactoryPageOpen"
      :close="closeFactoryPage"
      :selectFactoryMode="selectFactoryMode"
      :enterSelectFactoryMode="enterSelectFactoryMode"
      :exitSelectFactoryMode="exitSelectFactoryMode"
    />
  </div>
</template>

<script lang="ts">
import Map from '@/components/Map.vue'
import AppNavbar from '@/components/AppNavbar.vue'
import AppButton from '@/components/AppButton.vue'
import FilterModal from '@/components/FilterModal.vue'

import FormPage from '@/components/FormPage.vue'

import { createComponent, ref } from '@vue/composition-api'

export default createComponent({
  name: 'App',
  components: {
    Map,
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

    const selectFactoryMode = ref(false)
    const enterSelectFactoryMode = () => {
      selectFactoryMode.value = true
    }
    const exitSelectFactoryMode = () => {
      selectFactoryMode.value = false
    }

    return {
      filterModalOpen,
      closeFilterModal,

      createFactoryPageOpen,
      toggleFactoryPage,
      closeFactoryPage,

      selectFactoryMode,
      enterSelectFactoryMode,
      exitSelectFactoryMode
    }
  }
})
</script>

<style lang="scss">
@import '~@/styles/index';
</style>
