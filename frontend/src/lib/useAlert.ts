import { inject, provide, reactive } from '@vue/composition-api'

const AlertStateSymbol = Symbol('AlertState')

enum AlertLevel {
  info = 'info',
  warn = 'warn',
  error = 'error'
}

type Alert = {
  level: AlertLevel,
  title: string,
  dismissText: string
}

type AlertState = {
  alert: Alert | null,
  timeout?: number
}

export const provideAlertState = () => {
  const alertState = reactive({
    alert: null
  })

  provide(AlertStateSymbol, alertState)

  return [alertState]
}

export const alertActions = (state: AlertState) => ({
  showAlert: function (title: string, timeouts: number = 3000, level: AlertLevel = AlertLevel.warn, dismissText = '此錯誤訊息將在3秒後消失。') {
    state.alert = {
      title,
      level,
      dismissText
    }

    state.timeout = window.setTimeout(() => {
      state.alert = null
      state.timeout = undefined
    }, timeouts)
  },

  dismissAlert: function () {
    state.alert = null

    if (state.timeout) {
      window.clearTimeout(state.timeout)
      state.timeout = undefined
    }
  }
})

export const useAlertState: () => [AlertState, ReturnType<typeof alertActions>] = () => {
  const alertState = inject(AlertStateSymbol) as AlertState

  return [alertState, alertActions(alertState)]
}

