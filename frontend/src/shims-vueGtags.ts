declare module 'vue-gtag'

declare module 'vue/types/vue' {
  interface Vue {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    $gtag: any
  }
}
