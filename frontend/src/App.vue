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
    <getting-started-modal :open="gettingStartedModalOpen" :dismiss="closeGettingStartedModal" />
    <safety-modal :open="safetyModalOpen" :dismiss="closeSafetyModal" />

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
import FormPage from '@/components/FormPage.vue'

import FilterModal from '@/components/FilterModal.vue'
import AboutModal from '@/components/AboutModal.vue'
import ContactModal from '@/components/ContactModal.vue'
import GettingStartedModal from '@/components/GettingStartedModal.vue'
import SafetyModal from '@/components/SafetyModal.vue'
import CreateFactorySuccessModal from '@/components/CreateFactorySuccessModal.vue'

import { MapFactoryController } from './lib/map'
import { MainMapControllerSymbol } from './symbols'
import { FactoryData } from './types'
import { useModal } from './lib/hooks'
import { provideGA, useGA } from './lib/useGA'

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
    GettingStartedModal,
    SafetyModal,
    CreateFactorySuccessModal,
    FormPage
  },
  setup (_, context) {
    provideGA(context)
    const { pageview, event } = useGA()

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
      event('toggleSidebar', { target: !appState.sidebarOpen })
      appState.sidebarOpen = !appState.sidebarOpen
    }

    // Modal state utilities
    function closeFilterModal () {
      event('closeFilterModal')
      appState.filterModalOpen = false
    }

    function openFilterModal () {
      event('openFilterModal')
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
      pageview('/create')
    }

    const openEditFactoryForm = (factory: FactoryData) => {
      appState.factoryData = factory
      appState.formMode = 'edit'
      appState.factoryFormOpen = true
      pageview('/emit')
    }

    function closeFactoryPage () {
      appState.factoryFormOpen = false
      event('closeFactoryPage')
    }

    const setFactoryLocation = (value: [number, number]) => {
      appState.factoryLocation = value
      event('setFactoryLocation')
    }

    function enterSelectFactoryMode () {
      appState.selectFactoryMode = true
      event('enterSelectFactoryMode')
    }
    function exitSelectFactoryMode () {
      appState.selectFactoryMode = false
      event('exitSelectFactoryMode')
    }

    // register global accessible map instance
    provide(MainMapControllerSymbol, ref<MapFactoryController>(null))

    const [aboutModalOpen, { open: openAboutModal, dismiss: closeAboutModal }] = useModal()
    const [contactModalOpen, { open: openContactModal, dismiss: closeContactModal }] = useModal()
    const [safetyModalOpen, { open: openSafetyModal, dismiss: closeSafetyModal }] = useModal()
    const [gettingStartedModalOpen, { dismiss: closeGettingStartedModal }] = useModal(localStorage.getItem('use-app') !== 'true')

    localStorage.setItem('use-app', 'true')

    return {
      appState,

      // Sidebar state
      toggleSidebar,
      sidebarActions: [
        () => {},
        openSafetyModal,
        openContactModal,
        openAboutModal
      ],

      aboutModalOpen,
      closeAboutModal,

      contactModalOpen,
      closeContactModal,

      gettingStartedModalOpen,
      closeGettingStartedModal,

      safetyModalOpen,
      closeSafetyModal,

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
