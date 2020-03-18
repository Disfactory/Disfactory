import Vue from 'vue'
import App from './App.vue'
import VueCompositionApi from '@vue/composition-api'
import './registerServiceWorker'
import VueGtag from 'vue-gtag'

Vue.config.productionTip = false
Vue.use(VueCompositionApi)

Vue.use(VueGtag, {
  config: { id: 'UA-154739393-1' },
  enabled: process.env.NODE_ENV === 'production'
})

new Vue({
  render: (h) => h(App)
}).$mount('#app')
