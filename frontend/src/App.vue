<template>
  <div id="app">
    <app-navbar :hide="appState.factoryFormOpen || appState.selectFactoryMode" :fixed="true" @menu="modalActions.toggleSidebar">農地違章工廠舉報</app-navbar>
    <app-sidebar v-model="modalState.sidebarOpen" :clickActions="sidebarActions" />

    <filter-modal :open="modalState.filterModalOpen" :dismiss="modalActions.closeFilterModal" />
    <create-factory-success-modal
      :open="modalState.createFactorySuccessModal"
      :dismiss="modalActions.closeCreateFactorySuccessModal"
    />
    <update-factory-success-modal
      :open="modalState.updateFactorySuccessModal"
      :dismiss="modalActions.closeUpdateFactorySuccessModal"
    />
    <about-modal :open="modalState.aboutModalOpen" :dismiss="modalActions.closeAboutModal" />
    <contact-modal :open="modalState.contactModalOpen" :dismiss="modalActions.closeContactModal" />
    <getting-started-modal :open="modalState.gettingStartedModalOpen" :dismiss="modalActions.closeGettingStartedModal" />
    <safety-modal :open="modalState.safetyModalOpen" :dismiss="modalActions.closeSafetyModal" />

    <Map
      :openCreateFactoryForm="openCreateFactoryForm"
      :openEditFactoryForm="openEditFactoryForm"
      :selectFactoryMode="appState.selectFactoryMode"
      :enterSelectFactoryMode="enterSelectFactoryMode"
      :exitSelectFactoryMode="exitSelectFactoryMode"
      :setFactoryLocation="setFactoryLocation"
      :openFilterModal="modalActions.openFilterModal"
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
import UpdateFactorySuccessModal from '@/components/UpdateFactorySuccessModal.vue'

import { MapFactoryController } from './lib/map'
import { MainMapControllerSymbol } from './symbols'
import { FactoryData } from './types'
import { provideModalState, useModalState } from './lib/hooks'
import { providePopupState } from './lib/factoryPopup'
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
    UpdateFactorySuccessModal,
    FormPage
  },
  setup (_, context) {
    provideGA(context)
    providePopupState()

    provideModalState()
    localStorage.setItem('use-app', 'true')

    const [modalState, modalActions] = useModalState()

    const { pageview, event } = useGA()

    const appState = reactive({
      // Page state
      // TODO: should be rewritten with vue router?
      formMode: 'create',
      factoryFormOpen: false,
      factoryData: null as FactoryData | null,
      factoryLocation: [] as number[],

      // Map state
      selectFactoryMode: false
    })

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
      pageview('/edit')
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

    return {
      appState,

      sidebarActions: [
        () => {},
        modalActions.openSafetyModal,
        modalActions.openContactModal,
        modalActions.openAboutModal
      ],

      openCreateFactoryForm,
      openEditFactoryForm,
      closeFactoryPage,

      enterSelectFactoryMode,
      exitSelectFactoryMode,
      setFactoryLocation,

      modalState,
      modalActions
    }
  }
})
</script>

<style lang="scss">
@import '~@/styles/index';
</style>
