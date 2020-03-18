/* eslint-disable @typescript-eslint/no-explicit-any */
import { SetupContext, provide, inject } from '@vue/composition-api'

const GASymbol = Symbol('GASymbol')

export function provideGA (context: SetupContext) {
  provide(GASymbol, (context.root as any).$gtag)
}

export function useGA () {
  const gtag: any = inject(GASymbol)

  if (!gtag) {
    throw new Error('use provideGA before useGA')
  }

  const pageview = (path: string) => {
    // eslint-disable-next-line @typescript-eslint/camelcase
    gtag.pageview({ page_path: path })
  }

  const event = (event: string, data: any = {}) => {
    gtag.event(event, data)
  }

  return { pageview, event }
}
