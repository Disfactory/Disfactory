<template>
  <div id="app">
    <app-navbar :hide="createFactoryPageOpen" :fixed="true">農地違章工廠舉報</app-navbar>

    <filter-modal :open="filterModalOpen" :dismiss="closeFilterModal" />
    <create-factory-success-modal
      :open="createFactorySuccessModalOpen"
      :dismiss="() => setCreateFactorySuccessModal(false)"
    />

    <Map
      :openCreateFactoryForm="openCreateFactoryForm"
      :openEditFactoryForm="openEditFactoryForm"
      :selectFactoryMode="selectFactoryMode"
      :exitSelectFactoryMode="exitSelectFactoryMode"
      :setFactoryLocation="setFactoryLocation"
      :openFilterModal="openFilterModal"

    />

    <form-page
      v-if="createFactoryPageOpen"
      :mode="formMode"
      :factoryData="editingFactory"
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
import { createComponent, ref, provide } from '@vue/composition-api'

import Map from '@/components/Map.vue'
import AppNavbar from '@/components/AppNavbar.vue'
import AppButton from '@/components/AppButton.vue'
import FilterModal from '@/components/FilterModal.vue'
import CreateFactorySuccessModal from '@/components/CreateFactorySuccessModal.vue'
import FormPage from '@/components/FormPage.vue'

import { MapFactoryController } from './lib/map'
import { MainMapControllerSymbol } from './symbols'

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
    const openFilterModal = () => {
      filterModalOpen.value = true
    }

    const formMode = ref('create')
    const editingFactory = ref(null)

    const createFactoryPageOpen = ref(false)
    const toggleFactoryPage = () => {
      createFactoryPageOpen.value = !createFactoryPageOpen.value
    }

    const openCreateFactoryForm = () => {
      editingFactory.value = null
      formMode.value = 'create'
      createFactoryPageOpen.value = true
    }

    const openEditFactoryForm = (factory) => {
      editingFactory.value = factory
      formMode.value = 'edit'
      createFactoryPageOpen.value = true
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
    const setCreateFactorySuccessModal = (open: boolean) => {
      createFactorySuccessModalOpen.value = open
    }

    // register global accessible map instance
    provide(MainMapControllerSymbol, ref<MapFactoryController>(null))

    return {
      filterModalOpen,
      openFilterModal,
      closeFilterModal,

      createFactorySuccessModalOpen,
      setCreateFactorySuccessModal,

      createFactoryPageOpen,
      openCreateFactoryForm,
      openEditFactoryForm,
      closeFactoryPage,

      selectFactoryMode,
      enterSelectFactoryMode,
      exitSelectFactoryMode,
      factoryLocation,
      setFactoryLocation,

      formMode,
      editingFactory
    }
  }
})
</script>

<style lang="scss">
@import '~@/styles/index';
</style>
