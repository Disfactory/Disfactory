<template>
  <div id="app">
    <app-navbar :hide="appState.factoryFormOpen || appState.selectFactoryMode" :fixed="true" @menu="toggleSidebar">農地違章工廠舉報</app-navbar>
    <app-sidebar v-model="appState.sidebarOpen" :clickActions="sidebarActions" />

    <filter-modal :open="appState.filterModalOpen" :dismiss="closeFilterModal" />
    <create-factory-success-modal
      :open="appState.createFactorySuccessModalOpen"
      :dismiss="() => setCreateFactorySuccessModal(false)"
    />
    <about-modal :open="aboutModalOpen" :dismiss="closeAboutModal" />
    <contact-modal :open="contactModalOpen" :dismiss="closeContactModal" />

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
import AppSidebar from './components/AppSidebar.vue'
import FilterModal from '@/components/FilterModal.vue'
import AboutModal from '@/components/AboutModal.vue'
import ContactModal from '@/components/ContactModal.vue'
import CreateFactorySuccessModal from '@/components/CreateFactorySuccessModal.vue'
import FormPage from '@/components/FormPage.vue'

import { MapFactoryController } from './lib/map'
import { MainMapControllerSymbol } from './symbols'
import { FactoryData } from './types'
import { useModal } from './lib/hooks'

export default createComponent({
  name: 'App',
  components: {
    Map,
    AppButton,
    AppNavbar,
    AppSidebar,
    FilterModal,
    AboutModal,
    ContactModal,
    CreateFactorySuccessModal,
    FormPage
  },
  setup () {
    const appState = reactive({
      // Sidebar state
      sidebarOpen: false,

      // Modal open states
      filterModalOpen: false,
      createFactorySuccessModalOpen: false,

      // Page state
      // TODO: should be rewritten with vue router?
      formMode: 'create',
      factoryFormOpen: false,
      factoryData: null as FactoryData | null,
      factoryLocation: [] as number[],

      // Map state
      selectFactoryMode: false
    })

    const toggleSidebar = () => {
      appState.sidebarOpen = !appState.sidebarOpen
    }

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

    const [aboutModalOpen, { open: openAboutModal, dismiss: closeAboutModal }] = useModal()
    const [contactModalOpen, { open: openContactModal ,dismiss: closeContactModal }] = useModal()

    return {
      appState,

      // Sidebar state
      toggleSidebar,
      sidebarActions: [
        () => {},
        () => {},
        openContactModal,
        openAboutModal
      ],

      aboutModalOpen,
      closeAboutModal,

      contactModalOpen,
      closeContactModal,

      // Modal state utilities
      openFilterModal,
      closeFilterModal,
      setCreateFactorySuccessModal,

      openCreateFactoryForm,
      openEditFactoryForm,
      closeFactoryPage,

      enterSelectFactoryMode,
      exitSelectFactoryMode,
      setFactoryLocation
    }
  }
})
</script>

<style lang="scss">
@import '~@/styles/index';
</style>
