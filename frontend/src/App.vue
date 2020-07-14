<template>
  <v-app>
    <v-app-bar app color="#6E8501" dark clipped-right>
      <v-toolbar-title>農地工廠回報</v-toolbar-title>
      <v-spacer />
      <div class="d-none d-sm-flex">
        <v-btn text @click="sidebarActions[0]">
          使用教學
        </v-btn>
        <v-btn text @click="sidebarActions[1]">
          安全須知
        </v-btn>
        <v-btn text @click="sidebarActions[2]">
          聯絡我們
        </v-btn>
        <v-btn text :href="sidebarActions[4]" target="_blank">
          關於舉報系統
        </v-btn>
      </div>
      <v-app-bar-nav-icon class="d-flex d-sm-none" @click="drawer = !drawer" />
    </v-app-bar>
    <v-navigation-drawer v-model="drawer" app right hide-overlay stateless clipped>
      <v-list
        nav
        dense
      >
        <v-list-item-group
          v-model="group"
          active-class="deep-purple--text text--accent-4"
        >
          <v-list-item @click="sidebarActions[0]">
            <v-list-item-title>使用教學</v-list-item-title>
          </v-list-item>

          <v-list-item @click="sidebarActions[1]">
            <v-list-item-title>安全須知</v-list-item-title>
          </v-list-item>

          <v-list-item @click="sidebarActions[2]">
            <v-list-item-title>聯絡我們</v-list-item-title>
          </v-list-item>

          <v-list-item :href="sidebarActions[4]" target="_blank">
            <v-list-item-title>關於舉報系統</v-list-item-title>
          </v-list-item>
        </v-list-item-group>
      </v-list>
    </v-navigation-drawer>

    <v-main>
      <!-- alert or modal -->
      <app-alert :alert="alertState.alert" :dismiss="alertActions.dismissAlert" />
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
      <!-- alert or modal -->
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
    </v-main>
  </v-app>
</template>

<script lang="ts">
import { createComponent, ref, provide } from '@vue/composition-api'

import Map from '@/components/Map.vue'
import AppNavbar from '@/components/AppNavbar.vue'
import AppButton from '@/components/AppButton.vue'
import AppSidebar from './components/AppSidebar.vue'
import AppAlert from '@/components/AppAlert.vue'
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
import { provideGA } from './lib/useGA'
import { provideAppState, useAppState } from './lib/appState'
import { provideAlertState, useAlertState } from './lib/useAlert'
import { VApp, VAppBar, VToolbarTitle, VSpacer, VBtn, VNavigationDrawer, VList, VListGroup, VListItemGroup, VListItemTitle } from 'vuetify/lib'

export default createComponent({
  name: 'App',
  components: {
    VApp,
    VAppBar,
    VToolbarTitle,
    VSpacer,
    VBtn,
    VNavigationDrawer,
    VList,
    VListGroup,
    VListItemGroup,
    VListItemTitle,
    Map,
    AppAlert,
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
  setup (_, context) {
    provideGA(context)
    providePopupState()
    provideAppState()
    provideAlertState()

    provideModalState()

    const [modalState, modalActions] = useModalState()
    const [appState, appActions] = useAppState()
    const [alertState, alertActions] = useAlertState()

    // register global accessible map instance
    provide(MainMapControllerSymbol, ref<MapFactoryController>(null))

    const drawer = ref(false)
    return {
      appState,
      alertState,
      alertActions,
      appActions,
      sidebarActions: [
        modalActions.openTutorialModal,
        modalActions.openSafetyModal,
        modalActions.openContactModal,
        'https://about.disfactory.tw/#section-f_c360c8de-447e-4c0a-a856-4af18b9a5240',
        'https://about.disfactory.tw'
      ],
      modalState,
      modalActions,
      drawer
    }
  }
})
</script>

<style lang="scss">
@import '~@/styles/index';
</style>
