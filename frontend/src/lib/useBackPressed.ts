export function useBackPressed (onBack: () => void) {
  const hideModal = (event: PopStateEvent) => {
    if (event.state === 'backPressed') {
      onBack()
    }
  }

  window.history.pushState('backPressed', '', null)
  window.history.pushState('dummy', '', null)
  window.addEventListener('popstate', hideModal, { once: true })
}
