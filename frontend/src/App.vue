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
    <tutorial-modal :open="modalState.tutorialModalOpen" :dismiss="modalActions.closeTutorialModal" />

    <Map
      :openCreateFactoryForm="appActions.openCreateFactoryForm"
      :openEditFactoryForm="appActions.openEditFactoryForm"
      :selectFactoryMode="appState.selectFactoryMode"
      :enterSelectFactoryMode="appActions.enterSelectFactoryMode"
      :exitSelectFactoryMode="appActions.exitSelectFactoryMode"
      :setFactoryLocation="appActions.setFactoryLocation"
      :openFilterModal="modalActions.openFilterModal"
    />

    <form-page
      v-if="appState.factoryFormOpen"

      :mode="appState.formMode"
      :factoryData="appState.factoryData"
      :close="appActions.closeFactoryPage"
      :selectFactoryMode="appState.selectFactoryMode"
      :enterSelectFactoryMode="appActions.enterSelectFactoryMode"
      :exitSelectFactoryMode="appActions.exitSelectFactoryMode"
      :factoryLocation="appState.factoryLocation"
      :setCreateFactorySuccessModal="setCreateFactorySuccessModal"
    />

  </div>
</template>

<script lang="ts">
import { createComponent, ref, provide } from '@vue/composition-api'

import Map from '@/components/Map.vue'
import AppNavbar from '@/components/AppNavbar.vue'
import AppButton from '@/components/AppButton.vue'
import AppSidebar from './components/AppSidebar.vue'
import FormPage from '@/components/FormPage.vue'

import FilterModal from '@/components/FilterModal.vue'
import AboutModal from '@/components/AboutModal.vue'
import ContactModal from '@/components/ContactModal.vue'
import GettingStartedModal from '@/components/GettingStartedModal.vue'
import TutorialModal from '@/components/TutorialModal.vue'
import SafetyModal from '@/components/SafetyModal.vue'
import CreateFactorySuccessModal from '@/components/CreateFactorySuccessModal.vue'
import UpdateFactorySuccessModal from '@/components/UpdateFactorySuccessModal.vue'

import { MapFactoryController } from './lib/map'
import { MainMapControllerSymbol } from './symbols'
import { provideModalState, useModalState } from './lib/hooks'
import { providePopupState } from './lib/factoryPopup'
import { provideAppState, useAppState } from './lib/appState'

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
    TutorialModal,
    FormPage
  },
  setup () {
    providePopupState()
    provideAppState()

    provideModalState()
    localStorage.setItem('use-app', 'true')

    const [modalState, modalActions] = useModalState()
    const [appState, appActions] = useAppState()

    // register global accessible map instance
    provide(MainMapControllerSymbol, ref<MapFactoryController>(null))

    return {
      appState,
      appActions,
      sidebarActions: [
        modalActions.openTutorialModal,
        modalActions.openSafetyModal,
        modalActions.openContactModal,
        modalActions.openAboutModal
      ],
      modalState,
      modalActions
    }
  }
})
</script>

<style lang="scss">
@import '~@/styles/index';
</style>
