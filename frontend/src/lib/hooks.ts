import { ref, Ref, provide, inject, reactive, InjectionKey } from '@vue/composition-api'

export const useModal = (defaultOpen = false): [Ref<boolean>, { open: () => void, dismiss: () => void }] => {
  const state = ref(defaultOpen)

  const open = () => {
    state.value = true
  }

  const dismiss = () => {
    state.value = false
  }

  return [
    state,
    {
      open,
      dismiss
    }
  ]
}

const ModalStateSymbol: InjectionKey<ModalState> = Symbol('ModalStateSymbol')

export const provideModalState = () => {
  const modalState = reactive({
    updateFactorySuccessModal: false,
    createFactorySuccessModal: false,
    aboutModalOpen: false,
    contactModalOpen: false,
    safetyModalOpen: false,
    gettingStartedModalOpen: localStorage.getItem('use-app') !== 'true',
    tutorialModalOpen: false,

    sidebarOpen: false,
    filterModalOpen: false
  })

  provide(ModalStateSymbol, modalState)

  return modalState
}

type ModalState = ReturnType<typeof provideModalState>

type ModalActions = {
  openUpdateFactorySuccessModal: Function,
  closeUpdateFactorySuccessModal: Function,

  openCreateFactorySuccessModal: Function,
  closeCreateFactorySuccessModal: Function,

  openAboutModal: Function,
  closeAboutModal: Function,

  openContactModal: Function,
  closeContactModal: Function,

  openSafetyModal: Function,
  closeSafetyModal: Function,

  openGettingStartedModal: Function,
  closeGettingStartedModal: Function,

  toggleSidebar: Function,

  closeFilterModal: Function,
  openFilterModal: Function,

  closeTutorialModal: Function,
  openTutorialModal: Function
}

export const useModalState: () => [ModalState, ModalActions] = () => {
  const modalState = inject(ModalStateSymbol)

  if (!modalState) {
    throw new Error('Use useModalState before provideModalState')
  }

  const openUpdateFactorySuccessModal = () => { modalState.updateFactorySuccessModal = true }
  const closeUpdateFactorySuccessModal = () => { modalState.updateFactorySuccessModal = false }

  const openCreateFactorySuccessModal = () => { modalState.createFactorySuccessModal = true }
  const closeCreateFactorySuccessModal = () => { modalState.createFactorySuccessModal = false }

  const openAboutModal = () => { modalState.aboutModalOpen = true }
  const closeAboutModal = () => { modalState.aboutModalOpen = false }

  const openContactModal = () => { modalState.contactModalOpen = true }
  const closeContactModal = () => { modalState.contactModalOpen = false }

  const openSafetyModal = () => { modalState.safetyModalOpen = true }
  const closeSafetyModal = () => { modalState.safetyModalOpen = false }

  const openGettingStartedModal = () => { modalState.gettingStartedModalOpen = true }
  const closeGettingStartedModal = () => { modalState.gettingStartedModalOpen = false }

  const openTutorialModal = () => { modalState.tutorialModalOpen = true }
  const closeTutorialModal = () => { modalState.tutorialModalOpen = false }

  const toggleSidebar = () => {
    const open = !modalState.sidebarOpen
    modalState.sidebarOpen = open
  }

  const closeFilterModal = () => {
    modalState.filterModalOpen = false
  }
  const openFilterModal = () => {
    modalState.filterModalOpen = true
  }

  const modalActions = {
    openUpdateFactorySuccessModal,
    closeUpdateFactorySuccessModal,

    openCreateFactorySuccessModal,
    closeCreateFactorySuccessModal,

    openAboutModal,
    closeAboutModal,

    openContactModal,
    closeContactModal,

    openSafetyModal,
    closeSafetyModal,

    openGettingStartedModal,
    closeGettingStartedModal,

    openTutorialModal,
    closeTutorialModal,

    toggleSidebar,
    openFilterModal,
    closeFilterModal
  }

  return [modalState, modalActions]
}
