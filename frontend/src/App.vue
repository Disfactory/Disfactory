<template>
  <div id="app">
    <app-navbar :hide="createFactoryPageOpen" :fixed="true">農地違章工廠舉報</app-navbar>

    <filter-modal :open="filterModalOpen" :dismiss="closeFilterModal" />
    <create-factory-success-modal
      :open="createFactorySuccessModalOpen"
      :dismiss="() => setCreateFactorySuccessModal(false)"
    />

    <Map
      :toggleFactoryPage="toggleFactoryPage"
      :selectFactoryMode="selectFactoryMode"
      :exitSelectFactoryMode="exitSelectFactoryMode"
      :setFactoryLocation="setFactoryLocation"
    />

    <form-page
      v-if="createFactoryPageOpen"
      :close="closeFactoryPage"
      :selectFactoryMode="selectFactoryMode"
      :enterSelectFactoryMode="enterSelectFactoryMode"
      :exitSelectFactoryMode="exitSelectFactoryMode"
      :factoryLocation="factoryLocation"
      :setCreateFactorySuccessModal="setCreateFactorySuccessModal"
    />

  </div>
</template>

<script lang="ts">
import Map from '@/components/Map.vue'
import AppNavbar from '@/components/AppNavbar.vue'
import AppButton from '@/components/AppButton.vue'
import FilterModal from '@/components/FilterModal.vue'
import CreateFactorySuccessModal from '@/components/CreateFactorySuccessModal.vue'

import FormPage from '@/components/FormPage.vue'

import { createComponent, ref } from '@vue/composition-api'

export default createComponent({
  name: 'App',
  components: {
    Map,
    AppButton,
    AppNavbar,
    FilterModal,
    CreateFactorySuccessModal,
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

    const factoryLocation = ref<number[]>([])
    const setFactoryLocation = (value: [number, number]) => {
      factoryLocation.value = value
    }

    const selectFactoryMode = ref(false)
    const enterSelectFactoryMode = () => {
      selectFactoryMode.value = true
    }
    const exitSelectFactoryMode = () => {
      selectFactoryMode.value = false
    }

    const createFactorySuccessModalOpen = ref(false)
    const setCreateFactorySuccessModal = (open: boolean) => createFactorySuccessModalOpen.value = open

    return {
      filterModalOpen,
      closeFilterModal,

      createFactorySuccessModalOpen,
      setCreateFactorySuccessModal,

      createFactoryPageOpen,
      toggleFactoryPage,
      closeFactoryPage,

      selectFactoryMode,
      enterSelectFactoryMode,
      exitSelectFactoryMode,
      factoryLocation,
      setFactoryLocation
    }
  }
})
</script>

<style lang="scss">
@import '~@/styles/index';
</style>
