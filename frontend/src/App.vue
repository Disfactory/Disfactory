<template>
  <div id="app">
    <app-navbar :hide="appState.factoryFormOpen" :fixed="true">農地違章工廠舉報</app-navbar>

    <filter-modal :open="appState.filterModalOpen" :dismiss="closeFilterModal" />
    <create-factory-success-modal
      :open="appState.createFactorySuccessModalOpen"
      :dismiss="() => setCreateFactorySuccessModal(false)"
    />

    <Map
      :openCreateFactoryForm="openCreateFactoryForm"
      :openEditFactoryForm="openEditFactoryForm"
      :selectFactoryMode="appState.selectFactoryMode"
      :enterSelectFactoryMode="enterSelectFactoryMode"
      :exitSelectFactoryMode="exitSelectFactoryMode"
      :setFactoryLocation="setFactoryLocation"
      :openFilterModal="openFilterModal"
    />

    <form-page
      v-if="appState.factoryFormOpen"

      :mode="appState.formMode"
      :factoryData="appState.factoryData"
      :close="closeFactoryPage"
      :selectFactoryMode="appState.selectFactoryMode"
      :enterSelectFactoryMode="enterSelectFactoryMode"
      :exitSelectFactoryMode="exitSelectFactoryMode"
      :factoryLocation="appState.factoryLocation"
      :setCreateFactorySuccessModal="setCreateFactorySuccessModal"
    />

  </div>
</template>

<script lang="ts">
import { createComponent, ref, provide, reactive } from '@vue/composition-api'

import Map from '@/components/Map.vue'
import AppNavbar from '@/components/AppNavbar.vue'
import AppButton from '@/components/AppButton.vue'
import FilterModal from '@/components/FilterModal.vue'
import CreateFactorySuccessModal from '@/components/CreateFactorySuccessModal.vue'
import FormPage from '@/components/FormPage.vue'

import { MapFactoryController } from './lib/map'
import { MainMapControllerSymbol } from './symbols'
import { FactoryData } from './types'

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
    const appState = reactive({
      // Modal open states
      filterModalOpen: false,
      createFactorySuccessModalOpen: false,

      // Page State
      // TODO: should be rewritten with vue router?
      formMode: 'create',
      factoryFormOpen: false,
      factoryData: null as FactoryData | null,
      factoryLocation: [] as number[],

      // Map state
      selectFactoryMode: false
    })

    // Modal state utilities
    function closeFilterModal () {
      appState.filterModalOpen = false
    }

    function openFilterModal () {
      appState.filterModalOpen = true
    }

    function setCreateFactorySuccessModal (open: boolean) {
      appState.createFactorySuccessModalOpen = open
    }

    // Form Editing functions
    const openCreateFactoryForm = () => {
      appState.factoryData = null
      appState.formMode = 'create'
      appState.factoryFormOpen = true
    }

    const openEditFactoryForm = (factory: FactoryData) => {
      appState.factoryData = factory
      appState.formMode = 'edit'
      appState.factoryFormOpen = true
    }

    function closeFactoryPage () {
      appState.factoryFormOpen = false
    }

    const setFactoryLocation = (value: [number, number]) => {
      appState.factoryLocation = value
    }

    function enterSelectFactoryMode () {
      appState.selectFactoryMode = true
    }
    function exitSelectFactoryMode () {
      appState.selectFactoryMode = false
    }

    // register global accessible map instance
    provide(MainMapControllerSymbol, ref<MapFactoryController>(null))

    return {
      appState,

      // Modal state utilities
      openFilterModal,
      closeFilterModal,
      setCreateFactorySuccessModal,

      openCreateFactoryForm,
      openEditFactoryForm,
      closeFactoryPage,

      enterSelectFactoryMode,
      exitSelectFactoryMode,
      setFactoryLocation,
    }
  }
})
</script>

<style lang="scss">
@import '~@/styles/index';
</style>
